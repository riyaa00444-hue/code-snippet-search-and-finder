import { useState } from "react";
import { Link } from "react-router-dom";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";
import { useNavigate } from "react-router-dom";


function SignupForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {

    e.preventDefault();

    if (!email || !password) {
      setError("Email and password are required");
      return;
    }

    setError("");
    setSuccess("");
    setLoading(true);

     try {
        await createUserWithEmailAndPassword(auth, email, password);
        setSuccess("Account created successfully");

    
        setTimeout(() => {
           navigate("/login");
        }, 1500);
     } catch (err) {
      if (err.code === "auth/email-already-in-use") {
        setError("Email already exists");
      } else if (err.code === "auth/weak-password") {
        setError("Password should be at least 6 characters");
      } else {
        setError("Something went wrong. Please try again");
      }
    } finally {
      setLoading(false);
    }
   
  
  };

  return (
    <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-2 text-center">
        Sign Up
      </h2>

      <p className="text-sm text-gray-500 text-center mb-6">
        Create your account to get started
      </p>

      {error && (
        <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
          {error}
        </div>
      )}

      {success && (
         <div className="mb-4 text-sm text-green-600 bg-green-50 border border-green-200 rounded px-3 py-2">
            {success}
         </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
        >
          {loading ? "Creating account..." : "Create Account"}
        </button>

      </form>

      <p className="text-center text-sm text-gray-600 mt-6">
        Already have an account?{" "}
        <Link
          to="/"
          className="text-blue-600 hover:underline font-medium"
        >
          Back to Landing
        </Link>
      </p>
    </div>
  );
}

export default SignupForm;



