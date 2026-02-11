import { useNavigate } from "react-router-dom";

export default function HistoryItem({ item }) {
  const navigate = useNavigate();

  if (!item) return null; // ✅ prevents crash

  return (
    <div className="border p-3 rounded flex justify-between items-center">
      <div
        className="cursor-pointer"
        onClick={() =>
          navigate(`/search?query=${encodeURIComponent(item.query)}`)
        }
      >
        <p className="font-medium">{item.query}</p>
        <p className="text-sm text-gray-500">
          Results: {item.result_count} •{" "}
          {new Date(item.searched_at).toLocaleString()}
        </p>
      </div>

      <button
        onClick={() => {
          fetch(`http://localhost:8000/api/history/${item.id}`, {
            method: "DELETE",
          }).then(() => window.location.reload());
        }}
        className="text-red-500 text-sm"
      >
        Delete
      </button>
    </div>
  );
}
