import { useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import RepositoryList from "../components/RepositoryList";
import AddRepoButton from "../components/AddRepoButton";
import AddRepoModal from "../components/AddRepoModal";

function Dashboard() {
  // repositories added during this session
  const [repositories, setRepositories] = useState([]);

  // modal open/close state
  const [isModalOpen, setIsModalOpen] = useState(false);

  // called after successful POST /api/repositories
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
