import { useState, type ReactNode } from "react";
import { ApiError, askAssistant } from "../api/client";
import { BackButton } from "../components/BackButton";
import { CropPlant } from "../components/CropPlant";
import { titleCase } from "../data/farms";
import { useGame } from "../state/game";

function art(file: string): string {
  return `${import.meta.env.BASE_URL}images/${encodeURIComponent(file)}`;
}

const STEPS = [
  { icon: "Farmer Avatar Icon.png", label: "1 Farmer Information", active: false },
  { icon: "Glossy Green Magnifying Glass Badge.png", label: "2 Collect Evidence", active: false },
  { icon: "Forest Green Investigation Checklist Badge.png", label: "3 AI Investigation", active: false },
  { icon: "Case Solved Checkmark Badge.png", label: "4 Case Solved", active: true },
];

const CHIPS = ["Climate", "Water", "Vegetation", "Soil"];

export function Results() {
  const { result, draft, go, saveCurrent } = useGame();
  const [showEvidence, setShowEvidence] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);
  const [askError, setAskError] = useState("");

  if (!result) {
    return (
      <div className="grid h-screen place-items-center bg-[#07140f] text-white">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold">No case open</h1>
          <p className="mt-2 text-white/70">Run the analysis to score a rotation for this farm.</p>
          <button
            type="button"
            onClick={() => go("investigation")}
            className="mt-4 rounded-full bg-[#1f8a3a] px-4 py-2 text-sm font-extrabold"
          >
            Analyze with AI
          </button>
        </div>
      </div>
    );
  }

  const plan = result.recommended;
  const farmer = draft.farmerName.trim() || "your";
  const alternatives = result.alternatives.slice(0, 2);

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
    <div className="relative h-screen overflow-hidden bg-[#07140f] text-[#2c3428]">
      <img
        src={art("Sunset Farm with Windmill and Barn.png")}
        alt=""
        className="absolute inset-0 h-full w-full object-cover object-[18%_center]"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-[#07140f] via-[#07140f]/55 to-[#10261c]/35" />

      <BackButton previous="investigation" />

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
            <div className="relative mx-auto h-16 w-[min(440px,100%)]">
              <img src={art("Torn Cream Paper Banner.png")} alt="" className="h-full w-full object-cover object-center" />
              <div className="absolute inset-0 flex items-center justify-center gap-2 px-8">
                <img src={art("Case Solved Checkmark Badge.png")} alt="" className="h-9 w-9 object-contain" />
                <div className="min-w-0 text-left">
                  <p className="text-sm leading-tight font-extrabold text-[#2a2418]">Case Solved!</p>
                  <p className="text-[10px] text-[#6d6254]">A smarter 3-year rotation built from your evidence.</p>
                </div>
              </div>
            </div>
            <div
              className="absolute top-3 right-4 flex h-12 w-24 flex-col items-center justify-center bg-contain bg-center bg-no-repeat"
              style={{ backgroundImage: `url("${art("Aged Torn Paper Scrap.png")}")` }}
            >
              <p className="text-[10px] font-extrabold text-[#3a3228]">Step 4 of 4</p>
              <span className="mt-0.5 flex gap-1" aria-hidden="true">
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
              </span>
            </div>
          </header>

          <div className="min-h-0 flex-1 overflow-y-auto px-4 pt-2 pb-3">
            <div className="rounded-2xl bg-[#f6edd8] px-4 py-3 shadow-[0_8px_20px_rgba(70,45,10,0.08)]">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-[10px] font-extrabold tracking-[0.14em] text-[#8a8174]">
                    CASE REPORT · {result.case_id.slice(0, 6).toUpperCase()}
                  </p>
                  <h1 className="text-xl font-extrabold text-[#1d3a24]">Recommended crop rotation</h1>
                  <p className="text-[11px] text-[#6d6254]">
                    A 3-year plan built from {farmer}&apos;s climate, water, vegetation, and soil evidence.
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] font-extrabold text-[#6d6254]">Match Score</p>
                  <p className="text-3xl leading-none font-extrabold text-[#1f8a3a]">{plan.suitability}%</p>
                </div>
              </div>

              {result.used_fallback && (
                <p className="mt-2 text-[11px] font-semibold text-[#6d6254]">
                  These climate numbers came from a saved NASA POWER response, not a fresh download.
                </p>
              )}

              <div className="mt-3 flex items-center gap-2">
                <div className="flex min-w-0 flex-1 items-center justify-center gap-1.5">
                  {plan.rotation.map((crop, index) => (
                    <div key={`${crop}-${index}`} className="flex items-center gap-1.5">
                      <article className="w-[7.5rem] rounded-lg bg-white p-1.5 shadow-sm">
                        <p className="text-center text-[9px] font-extrabold tracking-wide text-[#6d6254]">YEAR {index + 1}</p>
                        <div className="mt-1 h-16 overflow-hidden rounded-md">
                          <CropPlant name={crop} />
                        </div>
                        <p className="py-1 text-center text-xs font-extrabold text-[#1d3a24]">{titleCase(crop)}</p>
                      </article>
                      {index < plan.rotation.length - 1 && <span className="text-sm font-bold text-[#8a8174]">→</span>}
                    </div>
                  ))}
                </div>
                <img
                  src={art("Smiling Sprout Robot Advisor.png")}
                  alt=""
                  className="hidden h-28 w-auto shrink-0 object-contain sm:block"
                />
              </div>

              <div className="mt-3 grid gap-2 lg:grid-cols-3">
                <Note title="Alternative plans">
                  {alternatives.length === 0 && <p className="text-[11px] text-[#6d6254]">No other plan scored close.</p>}
                  <ul className="space-y-1.5">
                    {alternatives.map((alt, index) => (
                      <li key={alt.rotation.join("-")} className="rounded-lg bg-white px-2 py-1.5">
                        <p className="text-[11px] font-extrabold text-[#1d3a24]">
                          Plan {index === 0 ? "B" : "C"}{" "}
                          <span className="text-[#1f8a3a]">{alt.suitability}% match</span>
                        </p>
                        <p className="text-[10px] text-[#6d6254]">{alt.rotation.map((crop) => titleCase(crop)).join(" → ")}</p>
                      </li>
                    ))}
                  </ul>
                </Note>
                <Note title="Why this plan?">
                  <p className="text-[11px] leading-snug text-[#4a4338]">{result.explanation}</p>
                  <ul className="mt-2 flex flex-wrap gap-1">
                    {CHIPS.map((chip) => (
                      <li key={chip} className="rounded-full bg-[#e7f6df] px-2 py-0.5 text-[10px] font-bold text-[#1d5c28]">
                        ✓ {chip}
                      </li>
                    ))}
                  </ul>
                </Note>
                <Note title="Watch out" warn>
                  {plan.risks.length === 0 ? (
                    <p className="text-[11px] text-[#6d6254]">No extra warning for this rotation.</p>
                  ) : (
                    <ul className="space-y-1 text-[11px] leading-snug text-[#4a4338]">
                      {plan.risks.map((risk) => (
                        <li key={risk}>• {risk}</li>
                      ))}
                    </ul>
                  )}
                </Note>
              </div>
            </div>

            {showEvidence && (
              <div className="mt-3 overflow-hidden rounded-2xl bg-white shadow-sm">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#f6edd8] text-[10px] tracking-wide text-[#6d6254] uppercase">
                    <tr>
                      <th className="px-3 py-2">Clue</th>
                      <th className="px-3 py-2">Value</th>
                      <th className="px-3 py-2">Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.evidence.map((row) => (
                      <tr key={row.label} className="border-t border-[#efe6d4]">
                        <td className="px-3 py-2 font-bold">{row.label}</td>
                        <td className="px-3 py-2">
                          {row.value}
                          {row.unit ? ` ${row.unit}` : ""}
                        </td>
                        <td className="px-3 py-2 text-[#6d6254]">{row.source}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="mt-3 rounded-2xl bg-white px-3 py-2 shadow-sm">
              <p className="text-xs font-extrabold text-[#1d3a24]">Ask about this case</p>
              <div className="mt-1.5 flex gap-2">
                <input
                  className="field-line"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Why this rotation?"
                  onKeyDown={(event) => {
                    if (event.key === "Enter") void ask();
                  }}
                />
                <button
                  type="button"
                  disabled={asking || question.trim().length === 0}
                  onClick={() => void ask()}
                  className="rounded-lg bg-[#1f8a3a] px-3 text-xs font-extrabold text-white disabled:opacity-40"
                >
                  {asking ? "Asking…" : "Ask"}
                </button>
              </div>
              {askError && <p className="mt-1 text-[11px] font-semibold text-[#b42318]">{askError}</p>}
              {answer && <p className="mt-1 text-[11px] leading-snug text-[#4a4338]">{answer}</p>}
            </div>
          </div>

          <div className="flex shrink-0 items-center justify-between gap-3 border-t border-[#e6dcc8] px-4 py-2.5">
            <button
              type="button"
              onClick={() => setShowEvidence((open) => !open)}
              className="rounded-full border border-[#1f8a3a] px-4 py-1.5 text-xs font-extrabold text-[#1f8a3a]"
            >
              {showEvidence ? "Hide the evidence" : "See the evidence"}
            </button>
            <button
              type="button"
              onClick={() => {
                saveCurrent();
                go("files");
              }}
              className="rounded-full bg-[#1f8a3a] px-4 py-1.5 text-xs font-extrabold text-white"
            >
              Complete case →
            </button>
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

function Note({ title, warn = false, children }: { title: string; warn?: boolean; children: ReactNode }) {
  return (
    <article className="rounded-xl bg-[#fbf6ea] px-3 py-2">
      <h2 className={`text-xs font-extrabold ${warn ? "text-[#b42318]" : "text-[#1d3a24]"}`}>{title}</h2>
      <div className="mt-1.5">{children}</div>
    </article>
  );
}
