"use client";

import { FormEvent, ReactNode, useState } from "react";

type GeneratedDraft = {
  message: string;
  file_name: string;
  quality_report?: string;
};

type DraftFile = {
  content: string;
  file_name: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "https://blog-automation-yw31.onrender.com";

function inlineMarkdown(text: string) {
  const parts: ReactNode[] = [];
  const matches =
    /(\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)|\*\*([^*]+)\*\*|`([^`]+)`|\*([^*\n]+)\*)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = matches.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    if (match[2] && match[3]) {
      parts.push(
        <a href={match[3]} key={match.index} rel="noreferrer" target="_blank">
          {match[2]}
        </a>,
      );
    } else if (match[4]) {
      parts.push(<strong key={match.index}>{match[4]}</strong>);
    } else if (match[5]) {
      parts.push(<code key={match.index}>{match[5]}</code>);
    } else if (match[6]) {
      parts.push(<em key={match.index}>{match[6]}</em>);
    }

    lastIndex = matches.lastIndex;
  }

  parts.push(text.slice(lastIndex));
  return parts;
}

function MarkdownPreview({ content }: { content: string }) {
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  const nodes: ReactNode[] = [];
  const metadata: string[] = [];
  let lineIndex = 0;
  let paragraph: string[] = [];
  let bullets: string[] = [];
  let numbered: string[] = [];
  let key = 0;

  if (lines[0]?.trim() === "---") {
    lineIndex = 1;
    while (lineIndex < lines.length && lines[lineIndex].trim() !== "---") {
      metadata.push(lines[lineIndex]);
      lineIndex += 1;
    }
    lineIndex += 1;
  }

  function flushParagraph() {
    if (paragraph.length) {
      nodes.push(<p key={key++}>{inlineMarkdown(paragraph.join(" "))}</p>);
      paragraph = [];
    }
  }

  function flushBullets() {
    if (bullets.length) {
      nodes.push(
        <ul key={key++}>
          {bullets.map((line, index) => (
            <li key={index}>{inlineMarkdown(line)}</li>
          ))}
        </ul>,
      );
      bullets = [];
    }
  }

  function flushNumbered() {
    if (numbered.length) {
      nodes.push(
        <ol key={key++}>
          {numbered.map((line, index) => (
            <li key={index}>{inlineMarkdown(line)}</li>
          ))}
        </ol>,
      );
      numbered = [];
    }
  }

  function flushText() {
    flushParagraph();
    flushBullets();
    flushNumbered();
  }

  while (lineIndex < lines.length) {
    const line = lines[lineIndex];
    const trimmed = line.trim();
    const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
    const bullet = trimmed.match(/^[-*]\s+(.+)$/);
    const ordered = trimmed.match(/^\d+\.\s+(.+)$/);

    if (trimmed.startsWith("```")) {
      flushText();
      const codeLines: string[] = [];
      lineIndex += 1;
      while (lineIndex < lines.length && !lines[lineIndex].trim().startsWith("```")) {
        codeLines.push(lines[lineIndex]);
        lineIndex += 1;
      }
      nodes.push(
        <pre key={key++}>
          <code>{codeLines.join("\n")}</code>
        </pre>,
      );
    } else if (!trimmed) {
      flushText();
    } else if (heading) {
      flushText();
      const level = Math.min(heading[1].length, 4);
      if (level === 1) {
        nodes.push(<h1 key={key++}>{inlineMarkdown(heading[2])}</h1>);
      } else if (level === 2) {
        nodes.push(<h2 key={key++}>{inlineMarkdown(heading[2])}</h2>);
      } else if (level === 3) {
        nodes.push(<h3 key={key++}>{inlineMarkdown(heading[2])}</h3>);
      } else {
        nodes.push(<h4 key={key++}>{inlineMarkdown(heading[2])}</h4>);
      }
    } else if (bullet) {
      flushParagraph();
      flushNumbered();
      bullets.push(bullet[1]);
    } else if (ordered) {
      flushParagraph();
      flushBullets();
      numbered.push(ordered[1]);
    } else if (trimmed.startsWith("> ")) {
      flushText();
      nodes.push(<blockquote key={key++}>{inlineMarkdown(trimmed.slice(2))}</blockquote>);
    } else {
      flushBullets();
      flushNumbered();
      paragraph.push(trimmed);
    }

    lineIndex += 1;
  }

  flushText();

  return (
    <article className="preview-content">
      {metadata.length > 0 && (
        <div className="frontmatter">
          <strong>Metadata</strong>
          {metadata.map((line, index) => (
            <div key={index}>{line}</div>
          ))}
        </div>
      )}
      {nodes}
    </article>
  );
}

export default function Home() {
  const [topic, setTopic] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [draftName, setDraftName] = useState("");
  const [draft, setDraft] = useState<GeneratedDraft | null>(null);
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [completionMessage, setCompletionMessage] = useState("");
  const [fileInputKey, setFileInputKey] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingDraft, setLoadingDraft] = useState(false);
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [dirty, setDirty] = useState(false);

  function showRequestError(caughtError: unknown, fallback: string) {
    setError(
      caughtError instanceof TypeError
        ? "Cannot reach the backend. Start it on port 8000 and try again."
        : caughtError instanceof Error
          ? caughtError.message
          : fallback,
    );
  }

  async function loadDraft(fileName: string) {
    setLoadingDraft(true);
    setError("");
    setSaveMessage("");

    try {
      const response = await fetch(`${apiUrl}/drafts/${encodeURIComponent(fileName)}`);
      const data: DraftFile & { detail?: string } = await response.json();
      if (!response.ok) {
        throw new Error(data.detail ?? "Unable to open the draft.");
      }

      setContent(data.content);
      setDirty(false);
      return true;
    } catch (caughtError) {
      showRequestError(caughtError, "Unable to open the draft.");
      return false;
    } finally {
      setLoadingDraft(false);
    }
  }

  async function generateDraft(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const value = topic.trim();
    if (!value && !pdfFile) {
      setError("Enter a topic or select a PDF file.");
      return;
    }

    if (pdfFile && pdfFile.size > 25 * 1024 * 1024) {
      setError("PDF source must be smaller than 25 MB.");
      return;
    }

    setLoading(true);
    setDraft(null);
    setContent("");
    setCompletionMessage("");
    setSaveMessage("");
    setError("");

    try {
      let body: BodyInit;
      let headers: HeadersInit | undefined;

      if (pdfFile) {
        const formData = new FormData();
        formData.append("file", pdfFile);
        formData.append("topic", value);
        body = formData;
      } else {
        headers = { "Content-Type": "application/json" };
        body = JSON.stringify({ topic: value });
      }

      const response = await fetch(`${apiUrl}/generate-blog`, {
        method: "POST",
        headers,
        body,
      });

      const data: GeneratedDraft & { detail?: string } = await response.json();
      if (!response.ok) {
        throw new Error(data.detail ?? "Unable to generate a draft.");
      }

      setDraft(data);
      setDraftName(data.file_name);
      await loadDraft(data.file_name);
    } catch (caughtError) {
      showRequestError(caughtError, "Unable to generate a draft.");
    } finally {
      setLoading(false);
    }
  }

  async function openExistingDraft(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fileName = draftName.trim();

    if (!fileName.endsWith(".mdx")) {
      setError("Enter an MDX file name, for example cts-blog-february.mdx.");
      return;
    }

    setCompletionMessage("");
    const loaded = await loadDraft(fileName);
    if (loaded) {
      setDraft({ message: "Draft ready for editing", file_name: fileName });
    }
  }

  async function saveDraft() {
    if (!draft) {
      return false;
    }

    setSaving(true);
    setError("");
    setSaveMessage("");

    try {
      const response = await fetch(
        `${apiUrl}/drafts/${encodeURIComponent(draft.file_name)}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content }),
        },
      );
      const data: { detail?: string } = await response.json();
      if (!response.ok) {
        throw new Error(data.detail ?? "Unable to save the draft.");
      }

      setDirty(false);
      setSaveMessage("Draft saved locally.");
      return true;
    } catch (caughtError) {
      showRequestError(caughtError, "Unable to save the draft.");
      return false;
    } finally {
      setSaving(false);
    }
  }

  async function publishDraft() {
    if (!draft) {
      return;
    }

    setPublishing(true);
    setError("");

    const saved = await saveDraft();
    if (!saved) {
      setPublishing(false);
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/publish-blog`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_name: draft.file_name }),
      });

      const data: { detail?: string } = await response.json();
      if (!response.ok) {
        throw new Error(data.detail ?? "Unable to publish the draft.");
      }

      setTopic("");
      setPdfFile(null);
      setDraftName("");
      setDraft(null);
      setContent("");
      setDirty(false);
      setSaveMessage("");
      setFileInputKey((currentKey) => currentKey + 1);
      setCompletionMessage("Blog published successfully to GitHub. Ready for the next blog.");
    } catch (caughtError) {
      showRequestError(caughtError, "Unable to publish the draft.");
    } finally {
      setPublishing(false);
    }
  }

  return (
    <main className={draft ? "page review-page" : "page"}>
      <header className="brand">
        <span className="mark">AI</span>
        <span>Blog Platform</span>
      </header>

      <section className="card generator">
        <p className="label">Draft generator</p>
        <h1>Write a new blog post</h1>
        <p className="intro">
          Add a topic or upload a PDF source. Your workflow turns it into a
          clean blog draft.
        </p>

        <form className="form" onSubmit={generateDraft}>
          <label htmlFor="topic">Blog topic <span>(optional with PDF)</span></label>
          <input
            autoComplete="off"
            id="topic"
            onChange={(event) => setTopic(event.target.value)}
            placeholder="Example: Using AI for small business marketing"
            value={topic}
          />
          <label className="file-label" htmlFor="pdf">
            Source PDF <span>(optional, max 25 MB)</span>
          </label>
          <input
            accept=".pdf,application/pdf"
            className="file-input"
            id="pdf"
            key={fileInputKey}
            onChange={(event) => setPdfFile(event.target.files?.[0] ?? null)}
            type="file"
          />
          <button disabled={loading} type="submit">
            {loading ? "Generating..." : "Generate draft"}
          </button>
        </form>

        <form className="open-draft" onSubmit={openExistingDraft}>
          <label htmlFor="draft-name">Open saved draft</label>
          <div className="inline-form">
            <input
              id="draft-name"
              onChange={(event) => setDraftName(event.target.value)}
              placeholder="cts-blog-february.mdx"
              value={draftName}
            />
            <button disabled={loadingDraft} type="submit">
              {loadingDraft ? "Opening..." : "Open"}
            </button>
          </div>
        </form>

        {error && (
          <p className="notice error" role="alert">
            {error}
          </p>
        )}

        {completionMessage && (
          <p className="notice publish-success" role="status">
            {completionMessage}
          </p>
        )}
      </section>

      {draft && (
        <section className="review">
          <div className="review-header">
            <div>
              <p className="label">Review draft</p>
              <h2 className="file-name">{draft.file_name}</h2>
              {draft.quality_report && <p className="quality-report">{draft.quality_report}</p>}
              {saveMessage && <p className="save-message">{saveMessage}</p>}
            </div>
            <div className="actions">
              <button
                className="secondary-button"
                disabled={saving || !dirty}
                onClick={saveDraft}
                type="button"
              >
                {saving ? "Saving..." : "Save draft"}
              </button>
              <button disabled={publishing} onClick={publishDraft} type="button">
                {publishing ? "Publishing..." : "Publish to GitHub"}
              </button>
            </div>
          </div>

          <div className="workspace">
            <div className="editor-panel">
              <label htmlFor="editor">MDX editor</label>
              <textarea
                id="editor"
                onChange={(event) => {
                  setContent(event.target.value);
                  setDirty(true);
                  setSaveMessage("");
                }}
                spellCheck="true"
                value={content}
              />
            </div>
            <div className="preview-panel">
              <span className="panel-title">Preview</span>
              <MarkdownPreview content={content} />
            </div>
          </div>
        </section>
      )}

      <p className="footer">Simple writing workflow powered by your backend.</p>
    </main>
  );
}
