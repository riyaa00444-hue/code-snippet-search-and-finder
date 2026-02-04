function AddRepoButton({ onClick }) {
  return (
    <button
      className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      onClick={onClick}
    >
      + Add Repository
    </button>
  );
}

export default AddRepoButton;

