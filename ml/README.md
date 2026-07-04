# Heritage Trace — Phase 3: Real AI Tagging Model

This replaces the random stub in `backend/app/ml/tagger.py` with a real
image classifier, fine-tuned on a small dataset you collect from
Wikimedia Commons.

## Step 1 — Collect training images (no camera needed)

Wikimedia Commons has real, freely-licensed museum/archaeological photos —
safe to use for training since they're public domain or Creative Commons
licensed (unlike random web-scraped images).

Go to these category pages and download ~20-30 images for each into the
matching folder:

| Category | Wikimedia Commons search | Save into |
|---|---|---|
| Pottery | commons.wikimedia.org → search "ancient pottery" or "Roman pottery" | `data/pottery/` |
| Coin | search "ancient coin" or "Roman coin" | `data/coin/` |
| Sculpture | search "ancient sculpture" or "Roman sculpture" | `data/sculpture/` |
| Tool | search "ancient tool artifact" | `data/tool/` |
| Jewelry | search "ancient jewelry artifact" | `data/jewelry/` |

**How to download from Wikimedia Commons:**
1. Search the term, click "Images" filter if needed
2. Click an image → right-click the full-size version → "Save image as"
3. Save directly into the right folder (e.g. `data/pottery/pottery_01.jpg`)
4. Repeat ~20-30 times per category — tedious but only needs doing once

Aim for at least 15-20 images per category minimum; more is better.

Final structure should look like:
```
ml/
  data/
    pottery/    (20-30 images)
    coin/
    sculpture/
    tool/
    jewelry/
  train.py
  inference.py
  requirements.txt
```

## Step 2 — Install dependencies and train

```powershell
cd ml
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python train.py
```

This will:
- Download a pretrained MobileNetV3-Small (ImageNet weights) — needs
  internet access, ~10MB download, happens automatically
- Fine-tune only the final classification layer on your images (fast,
  works fine on a CPU, no GPU needed — should take a few minutes)
- Print validation accuracy per epoch so you can see it's actually learning
- Save `model.pt` and `class_names.json` when done

**What to expect:** with ~20 images per category, don't expect 95%+
accuracy — this is a small dataset. 60-80% validation accuracy is a
reasonable, honest result for a v1 and is completely fine to describe
in an interview as "given the small dataset, transfer learning got me to
X% — the natural next step would be collecting more labeled data."
That's a mature, credible thing to say; don't oversell it as
production-grade.

## Step 3 — Wire it into the backend

1. Copy `model.pt`, `class_names.json`, and `inference.py` into
   `backend/app/ml/`
2. Open `backend/app/routes/submissions.py` and change this line:
   ```python
   from app.ml.tagger import suggest_tags
   ```
   to:
   ```python
   from app.ml.inference import suggest_tags
   ```
3. Restart the backend (`Ctrl+C`, then `python run.py` again)
4. Submit a real photo (via curl, the mobile app, or PowerShell) and
   check the dashboard — you should see a real predicted category
   instead of a random one

**Keep `tagger.py` in the repo** even after switching — it documents the
v1 stub and shows the progression from placeholder to real model, which
is a nice thing to point to in an interview or README.

## Known limitation (be upfront about this if asked)

This v1 model only predicts **category** (pottery/coin/sculpture/tool/
jewelry) — era and material are left as "Unknown" since that would need
separate labeled data per attribute. A natural "future work" answer if
asked: train a multi-head model, or three separate lightweight
classifiers, once more labeled data exists.
