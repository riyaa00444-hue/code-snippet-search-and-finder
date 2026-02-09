export default function CodeExplanation({ explanation, loading }) {
  if (loading) {
    return (
      <div className="mt-6 text-sm text-gray-500">
        Generating explanation…
      </div>
    );
  }

  if (!explanation) return null;

  return (
    <div className="mt-6 border rounded p-4 bg-gray-50">
      <h2 className="font-semibold mb-2">AI Explanation</h2>
      <p className="text-sm whitespace-pre-wrap">
        {explanation}
      </p>
    </div>
  );
}
