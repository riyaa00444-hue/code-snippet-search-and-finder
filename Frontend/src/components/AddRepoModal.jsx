import { useState } from "react";

export default function AddRepoModal({ isOpen, onClose, onSuccess }) {
  const [name, setName] = useState("");
  const [path, setPath] = useState("");
  const [type, setType] = useState("connect");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/repositories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, path, type }),
      });

      if (!res.ok) throw new Error("Failed to add repository");

      const data = await res.json();
      onSuccess(data);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <form onSubmit={handleSubmit} className="bg-white p-6 w-96 rounded">
        <h2 className="text-lg font-bold mb-4">Add Repository</h2>

        <input
          className="w-full border p-2 mb-2"
          placeholder="Repository Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <input
          className="w-full border p-2 mb-2"
          placeholder="Repository Path"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          required
        />

        <select
          className="w-full border p-2 mb-3"
          value={type}
          onChange={(e) => setType(e.target.value)}
        >
          <option value="connect">Connect</option>
          <option value="upload">Upload</option>
        </select>

        {error && <p className="text-red-500 text-sm mb-2">{error}</p>}

        <button
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 w-full"
        >
          {loading ? "Analyzing..." : "Add Repository"}
        </button>
      </form>
    </div>
  );
}

