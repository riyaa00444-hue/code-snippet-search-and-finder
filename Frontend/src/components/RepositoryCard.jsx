function RepositoryCard({ repo }) {
  return (
    <div className="bg-white p-4 rounded shadow hover:shadow-md transition">
      <h2 className="font-semibold text-lg">{repo.name}</h2>
      <p className="text-sm text-gray-600">
        Files: {repo.fileCount}
      </p>
      <p className="text-sm text-gray-600">
        Status: {repo.indexed ? "Indexed" : "Not Indexed"}
      </p>
    </div>
  );
}

export default RepositoryCard;
