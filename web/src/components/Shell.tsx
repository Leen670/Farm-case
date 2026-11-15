import type { ReactNode } from "react";
import { useGame, type Screen } from "../state/game";

const STEPS: { screen: Screen; label: string }[] = [
  { screen: "farmer", label: "Farmer" },
  { screen: "map", label: "Evidence" },
  { screen: "investigation", label: "Analysis" },
  { screen: "results", label: "Results" },
];

function stepIndex(screen: Screen): number {
  if (screen === "farmer") return 0;
  if (screen === "map" || screen === "board") return 1;
  if (screen === "investigation") return 2;
  if (screen === "results") return 3;
  return -1;
}

export function Logo({ light = true }: { light?: boolean }) {
  return (
    <span className={`text-xl font-extrabold tracking-tight ${light ? "text-white" : "text-navy"}`}>
      FARM<span className="text-lime">CASE</span>
    </span>
  );
}

export function Stepper({ tone = "cream" }: { tone?: "cream" | "dark" }) {
  const { screen } = useGame();
  const current = stepIndex(screen);
  if (current < 0) return null;
  const dark = tone === "dark";
  return (
    <ol className="flex flex-wrap gap-4">
      {STEPS.map((step, index) => {
        const done = index < current;
        const active = index === current;
        return (
          <li key={step.label} className="flex items-center gap-2 text-sm font-bold">
            <span
              className={`grid h-6 w-6 place-items-center rounded-full text-xs ${
                active ? "bg-lime text-navy" : done ? "bg-moss text-white" : dark ? "bg-white/10 text-white/70" : "bg-white text-moss"
              }`}
            >
              {index + 1}
            </span>
            <span className={dark ? "text-white/80" : active ? "text-navy" : "text-ink/45"}>{step.label}</span>
          </li>
        );
      })}
    </ol>
  );
}

export function PageHeader({
  eyebrow,
  title,
  subtitle,
  tone = "cream",
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  tone?: "cream" | "dark";
}) {
  const dark = tone === "dark";
  return (
    <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div className="max-w-xl">
        {eyebrow && (
          <p className={dark ? "text-xs font-bold uppercase tracking-[0.16em] text-lime" : "eyebrow"}>{eyebrow}</p>
        )}
        <h1 className={`mt-1 text-3xl font-extrabold sm:text-4xl ${dark ? "text-white" : "text-navy"}`}>{title}</h1>
        {subtitle && <p className={`mt-2 text-sm ${dark ? "text-white/70" : "text-ink/60"}`}>{subtitle}</p>}
      </div>
      <Stepper tone={tone} />
    </div>
  );
}

export function Shell({ children, tone = "cream" }: { children: ReactNode; tone?: "cream" | "dark" | "hero" }) {
  const { screen, go } = useGame();
  const dark = tone === "dark";
  const hero = tone === "hero";

  return (
    <div className={`flex min-h-screen flex-col ${hero ? "bg-sky" : dark ? "bg-navy-deep text-white" : "bg-cream text-ink"}`}>
      <header className="bg-navy text-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-3 px-5 py-3">
          <button type="button" onClick={() => go("welcome")} className="rounded-full">
            <Logo />
          </button>
          <nav className="flex flex-1 flex-wrap items-center gap-2 text-sm font-semibold text-white/75">
            <NavButton active={screen === "welcome"} onClick={() => go("welcome")}>
              Overview
            </NavButton>
            <NavButton active={screen === "files"} onClick={() => go("files")}>
              Case Files
            </NavButton>
            <NavButton active={screen === "data"} onClick={() => go("data")}>
              Farm Data
            </NavButton>
          </nav>
        </div>
      </header>
      <main className={hero ? "flex flex-1 flex-col" : "mx-auto w-full max-w-6xl flex-1 px-5 py-8"}>{children}</main>
    </div>
  );
}

function NavButton({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full px-3 py-1 ${active ? "bg-white/10 text-white" : "hover:text-white"}`}
    >
      {children}
    </button>
  );
}
