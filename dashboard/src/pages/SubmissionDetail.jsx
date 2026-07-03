import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import client from "../api/client";

export default function SubmissionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [submission, setSubmission] = useState(null);
  const [comment, setComment] = useState("");

  useEffect(() => {
    client.get(`/submissions/${id}`).then((res) => setSubmission(res.data));
  }, [id]);

  const verify = async (decision) => {
    await client.post(`/verifications/${id}`, { decision, comment });
    navigate("/submissions");
  };

  if (!submission) return <p>Loading...</p>;

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Submission #{submission.id}</h2>
      <img src={submission.photo_url} alt="artifact" style={{ maxWidth: "100%" }}
        onError={(e) => (e.target.style.display = "none")} />
      <p><strong>AI Category:</strong> {submission.ai_category}</p>
      <p><strong>AI Era:</strong> {submission.ai_era}</p>
      <p><strong>AI Material:</strong> {submission.ai_material}</p>
      <p><strong>Confidence:</strong> {submission.ai_confidence}</p>
      <p><strong>Notes:</strong> {submission.notes}</p>
      <p><strong>Status:</strong> {submission.status}</p>

      <textarea
        placeholder="Verification comment"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        style={{ width: "100%", height: 60, marginTop: 10 }}
      />
      <div style={{ marginTop: 10 }}>
        <button onClick={() => verify("verified")} style={{ marginRight: 10 }}>
          ✅ Verify
        </button>
        <button onClick={() => verify("rejected")}>❌ Reject</button>
      </div>
    </div>
  );
}