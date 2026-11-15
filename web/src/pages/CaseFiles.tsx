import { BackButton } from "../components/BackButton";
import { titleCase } from "../data/farms";
import { useGame } from "../state/game";

function art(file: string): string {
  return `${import.meta.env.BASE_URL}images/${encodeURIComponent(file)}`;
}

const STEPS = [
  { icon: "Farmer Avatar Icon.png", label: "1 Farmer Information" },
  { icon: "Glossy Green Magnifying Glass Badge.png", label: "2 Collect Evidence" },
  { icon: "Forest Green Investigation Checklist Badge.png", label: "3 AI Investigation" },
  { icon: "Case Solved Checkmark Badge.png", label: "4 Case Solved" },
];

export function CaseFiles() {
  const { saved, openSaved, resetDraft, result } = useGame();

  return (
    <div className="relative h-screen overflow-hidden bg-[#07140f] text-[#2c3428]">
      <img
        src={art("Sunset Farm with Windmill and Barn.png")}
        alt=""
        className="absolute inset-0 h-full w-full object-cover object-[18%_center]"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-[#07140f] via-[#07140f]/55 to-[#10261c]/35" />

      <BackButton previous={result ? "results" : "welcome"} />

      <div className="relative z-30 flex h-full gap-4 px-4 pt-16 pb-4 sm:px-6">
        <aside className="hidden w-52 shrink-0 flex-col md:flex">
          <img src={art("Farm Case Sprout Logo.png")} alt="Farm Case" className="mt-2 w-40 object-contain" />
          <ol className="mt-8 space-y-3">
            {STEPS.map((step) => (
              <li key={step.label} className="flex items-center gap-2 px-1.5 text-xs font-semibold text-white/85">
                <img src={art(step.icon)} alt="" className="h-8 w-8 object-contain" />
                <span>{step.label}</span>
              </li>
            ))}
          </ol>
        </aside>

        <section className="mb-2 flex min-w-0 flex-1 flex-col overflow-hidden rounded-[28px] bg-[#f4efe4] shadow-[0_18px_50px_rgba(0,0,0,0.28)]">
          <header className="relative shrink-0 px-5 pt-4 pb-2">
            <div className="relative mx-auto h-16 w-[min(420px,68%)]">
              <img src={art("Torn Cream Paper Banner.png")} alt="" className="h-full w-full object-cover object-center" />
              <div className="absolute inset-0 flex items-center justify-center gap-2 px-8">
                <img src={art("Forest Green Investigation Checklist Badge.png")} alt="" className="h-9 w-9 object-contain" />
                <div className="min-w-0 text-left">
                  <p className="text-sm leading-tight font-extrabold text-[#2a2418]">Case Files</p>
                  <p className="text-[10px] text-[#6d6254]">Saved on this browser. Nothing is sent to an account.</p>
                </div>
              </div>
            </div>
          </header>

          <div className="min-h-0 flex-1 overflow-y-auto px-5 py-3">
            {saved.length === 0 ? (
              <p className="rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-[#6d6254]">No cases filed yet.</p>
            ) : (
              <ul className="space-y-3">
                {saved.map((item, index) => (
                  <li key={item.id}>
                    <button
                      type="button"
                      onClick={() => openSaved(item.id)}
                      className="flex w-full items-center justify-between gap-4 rounded-2xl bg-white px-4 py-3 text-left shadow-sm"
                    >
                      <span>
                        <span className="block text-[10px] font-extrabold tracking-[0.14em] text-[#8a8174]">
                          FARM CASE {String(index + 1).padStart(3, "0")}
                        </span>
                        <span className="mt-1 block font-extrabold text-[#1d3a24]">
                          {item.farmerName} · {item.place}
                        </span>
                        <span className="mt-1 block text-sm text-[#6d6254]">
                          {item.rotation.map((crop) => titleCase(crop)).join(" → ")}
                        </span>
                      </span>
                      <span className="text-2xl font-extrabold text-[#1f8a3a]">{item.score}%</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="flex shrink-0 justify-end border-t border-[#e6dcc8] px-5 py-3">
            <button
              type="button"
              onClick={resetDraft}
              className="rounded-lg bg-[#2f8a34] px-5 py-2 text-sm font-extrabold text-white shadow-[0_3px_0_#1c5c22]"
            >
              Start another case
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
