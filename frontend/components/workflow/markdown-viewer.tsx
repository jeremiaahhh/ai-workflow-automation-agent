"use client";

import { useMemo } from "react";

interface Props {
  markdown: string;
}

function escape(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function inline(s: string): string {
  // ordering matters: do code first, then links, then bold/italic
  let html = escape(s);
  html = html.replace(/`([^`]+)`/g, '<code class="rounded bg-muted px-1 py-0.5 text-[0.85em]">$1</code>');
  html = html.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a class="text-primary underline-offset-2 hover:underline" href="$2" target="_blank" rel="noreferrer">$1</a>',
  );
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/(^|\s)\*([^*]+)\*/g, "$1<em>$2</em>");
  return html;
}

function renderMarkdown(md: string): string {
  const lines = md.split("\n");
  const out: string[] = [];
  let inList: "ul" | "ol" | null = null;
  let inCode = false;
  let codeBuf: string[] = [];

  const closeList = () => {
    if (inList) {
      out.push(`</${inList}>`);
      inList = null;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine;
    if (line.startsWith("```")) {
      if (inCode) {
        out.push(
          `<pre class="my-3 overflow-auto rounded-lg border bg-muted/50 p-3 text-xs"><code>${codeBuf
            .map(escape)
            .join("\n")}</code></pre>`,
        );
        codeBuf = [];
        inCode = false;
      } else {
        closeList();
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      codeBuf.push(line);
      continue;
    }

    if (line.startsWith("# ")) {
      closeList();
      out.push(
        `<h1 class="mt-6 mb-3 text-2xl font-semibold tracking-tight">${inline(line.slice(2))}</h1>`,
      );
      continue;
    }
    if (line.startsWith("## ")) {
      closeList();
      out.push(
        `<h2 class="mt-5 mb-2 text-lg font-semibold tracking-tight">${inline(line.slice(3))}</h2>`,
      );
      continue;
    }
    if (line.startsWith("### ")) {
      closeList();
      out.push(
        `<h3 class="mt-4 mb-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">${inline(
          line.slice(4),
        )}</h3>`,
      );
      continue;
    }
    if (/^>\s+/.test(line)) {
      closeList();
      out.push(
        `<blockquote class="my-2 border-l-2 border-primary/40 bg-primary/5 px-3 py-2 text-sm">${inline(line.replace(/^>\s+/, ""))}</blockquote>`,
      );
      continue;
    }
    const ulMatch = line.match(/^\s*[-*]\s+(.*)$/);
    if (ulMatch) {
      if (inList !== "ul") {
        closeList();
        out.push('<ul class="my-2 space-y-1 pl-5 list-disc text-sm">');
        inList = "ul";
      }
      out.push(`<li>${inline(ulMatch[1])}</li>`);
      continue;
    }
    const olMatch = line.match(/^\s*\d+\.\s+(.*)$/);
    if (olMatch) {
      if (inList !== "ol") {
        closeList();
        out.push('<ol class="my-2 space-y-1 pl-5 list-decimal text-sm">');
        inList = "ol";
      }
      out.push(`<li>${inline(olMatch[1])}</li>`);
      continue;
    }
    if (line.trim() === "") {
      closeList();
      out.push("");
      continue;
    }
    closeList();
    out.push(`<p class="my-2 text-sm leading-relaxed text-foreground/90">${inline(line)}</p>`);
  }
  closeList();
  if (inCode) {
    out.push(
      `<pre class="my-3 overflow-auto rounded-lg border bg-muted/50 p-3 text-xs"><code>${codeBuf
        .map(escape)
        .join("\n")}</code></pre>`,
    );
  }
  return out.join("\n");
}

export function MarkdownViewer({ markdown }: Props) {
  const html = useMemo(() => renderMarkdown(markdown), [markdown]);
  return (
    <article
      className="prose-zinc dark:prose-invert max-w-none"
      // The markdown source is rendered server-side by our backend (we never
      // pass arbitrary user-supplied HTML through this function), and the
      // renderer above escapes the source before inserting inline patterns.
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
