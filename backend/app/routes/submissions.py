from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import Submission
<<<<<<< HEAD
from app.ml.inference import suggest_tags
=======
from app.ml.tagger import suggest_tags
>>>>>>> origin/main

submissions_bp = Blueprint("submissions", __name__)


@submissions_bp.post("")
@jwt_required()
def create_submission():
    """
    Volunteer submits a photo (already uploaded to S3/local storage by the
    client, which sends back the photo_url) plus optional GPS + notes.
    The ML tagger runs synchronously here for simplicity; swap for an async
    task queue (Celery/SQS) once submission volume grows.
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    photo_url = data.get("photo_url")
    if not photo_url:
        return jsonify({"error": "photo_url is required"}), 400

    submission = Submission(
        user_id=user_id,
        photo_url=photo_url,
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        notes=data.get("notes"),
    )

    # Run AI tagging (stubbed model for now — see app/ml/tagger.py)
    tags = suggest_tags(photo_url)
    submission.ai_category = tags.get("category")
    submission.ai_era = tags.get("era")
    submission.ai_material = tags.get("material")
    submission.ai_confidence = tags.get("confidence")
    # Pre-fill researcher-facing fields with AI suggestions until reviewed
    submission.category = tags.get("category")
    submission.era = tags.get("era")
    submission.material = tags.get("material")

    db.session.add(submission)
    db.session.commit()

    return jsonify(submission.to_dict()), 201


@submissions_bp.get("")
@jwt_required()
def list_submissions():
    status = request.args.get("status")
    query = Submission.query
    if status:
        query = query.filter_by(status=status)
    submissions = query.order_by(Submission.created_at.desc()).all()
    return jsonify([s.to_dict() for s in submissions]), 200


@submissions_bp.get("/<int:submission_id>")
@jwt_required()
def get_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    return jsonify(submission.to_dict()), 200


@submissions_bp.patch("/<int:submission_id>")
@jwt_required()
def update_submission(submission_id):
    """Researcher edits AI-suggested tags before/while verifying."""
    submission = Submission.query.get_or_404(submission_id)
    data = request.get_json() or {}

    for field in ("category", "era", "material", "preservation_status", "notes"):
        if field in data:
            setattr(submission, field, data[field])

    db.session.commit()
    return jsonify(submission.to_dict()), 200
