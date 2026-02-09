import { useState } from "react";

export default function CopyButton({ code, filePath }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(
      `${code}\n\nSource: ${filePath}`
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="px-4 py-2 bg-gray-700 text-white rounded"
    >
      {copied ? "Copied ✓" : "Copy Code"}
    </button>
  );
}
