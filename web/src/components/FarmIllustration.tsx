import type { Clue } from "../types/api";

const HOTSPOTS = [
  { id: "climate", label: "Climate", x: "28%", y: "30%" },
  { id: "crop", label: "Vegetation", x: "34%", y: "58%" },
  { id: "soil", label: "Soil", x: "52%", y: "40%" },
  { id: "water", label: "Water", x: "72%", y: "62%" },
];

export function FarmIllustration({
  clues,
  collected,
  openId,
  onOpen,
}: {
  clues: Clue[];
  collected: string[];
  openId: string;
  onOpen: (id: string) => void;
}) {
  return (
    <div className="relative mx-auto w-full max-w-xl">
      <svg viewBox="0 0 640 460" className="h-auto w-full" role="img" aria-label="Isometric farm">
        <polygon points="320,36 600,176 320,330 40,176" fill="#6eb844" />
        <polygon points="320,52 572,176 320,308 68,176" fill="#8ed15f" />
        <polygon points="210,230 300,184 332,202 242,248" fill="#e4d2a4" />
        <polygon points="300,184 430,250 398,270 268,204" fill="#d8c392" />
        <polygon points="120,248 230,192 278,218 168,276" fill="#3f8c34" />
        <polygon points="138,244 210,208 222,215 150,251" fill="#2f6d28" />
        <polygon points="156,256 228,220 240,227 168,263" fill="#c9842a" />
        <polygon points="174,268 246,232 258,239 186,275" fill="#2f6d28" />
        <polygon points="360,168 470,118 512,142 402,194" fill="#c9842a" />
        <polygon points="372,164 452,124 464,131 384,171" fill="#e2b15a" />
        <polygon points="388,176 468,136 480,143 400,183" fill="#e2b15a" />
        <polygon points="430,250 530,198 575,224 475,278" fill="#2f92c9" />
        <polygon points="448,244 520,208 548,224 476,260" fill="#7ec8ea" />
        <polygon points="455,188 520,154 548,170 483,204" fill="#8a5a32" />
        <polygon points="150,200 230,160 230,236 150,276" fill="#e24b3c" />
        <polygon points="230,160 320,200 320,276 230,236" fill="#c7372c" />
        <polygon points="140,198 236,146 236,162 150,214" fill="#3d4c5c" />
        <polygon points="236,146 332,196 320,210 230,162" fill="#2c3a48" />
        <polygon points="186,214 208,202 208,228 186,240" fill="#f4e7c5" />
        <polygon points="400,150 470,114 470,168 400,204" fill="#d7f3f6" />
        <polygon points="470,114 530,146 530,200 470,168" fill="#b7e4ea" />
        <polygon points="392,150 474,104 538,142 456,188" fill="#eef9fb" />
        <Tree x={96} y={150} />
        <Tree x={500} y={150} />
        <Tree x={250} y={300} />
      </svg>
      {HOTSPOTS.map((spot) => {
        const clue = clues.find((item) => item.id === spot.id);
        if (!clue) return null;
        const on = collected.includes(spot.id) || openId === spot.id;
        return (
          <button
            key={spot.id}
            type="button"
            onClick={() => onOpen(spot.id)}
            className="absolute -translate-x-1/2 -translate-y-1/2"
            style={{ left: spot.x, top: spot.y }}
            aria-label={spot.label}
          >
            <span
              className={`grid h-8 w-8 place-items-center rounded-full text-xs font-extrabold shadow ${
                on ? "bg-lime text-navy" : "bg-white text-navy"
              }`}
            >
              {on ? "✓" : ""}
            </span>
          </button>
        );
      })}
    </div>
  );
}

function Tree({ x, y }: { x: number; y: number }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <rect x="16" y="28" width="8" height="18" fill="#6b4423" />
      <circle cx="20" cy="20" r="18" fill="#2f8a3a" />
      <circle cx="12" cy="24" r="10" fill="#46a34a" />
    </g>
  );
}
