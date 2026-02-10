import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import CodeExplanation from "../components/CodeExplanation";
import CopyButton from "../components/CopyButton";
import CodeViewer from "../components/CodeViewer";
import ExportButton from "../components/ExportButton";




export default function CodeDetail() {
  const { id } = useParams();

  const [snippet, setSnippet] = useState(null);
  const [explanation, setExplanation] = useState("");
  const [loadingExplain, setLoadingExplain] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/code/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load code");
        return res.json();
      })
      .then(setSnippet)
      .catch((err) => setError(err.message));
  }, [id]);

  const explainCode = async () => {
    setLoadingExplain(true);
    setExplanation("");

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/code/${id}/explain`,
        { method: "POST" }
      );
      const data = await res.json();
      setExplanation(data.explanation);
    } catch {
      setExplanation("Failed to generate explanation");
    } finally {
      setLoadingExplain(false);
    }
  };

  const copyCode = () => {
    navigator.clipboard.writeText(
      `${snippet.code}\n\nSource: ${snippet.file_path}`
    );
    alert("Code copied with attribution");
  };

  if (error) return <p className="p-6 text-red-500">{error}</p>;
  if (!snippet) return <p className="p-6">Loading…</p>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-xl font-semibold mb-2">Code Detail</h1>

      <p className="text-sm text-gray-500 mb-4">
        {snippet.repository} — {snippet.file_path}
      </p>

      <CodeViewer
        code={snippet.code}
        language={snippet.language || "python"}
      />


      <div className="flex gap-3 mt-4">
        <CopyButton
          code={snippet.code}
            filePath={snippet.file_path}
        />


        <button
          onClick={explainCode}
          className="px-4 py-2 bg-black text-white rounded"
          disabled={loadingExplain}
        >
          {loadingExplain ? "Explaining…" : "Explain Code"}
        </button>
      </div>
      <ExportButton
        type="code"
        data={snippet}
        filename={`code-snippet-${snippet.id}`}
      />


      <CodeExplanation
        explanation={explanation}
        loading={loadingExplain}
      />

    </div>
  );
}

