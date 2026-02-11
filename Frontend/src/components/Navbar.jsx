const Navbar = () => {
  return (
    <nav className="flex justify-between px-6 py-4 bg-gray-200">
      <div className="font-bold">
        Code Snippet Finder
      </div>

      <div className="flex gap-4">
        <a href="/login">Login</a>
        <a href="/signup">Sign Up</a>
        <a href="/search">Search</a>
      </div>
    </nav>
  );
};

export default Navbar;

