const Features = () => {
  return (
    <section className="px-6 py-10">
      <h2 className="text-xl font-bold mb-4">
        Features
      </h2>

      <div className="flex gap-6">
        <div>
          <h4 className="font-semibold">Semantic Search</h4>
          <p>Search code based on meaning.</p>
        </div>

        <div>
          <h4 className="font-semibold">LLM Analysis</h4>
          <p>Understand what the code does.</p>
        </div>

        <div>
          <h4 className="font-semibold">Code Explanation</h4>
          <p>Get simple explanations for code.</p>
        </div>
      </div>
    </section>
  );
};

export default Features;
