from __future__ import annotations
from pathlib import Path
from uuid import uuid4
from urllib.parse import quote
import mimetypes
import streamlit as st
from supabase import create_client


BUCKET_NAME = "Prakriti AI"


def get_supabase_client():
    url = "https://xfpfrqwjegbwcjgoucfi.supabase.co"
    key = "sb_secret_ETMak75kzudNmTXQ64yLJw_6iDNr8Zj"

    return create_client(url, key)


def upload_annotated_image(image_path: str) -> str:
    """
    Upload an annotated image to Supabase Storage
    and return its public URL.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Annotated image not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Annotated image path is not a file: {path}"
        )

    mime_type, _ = mimetypes.guess_type(path.name)

    if mime_type is None:
        mime_type = "image/jpeg"

    if not mime_type.startswith("image/"):
        raise ValueError(
            f"Unsupported file type: {mime_type}"
        )

    extension = path.suffix.lower()

    if not extension:
        extension = ".jpg"

    # Unique filename so previous results are never overwritten.
    filename = f"{uuid4().hex}{extension}"

    storage_path = f"predictions/{filename}"

    supabase = get_supabase_client()

    with path.open("rb") as file:
        supabase.storage.from_(BUCKET_NAME).upload(
            storage_path,
            file,
            {
                "content-type": mime_type,
                "cache-control": "3600",
                "upsert": "false",
            },
        )

    base_url = "https://xfpfrqwjegbwcjgoucfi.supabase.co"

    public_url = (
        f"{base_url}/storage/v1/object/public/"
        f"{quote(BUCKET_NAME, safe='')}/"
        f"{quote(storage_path, safe='/')}"
    )

    return public_url