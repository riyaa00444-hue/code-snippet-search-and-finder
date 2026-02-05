export default function ProgressBar({ label = "Indexing repository..." }) {
  return (
    <div className="w-full bg-gray-200 rounded h-3 mt-4">
      <div className="h-3 bg-blue-500 rounded animate-pulse w-1/2"></div>
      <p className="text-sm text-gray-600 mt-2">{label}</p>
    </div>
  );
}
