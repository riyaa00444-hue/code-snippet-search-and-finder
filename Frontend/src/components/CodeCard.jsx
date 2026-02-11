import { Link } from "react-router-dom";

export default function CodeCard({ snippet }) {
  return (
    <Link to={`/code/${snippet.id}`}>
      <div className="border rounded p-4 hover:bg-gray-50 cursor-pointer transition">
        
        {/* File path */}
        <p className="text-sm text-gray-500 mb-2 break-all">
          {snippet.file_path}
        </p>

        {/* Code preview */}
        <pre className="bg-gray-100 p-3 text-xs rounded overflow-hidden max-h-40">
          {snippet.code_preview}
        </pre>

        {/* Similarity score */}
        <p className="text-xs mt-3 text-gray-700 font-medium">
          Similarity score:{" "}
          {typeof snippet.similarity_score === "number"
            ? snippet.similarity_score.toFixed(3)
            : "N/A"}
        </p>
      </div>
    </Link>
  );
}
