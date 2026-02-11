import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import FileTree from "../components/FileTree";
import CodeViewer from "../components/CodeViewer";
import ProgressBar from "../components/ProgressBar";

export default function RepositoryDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [repo, setRepo] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [isIndexing, setIsIndexing] = useState(false);
  const [progress, setProgress] = useState(0);

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // ---------------- FETCH REPO DATA ----------------
  const fetchRepoData = useCallback(async () => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/repositories/${id}`
      );

      if (!res.ok) {
        throw new Error("Failed to fetch repository details");
      }

      const data = await res.json();

      setRepo({
        ...data,
        files: data.file_list ? data.file_list.split(",") : [],
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  // ✅ MISSING PART — THIS WAS THE BUG
  useEffect(() => {
    fetchRepoData();
  }, [fetchRepoData]);

  // ---------------- INDEX REPOSITORY ----------------
  const handleIndexRepository = async () => {
    setIsIndexing(true);
    setProgress(0);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/repositories/${id}/index`,
        { method: "POST" }
      );

      if (!res.ok) throw new Error("Failed to start indexing");

      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsIndexing(false);
            fetchRepoData();
            return 100;
          }
          return prev + 10;
        });
      }, 500);
    } catch (err) {
      alert(err.message);
      setIsIndexing(false);
    }
  };

  // ---------------- FILE SELECT ----------------
  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    setCode("// Loading code...");

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/repositories/${id}/file?path=${file}`
      );
      const data = await res.text();
      setCode(data);
    } catch {
      setCode("// Error loading file content");
    }
  };

  // ---------------- DELETE REPO ----------------
  const handleDeleteRepository = async () => {
    setIsDeleting(true);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/repositories/${id}`,
        { method: "DELETE" }
      );

      if (!res.ok) throw new Error("Delete failed");

      alert("Repository deleted successfully");
      navigate("/dashboard");
    } catch (err) {
      alert(err.message);
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  // ---------------- UI STATES ----------------
  if (loading)
    return <div className="p-10 text-center">Loading Repository...</div>;

  if (error)
    return <div className="p-10 text-red-500">Error: {error}</div>;

  // ---------------- MAIN UI ----------------
  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <header className="bg-white border p-6 rounded-xl shadow-sm flex justify-between">
          <div>
            <h1 className="text-3xl font-bold">{repo.name}</h1>
            <p className="text-sm text-slate-500 mt-2">
              📂 {repo.files?.length || 0} Files
            </p>
          </div>

          <div className="flex flex-col gap-2">
            <button
              onClick={handleIndexRepository}
              disabled={repo.indexed || isIndexing}
              className="px-6 py-2 bg-indigo-600 text-white rounded disabled:bg-gray-300"
            >
              {repo.indexed ? "Indexed ✓" : "Index Repository"}
            </button>

            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="px-6 py-2 bg-red-600 text-white rounded"
            >
              Delete Repository
            </button>
          </div>
        </header>

        {isIndexing && <ProgressBar progress={progress} />}

        <main className="flex gap-6 h-[70vh] overflow-hidden">
 
          <aside className="w-80 bg-white border rounded-xl p-2 flex flex-col">
            <h2 className="font-semibold px-2 py-1 border-b">Files</h2>

            <div className="flex-1 overflow-y-auto">
              <FileTree
                files={repo?.files || []}
                selectedFile={selectedFile}
                onSelect={handleFileSelect}
              />
           </div>
         </aside>


        <section className="flex-1 bg-slate-900 rounded-xl overflow-hidden">
          {selectedFile ? (
            <div className="h-full overflow-y-auto">
              <CodeViewer
                code={code}
                language={selectedFile.split(".").pop()}
              />
            </div>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400">
                Select a file to view code
              </div>
            )}
          </section>
        </main>

      </div>

      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white p-6 rounded">
            <p className="mb-4">
              Are you sure? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button onClick={() => setShowDeleteConfirm(false)}>
                Cancel
              </button>
              <button
                onClick={handleDeleteRepository}
                className="bg-red-600 text-white px-4 py-2 rounded"
              >
                {isDeleting ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
