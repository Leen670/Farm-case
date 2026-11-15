import type { Priority, Soil, WaterLevel, WaterSource } from "../types/api";

export const CROPS = [
  "wheat",
  "barley",
  "sorghum",
  "millet",
  "maize",
  "chickpea",
  "faba bean",
  "lentil",
  "sesame",
  "sunflower",
  "alfalfa",
  "tomato",
  "potato",
  "onion",
  "cotton",
] as const;

export const LEGUMES = new Set(["chickpea", "faba bean", "lentil", "alfalfa"]);

export const SOILS: { value: Soil | ""; label: string }[] = [
  { value: "loamy", label: "Loamy" },
  { value: "sandy", label: "Sandy" },
  { value: "clay", label: "Clay" },
  { value: "silty", label: "Silty" },
  { value: "", label: "Not sure" },
];

export const WATER_LEVELS: { value: WaterLevel; label: string }[] = [
  { value: "available", label: "Available" },
  { value: "moderate", label: "Moderate" },
  { value: "limited", label: "Limited" },
];

export const WATER_SOURCES: { value: WaterSource; label: string }[] = [
  { value: "rain", label: "Rain" },
  { value: "ground", label: "Ground" },
  { value: "surface", label: "Surface" },
  { value: "treated", label: "Treated" },
  { value: "desalinated", label: "Desalinated" },
];

export const PRIORITIES: { value: Priority; label: string }[] = [
  { value: "save_water", label: "Save water" },
  { value: "increase_yield", label: "Increase yield" },
  { value: "improve_soil", label: "Improve soil" },
  { value: "lower_cost", label: "Lower cost" },
];

export const DEMOS = [
  {
    id: "iowa",
    name: "Ames, Iowa",
    lat: 42.03,
    lon: -93.62,
    soil: "loamy" as Soil,
    waterLevel: "moderate" as WaterLevel,
    waterSource: "rain" as WaterSource,
  },
  {
    id: "punjab",
    name: "Ludhiana, Punjab",
    lat: 30.9,
    lon: 75.85,
    soil: "loamy" as Soil,
    waterLevel: "limited" as WaterLevel,
    waterSource: "ground" as WaterSource,
  },
  {
    id: "andalusia",
    name: "Córdoba, Andalusia",
    lat: 37.88,
    lon: -4.78,
    soil: "silty" as Soil,
    waterLevel: "limited" as WaterLevel,
    waterSource: "rain" as WaterSource,
  },
];

export function titleCase(name: string): string {
  return name.replace(/\b\w/g, (letter) => letter.toUpperCase());
}
