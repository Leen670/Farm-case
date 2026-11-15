import { PageHeader } from "../components/Shell";
import { useGame } from "../state/game";
import { titleCase } from "../data/farms";
import { clueValue } from "./clueText";

export function FarmData() {
  const { draft, clues, result } = useGame();
  const rows = [
    ["Farmer", draft.farmerName || "—"],
    ["Place", draft.place || "—"],
    ["Latitude", draft.lat == null ? "—" : draft.lat.toFixed(2)],
    ["Longitude", draft.lon == null ? "—" : draft.lon.toFixed(2)],
    ["Soil", draft.soil || "Not sure"],
    ["Water", `${draft.waterLevel}, ${draft.waterSource}`],
    ["Previous crops", draft.previousCrops.map(titleCase).join(", ") || "—"],
    ["Priorities", draft.priorities.join(", ") || "—"],
    ["Notes", draft.notes || "—"],
  ];

  return (
    <div>
      <PageHeader
        eyebrow="What this case is using"
        title="Farm data"
        subtitle="The form is what you entered. The clue values are what NASA POWER and the pictures returned."
      />
      <dl className="mt-6 overflow-hidden rounded-3xl bg-white shadow-sm">
        {rows.map(([label, value]) => (
          <div key={label} className="grid gap-1 border-b border-ink/5 px-4 py-3 sm:grid-cols-[180px_1fr]">
            <dt className="text-xs font-bold uppercase tracking-wide text-ink/45">{label}</dt>
            <dd className="font-semibold text-navy">{value}</dd>
          </div>
        ))}
      </dl>
      {clues && clues.length > 0 && (
        <div className="mt-4 overflow-hidden rounded-3xl bg-white shadow-sm">
          {clues.map((clue) => (
            <div key={clue.id} className="border-b border-ink/5 px-4 py-3">
              <p className="text-xs font-bold uppercase tracking-wide text-ink/45">{clue.title}</p>
              <p className="font-semibold text-navy">{clueValue(clue)}</p>
              <p className="text-sm text-ink/60">{clue.source}</p>
            </div>
          ))}
        </div>
      )}
      {result && (
        <p className="mt-4 text-sm text-ink/60">
          Recommended score {result.recommended.suitability}%. Case {result.case_id.slice(0, 6)}.
        </p>
      )}
      <p className="mt-6 text-xs text-ink/45">Data: NASA POWER, NASA GIBS (MODIS, SMAP, IMERG).</p>
    </div>
  );
}
