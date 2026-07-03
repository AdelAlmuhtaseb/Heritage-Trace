"""
Placeholder AI tagging service.

Phase 1-2: returns a stub result so the API and dashboard can be built and
tested end-to-end without a trained model yet.

Phase 3: replace `suggest_tags` with a real call to a fine-tuned image
classification model (e.g. MobileNetV3 fine-tuned on a small labeled
artifact dataset, served via TorchServe/TF-Serving, or just loaded directly
in-process with PyTorch/TensorFlow for a v1).

Keeping this behind a single function means nothing else in the codebase
needs to change when the real model is plugged in.
"""

import random

CATEGORIES = ["pottery", "coin", "sculpture", "inscription", "tool", "jewelry"]
ERAS = ["Bronze Age", "Roman", "Byzantine", "Ottoman", "Medieval", "Unknown"]
MATERIALS = ["ceramic", "stone", "metal", "glass", "bone", "unknown"]


def suggest_tags(photo_url: str) -> dict:
    """
    Given a photo URL, return suggested (category, era, material, confidence).
    Currently a random stub — swap for real inference in Phase 3.
    """
    return {
        "category": random.choice(CATEGORIES),
        "era": random.choice(ERAS),
        "material": random.choice(MATERIALS),
        "confidence": round(random.uniform(0.55, 0.95), 2),
    }
