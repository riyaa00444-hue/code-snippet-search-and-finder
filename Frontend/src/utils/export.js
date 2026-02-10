// Frontend/src/utils/export.js

// Format search results (from /api/search) into Markdown
export function formatSearchResultsMarkdown(results) {
  let output = "# Search Results Export\n\n";

  results.forEach((item, index) => {
    output += `## Result ${index + 1}\n`;
    output += `Snippet ID: ${item.id}\n`;
    output += `File Path: ${item.file_path}\n`;
    output += `Similarity Score: ${item.similarity_score}\n\n`;
    output += "```text\n";
    output += item.code_preview || "";
    output += "\n```\n\n";
  });

  return output;
}

// Format single code snippet (from /api/code/{id})
export function formatCodeDetailMarkdown(snippet) {
  return `# Code Snippet Export

Snippet ID: ${snippet.id}
Repository: ${snippet.repository_name}
File Path: ${snippet.file_path}

\`\`\`text
${snippet.code}
\`\`\`
`;
}

// Download helper using browser APIs
export function downloadFile(content, filename) {
  const blob = new Blob([content], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename;

  document.body.appendChild(link);
  link.click();

  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
