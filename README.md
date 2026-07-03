# Heritage Trace

A crowdsourced platform for documenting and preserving at-risk or undocumented
heritage artifacts and sites. Volunteers photograph items via a mobile app;
an AI model auto-suggests tags (category, era, material); researchers verify
submissions and track preservation status via a web dashboard.

## Status

- [x] **Phase 1 — Backend API** (this repo, working & tested)
- [ ] **Phase 2 — React researcher dashboard**
- [ ] **Phase 3 — Real AI tagging model** (currently a stub, see below)
- [ ] **Phase 4 — React Native mobile app**
- [ ] **Phase 5 — Cloud deployment (AWS free tier)**

## Architecture

```
heritage-trace/
├── backend/          # Flask REST API (done)
│   ├── app/
│   │   ├── models/   # SQLAlchemy models: User, Submission, Verification
│   │   ├── routes/   # auth, submissions, verifications blueprints
│   │   └── ml/        # tagger.py — swap stub for real model in Phase 3
│   ├── tests/         # pytest suite, 7 passing tests
│   └── run.py
├── dashboard/        # React app (Phase 2 — not yet scaffolded)
├── mobile/           # React Native app (Phase 4 — not yet scaffolded)
├── ml/                # Model training scripts (Phase 3 — not yet started)
└── .github/workflows/ci.yml   # runs backend tests on every push
```

## Data model

**User** — id, email, password_hash, role (`volunteer` | `researcher` | `admin`)

**Submission** — id, user_id, photo_url, latitude, longitude, notes,
ai_category/ai_era/ai_material/ai_confidence (from the AI tagger),
category/era/material (researcher-editable, defaults to AI values),
status (`pending` | `verified` | `rejected`), preservation_status
(`good` | `at_risk` | `critical`)

**Verification** — id, submission_id, researcher_id, decision, comment

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

## Running the backend locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit if needed, defaults work for local dev
python run.py                   # runs on http://127.0.0.1:5000
```

Run the tests:

```bash
python -m pytest tests/ -v
```

Try it with curl:

```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"pass123","role":"volunteer"}'
```

---

## Next steps — what YOU do from here

### Phase 2: React dashboard (do this next)

```bash
cd heritage-trace
npx create-react-app dashboard
# or, if you'd rather use Vite (faster, more modern — recommended):
npm create vite@latest dashboard -- --template react
cd dashboard
npm install axios react-router-dom
```

Build these pages first, in this order:
1. **Login page** — POST to `/api/auth/login`, store JWT in React state (not
   localStorage — keep it simple with Context/state for v1)
2. **Submissions list** — GET `/api/submissions`, table with photo thumbnail,
   AI-suggested tags, status badge
3. **Submission detail** — GET `/api/submissions/<id>`, editable tag fields
   (PATCH), verify/reject buttons (POST `/api/verifications/<id>`)

### Phase 3: Real AI tagging model

Right now `backend/app/ml/tagger.py` returns random stub tags so the rest of
the system works end-to-end. To make it real:

1. Collect ~15-20 labeled photos per category (pottery, coin, sculpture, etc.)
   — even phone photos of museum pieces or reference images work for a v1
2. Fine-tune a small pretrained model (MobileNetV3 or ResNet18 via PyTorch/
   TensorFlow) on your labeled set — this is a well-documented, tractable
   task, not a research project
3. Save the trained model, load it in `tagger.py`, replace the random stub
   with real `model.predict(photo)` calls
4. Keep the function signature (`suggest_tags(photo_url) -> dict`) identical
   so nothing else in the codebase changes

### Phase 4: React Native mobile app

```bash
npx create-expo-app mobile
cd mobile
npx expo install expo-camera expo-location
```

Core screens: camera capture → confirm GPS → optional notes → POST to
`/api/submissions`. Use Expo so you can test on your own phone instantly
without dealing with Apple/Google developer accounts yet.

### Phase 5: Cloud deployment

- Photo storage: S3 bucket (swap `photo_url` handling to actually upload to
  S3 instead of accepting arbitrary URLs)
- Backend: Elastic Beanstalk or a plain EC2 instance running gunicorn
  (`gunicorn run:app` — already in requirements.txt)
- Database: switch `DATABASE_URL` to an RDS Postgres instance
- **Set a billing alert immediately** when you create the AWS account — see
  earlier note, stay inside free tier limits

### CI/CD

`.github/workflows/ci.yml` already runs the backend test suite on every push
to `main`/`develop`. Once the dashboard exists, uncomment the
`dashboard-tests` job and add a `npm test` script.

---

## Why this project (for your CV / interviews)

This project deliberately covers gaps your existing CV doesn't show:
**React** (dashboard), **mobile** (React Native), **AI/ML** (image tagging
model), **cloud deployment** (AWS), and **CI/CD** (GitHub Actions) — on top
of the backend/API/database work you already have real experience in from
FutureSys and the Bulgaria internship. It also connects to your existing
Erasmus+/UNESCO Chair network from the "Dig in History" project, which is
worth pursuing if you want a real pilot user rather than just a demo.
