import React from "react";

type Block =
  | { type: "h1" | "h2" | "h3"; text: string }
  | { type: "p"; text: string }
  | { type: "ul"; items: string[] }
  | { type: "code"; text: string };

const parseMarkdown = (content: string): Block[] => {
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  const blocks: Block[] = [];

  let inCode = false;
  let codeBuffer: string[] = [];
  let listBuffer: string[] = [];
  let paraBuffer: string[] = [];

  const flushList = () => {
    if (listBuffer.length) {
      blocks.push({ type: "ul", items: listBuffer });
      listBuffer = [];
    }
  };

  const flushPara = () => {
    if (paraBuffer.length) {
      blocks.push({ type: "p", text: paraBuffer.join(" ") });
      paraBuffer = [];
    }
  };

  const flushCode = () => {
    if (codeBuffer.length) {
      blocks.push({ type: "code", text: codeBuffer.join("\n") });
      codeBuffer = [];
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();

    if (line.startsWith("```")) {
      if (inCode) {
        inCode = false;
        flushCode();
      } else {
        flushList();
        flushPara();
        inCode = true;
      }
      continue;
    }

    if (inCode) {
      codeBuffer.push(rawLine);
      continue;
    }

    if (!line) {
      flushList();
      flushPara();
      continue;
    }

    if (line.startsWith("# ")) {
      flushList();
      flushPara();
      blocks.push({ type: "h1", text: line.slice(2).trim() });
      continue;
    }

    if (line.startsWith("## ")) {
      flushList();
      flushPara();
      blocks.push({ type: "h2", text: line.slice(3).trim() });
      continue;
    }

    if (line.startsWith("### ")) {
      flushList();
      flushPara();
      blocks.push({ type: "h3", text: line.slice(4).trim() });
      continue;
    }

    if (line.startsWith("- ")) {
      flushPara();
      listBuffer.push(line.slice(2).trim());
      continue;
    }

    paraBuffer.push(line);
  }

  flushList();
  flushPara();
  flushCode();

  return blocks;
};

export const Markdown = ({ content }: { content: string }) => {
  const blocks = React.useMemo(() => parseMarkdown(content), [content]);

  return (
    <div className="space-y-4 leading-7">
      {blocks.map((block, idx) => {
        if (block.type === "h1") {
          return (
            <h1 key={idx} className="text-2xl font-bold">
              {block.text}
            </h1>
          );
        }
        if (block.type === "h2") {
          return (
            <h2 key={idx} className="text-xl font-semibold">
              {block.text}
            </h2>
          );
        }
        if (block.type === "h3") {
          return (
            <h3 key={idx} className="text-lg font-semibold">
              {block.text}
            </h3>
          );
        }
        if (block.type === "ul") {
          return (
            <ul key={idx} className="list-disc space-y-1 pl-5">
              {block.items.map((item, itemIdx) => (
                <li key={itemIdx}>{item}</li>
              ))}
            </ul>
          );
        }
        if (block.type === "code") {
          return (
            <pre key={idx} className="bg-muted overflow-auto rounded-md p-3 text-sm">
              <code>{block.text}</code>
            </pre>
          );
        }
        return <p key={idx}>{block.text}</p>;
      })}
    </div>
  );
};
