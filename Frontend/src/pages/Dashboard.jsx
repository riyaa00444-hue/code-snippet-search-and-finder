import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import RepositoryList from "../components/RepositoryList";
import AddRepoButton from "../components/AddRepoButton";
import AddRepoModal from "../components/AddRepoModal";

function Dashboard() {
  const [repositories, setRepositories] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // ✅ REQUIRED: load repos from backend
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/repositories")
      .then((res) => res.json())
      .then((data) => setRepositories(data));
  }, []);

  const handleRepoAdded = (repo) => {
    setRepositories((prev) => [repo, ...prev]);
  };

  return (
    <>
      <Navbar />

      <div className="min-h-screen bg-gray-100 p-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold">My Repositories</h1>
            <AddRepoButton onClick={() => setIsModalOpen(true)} />
          </div>

          <RepositoryList repositories={repositories} />
        </div>
      </div>

      <Footer />

      <AddRepoModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={handleRepoAdded}
      />
    </>
  );
}

export default Dashboard;
