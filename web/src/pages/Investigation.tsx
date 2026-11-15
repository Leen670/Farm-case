import { useEffect, useState } from "react";
import { ApiError, createCase } from "../api/client";
import { Button } from "../components/Button";
import { PageHeader } from "../components/Shell";
import { toRequest, useGame } from "../state/game";
import { CLUE_ORDER, clueTitle } from "./clueText";

export function Investigation() {
  const { draft, clues, result, setResult, go } = useGame();
  const [error, setError] = useState("");
  const [slow, setSlow] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const waiting = !result && !error;
  const ready = Boolean(result);

  useEffect(() => {
    if (result) return;
    let cancel = false;
    setError("");
    const timer = window.setTimeout(() => setSlow(true), 4000);
    createCase(toRequest(draft))
      .then((next) => {
        if (!cancel) setResult(next);
      })
      .catch((reason: unknown) => {
        if (!cancel) setError(reason instanceof ApiError ? reason.message : "The case could not be scored.");
      });
    return () => {
      cancel = true;
      window.clearTimeout(timer);
    };
  }, [draft, result, setResult, attempt]);

  const status = ready
    ? "The rotation is scored."
    : slow
      ? "Waking up the satellites…"
      : "Scoring this farm's rotation";

  return (
    <div>
      <PageHeader
        tone="dark"
        eyebrow="Analysis in progress"
        title="Connecting the clues…"
        subtitle="The checks and the bar follow the case response. They do not run on a timer."
      />

      <div className="grid items-center gap-4 lg:grid-cols-[1fr_auto_1fr]">
        <ClueSlot id="climate" done={(clues?.length ?? 0) >= 4} />
        <Hub spinning={waiting} />
        <ClueSlot id="water" done={(clues?.length ?? 0) >= 4} />
        <ClueSlot id="crop" done={ready} />
        <ClueSlot id="soil" done={ready} />
      </div>

      <div className="mx-auto mt-8 max-w-xl rounded-2xl bg-[#f7f3e4] px-5 py-4 text-ink">
        <p className="font-extrabold text-navy">{status}</p>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-ink/10">
          <div className="h-full rounded-full bg-moss transition-all" style={{ width: ready ? "100%" : "35%" }} />
        </div>
        <p className="mt-2 text-xs text-ink/55">
          {ready ? "Open the results when you are ready." : "NASA POWER and the ranker are still working."}
        </p>
      </div>

      {error && <p className="mt-4 font-semibold text-[#ffb4ae]">{error}</p>}
      <div className="mt-4 flex flex-wrap gap-3">
        {ready && <Button onClick={() => go("results")}>See the rotation</Button>}
        {error && (
          <Button
            variant="secondary"
            onClick={() => {
              setResult(null);
              setAttempt((value) => value + 1);
            }}
          >
            Try again
          </Button>
        )}
      </div>
    </div>
  );
}

function Hub({ spinning }: { spinning: boolean }) {
  return (
    <div className={`row-span-2 hidden place-items-center lg:grid ${spinning ? "animate-pulse" : ""}`}>
      <div className="grid h-40 w-40 place-items-center rounded-full bg-[#145c32]">
        <div className="grid h-24 w-24 place-items-center rounded-full bg-lime text-4xl font-extrabold text-navy">+</div>
      </div>
    </div>
  );
}

function ClueSlot({ id, done }: { id: (typeof CLUE_ORDER)[number]; done: boolean }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl bg-[#f7f3e4] px-4 py-3 text-ink">
      <span className="grid h-8 w-8 place-items-center rounded-full bg-lime text-sm font-extrabold text-navy">
        {clueTitle(id).slice(0, 1)}
      </span>
      <span className="flex-1 font-extrabold text-navy">{clueTitle(id)}</span>
      <span className="font-bold text-moss">{done ? "✓" : ""}</span>
    </div>
  );
}
