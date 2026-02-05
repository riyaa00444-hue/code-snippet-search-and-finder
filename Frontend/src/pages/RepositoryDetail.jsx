import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import FileTree from "../components/FileTree";
import CodeViewer from "../components/CodeViewer";
import ProgressBar from "../components/ProgressBar"; // New Component

export default function RepositoryDetail() {
  const { id } = useParams();

  const [repo, setRepo] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Indexing States
  const [isIndexing, setIsIndexing] = useState(false);
  const [progress, setProgress] = useState(0);

  const fetchRepoData = useCallback(async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/repositories/${id}`);
      if (!res.ok) throw new Error("Failed to fetch repository details");
      const data = await res.json();
      setRepo(data);
      // If backend says it's currently indexing, flip the state
      if (data.status === "indexing") setIsIndexing(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchRepoData();
  }, [fetchRepoData]);

  const handleIndexRepository = async () => {
    setIsIndexing(true);
    setProgress(0);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/repositories/${id}/index`, {
        method: "POST",
      });
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

  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    setCode("// Loading code...");
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/repositories/${id}/file?path=${file}`);
      const data = await res.text();
      setCode(data);
    } catch (err) {
      setCode("// Error loading file content");
    }
  };

  if (loading) return <div className="p-10 text-center animate-pulse">Loading Repository...</div>;
  if (error) return <div className="p-10 text-red-500 font-medium">Error: {error}</div>;

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">

        <header className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm flex flex-col md:flex-row justify-between items-start gap-4">
          <div className="space-y-2 flex-1">
            <h1 className="text-3xl font-bold text-slate-900">{repo.name}</h1>
            <div className="mt-3 space-y-3">
               <p className="text-slate-600 text-sm leading-relaxed">
                   📦 <span className="font-medium">Repository Overview:</span>{" "}
                   This repository contains source code and related files for this project.
               </p>

               {repo.description && (
                <details className="group">
                   <summary className="cursor-pointer text-indigo-600 text-sm font-medium flex items-center gap-1">
                      📖 View detailed explanation
                   </summary>

                   <div className="mt-2 bg-slate-50 border border-slate-200 rounded-lg p-4 text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">
                       {repo.description}
                   </div>
                </details>
             )}
            </div>

            <div className="flex gap-4 pt-2 text-sm font-medium text-slate-500">
              <span className="flex items-center gap-1">📂 {repo.files?.length || 0} Files</span>
              <span className={`px-2 py-0.5 rounded-full text-xs ${repo.indexed ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                {repo.indexed ? "✓ Indexed" : "○ Not Indexed"}
              </span>
            </div>
          </div>

          <button 
            onClick={handleIndexRepository}
            disabled={isIndexing || repo.indexed}
            className="w-full md:w-auto px-6 py-2.5 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:bg-slate-300 transition-all shadow-md active:scale-95"
          >
            {isIndexing ? "Indexing..." : repo.indexed ? "Indexed ✓" : "Index Repository"}

          </button>
        </header>


        {isIndexing && (
          <div className="bg-white p-4 rounded-xl border border-indigo-100 shadow-sm">
            <ProgressBar progress={progress} />
          </div>
        )}

        <main className="flex flex-col md:flex-row gap-6 h-[70vh]">
   
          <aside className="w-full md:w-80 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50 rounded-t-xl">
              <h2 className="font-bold text-slate-700 flex items-center gap-2">
                <span className="text-lg">📁</span> File Explorer
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-2">
              <FileTree 
                files={repo.files} 
                selectedFile={selectedFile} 
                onSelect={handleFileSelect} 
              />
            </div>
          </aside>

        
          <section className="flex-1 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col">
            {selectedFile ? (
              <>
                <div className="bg-slate-800/50 px-4 py-2 text-xs font-mono text-slate-400 border-b border-slate-700 flex justify-between items-center">
                  <span>{selectedFile}</span>
                  <span className="uppercase">{selectedFile.split('.').pop()}</span>
                </div>
                <div className="flex-1 overflow-auto custom-scrollbar">
                  <CodeViewer 
                    code={code} 
                    language={selectedFile.split('.').pop()} 
                  />
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-500 space-y-4">
                <div className="text-5xl">📄</div>
                <p className="font-medium italic">Select a file from the explorer to view its contents</p>
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}