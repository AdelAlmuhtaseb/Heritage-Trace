from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.models import Submission, Verification

verifications_bp = Blueprint("verifications", __name__)


def _require_researcher():
    claims = get_jwt()
    return claims.get("role") in ("researcher", "admin")


@verifications_bp.post("/<int:submission_id>")
@jwt_required()
def verify_submission(submission_id):
    if not _require_researcher():
        return jsonify({"error": "researcher role required"}), 403

    data = request.get_json() or {}
    decision = data.get("decision")  # "verified" | "rejected"
    comment = data.get("comment")

    if decision not in ("verified", "rejected"):
        return jsonify({"error": "decision must be 'verified' or 'rejected'"}), 400

    submission = Submission.query.get_or_404(submission_id)
    researcher_id = get_jwt_identity()

    verification = Verification(
        submission_id=submission.id,
        researcher_id=researcher_id,
        decision=decision,
        comment=comment,
    )
    submission.status = decision

    db.session.add(verification)
    db.session.commit()

    return jsonify(submission.to_dict()), 200


@verifications_bp.get("/<int:submission_id>")
@jwt_required()
def list_verifications(submission_id):
    verifications = Verification.query.filter_by(submission_id=submission_id).all()
    return jsonify([v.to_dict() for v in verifications]), 200
