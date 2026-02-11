import HistoryItem from "./HistoryItem";

export default function HistoryList({ history }) {
  if (!history || history.length === 0) {
    return <p className="text-gray-500">No search history found.</p>;
  }

  return (
    <div className="space-y-3">
      {history.map(item => (
        <HistoryItem
          key={item.id}
          item={item}   // ✅ THIS WAS MISSING OR WRONG
        />
      ))}
    </div>
  );
}
