import { HeaderNav } from "@/components/HeaderNav";
import { getBibliographyEntries } from "@/lib/bibliography";

export default async function BibliographyPage() {
  const entries = await getBibliographyEntries();

  return (
    <main className="min-h-screen bg-paper text-ink">
      <header className="border-b border-ink/15 bg-vellum">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-6 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="section-kicker">Source registry</p>
            <h1 className="font-serif text-4xl font-semibold leading-tight md:text-5xl">
              Bibliography
            </h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-slate">
              The online PDF links for every source document.
            </p>
          </div>
          <HeaderNav activePage="bibliography" />
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-5 py-8">
        <div className="bibliography-list">
          {entries.map((entry) => (
            <article id={entry.anchorId} key={entry.fileName} className="bibliography-item">
              <h2>{entry.title}</h2>
              <p>
                <strong>About:</strong> {entry.description}
              </p>
              <p>
                <strong>Online PDF:</strong>{" "}
                <a href={entry.onlinePdfUrl} target="_blank" rel="noreferrer">
                  {entry.onlinePdfUrl}
                </a>
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
