from ultralytics import YOLO
import os
from huggingface_hub import hf_hub_download

repo_id = "https://huggingface.co/JK-TK/PlantDiseaseDetection/blob/main/PlantDiseaseDetection.pt"

hf_hub_download(
    repo_id=repo_id,
    filename="PlantDiseaseDetection.pt"
)

def disease_detection(file_path, model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = YOLO(model_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    results = model.predict(
        source=file_path,
        save=True,
        verbose=False,
        conf=0.25
    )

    detection = []

    for result in results:

        if result.boxes is None or len(result.boxes) == 0:
            continue

        for box in result.boxes:

            class_id = int(box.cls.item())
            confidence = float(box.conf.item())

            detection.append({
                "disease_name": result.names[class_id],
                "confidence": round(confidence * 100, 2),
                "saved_path": str(result.save_dir)
            })

    if not detection:
        return []

    highest_confidence = max(
        detection,
        key=lambda x: x["confidence"]
    )

    return [highest_confidence]
