# Heritage Trace

A crowdsourced platform for documenting and preserving at-risk or undocumented
heritage artifacts and sites. Volunteers photograph items via a mobile app; a
self-trained AI model auto-suggests tags (category); researchers verify
submissions and track preservation status via a web dashboard.

**Live demo:**
- Dashboard: https://YOUR-NETLIFY-URL.netlify.app
- Backend API: https://heritage-trace-2.onrender.com/api/health

> Note: the backend is on a free-tier host and spins down when idle — the
> first request after inactivity may take ~30-60 seconds to respond.

## What it does

- Volunteers capture a photo of an artifact on their phone, tag its GPS
  location, and submit it
- A PyTorch image classification model (fine-tuned via transfer learning on
  MobileNetV3-Small) automatically suggests a category — pottery, coin,
  sculpture, tool, or jewelry — with 85-95% validation accuracy across
  categories
- Researchers review submissions on a web dashboard, confirm or correct the
  AI's tags, and mark preservation status

## Architecture

heritage-trace/
├── backend/          # Flask REST API — deployed on Render
│   ├── app/
│   │   ├── models/    # SQLAlchemy models: User, Submission, Verification
│   │   ├── routes/    # auth, submissions, verifications blueprints
│   │   └── ml/         # inference.py — the real trained model
│   └── tests/          # pytest suite
├── dashboard/         # React (Vite) researcher dashboard — deployed on Netlify
├── mobile/            # React Native (Expo) volunteer app
├── ml/                 # Model training script + dataset
└── .github/workflows/ci.yml   # runs backend tests on every push

## Tech stack

Python, Flask, PostgreSQL, SQLAlchemy, JWT auth, React, React Native (Expo),
PyTorch (transfer learning on MobileNetV3-Small), Render, Netlify, GitHub
Actions CI/CD

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | – | Create account (volunteer/researcher/admin) |
| POST | `/api/auth/login` | – | Get JWT token |
| POST | `/api/submissions` | JWT | Submit a photographed artifact (runs AI tagging) |
| GET | `/api/submissions` | JWT | List submissions (`?status=pending` to filter) |
| GET | `/api/submissions/<id>` | JWT | Get one submission |
| PATCH | `/api/submissions/<id>` | JWT | Edit tags/preservation status |
| POST | `/api/verifications/<id>` | JWT, researcher role | Approve/reject a submission |
| GET | `/api/verifications/<id>` | JWT | List verification history for a submission |

---

## Running it locally

You'll need three terminals open at once — backend, dashboard, and (optionally) mobile.

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
copy .env.example .env            # Windows: copy · macOS/Linux: cp

python run.py
```

Runs on `http://127.0.0.1:5000`. Confirm it's alive:
```bash
curl http://127.0.0.1:5000/api/health
```

Run the test suite:
```bash
python -m pytest tests/ -v
```

### 2. Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Runs on `http://localhost:5173`. Log in with a researcher account (register
one first via the API if you don't have one — see below).

### 3. Mobile app (optional — needs a phone with Expo Go installed)

```bash
cd mobile
npm install
npx expo start
```

Scan the QR code with the Expo Go app. **Before running**, update the
`API_BASE` constant in `app/(tabs)/index.tsx` to your computer's LAN IP
(find it via `ipconfig` / `ifconfig`) so your phone can reach the backend —
`127.0.0.1` only works for the same device.

### Creating a test account

```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"pass123","role":"researcher"}'
```

Use `"role":"volunteer"` for a mobile app account, `"role":"researcher"` for
the dashboard.

---

## Model details & limitations

The AI tagger (`backend/app/ml/inference.py`) is a MobileNetV3-Small backbone
pretrained on ImageNet, with only the final classification layer fine-tuned
on a small dataset (~120 images across 5 categories, sourced from Wikimedia
Commons). It correctly classifies objects within its trained categories at
85-95% validation accuracy, but — as expected for a small dataset — it also
confidently misclassifies out-of-distribution objects (e.g. a household item
gets mapped to whichever trained category looks closest). It currently
predicts category only; era and material are placeholder values, since that
would require separate labeled data per attribute.

**Natural next steps:** collect more/varied training images, add an
"unknown" rejection threshold for low-confidence predictions, and extend to
multi-attribute classification (era, material) with additional labeled data.
