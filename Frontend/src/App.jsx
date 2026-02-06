import { Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import RepositoryDetail from "./pages/RepositoryDetail";


import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/login" element={<Login />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/repositories/:id"
        element={
          <ProtectedRoute>
            <RepositoryDetail />
          </ProtectedRoute>
        }
      />

    </Routes>
  );
}

export default App;
