export default function FileTree({ files, selectedFile, onSelect }) {
  return (
    <div className="border p-3">
      <h3 className="font-semibold mb-2">Files</h3>

      {files.length === 0 ? (
        <p>No files found</p>
      ) : (
        <ul>
          {files.map((file, index) => (
            <li
              key={index}
              onClick={() => onSelect(file)}
              style={{
                cursor: "pointer",
                fontWeight: selectedFile === file ? "bold" : "normal"
              }}
            >
              {file}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
