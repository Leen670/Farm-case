import { useEffect, useRef, useState } from "react";
import { ApiError, askAssistant } from "../api/client";
import { BackButton } from "../components/BackButton";
import { useGame } from "../state/game";

function art(file: string): string {
  return `/images/${encodeURIComponent(file)}`;
}

const STEPS = [
  { icon: "Farmer Avatar Icon.png", label: "1 Farmer Information" },
  { icon: "Glossy Green Magnifying Glass Badge.png", label: "2 Collect Evidence" },
  { icon: "Forest Green Investigation Checklist Badge.png", label: "3 AI Investigation" },
  { icon: "Case Solved Checkmark Badge.png", label: "4 Case Solved" },
];

type ChatLine = { role: "user" | "assistant"; text: string };

export function Assistant() {
  const { result, saved, openSaved, go } = useGame();
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatLine[]>([]);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");
  const thread = useRef<HTMLDivElement>(null);
  const active = result ?? saved[0]?.result ?? null;
  const savedCase = !result && saved[0] ? saved[0] : null;
  const caseId = active?.case_id ?? "";

  useEffect(() => {
    setMessages([]);
    setQuestion("");
    setError("");
  }, [caseId]);

  useEffect(() => {
    const box = thread.current;
    if (box) box.scrollTop = box.scrollHeight;
  }, [messages, asking]);

  async function ask() {
    const text = question.trim();
    if (!text || !active || asking) return;
    const history = messages.slice(-8);
    const next = [...messages, { role: "user" as const, text }];
    setMessages(next);
    setQuestion("");
    setAsking(true);
    setError("");
    try {
      const reply = await askAssistant(active, text, history);
      setMessages([...next, { role: "assistant", text: reply }]);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "The assistant could not answer.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="relative h-screen overflow-hidden bg-[#07140f] text-[#2c3428]">
      <img
        src={art("Sunset Farm with Windmill and Barn.png")}
        alt=""
        className="absolute inset-0 h-full w-full object-cover object-[18%_center]"
      />
      <div className="absolute inset-0 bg-gradient-to-r from-[#07140f] via-[#07140f]/55 to-[#10261c]/35" />

      <BackButton previous={result ? "results" : "welcome"} />

      <div className="relative z-30 flex h-full gap-4 px-4 pt-16 pb-4 sm:px-6">
        <aside className="hidden w-52 shrink-0 flex-col md:flex">
          <img src={art("Farm Case Sprout Logo.png")} alt="Farm Case" className="mt-2 w-40 object-contain" />
          <ol className="mt-8 space-y-3">
            {STEPS.map((step) => (
              <li key={step.label} className="flex items-center gap-2 px-1.5 text-xs font-semibold text-white/85">
                <img src={art(step.icon)} alt="" className="h-8 w-8 object-contain" />
                <span>{step.label}</span>
              </li>
            ))}
          </ol>
        </aside>

        <section className="mb-2 flex min-w-0 flex-1 flex-col overflow-hidden rounded-[28px] bg-[#f4efe4] shadow-[0_18px_50px_rgba(0,0,0,0.28)]">
          <header className="relative shrink-0 px-5 pt-4 pb-2">
            <div className="relative mx-auto h-16 w-[min(420px,68%)]">
              <img src={art("Torn Cream Paper Banner.png")} alt="" className="h-full w-full object-cover object-center" />
              <div className="absolute inset-0 flex items-center justify-center gap-2 px-8">
                <img src={art("Cream Brain Icon with Green Outline.png")} alt="" className="h-9 w-9 object-contain" />
                <div className="min-w-0 text-left">
                  <p className="text-sm leading-tight font-extrabold text-[#2a2418]">AI Assistant</p>
                  <p className="text-[10px] text-[#6d6254]">Questions stay on this farm. It does not pick a new rotation.</p>
                </div>
              </div>
            </div>
          </header>

          <div ref={thread} className="min-h-0 flex-1 space-y-3 overflow-y-auto px-5 py-3">
            {!active && (
              <div className="rounded-2xl bg-white px-4 py-4 shadow-sm">
                <p className="text-sm font-semibold text-[#1d3a24]">
                  Start a case before asking. The assistant only talks about a farm that is already open.
                </p>
                <button
                  type="button"
                  onClick={() => go("farmer")}
                  className="mt-3 rounded-lg bg-[#2f8a34] px-4 py-2 text-sm font-extrabold text-white shadow-[0_3px_0_#1c5c22]"
                >
                  Start a case
                </button>
              </div>
            )}

            {active && messages.length === 0 && (
              <div className="flex items-center gap-3">
                <img src={art("Smiling Sprout Robot Advisor.png")} alt="" className="h-16 w-auto object-contain" />
                <p className="text-sm font-semibold text-[#6d6254]">Ask about this farm. I will remember this chat.</p>
              </div>
            )}

            {savedCase && (
              <button
                type="button"
                onClick={() => openSaved(savedCase.id)}
                className="text-left text-xs font-bold text-[#1f8a3a] underline"
              >
                Using {savedCase.farmerName}&apos;s saved case. Open it.
              </button>
            )}

            {messages.map((line, index) =>
              line.role === "user" ? (
                <p
                  key={`${line.role}-${index}`}
                  className="ml-auto w-fit max-w-[80%] rounded-2xl bg-[#1f8a3a] px-3 py-2 text-sm font-semibold text-white"
                >
                  {line.text}
                </p>
              ) : (
                <div key={`${line.role}-${index}`} className="flex items-start gap-2">
                  <img src={art("Smiling Sprout Robot Advisor.png")} alt="" className="h-8 w-8 shrink-0 object-contain" />
                  <p className="max-w-[80%] rounded-2xl bg-white px-3 py-2 text-sm leading-relaxed text-[#4a4338] shadow-sm">
                    {line.text}
                  </p>
                </div>
              ),
            )}
            {asking && <p className="text-xs font-semibold text-[#6d6254]">Thinking…</p>}
          </div>

          {active && (
            <div className="shrink-0 border-t border-[#e6dcc8] px-5 py-3">
              <div className="flex gap-2">
                <input
                  className="field-line"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Why this rotation?"
                  onKeyDown={(event) => {
                    if (event.key === "Enter") void ask();
                  }}
                />
                <button
                  type="button"
                  disabled={asking || question.trim().length === 0}
                  onClick={() => void ask()}
                  className="rounded-lg bg-[#1f8a3a] px-4 text-xs font-extrabold text-white disabled:opacity-40"
                >
                  Ask
                </button>
              </div>
              {error && <p className="mt-2 text-xs font-semibold text-[#b42318]">{error}</p>}
            </div>
          )}
        </section>
      </div>

      <img
        src={art("Glossy Green Leafy Corner Frame.png")}
        alt=""
        className="pointer-events-none absolute inset-0 z-20 h-full w-full object-cover"
      />
    </div>
  );
}
