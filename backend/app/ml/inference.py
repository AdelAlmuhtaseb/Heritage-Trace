"""
Real inference implementation to replace the random stub in
backend/app/ml/tagger.py once you've trained a model with train.py.

This file is meant to be copied into backend/app/ml/ alongside model.pt
and class_names.json, OR you can just port the logic below directly into
tagger.py — either works, this is kept separate so it's easy to review.
"""

import json
import io
import base64
import torch
from torchvision import transforms, models
from PIL import Image
import urllib.request

import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_THIS_DIR, "model.pt")
CLASSES_PATH = os.path.join(_THIS_DIR, "class_names.json")

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

_model = None
_class_names = None


def _load_model():
    global _model, _class_names
    if _model is not None:
        return

    with open(CLASSES_PATH) as f:
        _class_names = json.load(f)

    model = models.mobilenet_v3_small(weights=None)
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = torch.nn.Linear(in_features, len(_class_names))
    model.load_state_dict(torch.load(MODEL_PATH, map_location=_device))
    model.eval()
    model.to(_device)
    _model = model


def _load_image(photo_url: str) -> Image.Image:
    """Handles both real URLs and base64 data URLs (what the mobile app sends)."""
    if photo_url.startswith("data:image"):
        header, encoded = photo_url.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        return Image.open(io.BytesIO(img_bytes)).convert("RGB")
    else:
        with urllib.request.urlopen(photo_url) as response:
            img_bytes = response.read()
        return Image.open(io.BytesIO(img_bytes)).convert("RGB")


def suggest_tags(photo_url: str) -> dict:
    """
    Drop-in replacement for the stub in tagger.py. Same function signature,
    same return shape — swap the import in submissions.py and nothing else
    needs to change.

    Note: this predicts *category* only (pottery/coin/sculpture/tool/jewelry).
    Era and material aren't predicted by this v1 model — you'd need
    separate labeled data and either a multi-head model or separate
    classifiers to add those. For now they're left as "Unknown" so the
    rest of the pipeline (dashboard, verification flow) keeps working
    unchanged.
    """
    _load_model()

    image = _load_image(photo_url)
    tensor = _transform(image).unsqueeze(0).to(_device)

    with torch.no_grad():
        outputs = _model(tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probs, 1)

    category = _class_names[predicted_idx.item()]

    return {
        "category": category,
        "era": "Unknown",       # not predicted by this model version
        "material": "Unknown",  # not predicted by this model version
        "confidence": round(confidence.item(), 2),
    }
