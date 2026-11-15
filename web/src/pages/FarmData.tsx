import { BackButton } from "../components/BackButton";
import { PRIORITIES, SOILS, titleCase, WATER_LEVELS, WATER_SOURCES } from "../data/farms";
import { useGame } from "../state/game";
import { clueTitle, clueValue } from "./clueText";

function art(file: string): string {
  return `/images/${encodeURIComponent(file)}`;
}

const STEPS = [
  { icon: "Farmer Avatar Icon.png", label: "1 Farmer Information" },
  { icon: "Glossy Green Magnifying Glass Badge.png", label: "2 Collect Evidence" },
  { icon: "Forest Green Investigation Checklist Badge.png", label: "3 AI Investigation" },
  { icon: "Case Solved Checkmark Badge.png", label: "4 Case Solved" },
];

function choiceLabel(options: readonly { value: string; label: string }[], value: string): string {
  return options.find((item) => item.value === value)?.label ?? titleCase(value.replaceAll("_", " "));
}

export function FarmData() {
  const { draft, clues, result } = useGame();
  const place = draft.place || (draft.lat != null && draft.lon != null ? "Custom pin" : "");
  const coords = draft.lat != null && draft.lon != null ? `${draft.lat.toFixed(2)}, ${draft.lon.toFixed(2)}` : "";
  const rows = [
    ["Farmer", draft.farmerName || "—"],
    ["Place", [place, coords].filter(Boolean).join(" · ") || "—"],
    ["Soil", draft.soil ? choiceLabel(SOILS, draft.soil) : "Not sure"],
    [
      "Water",
      `${choiceLabel(WATER_LEVELS, draft.waterLevel)} · ${choiceLabel(WATER_SOURCES, draft.waterSource)}`,
    ],
    ["Previous crops", draft.previousCrops.map(titleCase).join(", ") || "—"],
    ["Priorities", draft.priorities.map((item) => choiceLabel(PRIORITIES, item)).join(", ") || "—"],
    ["Notes", draft.notes || "—"],
  ];

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
                <img src={art("Glossy Green Magnifying Glass Badge.png")} alt="" className="h-9 w-9 object-contain" />
                <div className="min-w-0 text-left">
                  <p className="text-sm leading-tight font-extrabold text-[#2a2418]">Farm Data</p>
                  <p className="text-[10px] text-[#6d6254]">What you entered, and what NASA returned for this pin.</p>
                </div>
              </div>
            </div>
          </header>

          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-5 py-3">
            <dl className="overflow-hidden rounded-2xl bg-white shadow-sm">
              {rows.map(([label, value]) => (
                <div key={label} className="grid gap-1 border-b border-[#efe6d6] px-4 py-2.5 last:border-b-0 sm:grid-cols-[150px_1fr]">
                  <dt className="text-[10px] font-extrabold tracking-[0.14em] text-[#8a8174]">{label.toUpperCase()}</dt>
                  <dd className="text-sm font-extrabold text-[#1d3a24]">{value}</dd>
                </div>
              ))}
            </dl>

            {clues && clues.length > 0 && (
              <div className="overflow-hidden rounded-2xl bg-white shadow-sm">
                {clues.map((clue) => (
                  <div key={clue.id} className="border-b border-[#efe6d6] px-4 py-2.5 last:border-b-0">
                    <p className="text-[10px] font-extrabold tracking-[0.14em] text-[#8a8174]">
                      {clueTitle(clue.id).toUpperCase()}
                    </p>
                    <p className="text-sm font-extrabold text-[#1d3a24]">{clueValue(clue)}</p>
                    <p className="text-xs text-[#6d6254]">{clue.source}</p>
                  </div>
                ))}
              </div>
            )}
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
