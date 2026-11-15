import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import type { CaseRequest, CaseResponse, Clue, Priority, Soil, WaterLevel, WaterSource } from "../types/api";

export type Screen =
  | "welcome"
  | "farmer"
  | "map"
  | "board"
  | "investigation"
  | "results"
  | "files"
  | "data"
  | "assistant";

export type Draft = {
  farmerName: string;
  lat: number | null;
  lon: number | null;
  place: string;
  soil: Soil | "";
  waterLevel: WaterLevel;
  waterSource: WaterSource;
  previousCrops: string[];
  priorities: Priority[];
  notes: string;
};

export type SavedCase = {
  id: string;
  farmerName: string;
  place: string;
  rotation: string[];
  score: number;
  savedAt: string;
  draft: Draft;
  result: CaseResponse;
};

const STORAGE_KEY = "farm-case.files";

const EMPTY_DRAFT: Draft = {
  farmerName: "",
  lat: null,
  lon: null,
  place: "",
  soil: "loamy",
  waterLevel: "moderate",
  waterSource: "rain",
  previousCrops: [],
  priorities: [],
  notes: "",
};

const SCORING_FIELDS: (keyof Draft)[] = [
  "lat",
  "lon",
  "soil",
  "waterLevel",
  "waterSource",
  "previousCrops",
  "priorities",
];

type GameValue = {
  screen: Screen;
  go: (screen: Screen) => void;
  draft: Draft;
  updateDraft: (patch: Partial<Draft>) => void;
  resetDraft: () => void;
  clues: Clue[] | null;
  setClues: (clues: Clue[] | null) => void;
  loadedKey: string;
  setLoadedKey: (key: string) => void;
  collected: string[];
  collect: (id: string) => void;
  result: CaseResponse | null;
  setResult: (result: CaseResponse | null) => void;
  saved: SavedCase[];
  saveCurrent: () => void;
  openSaved: (id: string) => void;
};

const GameContext = createContext<GameValue | null>(null);

function readSaved(): SavedCase[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as SavedCase[]) : [];
  } catch {
    return [];
  }
}

export function pinKey(draft: Draft): string {
  if (draft.lat == null || draft.lon == null) return "";
  return [
    draft.lat.toFixed(4),
    draft.lon.toFixed(4),
    draft.soil,
    draft.waterLevel,
    draft.waterSource,
    draft.previousCrops.join(","),
    draft.priorities.join(","),
  ].join("|");
}

export function toRequest(draft: Draft): CaseRequest {
  if (draft.lat == null || draft.lon == null) {
    throw new Error("Choose a point on the map.");
  }
  return {
    farmer_name: draft.farmerName.trim(),
    lat: draft.lat,
    lon: draft.lon,
    soil: draft.soil || null,
    water_level: draft.waterLevel,
    water_source: draft.waterSource,
    previous_crops: draft.previousCrops,
    priorities: draft.priorities,
    priorities_text: draft.notes.trim(),
  };
}

export function GameProvider({ children }: { children: ReactNode }) {
  const [screen, setScreen] = useState<Screen>("welcome");
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [clues, setClues] = useState<Clue[] | null>(null);
  const [loadedKey, setLoadedKey] = useState("");
  const [collected, setCollected] = useState<string[]>([]);
  const [result, setResult] = useState<CaseResponse | null>(null);
  const [saved, setSaved] = useState<SavedCase[]>(() => readSaved());

  const value = useMemo<GameValue>(() => {
    function updateDraft(patch: Partial<Draft>) {
      setDraft((current) => ({ ...current, ...patch }));
      if (SCORING_FIELDS.some((field) => field in patch)) {
        setResult(null);
        setClues(null);
        setCollected([]);
        setLoadedKey("");
      }
    }

    function saveCurrent() {
      if (!result) return;
      const entry: SavedCase = {
        id: result.case_id,
        farmerName: draft.farmerName.trim() || "Unnamed farmer",
        place: draft.place || `${draft.lat?.toFixed(2)}, ${draft.lon?.toFixed(2)}`,
        rotation: result.recommended.rotation,
        score: result.recommended.suitability,
        savedAt: new Date().toISOString(),
        draft,
        result,
      };
      setSaved((current) => {
        const next = [entry, ...current.filter((item) => item.id !== entry.id)].slice(0, 20);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        return next;
      });
    }

    function openSaved(id: string) {
      const found = saved.find((item) => item.id === id);
      if (!found) return;
      setDraft(found.draft);
      setResult(found.result);
      setClues(found.result.clues);
      setCollected(found.result.clues.map((clue) => clue.id));
      setLoadedKey(pinKey(found.draft));
      setScreen("results");
    }

    function resetDraft() {
      setDraft(EMPTY_DRAFT);
      setClues(null);
      setLoadedKey("");
      setCollected([]);
      setResult(null);
      setScreen("farmer");
    }

    return {
      screen,
      go: setScreen,
      draft,
      updateDraft,
      resetDraft,
      clues,
      setClues,
      loadedKey,
      setLoadedKey,
      collected,
      collect: (id: string) =>
        setCollected((current) => (current.includes(id) ? current : [...current, id])),
      result,
      setResult,
      saved,
      saveCurrent,
      openSaved,
    };
  }, [screen, draft, clues, loadedKey, collected, result, saved]);

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

export function useGame(): GameValue {
  const value = useContext(GameContext);
  if (!value) throw new Error("useGame must be used inside GameProvider");
  return value;
}
