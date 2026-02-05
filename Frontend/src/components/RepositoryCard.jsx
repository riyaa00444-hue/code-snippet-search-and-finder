import { useNavigate } from "react-router-dom";

function RepositoryCard({ repo }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/repositories/${repo.id}`)}
      className="bg-white p-4 rounded shadow cursor-pointer"
    >
      <h2 className="font-semibold text-lg">{repo.name}</h2>

      <p className="text-sm text-gray-600">
        Files: {repo.file_count}
      </p>

      <p className="text-sm text-gray-600">
        Status: {repo.indexed ? "Indexed" : "Not Indexed"}
      </p>
    </div>
  );
}

export default RepositoryCard;
