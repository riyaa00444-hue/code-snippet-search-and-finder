import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { prism } from "react-syntax-highlighter/dist/esm/styles/prism";


export default function CodeViewer({ code, language = "python" }) {
  return (
    <div className="border rounded overflow-auto">
      <SyntaxHighlighter
        language={language}
        style={prism}
        showLineNumbers
        wrapLines
        lineProps={() => ({
          style: { display: "flex" },
        })}
        lineNumberStyle={{
          minWidth: "40px",
          paddingRight: "12px",
          textAlign: "right",
          userSelect: "none",
        }}
        customStyle={{
          margin: 0,
          fontSize: "14px",
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

