type Kind = "ear" | "head" | "maize" | "pod" | "flower" | "leaf" | "tomato" | "onion" | "cotton";

function kindFor(name: string): Kind {
  if (name === "sorghum" || name === "millet") return "head";
  if (name === "maize") return "maize";
  if (name === "chickpea" || name === "faba bean" || name === "lentil" || name === "sesame") return "pod";
  if (name === "sunflower") return "flower";
  if (name === "tomato") return "tomato";
  if (name === "onion") return "onion";
  if (name === "cotton") return "cotton";
  if (name === "wheat" || name === "barley") return "ear";
  return "leaf";
}

export function CropPlant({ name }: { name: string }) {
  const kind = kindFor(name.toLowerCase());
  return (
    <svg viewBox="0 0 160 108" className="h-full w-full" role="img" aria-label={name}>
      <rect width="160" height="108" fill="#8ecbef" />
      <circle cx="28" cy="20" r="9" fill="#ffe56a" />
      <path d="M0 74c28-16 52-8 80-14s50-2 80 8v40H0Z" fill="#9ed85f" />
      <path d="M0 90c40-12 70-4 160 6v12H0Z" fill="#6bb844" />
      {kind === "ear" && <Ears gold={name.toLowerCase() !== "barley"} />}
      {kind === "head" && <SeedHead />}
      {kind === "maize" && <Maize />}
      {kind === "pod" && <Pods />}
      {kind === "flower" && <Sunflower />}
      {kind === "leaf" && <Leaves />}
      {kind === "tomato" && <Tomato />}
      {kind === "onion" && <Onion />}
      {kind === "cotton" && <Cotton />}
    </svg>
  );
}

function Ears({ gold }: { gold: boolean }) {
  const fill = gold ? "#e2b340" : "#d7c07a";
  return (
    <g>
      <Stalk x={58} />
      <Stalk x={102} />
      <ellipse cx="58" cy="40" rx="7" ry="18" fill={fill} />
      <ellipse cx="102" cy="46" rx="6" ry="16" fill={fill} />
      <path d="M52 28l6 8M64 28l-6 8M96 34l6 8M108 34l-6 8" stroke="#c48a28" strokeWidth="1.4" />
    </g>
  );
}

function Stalk({ x }: { x: number }) {
  return <rect x={x - 1.5} y="48" width="3" height="40" rx="1" fill="#6a9a3a" />;
}

function SeedHead() {
  return (
    <g>
      <Stalk x={80} />
      <ellipse cx="80" cy="36" rx="10" ry="22" fill="#c4483a" />
      <ellipse cx="80" cy="34" rx="5" ry="16" fill="#e07060" />
    </g>
  );
}

function Maize() {
  return (
    <g>
      <rect x="76" y="30" width="5" height="58" rx="2" fill="#5f9a32" />
      <path d="M78 36c18-8 22 20 4 28-16 6-22-16-4-28z" fill="#3e8a34" />
      <path d="M80 40c-16-4-18 18-2 24 14 4 18-16 2-24z" fill="#4ea03a" />
      <ellipse cx="92" cy="62" rx="8" ry="14" fill="#f2c14e" transform="rotate(18 92 62)" />
      <path d="M86 50c10-2 14 16 4 22" fill="#6aaa40" />
    </g>
  );
}

function Pods() {
  return (
    <g>
      <Stalk x={70} />
      <Stalk x={92} />
      <ellipse cx="62" cy="58" rx="7" ry="12" fill="#3e9a45" transform="rotate(-24 62 58)" />
      <ellipse cx="100" cy="54" rx="7" ry="12" fill="#2f8a38" transform="rotate(22 100 54)" />
      <ellipse cx="80" cy="42" rx="6" ry="11" fill="#57b056" transform="rotate(-8 80 42)" />
    </g>
  );
}

function Sunflower() {
  return (
    <g>
      <Stalk x={80} />
      <circle cx="80" cy="38" r="16" fill="#f2c14e" />
      <circle cx="80" cy="38" r="8" fill="#6a3e16" />
      <circle cx="76" cy="36" r="2" fill="#8a5a28" />
    </g>
  );
}

function Leaves() {
  return (
    <g>
      <Stalk x={80} />
      <ellipse cx="66" cy="58" rx="14" ry="7" fill="#3d9a40" transform="rotate(-20 66 58)" />
      <ellipse cx="96" cy="52" rx="14" ry="7" fill="#2f8a34" transform="rotate(18 96 52)" />
      <ellipse cx="72" cy="42" rx="12" ry="6" fill="#57b056" transform="rotate(-30 72 42)" />
      <ellipse cx="92" cy="40" rx="12" ry="6" fill="#3e9a45" transform="rotate(24 92 40)" />
    </g>
  );
}

function Tomato() {
  return (
    <g>
      <Stalk x={80} />
      <circle cx="68" cy="62" r="10" fill="#d6453d" />
      <circle cx="90" cy="56" r="9" fill="#e15b4a" />
      <path d="M64 54h8M86 48h8" stroke="#3e9a45" strokeWidth="2" />
    </g>
  );
}

function Onion() {
  return (
    <g>
      <ellipse cx="80" cy="72" rx="16" ry="12" fill="#f0ddb0" />
      <ellipse cx="80" cy="70" rx="8" ry="6" fill="#e4c98a" />
      <path d="M80 62c-6-16 2-28 0-36M80 62c8-14 2-26 6-34" stroke="#5fa83a" strokeWidth="2" fill="none" />
    </g>
  );
}

function Cotton() {
  return (
    <g>
      <Stalk x={80} />
      <circle cx="64" cy="50" r="8" fill="#f7f4ee" />
      <circle cx="74" cy="46" r="7" fill="#fff" />
      <circle cx="98" cy="58" r="8" fill="#f4efe6" />
      <circle cx="90" cy="54" r="7" fill="#fff" />
    </g>
  );
}
