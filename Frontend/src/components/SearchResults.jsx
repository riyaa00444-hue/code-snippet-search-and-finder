import CodeCard from "./CodeCard";

export default function SearchResults({ results = [] }) {
  if (!results.length) {
    return (
      <p className="text-gray-500 mt-4">
        No results found.
      </p>
    );
  }

  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold mb-3">
        Search Results ({results.length})
      </h2>

      <div className="space-y-4">
        {results.map((item) => (
          <CodeCard key={item.id} snippet={item} />
        ))}
      </div>
    </div>
  );
}
