import { useState } from "react";
import { ApiError, askAssistant } from "../api/client";
import { Button } from "../components/Button";
import { PageHeader } from "../components/Shell";
import { useGame } from "../state/game";

export function Assistant() {
  const { result, saved, openSaved, go } = useGame();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");
  const active = result ?? saved[0]?.result ?? null;

  async function ask() {
    const text = question.trim();
    if (!text || !active) return;
    setAsking(true);
    setError("");
    try {
      setAnswer(await askAssistant(active, text));
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "The assistant could not answer.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Grounded in the open case"
        title="AI Assistant"
        subtitle="Questions stay on this farm. The assistant does not pick a new rotation."
      />
      {!active && (
        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <p className="font-semibold text-navy">Start a case before asking. The assistant only talks about a farm that is already on screen.</p>
          <Button className="mt-4" onClick={() => go("farmer")}>
            Start a case
          </Button>
        </div>
      )}
      {active && !result && saved[0] && (
        <button type="button" className="mb-4 text-sm font-bold text-navy underline" onClick={() => openSaved(saved[0].id)}>
          Using {saved[0].farmerName}&apos;s saved case. Open it on the results screen.
        </button>
      )}
      {active && (
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-2 sm:flex-row">
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
          {error && <p className="mt-3 text-sm font-semibold text-watch">{error}</p>}
          {answer && <p className="mt-3 leading-relaxed text-ink/80">{answer}</p>}
        </section>
      )}
    </div>
  );
}
