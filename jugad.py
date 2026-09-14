from __future__ import annotations
import tempfile
from pathlib import Path
import streamlit as st
from MAIN import call_models
from supabase_utils import upload_annotated_image


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Prakriti AI",
    page_icon="🌾",
    layout="centered",
)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def save_uploaded_file(uploaded_file) -> str:
    """
    Save Streamlit's uploaded file to a temporary local file.
    """

    suffix = Path(uploaded_file.name).suffix.lower()

    if not suffix:
        suffix = ".jpg"

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    )

    try:
        temp.write(uploaded_file.getbuffer())
        temp.flush()
    finally:
        temp.close()

    return temp.name


def get_annotation_path(result: dict, detection_type: str) -> str | None:
    """
    Get the actual annotated image file from the path returned by MAIN.py.

    Handles:
    - direct image file path
    - YOLO output directory such as runs/detect/predict-3
    """

    if detection_type == "disease":
        raw_path = result.get("Disease Annotation Path")
    elif detection_type == "pest":
        raw_path = result.get("Pest Annotation Path")
    else:
        return None

    if not raw_path:
        return None

    path = Path(str(raw_path))

    # Case 1: MAIN.py already returned the image file.
    if path.is_file():
        return str(path)

    # Case 2: MAIN.py returned a YOLO output directory.
    if path.is_dir():
        image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".bmp",
        }

        image_files = [
            p
            for p in path.iterdir()
            if p.is_file()
            and p.suffix.lower() in image_extensions
        ]

        if not image_files:
            return None

        # Usually there is one annotated image in this directory.
        return str(image_files[0])

    return None

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

st.title("🌾 Prakriti AI")

st.write(
    "Plant disease and pest detection with environmental analysis."
)


uploaded_file = st.file_uploader(
    "Upload plant image",
    type=["jpg", "jpeg", "png", "webp"],
)


detection_type = st.selectbox(
    "Detection Type",
    [
        "disease",
        "pest",
    ],
)


address = st.text_input(
    "Address",
    placeholder="Bhopal",
)


soil_type = st.selectbox(
    "Soil Type",
    [
        "loamy",
        "sandy",
        "clayey",
        "black",
        "red",
    ],
)


disease_category = None

if detection_type == "disease":

    disease_category = st.selectbox(
        "Disease Category",
        [
            "other",
            "rice",
            "wheat",
        ],
    )


# ---------------------------------------------------------
# ANALYZE
# ---------------------------------------------------------

if st.button(
    "Analyze",
    type="primary",
    use_container_width=True,
):

    # ---------------------------------------------
    # Validation
    # ---------------------------------------------

    if uploaded_file is None:
        st.error("Please upload an image.")
        st.stop()

    if not address.strip():
        st.error("Please enter an address.")
        st.stop()


    temp_input_path = None

    try:

        # -----------------------------------------
        # Save uploaded image
        # -----------------------------------------

        with st.spinner("Preparing image..."):

            temp_input_path = save_uploaded_file(
                uploaded_file
            )


        # -----------------------------------------
        # Run your existing MAIN.py
        # -----------------------------------------

        with st.spinner(
            "Running Prakriti AI analysis..."
        ):

            result = call_models(
                disease_or_pest=detection_type,
                address=address.strip(),
                soil_type=soil_type,
                filepath=temp_input_path,
                disease_category=disease_category,
            )


        # -----------------------------------------
        # Check result
        # -----------------------------------------

        if not isinstance(result, dict):
            st.error(
                "call_models() did not return a dictionary."
            )

            st.write(result)
            st.stop()


        # -----------------------------------------
        # Get annotation path
        # -----------------------------------------

        annotation_path = get_annotation_path(
            result,
            detection_type,
        )


        if not annotation_path:
            st.error(
                "No annotated image path was returned "
                "by the model."
            )

            st.json(result)
            st.stop()


        # -----------------------------------------
        # Verify local image
        # -----------------------------------------

        annotation_path = Path(
            annotation_path
        )

        if not annotation_path.exists():
            st.error(
                "The annotated image path returned by "
                "the model does not exist."
            )

            st.code(str(annotation_path))
            st.stop()


        # -----------------------------------------
        # Upload to Supabase
        # -----------------------------------------

        with st.spinner(
            "Uploading annotated image to Supabase..."
        ):

            image_url = upload_annotated_image(
                str(annotation_path)
            )


        # -----------------------------------------
        # Add URL to model result
        # -----------------------------------------

        result["Annotated Image URL"] = image_url


        # -----------------------------------------
        # Display success
        # -----------------------------------------

        st.success(
            "Analysis completed successfully."
        )


        # -----------------------------------------
        # Annotated image
        # -----------------------------------------

        st.subheader(
            "Annotated Image"
        )

        st.image(
            image_url,
            caption="Prakriti AI Detection Result",
            use_container_width=True,
        )


        # -----------------------------------------
        # Public URL
        # -----------------------------------------

        st.subheader(
            "Annotated Image URL"
        )

        st.code(
            image_url,
            language="text",
        )


        # -----------------------------------------
        # Result
        # -----------------------------------------

        st.subheader(
            "Analysis Result"
        )

        st.json(result)


    except Exception as e:

        st.error(
            "An error occurred while processing the request."
        )

        st.exception(e)


    finally:

        # -----------------------------------------
        # Remove temporary user upload
        # -----------------------------------------

        if temp_input_path is not None:

            try:

                temp_path = Path(
                    temp_input_path
                )

                if temp_path.exists():
                    temp_path.unlink()

            except Exception:
                pass