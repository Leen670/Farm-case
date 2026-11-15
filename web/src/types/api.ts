/** Mirrors api/app/models.py. Field names match the JSON on the wire. */

export type Soil = "sandy" | "clay" | "silty" | "loamy";
export type WaterLevel = "available" | "moderate" | "limited";
export type WaterSource = "rain" | "ground" | "surface" | "treated" | "desalinated";
export type Priority = "save_water" | "increase_yield" | "improve_soil" | "lower_cost";

export type CaseRequest = {
  farmer_name: string;
  lat: number;
  lon: number;
  soil: Soil | null;
  water_level: WaterLevel;
  water_source: WaterSource;
  previous_crops: string[];
  priorities: Priority[];
  priorities_text: string;
};

export type Clue = {
  id: "climate" | "soil" | "water" | "crop";
  title: string;
  values: Record<string, number | string>;
  summary: string;
  source: string;
  source_url: string;
  image_url: string | null;
};

export type Plan = {
  rotation: string[];
  suitability: number;
  reasons: string[];
  risks: string[];
};

export type Evidence = {
  label: string;
  value: string;
  unit: string;
  source: string;
};

export type CaseResponse = {
  case_id: string;
  clues: Clue[];
  recommended: Plan;
  alternatives: Plan[];
  explanation: string;
  evidence: Evidence[];
  used_fallback: boolean;
};

export type WorldMap = {
  image_url: string;
  width: number;
  height: number;
  proxy_path: string;
};
