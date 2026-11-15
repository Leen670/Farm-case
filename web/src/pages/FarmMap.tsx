import { useEffect, useState } from "react";
import { ApiError, fetchClues } from "../api/client";
import { BackButton } from "../components/BackButton";
import { pinKey, toRequest, useGame } from "../state/game";
import { CLUE_ORDER, clueValue } from "./clueText";

function art(file: string): string {
  return `/images/${encodeURIComponent(file)}`;
}

const STEPS = [
  { icon: "Farmer Avatar Icon.png", label: "1 Farmer Information", active: false },
  { icon: "Glossy Green Magnifying Glass Badge.png", label: "2 Collect Evidence", active: true },
  { icon: "Forest Green Investigation Checklist Badge.png", label: "3 AI Investigation", active: false },
  { icon: "Case Solved Checkmark Badge.png", label: "4 Case Solved", active: false },
];

const STATIONS = [
  {
    id: "climate",
    title: "Weather",
    source: "NASA POWER · Climate",
    icon: "Sunny Cloud Cartoon Icon.png",
    x: "62%",
    y: "26%",
  },
  {
    id: "water",
    title: "Water",
    source: "NASA POWER + SMAP",
    icon: "Glossy Teal Water Droplet Icon.png",
    x: "74%",
    y: "66%",
  },
  {
    id: "crop",
    title: "Crop health",
    source: "MODIS vegetation",
    icon: "Glossy Green Leaf Icon.png",
    x: "75%",
    y: "38%",
  },
  {
    id: "soil",
    title: "Soil",
    source: "Farmer input",
    icon: "Glossy Soil Mound Icon.png",
    x: "33%",
    y: "69%",
  },
] as const;

export function FarmMap() {
  const { draft, clues, setClues, loadedKey, setLoadedKey, collected, collect, go } = useGame();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [slow, setSlow] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [openId, setOpenId] = useState("");
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
    if (!clues?.some((clue) => clue.id === id)) return;
    setOpenId(id);
    collect(id);
  }

  return (
    <div className="relative h-screen overflow-hidden bg-[#07140f] text-[#2c3428]">
      <img
        src={art("Sunset Farm with Windmill and Barn.png")}
        alt=""
        className="absolute inset-0 h-full w-full object-cover object-[18%_center]"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-[#07140f] via-[#07140f]/55 to-[#10261c]/35" />

      <BackButton previous="farmer" />

      <div className="relative z-30 flex h-full gap-4 px-4 pt-16 pb-4 sm:px-6">
        <aside className="hidden w-52 shrink-0 flex-col md:flex">
          <img src={art("Farm Case Sprout Logo.png")} alt="Farm Case" className="mt-2 w-40 object-contain" />
          <ol className="mt-8 space-y-3">
            {STEPS.map((step) => (
              <li key={step.label}>
                {step.active ? (
                  <div className="flex items-center gap-2 rounded-full border border-[#c8f5a8] bg-[#14301c]/90 px-1.5 py-1 shadow-[0_0_18px_rgba(150,255,120,0.35)]">
                    <img src={art(step.icon)} alt="" className="h-9 w-9 object-contain" />
                    <span className="text-xs font-extrabold text-white">{step.label}</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 px-1.5 text-xs font-semibold text-white/85">
                    <img src={art(step.icon)} alt="" className="h-8 w-8 object-contain" />
                    <span>{step.label}</span>
                  </div>
                )}
              </li>
            ))}
          </ol>
        </aside>

        <section className="mb-2 flex min-w-0 flex-1 flex-col overflow-hidden rounded-[28px] bg-[#f4efe4] shadow-[0_18px_50px_rgba(0,0,0,0.28)]">
          <header className="relative shrink-0 px-5 pt-3 pr-28 pb-1">
            <div className="relative mx-auto h-16 w-[min(420px,100%)]">
              <img src={art("Torn Cream Paper Banner.png")} alt="" className="h-full w-full object-cover object-center" />
              <div className="absolute inset-0 flex items-center justify-center gap-2 px-8">
                <img src={art("Cartoon Magnifying Glass Icon.png")} alt="" className="h-9 w-9 object-contain" />
                <div className="min-w-0 text-left">
                  <p className="text-sm leading-tight font-extrabold text-[#2a2418]">Collect the Clues</p>
                  <p className="text-[10px] text-[#6d6254]">Explore each station to reveal the evidence for your farm.</p>
                </div>
              </div>
            </div>
            <div
              className="absolute top-3 right-4 flex h-12 w-24 flex-col items-center justify-center bg-contain bg-center bg-no-repeat"
              style={{ backgroundImage: `url("${art("Aged Torn Paper Scrap.png")}")` }}
            >
              <p className="text-[10px] font-extrabold text-[#3a3228]">Step 2 of 4</p>
              <span className="mt-0.5 flex gap-1" aria-hidden="true">
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#d9d0c0]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#d9d0c0]" />
              </span>
            </div>
          </header>

          <div className="flex min-h-0 flex-1 items-center gap-3 overflow-hidden px-4 pb-4">
            <div className="flex h-full min-h-0 min-w-0 flex-1 items-center justify-center">
              <div className="relative aspect-[3/2] w-full max-h-full">
                <img
                  src={art("Isometric Cartoon Farm Island.png")}
                  alt="Isometric farm with a barn, gardens, weather station, greenhouse, and pond"
                  className="h-full w-full object-contain"
                />
                {STATIONS.map((station) => {
                  const on = collected.includes(station.id);
                  return (
                    <button
                      key={station.id}
                      type="button"
                      aria-label={station.title}
                      onClick={() => openClue(station.id)}
                      className="absolute grid h-16 w-16 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full hover:bg-white/30"
                      style={{ left: station.x, top: station.y }}
                    >
                      {on && (
                        <span className="grid h-6 w-6 place-items-center rounded-full bg-[#2f8a34] text-xs font-bold text-white shadow">
                          ✓
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            <aside className="flex max-h-full w-64 shrink-0 flex-col overflow-y-auto rounded-2xl bg-[#f7f4ea] p-3.5 shadow-[0_8px_24px_rgba(60,40,10,0.06)] xl:w-72">
              <h2 className="text-sm font-extrabold tracking-wide text-[#1d5c28]">NASA EVIDENCE</h2>
              <p className="mt-0.5 text-[11px] text-[#8a8174]">4 clues from trusted data sources</p>
              {loading && (
                <p className="mt-2 text-[11px] font-semibold text-[#1d5c28]">
                  {slow ? "Waking up the satellites…" : "Reading NASA POWER for this pin…"}
                </p>
              )}
              {error && (
                <p className="mt-2 text-[11px] font-semibold text-[#b42318]">
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
              <ul className="mt-3 space-y-2">
                {STATIONS.map((station) => {
                  const clue = clues?.find((item) => item.id === station.id);
                  const on = collected.includes(station.id);
                  return (
                    <li key={station.id}>
                      <button
                        type="button"
                        disabled={!clue}
                        onClick={() => openClue(station.id)}
                        className={`flex w-full items-center gap-3 rounded-xl bg-white px-2.5 py-2 text-left shadow-sm disabled:opacity-60 ${
                          openId === station.id && on ? "ring-2 ring-[#2f8a34]" : ""
                        }`}
                      >
                        <span className="grid h-11 w-11 shrink-0 place-items-center overflow-hidden rounded-xl">
                          <img src={art(station.icon)} alt="" className="h-12 w-12 scale-125 object-cover" />
                        </span>
                        <span className="min-w-0 flex-1">
                          <span className="block text-sm font-extrabold text-[#243026]">{station.title}</span>
                          <span className="block truncate text-[11px] text-[#8a8174]">
                            {on && clue ? clueValue(clue) : station.source}
                          </span>
                        </span>
                        <span
                          className={`grid h-5 w-5 shrink-0 place-items-center rounded-full border-2 ${
                            on ? "border-[#2f8a34] bg-[#2f8a34]" : "border-[#d7d1c4] bg-white"
                          }`}
                          aria-hidden="true"
                        >
                          {on && <span className="h-2 w-2 rounded-full bg-white" />}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
              <button
                type="button"
                disabled={!done}
                onClick={() => go("investigation")}
                className="mt-4 rounded-xl bg-[#1f6b32] px-4 py-3 text-sm font-extrabold text-white shadow-[0_3px_0_#145024] disabled:cursor-not-allowed disabled:opacity-40"
              >
                Analyze with AI →
              </button>
            </aside>
          </div>
        </section>
      </div>

      <img
        src={art("Glossy Green Leafy Corner Frame.png")}
        alt=""
        className="pointer-events-none absolute inset-0 z-20 h-full w-full object-cover"
      />
    </div>
  );
}
