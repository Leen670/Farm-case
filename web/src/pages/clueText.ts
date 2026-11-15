import type { Clue } from "../types/api";

export const CLUE_ORDER = ["climate", "water", "crop", "soil"] as const;

export function clueTitle(id: string): string {
  if (id === "crop") return "Vegetation";
  if (id === "water") return "Water";
  if (id === "soil") return "Soil";
  return "Climate";
}

export function clueHint(id: string): string {
  if (id === "climate") return "Temp and rainfall";
  if (id === "water") return "Root-zone wetness";
  if (id === "crop") return "Crop greenness";
  return "Soil type";
}

export function sourcePill(id: string): string {
  if (id === "climate" || id === "water") return "NASA POWER";
  if (id === "crop") return "NASA MODIS";
  return "Farmer report";
}

export function clueHeadline(clue: Clue): string {
  const values = clue.values;
  if (clue.id === "climate") return `${Number(values.avg_temp_c).toFixed(1)}°C`;
  if (clue.id === "soil") {
    const soil = String(values.soil);
    return soil.charAt(0).toUpperCase() + soil.slice(1);
  }
  if (clue.id === "water") return Number(values.root_zone_wetness).toFixed(2);
  return String(values.image_date);
}

export function clueValue(clue: Clue): string {
  const values = clue.values;
  if (clue.id === "climate") {
    return `${Number(values.avg_temp_c).toFixed(1)}°C · ${Math.round(Number(values.rain_mm_per_year))} mm rain`;
  }
  if (clue.id === "soil") return clueHeadline(clue);
  if (clue.id === "water") return `Wetness ${Number(values.root_zone_wetness).toFixed(2)}`;
  return `MODIS picture ${values.image_date}`;
}
