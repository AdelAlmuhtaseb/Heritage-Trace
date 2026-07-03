import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

export default function Submissions() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get("/submissions").then((res) => {
      setSubmissions(res.data);
      setLoading(false);
    });
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Submissions</h2>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>
            <th>ID</th>
            <th>AI Category</th>
            <th>AI Era</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {submissions.map((s) => (
            <tr key={s.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>{s.id}</td>
              <td>{s.ai_category}</td>
              <td>{s.ai_era}</td>
              <td>{s.status}</td>
              <td>
                <Link to={`/submissions/${s.id}`}>Review</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}