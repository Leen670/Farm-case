import { useEffect, useState, type MouseEvent } from "react";
import { API_URL, fetchWorldMap } from "../api/client";
import { Button } from "../components/Button";
import { PageHeader } from "../components/Shell";
import { CROPS, DEMOS, PRIORITIES, SOILS, WATER_LEVELS, WATER_SOURCES, titleCase } from "../data/farms";
import { useGame } from "../state/game";
import type { WorldMap } from "../types/api";

export function FarmerProfile() {
  const { draft, updateDraft, go } = useGame();
  const [map, setMap] = useState<WorldMap | null>(null);
  const [mapError, setMapError] = useState("");
  const ready = draft.farmerName.trim().length > 0 && draft.lat != null && draft.lon != null;

  useEffect(() => {
    let cancel = false;
    fetchWorldMap()
      .then((world) => {
        if (!cancel) setMap(world);
      })
      .catch(() => {
        if (!cancel) setMapError("The world picture did not load. Type a latitude and longitude instead.");
      });
    return () => {
      cancel = true;
    };
  }, []);

  function pinFromMap(event: MouseEvent<HTMLImageElement>) {
    if (!map) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * map.width;
    const y = ((event.clientY - rect.top) / rect.height) * map.height;
    const lon = (x / map.width) * 360 - 180;
    const lat = 90 - (y / map.height) * 180;
    updateDraft({
      lat: Math.round(lat * 100) / 100,
      lon: Math.round(lon * 100) / 100,
      place: "Custom pin",
    });
  }

  return (
    <div>
      <PageHeader
        eyebrow="Farmer profile"
        title="Tell us about your farm"
        subtitle="The pin is the clue. Soil, water, and last year's crops tell the score what the satellites cannot see."
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="space-y-4 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-extrabold text-navy">Farmer details</h2>
          <label className="block space-y-1.5">
            <span className="eyebrow">Farmer name</span>
            <input
              className="field"
              value={draft.farmerName}
              onChange={(event) => updateDraft({ farmerName: event.target.value })}
              placeholder="Ada"
            />
          </label>
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="eyebrow">Farm location</span>
              <span className="text-xs font-bold text-navy">
                {draft.lat == null || draft.lon == null ? "Drop a pin" : `${draft.lat.toFixed(2)}, ${draft.lon.toFixed(2)}`}
              </span>
            </div>
            <div className="overflow-hidden rounded-xl bg-leaf p-2">
              {map ? (
                <div className="relative">
                  <img
                    src={`${API_URL}${map.proxy_path}`}
                    alt="World map. Click to drop a pin."
                    className="h-36 w-full cursor-crosshair rounded-lg object-cover"
                    onClick={pinFromMap}
                  />
                  {draft.lat != null && draft.lon != null && (
                    <span
                      className="pointer-events-none absolute h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white bg-watch"
                      style={{
                        left: `${((draft.lon + 180) / 360) * 100}%`,
                        top: `${((90 - draft.lat) / 180) * 100}%`,
                      }}
                    />
                  )}
                </div>
              ) : (
                <p className="px-2 py-6 text-sm text-ink/60">{mapError || "Loading the NASA world picture…"}</p>
              )}
              <div className="mt-2 flex flex-wrap gap-2">
                {DEMOS.map((demo) => (
                  <button
                    key={demo.id}
                    type="button"
                    onClick={() =>
                      updateDraft({
                        lat: demo.lat,
                        lon: demo.lon,
                        place: demo.name,
                        soil: demo.soil,
                        waterLevel: demo.waterLevel,
                        waterSource: demo.waterSource,
                      })
                    }
                    className={`rounded-lg px-2.5 py-1 text-xs font-bold ${
                      draft.place === demo.name ? "bg-navy text-white" : "bg-white text-navy"
                    }`}
                  >
                    {demo.name}
                  </button>
                ))}
              </div>
              {mapError && (
                <div className="mt-2 grid grid-cols-2 gap-2">
                  <NumberField label="Latitude" value={draft.lat} onChange={(lat) => updateDraft({ lat, place: "Custom pin" })} />
                  <NumberField label="Longitude" value={draft.lon} onChange={(lon) => updateDraft({ lon, place: "Custom pin" })} />
                </div>
              )}
            </div>
          </div>
          <div className="space-y-1.5">
            <span className="eyebrow">Soil type</span>
            <div className="flex flex-wrap gap-2">
              {SOILS.map((soil) => (
                <Choice
                  key={soil.label}
                  label={soil.label}
                  on={draft.soil === soil.value}
                  onClick={() => updateDraft({ soil: soil.value })}
                />
              ))}
            </div>
          </div>
          <div className="space-y-1.5">
            <span className="eyebrow">Previous crops</span>
            <div className="flex flex-wrap gap-2">
              {CROPS.map((crop) => {
                const on = draft.previousCrops.includes(crop);
                return (
                  <Choice
                    key={crop}
                    label={titleCase(crop)}
                    on={on}
                    onClick={() =>
                      updateDraft({
                        previousCrops: on
                          ? draft.previousCrops.filter((item) => item !== crop)
                          : [...draft.previousCrops, crop],
                      })
                    }
                  />
                );
              })}
            </div>
          </div>
        </section>

        <section className="space-y-4 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-extrabold text-navy">Water & priorities</h2>
          <div className="space-y-1.5">
            <span className="eyebrow">Water availability</span>
            <div className="flex flex-wrap gap-2">
              {WATER_LEVELS.map((level) => (
                <Choice
                  key={level.value}
                  label={level.label}
                  on={draft.waterLevel === level.value}
                  onClick={() => updateDraft({ waterLevel: level.value })}
                />
              ))}
            </div>
          </div>
          <div className="space-y-1.5">
            <span className="eyebrow">Water source</span>
            <div className="flex flex-wrap gap-2">
              {WATER_SOURCES.map((source) => (
                <Choice
                  key={source.value}
                  label={source.value === "ground" ? "Groundwater" : source.label}
                  on={draft.waterSource === source.value}
                  onClick={() => updateDraft({ waterSource: source.value })}
                />
              ))}
            </div>
          </div>
          <label className="block space-y-1.5">
            <span className="eyebrow">Priority notes</span>
            <input
              className="field"
              value={draft.notes}
              onChange={(event) => updateDraft({ notes: event.target.value })}
              placeholder="Optional. Quoted in the case, not scored."
            />
          </label>
          <div className="space-y-1.5">
            <span className="eyebrow">Priorities</span>
            <div className="flex flex-wrap gap-2">
              {PRIORITIES.map((priority) => {
                const on = draft.priorities.includes(priority.value);
                return (
                  <Choice
                    key={priority.value}
                    label={priority.label}
                    on={on}
                    onClick={() =>
                      updateDraft({
                        priorities: on
                          ? draft.priorities.filter((item) => item !== priority.value)
                          : [...draft.priorities, priority.value],
                      })
                    }
                  />
                );
              })}
            </div>
          </div>
        </section>
      </div>

      <div className="mt-6 flex justify-end">
        <Button disabled={!ready} onClick={() => go("map")}>
          Next
        </Button>
      </div>
    </div>
  );
}

function Choice({ label, on, onClick }: { label: string; on: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-lg px-3 py-2 text-sm font-bold ${on ? "bg-lime text-navy" : "bg-cream text-navy"}`}
    >
      {label}
    </button>
  );
}

function NumberField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number | null;
  onChange: (value: number) => void;
}) {
  return (
    <label className="block space-y-1">
      <span className="eyebrow">{label}</span>
      <input
        className="field"
        inputMode="decimal"
        value={value ?? ""}
        onChange={(event) => {
          const next = Number(event.target.value);
          if (Number.isFinite(next)) onChange(next);
        }}
      />
    </label>
  );
}
