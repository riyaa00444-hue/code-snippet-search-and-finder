import { useEffect, useState } from "react";
import HistoryList from "../components/HistoryList";

export default function History() {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/history")
      .then(res => {
        if (!res.ok) throw new Error("Failed to load history");
        return res.json();
      })
      .then(data => {
        setHistory(data); // ✅ NOT data.history unless backend wraps it
      })
      .catch(err => setError(err.message));
  }, []);

  if (error) return <p className="text-red-500">{error}</p>;

  return <HistoryList history={history} />;
}
