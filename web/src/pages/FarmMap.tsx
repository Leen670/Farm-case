import { useEffect, useState } from "react";
import { ApiError, fetchClues } from "../api/client";
import { Button } from "../components/Button";
import { FarmIllustration } from "../components/FarmIllustration";
import { PageHeader } from "../components/Shell";
import { pinKey, toRequest, useGame } from "../state/game";
import { CLUE_ORDER, clueHint, clueTitle, clueValue } from "./clueText";

export function FarmMap() {
  const { draft, clues, setClues, loadedKey, setLoadedKey, collected, collect, go } = useGame();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [slow, setSlow] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [openId, setOpenId] = useState("climate");
  const key = pinKey(draft);

  useEffect(() => {
    if (!key || key === loadedKey) return;
    let cancel = false;
    setLoading(true);
    setError("");
    setSlow(false);
    const timer = window.setTimeout(() => setSlow(true), 4000);
    fetchClues(toRequest(draft))
      .then((next) => {
        if (cancel) return;
        setClues(next);
        setLoadedKey(key);
      })
      .catch((reason: unknown) => {
        if (cancel) return;
        setError(reason instanceof ApiError ? reason.message : "The clues did not load.");
      })
      .finally(() => {
        if (!cancel) setLoading(false);
      });
    return () => {
      cancel = true;
      window.clearTimeout(timer);
    };
  }, [key, loadedKey, attempt, draft, setClues, setLoadedKey]);

  const done = clues != null && CLUE_ORDER.every((id) => collected.includes(id));

  function openClue(id: string) {
    setOpenId(id);
    collect(id);
  }

  return (
    <div>
      <PageHeader
        eyebrow={draft.place || "Your pin"}
        title="Collect the clues"
        subtitle="Tap a spot on the farm. Each row keeps the value and the source for this pin."
      />

      {loading && (
        <p className="mb-4 rounded-xl bg-white px-4 py-3 font-semibold text-navy">
          {slow ? "Waking up the satellites…" : "Reading NASA POWER for this pin…"}
        </p>
      )}
      {error && (
        <p className="mb-4 rounded-xl bg-white px-4 py-3 font-semibold text-watch">
          {error}{" "}
          <button
            type="button"
            className="underline"
            onClick={() => {
              setLoadedKey("");
              setAttempt((value) => value + 1);
            }}
          >
            Try again
          </button>
        </p>
      )}

      <div className="grid items-start gap-6 md:grid-cols-[1.15fr_0.85fr]">
        {clues ? (
          <FarmIllustration clues={clues} collected={collected} openId={openId} onOpen={openClue} />
        ) : (
          <div className="min-h-64 rounded-3xl bg-white/60" />
        )}

        <aside className="rounded-2xl bg-[#f7f3e4] p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <p className="eyebrow">Collected clues</p>
            <p className="text-sm font-bold text-navy">
              {collected.length} of {CLUE_ORDER.length}
            </p>
          </div>
          <ul className="space-y-2">
            {CLUE_ORDER.map((id) => {
              const clue = clues?.find((item) => item.id === id);
              const on = collected.includes(id);
              return (
                <li key={id}>
                  <button
                    type="button"
                    disabled={!clue}
                    onClick={() => openClue(id)}
                    className={`flex w-full items-center gap-3 rounded-xl bg-white px-3 py-3 text-left ${
                      openId === id && on ? "ring-2 ring-lime" : ""
                    }`}
                  >
                    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-lime text-sm font-extrabold text-navy">
                      {clueTitle(id).slice(0, 1)}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block font-extrabold text-navy">{clueTitle(id)}</span>
                      <span className="block truncate text-sm text-ink/55">
                        {on && clue ? clueValue(clue) : clueHint(id)}
                      </span>
                    </span>
                    <span className="text-lg font-bold text-ink/30">{on ? "✓" : "›"}</span>
                  </button>
                </li>
              );
            })}
          </ul>
          <Button className="mt-4 w-full" disabled={!done} onClick={() => go("board")}>
            Review the evidence
          </Button>
        </aside>
      </div>
    </div>
  );
}
