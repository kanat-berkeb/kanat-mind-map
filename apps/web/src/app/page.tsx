"use client";

import { FormEvent, useState } from "react";

type SourceType = "pdf" | "txt" | "markdown" | "software_note";

interface EvidenceAtom {
  atomId: string;
  atomIndex: number;
  text: string;
  qualityScore: number;
  sectionPath: string[];
  location: { page?: number | null } | null;
}

interface ProcessResult {
  evidenceAtoms: EvidenceAtom[];
  candidateFacts: unknown[];
  metadata: {
    fileName: string;
    sourceType: string;
    atomCount: number;
    candidateFactCount: number;
  };
  warnings: Array<{ code: string; message: string }>;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:3001";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [sourceType, setSourceType] = useState<SourceType>("txt");
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;

    setLoading(true);
    setError("");
    setResult(null);
    const form = new FormData();
    form.append("file", file);
    form.append("sourceType", sourceType);

    try {
      const response = await fetch(`${API_BASE_URL}/documents/process`, {
        method: "POST",
        body: form,
      });
      const payload: unknown = await response.json();
      if (!response.ok) {
        const message =
          payload && typeof payload === "object" && "message" in payload
            ? String(payload.message)
            : "Doküman işlenemedi.";
        throw new Error(message);
      }
      setResult(payload as ProcessResult);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Bağlantı hatası.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 px-5 py-12 text-zinc-100">
      <div className="mx-auto max-w-4xl space-y-8">
        <header className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-400">
            Kanat MindMap · Dikey Akış
          </p>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-5xl">
            Dokümanı evidence atomlarına böl
          </h1>
          <p className="text-zinc-400">
            Next.js → NestJS → FastAPI. Şimdilik persistence ve LLM extraction
            yok.
          </p>
        </header>

        <form
          onSubmit={submit}
          className="grid gap-4 rounded-2xl border border-zinc-800 bg-zinc-900 p-5 sm:grid-cols-[1fr_180px_auto] sm:items-end"
        >
          <label className="space-y-2 text-sm">
            <span className="block font-medium">Doküman</span>
            <input
              type="file"
              accept=".pdf,.txt,.md"
              required
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              className="block w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-zinc-300 file:mr-3 file:border-0 file:bg-transparent file:text-emerald-400"
            />
          </label>

          <label className="space-y-2 text-sm">
            <span className="block font-medium">Kaynak tipi</span>
            <select
              value={sourceType}
              onChange={(event) =>
                setSourceType(event.target.value as SourceType)
              }
              className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2.5"
            >
              <option value="txt">TXT</option>
              <option value="markdown">Markdown</option>
              <option value="software_note">Software note</option>
              <option value="pdf">PDF</option>
            </select>
          </label>

          <button
            type="submit"
            disabled={!file || loading}
            className="rounded-lg bg-emerald-400 px-5 py-2.5 font-semibold text-zinc-950 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading ? "İşleniyor…" : "Yükle ve işle"}
          </button>
        </form>

        {error && (
          <p className="rounded-xl border border-red-900 bg-red-950/40 p-4 text-red-300">
            {error}
          </p>
        )}

        {result && (
          <section className="space-y-4">
            <div className="flex flex-wrap gap-3 text-sm">
              <span className="rounded-full border border-zinc-700 px-3 py-1">
                {result.metadata.fileName}
              </span>
              <span className="rounded-full border border-zinc-700 px-3 py-1">
                {result.metadata.atomCount} atom
              </span>
              <span className="rounded-full border border-zinc-700 px-3 py-1">
                {result.metadata.candidateFactCount} candidate fact
              </span>
            </div>

            {result.warnings.map((warning) => (
              <p key={warning.code} className="text-sm text-amber-300">
                {warning.code}: {warning.message}
              </p>
            ))}

            <div className="space-y-3">
              {result.evidenceAtoms.map((atom) => (
                <article
                  key={atom.atomId}
                  className="rounded-xl border border-zinc-800 bg-zinc-900 p-5"
                >
                  <div className="mb-3 flex flex-wrap justify-between gap-2 text-xs text-zinc-500">
                    <code>{atom.atomId}</code>
                    <span>
                      kalite {atom.qualityScore}
                      {atom.location?.page
                        ? ` · sayfa ${atom.location.page}`
                        : ""}
                    </span>
                  </div>
                  {atom.sectionPath.length > 0 && (
                    <p className="mb-2 text-xs text-emerald-400">
                      {atom.sectionPath.join(" / ")}
                    </p>
                  )}
                  <p className="leading-7 text-zinc-200">{atom.text}</p>
                </article>
              ))}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
