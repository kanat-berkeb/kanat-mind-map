export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 py-16 text-foreground">
      <section className="w-full max-w-3xl space-y-8 rounded-3xl border bg-card p-8 shadow-sm sm:p-12">
        <div className="space-y-4">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-muted-foreground">
            Human-reviewed knowledge graph
          </p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-6xl">
            Singularity Mini KG Demo
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-muted-foreground">
            Dokümanlardan evidence atomları ve candidate fact&apos;ler üretin,
            onaylanan bilgileri knowledge graph üzerinde inceleyin.
          </p>
        </div>

        <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
          {[
            "PDF / TXT / MD",
            "Human review",
            "Neo4j graph",
            "Basic ask",
          ].map((label) => (
            <span key={label} className="rounded-full border px-4 py-2">
              {label}
            </span>
          ))}
        </div>
      </section>
    </main>
  );
}
