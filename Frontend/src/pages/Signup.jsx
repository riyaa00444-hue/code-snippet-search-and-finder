import SignupForm from "../components/SignupForm";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

function Signup() {
  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
        <SignupForm />
      </div>
      <Footer />
    </>
  );
}

export default Signup;

