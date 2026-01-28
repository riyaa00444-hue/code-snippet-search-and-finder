const Hero = () => {
  return (
    <section className="px-6 py-12">
      <h1 className="text-3xl font-bold mb-3">
        Code Snippet Search & Finder
      </h1>

      <p className="mb-5">
        Search and understand code snippets easily using intelligent analysis.
      </p>

      <div className="flex gap-4">
        <a className="bg-black text-white px-4 py-2" href="/signup">
          Get Started
        </a>

        <a className="border px-4 py-2" href="/login">
          Login
        </a>
      </div>
    </section>
  );
};

export default Hero;

