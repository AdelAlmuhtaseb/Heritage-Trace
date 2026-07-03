import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="volunteer")  # volunteer | researcher | admin
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    submissions = db.relationship("Submission", backref="submitter", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "email": self.email, "role": self.role}


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    photo_url = db.Column(db.String(512), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # AI-suggested tags (filled by ML service, editable by researcher)
    ai_category = db.Column(db.String(100), nullable=True)
    ai_era = db.Column(db.String(100), nullable=True)
    ai_material = db.Column(db.String(100), nullable=True)
    ai_confidence = db.Column(db.Float, nullable=True)

    # Researcher-confirmed values (defaults to AI values until edited)
    category = db.Column(db.String(100), nullable=True)
    era = db.Column(db.String(100), nullable=True)
    material = db.Column(db.String(100), nullable=True)

    status = db.Column(db.String(20), nullable=False, default="pending")  # pending | verified | rejected
    preservation_status = db.Column(db.String(20), nullable=True)  # good | at_risk | critical

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    verifications = db.relationship("Verification", backref="submission", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "photo_url": self.photo_url,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "notes": self.notes,
            "ai_category": self.ai_category,
            "ai_era": self.ai_era,
            "ai_material": self.ai_material,
            "ai_confidence": self.ai_confidence,
            "category": self.category,
            "era": self.era,
            "material": self.material,
            "status": self.status,
            "preservation_status": self.preservation_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Verification(db.Model):
    __tablename__ = "verifications"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False)
    researcher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    decision = db.Column(db.String(20), nullable=False)  # verified | rejected
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "researcher_id": self.researcher_id,
            "decision": self.decision,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
