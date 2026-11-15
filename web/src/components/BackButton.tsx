import { useEffect, useRef, useState } from "react";
import { useGame, type Screen } from "../state/game";

export function BackButton({ previous }: { previous: Screen }) {
  const { go } = useGame();
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function close(event: PointerEvent) {
      if (!root.current?.contains(event.target as Node)) setOpen(false);
    }
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("pointerdown", close);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", close);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  function choose(screen: Screen) {
    setOpen(false);
    go(screen);
  }

  return (
    <div ref={root} className="absolute top-4 left-4 z-40">
      <button
        type="button"
        aria-label="Back"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        className="grid h-10 w-10 place-items-center rounded-xl bg-[#1f7a34] text-lg text-white shadow-md"
      >
        ‹
      </button>
      {open && (
        <div className="absolute top-12 left-0 min-w-40 overflow-hidden rounded-xl bg-[#f4efe4] py-1 shadow-[0_12px_28px_rgba(0,0,0,0.28)]">
          <button
            type="button"
            onClick={() => choose(previous)}
            className="block w-full px-3 py-2 text-left text-xs font-extrabold text-[#1d3a24] hover:bg-white"
          >
            Previous step
          </button>
          <button
            type="button"
            onClick={() => choose("welcome")}
            className="block w-full px-3 py-2 text-left text-xs font-extrabold text-[#1d3a24] hover:bg-white"
          >
            Back to home
          </button>
        </div>
      )}
    </div>
  );
}
