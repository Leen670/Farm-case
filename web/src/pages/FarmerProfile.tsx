import { useState, type ReactNode } from "react";
import { BackButton } from "../components/BackButton";
import { LocationMap, type MapTarget } from "../components/LocationMap";
import { CROPS, DEMOS, PRIORITIES, titleCase } from "../data/farms";
import { useGame } from "../state/game";
import type { Priority, Soil, WaterLevel, WaterSource } from "../types/api";

function art(file: string): string {
  return `${import.meta.env.BASE_URL}images/${encodeURIComponent(file)}`;
}

const SOIL_CARDS: { value: Soil; label: string; image: string }[] = [
  { value: "sandy", label: "Sandy", image: "Sandy Soil Texture Close-Up.png" },
  { value: "clay", label: "Clay", image: "Reddish-Brown Clumpy Soil Texture.png" },
  { value: "silty", label: "Silty", image: "Dry Earth and Pebbles Texture.png" },
  { value: "loamy", label: "Loamy", image: "Rich Loamy Soil Texture.png" },
];

const WATER_LEVELS: { value: WaterLevel; label: string }[] = [
  { value: "available", label: "Available" },
  { value: "moderate", label: "Moderate" },
  { value: "limited", label: "Limited" },
];

const WATER_SOURCES: { value: WaterSource; label: string; image: string }[] = [
  { value: "rain", label: "Rainwater", image: "Cartoon Raincloud Over Green Fields.png" },
  { value: "ground", label: "Groundwater", image: "Cartoon Stone Well in Green Hills.png" },
  { value: "surface", label: "Surface Water", image: "Colorful Cartoon River Landscape.png" },
  { value: "treated", label: "Treated Water", image: "Colorful Water Treatment Facility.png" },
  { value: "desalinated", label: "Desalinated Water", image: "Desalinated Water Plant by the Shore.png" },
];

const STEPS = [
  { icon: "Farmer Avatar Icon.png", label: "1 Farmer Information", active: true },
  { icon: "Glossy Green Magnifying Glass Badge.png", label: "2 Collect Evidence", active: false },
  { icon: "Forest Green Investigation Checklist Badge.png", label: "3 AI Investigation", active: false },
  { icon: "Case Solved Checkmark Badge.png", label: "4 Case Solved", active: false },
];

export function FarmerProfile() {
  const { draft, updateDraft, go } = useGame();
  const [flyTo, setFlyTo] = useState<MapTarget | null>(null);
  const ready = draft.farmerName.trim().length > 0 && draft.lat != null && draft.lon != null;
  const pinned = draft.lat != null && draft.lon != null;

  function pickOnMap(lat: number, lon: number) {
    updateDraft({
      lat: Math.round(lat * 10000) / 10000,
      lon: Math.round(lon * 10000) / 10000,
      place: "Custom pin",
    });
  }

  function toggleCrop(crop: string) {
    const on = draft.previousCrops.includes(crop);
    updateDraft({
      previousCrops: on ? draft.previousCrops.filter((item) => item !== crop) : [...draft.previousCrops, crop],
    });
  }

  function togglePriority(priority: Priority) {
    const on = draft.priorities.includes(priority);
    updateDraft({
      priorities: on ? draft.priorities.filter((item) => item !== priority) : [...draft.priorities, priority],
    });
  }

  return (
    <div className="relative h-screen overflow-hidden bg-[#07140f] text-[#2c3428]">
      <img
        src={art("Sunset Farm with Windmill and Barn.png")}
        alt=""
        className="absolute inset-0 h-full w-full object-cover object-[18%_center]"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-[#07140f] via-[#07140f]/55 to-[#10261c]/35" />

      <BackButton previous="welcome" />

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
          <header className="relative shrink-0 px-5 pt-4 pb-3">
            <div className="relative mx-auto h-16 w-[min(420px,68%)]">
              <img src={art("Torn Cream Paper Banner.png")} alt="" className="h-full w-full object-cover object-center" />
              <div className="absolute inset-0 flex items-center justify-center gap-2 px-6">
                <img src={art("Dark Brown Hat with Cream Band.png")} alt="" className="h-9 w-12 object-contain" />
                <div className="min-w-0 text-left">
                  <p className="text-sm leading-tight font-extrabold text-[#2a2418]">Farmer Information</p>
                  <p className="text-[10px] text-[#6d6254]">Tell us about your farm to start the case.</p>
                </div>
              </div>
            </div>
            <div
              className="absolute top-3 right-4 flex h-12 w-24 flex-col items-center justify-center bg-contain bg-center bg-no-repeat"
              style={{ backgroundImage: `url("${art("Aged Torn Paper Scrap.png")}")` }}
            >
              <p className="text-[10px] font-extrabold text-[#3a3228]">Step 1 of 4</p>
              <span className="mt-0.5 flex gap-1" aria-hidden="true">
                <span className="h-1.5 w-1.5 rounded-full bg-[#2f8a34]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#d9d0c0]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#d9d0c0]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#d9d0c0]" />
                <span className="h-1.5 w-1.5 rounded-full bg-[#d9d0c0]" />
              </span>
            </div>
          </header>

          <form
            id="farmer-form"
            className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-5 pb-4"
            onSubmit={(event) => {
              event.preventDefault();
              if (ready) go("map");
            }}
          >
            <Field icon="Dark Green User Outline Icon.png" label="Farmer's Name">
              <input
                className="field-line w-full"
                value={draft.farmerName}
                onChange={(event) => updateDraft({ farmerName: event.target.value })}
                placeholder="Enter the farmer's name..."
              />
            </Field>

            <Field icon="Dark Green Map Pin Icon.png" label="Farm Location">
              <div className="overflow-hidden rounded-xl">
                <LocationMap lat={draft.lat} lon={draft.lon} flyTo={flyTo} onPick={pickOnMap} />
              </div>
              <p className="text-[11px] font-bold text-[#2f6a32]">
                {pinned
                  ? `${draft.place ? `${draft.place} · ` : ""}${draft.lat!.toFixed(2)}, ${draft.lon!.toFixed(2)}`
                  : "Click the map to drop a pin."}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {DEMOS.map((demo) => (
                  <button
                    key={demo.id}
                    type="button"
                    onClick={() => {
                      setFlyTo({ lat: demo.lat, lon: demo.lon, key: Date.now() });
                      updateDraft({
                        lat: demo.lat,
                        lon: demo.lon,
                        place: demo.name,
                        soil: demo.soil,
                        waterLevel: demo.waterLevel,
                        waterSource: demo.waterSource,
                      });
                    }}
                    className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${
                      draft.place === demo.name ? "bg-[#1f7a34] text-white" : "bg-white text-[#2c3428]"
                    }`}
                  >
                    {demo.name}
                  </button>
                ))}
              </div>
            </Field>

            <Field icon="Dark Green Soil Mound Icon.png" label="Soil Type">
              <div className="grid grid-cols-4 gap-2">
                {SOIL_CARDS.map((soil) => {
                  const on = draft.soil === soil.value;
                  return (
                    <button
                      key={soil.value}
                      type="button"
                      aria-pressed={on}
                      onClick={() => updateDraft({ soil: soil.value })}
                      className={`overflow-hidden rounded-xl bg-white text-center shadow-sm ${on ? "ring-2 ring-[#2f8a34]" : ""}`}
                    >
                      <img src={art(soil.image)} alt="" className="h-12 w-full object-cover" />
                      <span className="mt-1 block text-[11px] font-bold">{soil.label}</span>
                      <Radio on={on} />
                    </button>
                  );
                })}
              </div>
            </Field>

            <Field icon="Dark Green Water Drop Outline.png" label="Water Availability" iconClass="h-7 w-7">
              <div className="flex flex-wrap gap-2">
                {WATER_LEVELS.map((level) => {
                  const on = draft.waterLevel === level.value;
                  return (
                    <button
                      key={level.value}
                      type="button"
                      aria-pressed={on}
                      onClick={() => updateDraft({ waterLevel: level.value })}
                      className={`rounded-full border px-3 py-1.5 text-[11px] font-bold ${
                        on ? "border-[#2f8a34] bg-[#e7f6df] text-[#1d5c28]" : "border-[#e6dcc8] bg-white text-[#3d4a38]"
                      }`}
                    >
                      {level.label}
                    </button>
                  );
                })}
              </div>
            </Field>

            <Field icon="Glowing Green Faucet Icon.png" label="Water Source">
              <div className="grid grid-cols-5 gap-2">
                {WATER_SOURCES.map((source) => {
                  const on = draft.waterSource === source.value;
                  return (
                    <button
                      key={source.value}
                      type="button"
                      aria-pressed={on}
                      onClick={() => updateDraft({ waterSource: source.value })}
                      className={`overflow-hidden rounded-xl bg-white text-center shadow-sm ${on ? "ring-2 ring-[#2f8a34]" : ""}`}
                    >
                      <img src={art(source.image)} alt="" className="aspect-square w-full bg-[#f4f7fb] object-contain" />
                      <span className="mt-1 block px-1 text-[10px] leading-tight font-bold">{source.label}</span>
                      <Radio on={on} />
                    </button>
                  );
                })}
              </div>
            </Field>

            <Field icon="Glowing Green Sprout Icon.png" label="Previous Crops">
              <div className="flex flex-wrap gap-1.5">
                {CROPS.map((crop) => {
                  const on = draft.previousCrops.includes(crop);
                  return (
                    <button
                      key={crop}
                      type="button"
                      aria-pressed={on}
                      onClick={() => toggleCrop(crop)}
                      className={`rounded-full border px-2.5 py-1 text-[11px] font-bold ${
                        on ? "border-[#2f8a34] bg-[#e7f6df] text-[#1d5c28]" : "border-[#e6dcc8] bg-white text-[#3d4a38]"
                      }`}
                    >
                      {titleCase(crop)}
                    </button>
                  );
                })}
              </div>
            </Field>

            <Field icon="Glowing Dark Green Flag Icon.png" label="Farming Priorities">
              <div className="flex flex-wrap gap-1.5">
                {PRIORITIES.map((priority) => {
                  const on = draft.priorities.includes(priority.value);
                  return (
                    <button
                      key={priority.value}
                      type="button"
                      aria-pressed={on}
                      onClick={() => togglePriority(priority.value)}
                      className={`rounded-full border px-2.5 py-1 text-[11px] font-bold ${
                        on ? "border-[#2f8a34] bg-[#e7f6df] text-[#1d5c28]" : "border-[#e6dcc8] bg-white text-[#3d4a38]"
                      }`}
                    >
                      {priority.label}
                    </button>
                  );
                })}
              </div>
              <input
                className="field-line w-full"
                onChange={(event) => updateDraft({ notes: event.target.value })}
                placeholder="Optional note for the case write-up"
              />
            </Field>
          </form>

          <div className="flex shrink-0 justify-end border-t border-[#e6dcc8] px-5 py-3">
            <button
              type="submit"
              form="farmer-form"
              disabled={!ready}
              className="rounded-lg bg-[#2f8a34] px-5 py-2 text-sm font-extrabold text-white shadow-[0_3px_0_#1c5c22] disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next →
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

function Field({
  icon,
  label,
  iconClass = "h-5 w-5",
  children,
}: {
  icon: string;
  label: string;
  iconClass?: string;
  children?: ReactNode;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <img src={art(icon)} alt="" className={`${iconClass} shrink-0 object-contain`} />
        <span className="text-xs font-extrabold">{label}</span>
      </div>
      <div className="space-y-2 pl-7">{children}</div>
    </div>
  );
}

function Radio({ on }: { on: boolean }) {
  return (
    <span className="my-1.5 inline-grid h-3.5 w-3.5 place-items-center rounded-full border border-[#cfc6b4]">
      {on && <span className="h-2 w-2 rounded-full bg-[#2f8a34]" />}
    </span>
  );
}
