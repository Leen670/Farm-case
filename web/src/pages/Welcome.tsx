import { Button } from "../components/Button";
import { useGame } from "../state/game";

export function Welcome() {
  const { go } = useGame();

  return (
    <div className="flex flex-1 flex-col bg-sky text-white">
      <div className="mx-auto grid w-full max-w-6xl flex-1 items-center gap-8 px-6 py-10 lg:grid-cols-[1.1fr_0.9fr]">
        <div>
          <p className="text-xs font-extrabold uppercase tracking-[0.18em] text-lime">
            Follow the evidence. Open a better rotation.
          </p>
          <h1 className="mt-4 text-6xl font-extrabold leading-[0.9] sm:text-7xl">
            FARM
            <br />
            <span className="text-lime">CASE</span>
          </h1>
          <p className="mt-4 max-w-md text-base text-white/90">
            Every clue leads to a better harvest. Pin any farm, collect the NASA evidence, and leave with a 3-year rotation.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button onClick={() => go("farmer")}>Start a case</Button>
            <Button variant="secondary" onClick={() => go("files")}>
              Case files
            </Button>
          </div>
        </div>
        <HeroArt />
      </div>
      <div className="bg-[#c6a56a]">
        <div className="mx-auto flex h-24 max-w-6xl items-end justify-between px-6">
          {Array.from({ length: 14 }, (_, index) => (
            <span key={index} className="mb-4 h-14 w-4 rounded-full bg-[#1f6b32]" />
          ))}
        </div>
      </div>
    </div>
  );
}

function HeroArt() {
  return (
    <svg viewBox="0 0 420 280" className="h-auto w-full" role="img" aria-label="Two investigators in a field">
      <rect width="420" height="210" fill="#2090f0" />
      <circle cx="340" cy="48" r="28" fill="#f5a623" />
      <rect y="186" width="420" height="94" fill="#3c9a45" />
      <Investigator x={150} prop="glass" />
      <Investigator x={250} prop="board" />
    </svg>
  );
}

function Investigator({ x, prop }: { x: number; prop: "glass" | "board" }) {
  return (
    <g transform={`translate(${x} 78)`}>
      <ellipse cx="36" cy="168" rx="28" ry="6" fill="#1d6a30" />
      <path d="M10 36 h52 l-8 14 H18 Z" fill="#e2b657" />
      <circle cx="36" cy="48" r="16" fill="#f0c09a" />
      <rect x="22" y="66" width="28" height="22" rx="4" fill="#f4f1dc" />
      <rect x="20" y="80" width="32" height="40" rx="6" fill="#1f6b32" />
      <rect x="24" y="118" width="10" height="32" rx="3" fill="#6b3e22" />
      <rect x="38" y="118" width="10" height="32" rx="3" fill="#6b3e22" />
      {prop === "glass" ? (
        <g transform="translate(48 78)">
          <circle cx="10" cy="10" r="10" fill="none" stroke="#d7ecff" strokeWidth="3" />
          <rect x="16" y="16" width="10" height="3" rx="1" transform="rotate(40 16 16)" fill="#d7ecff" />
        </g>
      ) : (
        <g transform="translate(50 84)">
          <rect width="22" height="28" rx="2" fill="#f4f1dc" />
          <rect x="4" y="6" width="14" height="2" fill="#1f6b32" />
          <rect x="4" y="12" width="14" height="2" fill="#e24b3c" />
          <rect x="4" y="18" width="10" height="2" fill="#1f6b32" />
        </g>
      )}
    </g>
  );
}
