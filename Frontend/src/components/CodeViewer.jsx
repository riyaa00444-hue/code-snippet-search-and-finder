export default function CodeViewer({ code }) {
  return (
    <pre
      style={{
        whiteSpace: "pre-wrap",
        backgroundColor: "#f4f4f4",
        padding: "10px",
        border: "1px solid #ccc",
        height: "400px",
        overflowY: "auto"
      }}
    >
      <code>{code}</code>
    </pre>
  );
}
