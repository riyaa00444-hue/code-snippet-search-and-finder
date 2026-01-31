import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import RepositoryList from "../components/RepositoryList";
import AddRepoButton from "../components/AddRepoButton";

function Dashboard() {
  const repositories = []; // static empty state

  return (
    <>
      <Navbar />

      <div className="min-h-screen bg-gray-100 p-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold">My Repositories</h1>
            <AddRepoButton />
          </div>

          <RepositoryList repositories={repositories} />
        </div>
      </div>

      <Footer />
    </>
  );
}

export default Dashboard;

