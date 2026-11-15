import { useState } from "react";
import { Button } from "../components/Button";
import { EvidenceCard } from "../components/EvidenceCard";
import { PageHeader } from "../components/Shell";
import { useGame } from "../state/game";
import { CLUE_ORDER, clueHeadline, clueTitle, sourcePill } from "./clueText";

export function EvidenceBoard() {
  const { clues, go } = useGame();
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const cards = CLUE_ORDER.map((id) => clues?.find((clue) => clue.id === id)).filter((clue) => clue != null);

  return (
    <div>
      <PageHeader
        eyebrow="Evidence room"
        title="Your farm, decoded"
        subtitle="Each clue includes its value, source, and the reason it matters."
      />
      <div className="grid gap-4 md:grid-cols-2">
        {cards.map((clue) => (
          <EvidenceCard
            key={clue.id}
            title={clueTitle(clue.id)}
            value={clueHeadline(clue)}
            detail={clue.summary}
            source={clue.source}
            pill={sourcePill(clue.id)}
            imageUrl={clue.image_url}
          />
        ))}
      </div>
      {cards.length === 0 && (
        <p className="mt-6 rounded-xl bg-white px-4 py-3 font-semibold">Collect the four clues on the farm first.</p>
      )}
      <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
        <Button variant="secondary" onClick={() => setSourcesOpen((open) => !open)}>
          {sourcesOpen ? "Hide sources" : "View all sources"}
        </Button>
        <Button disabled={cards.length < 4} onClick={() => go("investigation")}>
          Run the analysis
        </Button>
      </div>
      {sourcesOpen && (
        <ul className="mt-4 space-y-2">
          {cards.map((clue) => (
            <li key={clue.id} className="rounded-xl bg-white px-4 py-3 text-sm">
              <p className="font-extrabold text-navy">{clueTitle(clue.id)}</p>
              <p className="text-ink/70">{clue.source}</p>
              {clue.source_url && (
                <a className="text-sky underline" href={clue.source_url} target="_blank" rel="noreferrer">
                  {clue.source_url}
                </a>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
