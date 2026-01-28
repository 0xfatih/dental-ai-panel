from pathlib import Path
from ultralytics import YOLO
import cv2
# Modeli tek sefer yüklemek için cache
_MODEL = None

# Sınıf isimleri
CLASS_NAMES = [
    "Caries",
    "Crown - bridge",
    "Filling",
    "Implant",
    "Post-screw",
    "Root Canal Obturation",
]

def get_model(weights_path: str | Path):
    global _MODEL
    if _MODEL is None:
        _MODEL = YOLO(str(weights_path))
    return _MODEL


def predict_image(weights_path: str | Path, image_path: str | Path, conf: float = 0.25):
    """
    Return: list of dict
    [
      {"label": "Caries", "score": 0.91, "x1":..., "y1":..., "x2":..., "y2":...},
      ...
    ]
    """
    model = get_model(weights_path)

    results = model.predict(source=str(image_path), conf=conf, verbose=False)
    r = results[0]

    preds = []
    if r.boxes is None:
        return preds

    # boxes.xyxy: [N,4], boxes.cls: [N], boxes.conf: [N]
    xyxy = r.boxes.xyxy.cpu().tolist()
    clss = r.boxes.cls.cpu().tolist()
    confs = r.boxes.conf.cpu().tolist()

    for (x1, y1, x2, y2), cls_id, score in zip(xyxy, clss, confs):
        cls_id = int(cls_id)
        label = CLASS_NAMES[cls_id] if 0 <= cls_id < len(CLASS_NAMES) else str(cls_id)
        preds.append({
            "label": label,
            "score": float(score),
            "x1": float(x1), "y1": float(y1), "x2": float(x2), "y2": float(y2),
        })

    return preds

def draw_bboxes(image_path, predictions, output_path):
    img = cv2.imread(str(image_path))

    for p in predictions:
        x1, y1, x2, y2 = int(p.x1), int(p.y1), int(p.x2), int(p.y2)
        label = p.label
        score = p.score * 100 if p.score <= 1 else p.score

        color = CLASS_COLORS.get(label, (0, 255, 0))  # default yeşil

        # BBox
        cv2.rectangle(
            img,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        # Label arkaplanı
        text = f"{label} %{score:.1f}"
        (tw, th), _ = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            2
        )

        cv2.rectangle(
            img,
            (x1, y1 - th - 8),
            (x1 + tw + 6, y1),
            color,
            -1
        )

        cv2.putText(
            img,
            text,
            (x1 + 3, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2
        )

    cv2.imwrite(str(output_path), img)

    # BGR format (OpenCV kullanıyor)
CLASS_COLORS = {
    "Caries": (0, 0, 255),                 # kırmızı
    "Filling": (255, 0, 0),                # mavi
    "Crown - bridge": (128, 0, 128),       # mor
    "Implant": (0, 200, 0),                # yeşil
    "Post-screw": (0, 255, 255),           # sarı
    "Root Canal Obturation": (0, 165, 255) # turuncu
}
