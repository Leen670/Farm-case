import { useEffect, useState } from "react";
import { ApiError, createCase } from "../api/client";
import { BackButton } from "../components/BackButton";
import { toRequest, useGame } from "../state/game";

function art(file: string): string {
  return `/images/${encodeURIComponent(file)}`;
}

const STEPS = [
  { icon: "Farmer Avatar Icon.png", label: "1 Farmer Information", active: false },
  { icon: "Glossy Green Magnifying Glass Badge.png", label: "2 Collect Evidence", active: false },
  { icon: "Forest Green Investigation Checklist Badge.png", label: "3 AI Investigation", active: true },
  { icon: "Case Solved Checkmark Badge.png", label: "4 Case Solved", active: false },
];

const CARDS = [
  {
    title: "Climate Data",
    photo: "Cartoon Raincloud Over Green Fields.png",
    icon: "Sunny Cloud Cartoon Icon.png",
    points: ["Temperature", "Rainfall", "Weather patterns"],
    className: "col-start-1 row-start-1",
  },
  {
    title: "Crop Data",
    photo: "Aerial Patchwork of Farmland.png",
    icon: "Glossy Green Leaf Icon.png",
    points: ["Crop types", "Growth needs", "Rotation options"],
    className: "col-start-3 row-start-1",
  },
  {
    title: "Soil Data",
    photo: "Rich Loamy Soil Texture.png",
    icon: "Glossy Soil Mound Icon.png",
    points: ["Soil type", "Nutrients", "Moisture"],
    className: "col-start-1 row-start-2",
  },
  {
    title: "Water Data",
    photo: "Colorful Cartoon River Landscape.png",
    icon: "Glossy Teal Water Droplet Icon.png",
    points: ["Availability", "Usage", "Irrigation needs"],
    className: "col-start-3 row-start-2",
  },
] as const;

const CHECKS = [
  "Climate & Weather Patterns",
  "Soil Health & Composition",
  "Crop Compatibility",
  "Water Availability",
] as const;

export function Investigation() {
  const { draft, result, setResult, go } = useGame();
  const [error, setError] = useState("");
  const [slow, setSlow] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const ready = Boolean(result);
  const waiting = !result && !error;

  useEffect(() => {
    if (result) return;
    let cancel = false;
    setError("");
    setSlow(false);
    const timer = window.setTimeout(() => setSlow(true), 4000);
    let pending: Promise<unknown>;
    try {
      pending = createCase(toRequest(draft));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The case could not be scored.");
      return () => window.clearTimeout(timer);
    }
    pending
      .then((next) => {
        if (!cancel) setResult(next as NonNullable<typeof result>);
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
    ? "The rotation is scored"
    : slow
      ? "Waking up the satellites…"
      : "Analyzing crop rotation scenarios";

  return (
    <div className="relative h-screen overflow-hidden bg-[#07140f] text-[#2c3428]">
      <img
        src={art("Sunset Farm with Windmill and Barn.png")}
        alt=""
        className="absolute inset-0 h-full w-full object-cover object-[18%_center]"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-[#07140f] via-[#07140f]/55 to-[#10261c]/35" />

      <BackButton previous="map" />

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
                <img src={art("Cream Brain Icon with Green Outline.png")} alt="" className="h-9 w-9 object-contain" />
                <div className="min-w-0 text-left">
                  <p className="text-sm leading-tight font-extrabold text-[#2a2418]">AI Investigation</p>
                  <p className="text-[10px] text-[#6d6254]">Connecting the clues for a sustainable tomorrow.</p>
                </div>
              </div>
            </div>
            <div
              className="absolute top-3 right-4 flex h-12 w-24 flex-col items-center justify-center bg-contain bg-center bg-no-repeat"
              style={{ backgroundImage: `url("${art("Aged Torn Paper Scrap.png")}")` }}
            >
              <p className="text-[10px] font-extrabold text-[#3a3228]">Step 3 of 4</p>
              <span className="mt-0.5 flex gap-1" aria-hidden="true">
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#d9d0c0]" />
              </span>
            </div>
          </header>

          <div className="shrink-0 px-6 pt-1">
            <p className="text-[10px] font-extrabold tracking-[0.16em] text-[#1f8a3a]">
              {ready ? "INVESTIGATION COMPLETE" : "INVESTIGATION IN PROGRESS"}
            </p>
            <h1 className="text-2xl leading-tight font-extrabold text-[#16301c]">Connecting the clues...</h1>
            <p className="text-xs text-[#6d6254]">
              {ready
                ? "The clues are connected. Open the rotation when you are ready."
                : "Our crop advisor is comparing your farm conditions with the evidence."}
            </p>
          </div>

          <div className="relative mx-auto grid min-h-0 w-full max-w-4xl flex-1 grid-cols-[minmax(0,1fr)_14rem_minmax(0,1fr)] grid-rows-2 items-center gap-x-2 gap-y-2 px-4 py-2">
            <svg
              className="pointer-events-none absolute inset-0 h-full w-full"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <path d="M 30 24 C 40 20, 44 38, 50 46" stroke="#8fd6a8" strokeWidth="2.4" fill="none" vectorEffect="non-scaling-stroke" />
              <path d="M 70 24 C 60 20, 56 38, 50 46" stroke="#8fd6a8" strokeWidth="2.4" fill="none" vectorEffect="non-scaling-stroke" />
              <path d="M 30 76 C 40 80, 44 66, 48 60" stroke="#8fd6a8" strokeWidth="2.4" fill="none" vectorEffect="non-scaling-stroke" />
              <path d="M 70 76 C 60 80, 56 66, 52 60" stroke="#8fd6a8" strokeWidth="2.4" fill="none" vectorEffect="non-scaling-stroke" />
            </svg>

            {CARDS.map((card) => (
              <article
                key={card.title}
                className={`relative z-10 justify-self-center rounded-xl bg-[#f7f0dc] px-3 py-2 shadow-[0_8px_18px_rgba(70,45,10,0.08)] ${card.className}`}
              >
                <Paperclip />
                <div className="flex items-start gap-2 pr-4">
                  <div className="relative h-14 w-[4.5rem] shrink-0">
                    <img src={art(card.photo)} alt="" className="h-full w-full rounded-lg object-cover" />
                    <span className="absolute -top-1.5 -right-1.5 grid h-7 w-7 place-items-center overflow-hidden rounded-lg">
                      <img src={art(card.icon)} alt="" className="h-8 w-8 scale-125 object-cover" />
                    </span>
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-extrabold text-[#1d3a24]">{card.title}</p>
                    <ul className="mt-0.5 text-[10px] leading-tight text-[#6d6254]">
                      {card.points.map((point) => (
                        <li key={point}>• {point}</li>
                      ))}
                    </ul>
                  </div>
                </div>
                <span className="absolute right-2 bottom-2 grid h-5 w-5 place-items-center rounded-full bg-[#1f8a3a] text-[10px] font-bold text-white">
                  ✓
                </span>
              </article>
            ))}

            <div className="relative z-10 col-start-2 row-span-2 row-start-1 flex h-full flex-col items-center justify-center">
              <div className="pointer-events-none absolute top-[6%] h-36 w-36 rounded-full bg-[#d9f8e2] blur-md" />
              <div className="pointer-events-none absolute top-[10%] h-32 w-32 rounded-full border-[12px] border-[#e7f8ec]" />
              <div className="pointer-events-none absolute top-[16%] h-20 w-20 rounded-full border-8 border-[#c8f0d4]" />
              <img
                src={art("Smiling Sprout Robot Advisor.png")}
                alt="Crop advisor"
                className="relative z-10 h-32 w-auto object-contain"
              />
              <div className="relative z-10 -mt-3 w-full rounded-2xl bg-[#146b34] px-3.5 py-3 text-white shadow-[0_10px_24px_rgba(16,70,30,0.25)]">
                <p className="text-center text-sm font-extrabold">{ready ? "Analysis complete" : "Analyzing Data..."}</p>
                <ul className="mt-2 space-y-1.5 text-[11px] font-semibold">
                  {CHECKS.map((item) => (
                    <li key={item} className="flex items-center gap-2 border-b border-white/10 pb-1">
                      <Check />
                      <span>{item}</span>
                    </li>
                  ))}
                  <li className="flex items-center gap-2 pt-0.5">
                    {ready ? <Check /> : <Spinner />}
                    <span>{ready ? "Recommendations ready" : "Generating Recommendations..."}</span>
                  </li>
                </ul>
                {error && <p className="mt-2 text-[11px] font-semibold text-[#ffd0cb]">{error}</p>}
              </div>
            </div>
          </div>

          <div className="mx-5 mb-3 flex shrink-0 items-center gap-4 rounded-full bg-white px-5 py-2.5 shadow-sm">
            {ready ? (
              <button
                type="button"
                onClick={() => go("results")}
                className="rounded-full bg-[#1f8a3a] px-4 py-1.5 text-sm font-extrabold text-white"
              >
                See the rotation →
              </button>
            ) : error ? (
              <button
                type="button"
                onClick={() => {
                  setResult(null);
                  setAttempt((value) => value + 1);
                }}
                className="text-sm font-extrabold text-[#b42318]"
              >
                Try again
              </button>
            ) : (
              <p className="text-sm font-extrabold text-[#1d3a24]">{status}</p>
            )}
            <div className="h-2.5 min-w-0 flex-1 overflow-hidden rounded-full bg-[#e5efe4]">
              <div
                className="h-full rounded-full bg-[#1f8a3a] transition-all"
                style={{ width: ready ? "100%" : waiting ? "75%" : "35%" }}
              />
            </div>
            <p className="shrink-0 text-[11px] font-semibold text-[#6d6254]">
              {ready ? "4 of 4 analysis steps complete" : "3 of 4 analysis steps complete"}
            </p>
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

function Check() {
  return (
    <span className="grid h-3.5 w-3.5 shrink-0 place-items-center rounded-full bg-[#d8ffe4] text-[9px] font-bold text-[#146b34]">
      ✓
    </span>
  );
}

function Spinner() {
  return <span className="h-3.5 w-3.5 shrink-0 animate-spin rounded-full border-2 border-white/30 border-t-white" />;
}

function Paperclip() {
  return (
    <svg viewBox="0 0 24 36" className="absolute -top-3 left-4 h-6 w-4 text-[#c5bfb2]" aria-hidden="true">
      <path
        d="M9 12c0-5 7-7 7 1v14c0 4-5 6-7 2"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
    </svg>
  );
}
