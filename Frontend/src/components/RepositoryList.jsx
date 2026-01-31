import RepositoryCard from "./RepositoryCard";

function RepositoryList({ repositories }) {
  if (repositories.length === 0) {
    return (
      <div className="text-center text-gray-500 mt-12">
        No repositories yet. Add one to get started.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {repositories.map((repo, index) => (
        <RepositoryCard key={index} repo={repo} />
      ))}
    </div>
  );
}

export default RepositoryList;
