import { useState } from "react";

export default function SearchBar({ onSearch, repositories }) {
  const [query, setQuery] = useState("");
  const [repoId, setRepoId] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    const trimmedQuery = query.trim();
    if (trimmedQuery.length < 3) return;

    onSearch(trimmedQuery, repoId ? Number(repoId) : null);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex gap-3 mb-6 items-center"
    >
      <input
        type="text"
        placeholder="Search code using natural language..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="flex-1 border rounded px-3 py-2"
        aria-label="Search query"
      />

      <select
        value={repoId}
        onChange={(e) => setRepoId(e.target.value)}
        className="border rounded px-3 py-2"
        aria-label="Repository filter"
      >
        <option value="">All Repositories</option>
        {repositories.map((repo) => (
          <option key={repo.id} value={repo.id}>
            {repo.name}
          </option>
        ))}
      </select>

      <button
        type="submit"
        className="bg-black text-white px-5 py-2 rounded hover:bg-gray-800"
      >
        Search
      </button>
    </form>
  );
}
