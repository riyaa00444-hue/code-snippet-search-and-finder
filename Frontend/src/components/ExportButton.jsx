

import { useState } from "react";
import {
  formatSearchResultsMarkdown,
  formatCodeDetailMarkdown,
  downloadFile,
} from "../utils/export";

export default function ExportButton({ type, data, filename }) {
  const [error, setError] = useState(null);

  const handleExport = () => {
    try {
      setError(null);

      if (!data || (Array.isArray(data) && data.length === 0)) {
        throw new Error("No data available to export");
      }

      let content = "";

      if (type === "search") {
        content = formatSearchResultsMarkdown(data);
      } else if (type === "code") {
        content = formatCodeDetailMarkdown(data);
      } else {
        throw new Error("Invalid export type");
      }

      downloadFile(content, `${filename}.md`);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="mt-4">
      <button
        onClick={handleExport}
        className="px-4 py-2 bg-green-600 text-white rounded"
      >
        Export
      </button>

      {error && (
        <p className="mt-2 text-sm text-red-500">
          {error}
        </p>
      )}
    </div>
  );
}

