import { useState } from "react";
import { ApiError, askAssistant } from "../api/client";
import { Button } from "../components/Button";
import { LEGUMES, titleCase } from "../data/farms";
import { PageHeader } from "../components/Shell";
import { useGame } from "../state/game";

export function Results() {
  const { result, draft, go, saveCurrent } = useGame();
  const [showEvidence, setShowEvidence] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);
  const [askError, setAskError] = useState("");

  if (!result) {
    return (
      <div>
        <h1 className="text-3xl font-extrabold text-navy">No case open</h1>
        <p className="mt-2 text-ink/70">Run the analysis to score a rotation for this farm.</p>
        <Button className="mt-4" onClick={() => go("investigation")}>
          Analyze with AI
        </Button>
      </div>
    );
  }

  const plan = result.recommended;
  const farmer = draft.farmerName.trim() || "This farm";

  async function ask() {
    const text = question.trim();
    if (!text || !result) return;
    setAsking(true);
    setAskError("");
    try {
      setAnswer(await askAssistant(result, text));
    } catch (reason) {
      setAskError(reason instanceof ApiError ? reason.message : "The assistant could not answer.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow={`Case ${result.case_id.slice(0, 6)}`}
        title="A smarter 3-year rotation"
        subtitle={`A plan built from ${farmer}'s climate, water, vegetation, and soil evidence.`}
      />
      {result.used_fallback && (
        <p className="mt-4 rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-navy">
          These climate numbers came from a saved NASA POWER response, not a fresh download.
        </p>
      )}

      <section className="mt-6 rounded-3xl bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <span className="rounded-full bg-moss px-3 py-1 text-xs font-extrabold tracking-wide text-white">
              BEST MATCH
            </span>
            <h2 className="mt-3 text-2xl font-extrabold text-navy">Recommended crop rotation</h2>
          </div>
          <p className="text-5xl font-extrabold text-lime-dark">{plan.suitability}%</p>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          {plan.rotation.map((crop, index) => {
            const legume = LEGUMES.has(crop);
            const reason = plan.reasons.find((line) => line.toLowerCase().includes(crop.toLowerCase()));
            return (
              <article key={`${crop}-${index}`} className={`rounded-2xl p-4 ${legume ? "bg-leaf" : "bg-cream"}`}>
                <p className="eyebrow">Year {index + 1}</p>
                <h3 className="mt-2 text-xl font-extrabold uppercase text-navy">{titleCase(crop)}</h3>
                <p className="mt-2 text-sm text-ink/70">
                  {reason ?? "Chosen for this farm's climate, water, and soil."}
                </p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="mt-4 rounded-3xl bg-white p-5 shadow-sm">
        <h2 className="text-lg font-extrabold text-navy">Alternative plans</h2>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {result.alternatives.map((alt, index) => (
            <article key={alt.rotation.join("-")} className="rounded-2xl bg-cream p-4">
              <p className="font-extrabold text-navy">
                Plan {index === 0 ? "B" : "C"} · {alt.suitability}% match
              </p>
              <p className="mt-1 text-sm text-ink/75">
                {alt.rotation.map((crop) => titleCase(crop)).join(" → ")}
              </p>
            </article>
          ))}
        </div>
        <p className="mt-3 text-sm text-ink/55">Compare water demand and seasonal risk.</p>
      </section>

      <section className="mt-4 rounded-3xl bg-white p-5 shadow-sm">
        <h2 className="text-lg font-extrabold text-navy">Why this plan</h2>
        <p className="mt-2 leading-relaxed text-ink/80">{result.explanation}</p>
        <p className="mt-3 text-xs text-ink/45">
          The crops and the score come from the ranker. This paragraph only restates them, and may be rewritten by an AI model.
        </p>
      </section>

      {plan.risks.length > 0 && (
        <section className="mt-4 rounded-3xl bg-white p-5 shadow-sm">
          <h2 className="text-lg font-extrabold text-watch">Watch out</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink/80">
            {plan.risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </section>
      )}

      <div className="mt-6 flex flex-wrap gap-3">
        <Button variant="secondary" onClick={() => setShowEvidence((open) => !open)}>
          {showEvidence ? "Hide the evidence" : "See the evidence"}
        </Button>
        <Button
          onClick={() => {
            saveCurrent();
            go("files");
          }}
        >
          Complete case
        </Button>
      </div>

      {showEvidence && (
        <div className="mt-4 overflow-hidden rounded-3xl bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-cream text-xs uppercase tracking-wide text-ink/50">
              <tr>
                <th className="px-4 py-3">Clue</th>
                <th className="px-4 py-3">Value</th>
                <th className="px-4 py-3">Source</th>
              </tr>
            </thead>
            <tbody>
              {result.evidence.map((row) => (
                <tr key={row.label} className="border-t border-ink/5">
                  <td className="px-4 py-3 font-bold">{row.label}</td>
                  <td className="px-4 py-3">
                    {row.value}
                    {row.unit ? ` ${row.unit}` : ""}
                  </td>
                  <td className="px-4 py-3 text-ink/60">{row.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <section className="mt-6 rounded-3xl bg-white p-5 shadow-sm">
        <h2 className="text-lg font-extrabold text-navy">Ask about this case</h2>
        <p className="mt-1 text-sm text-ink/60">
          Questions stay on this farm. The assistant does not pick a new rotation.
        </p>
        <div className="mt-3 flex flex-col gap-2 sm:flex-row">
          <input
            className="field"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Why this rotation?"
            onKeyDown={(event) => {
              if (event.key === "Enter") void ask();
            }}
          />
          <Button disabled={asking || question.trim().length === 0} onClick={() => void ask()}>
            {asking ? "Asking…" : "Ask"}
          </Button>
        </div>
        {askError && <p className="mt-3 text-sm font-semibold text-watch">{askError}</p>}
        {answer && <p className="mt-3 leading-relaxed text-ink/80">{answer}</p>}
      </section>

      <p className="mt-6 text-xs text-ink/45">
        Data: NASA POWER, NASA GIBS (MODIS, SMAP, IMERG). Crop water needs follow FAO tables.
      </p>
    </div>
  );
}
