import { Button } from "../components/Button";
import { titleCase } from "../data/farms";
import { PageHeader } from "../components/Shell";
import { useGame } from "../state/game";

export function CaseFiles() {
  const { saved, openSaved, resetDraft } = useGame();

  return (
    <div>
      <PageHeader
        eyebrow="Solved on this browser"
        title="Case files"
        subtitle="Completed cases stay in this browser. Nothing is sent to an account."
      />
      {saved.length === 0 ? (
        <p className="mt-6 rounded-2xl bg-white px-4 py-3 font-semibold">No cases filed yet.</p>
      ) : (
        <ul className="mt-6 space-y-3">
          {saved.map((item, index) => (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => openSaved(item.id)}
                className="flex w-full items-center justify-between gap-4 rounded-2xl bg-white px-4 py-4 text-left shadow-sm hover:bg-leaf"
              >
                <span>
                  <span className="block text-xs font-bold uppercase tracking-wide text-ink/45">
                    Farm case {String(index + 1).padStart(3, "0")}
                  </span>
                  <span className="mt-1 block font-extrabold text-navy">
                    {item.farmerName} · {item.place}
                  </span>
                  <span className="mt-1 block text-sm text-ink/70">
                    {item.rotation.map((crop) => titleCase(crop)).join(" → ")}
                  </span>
                </span>
                <span className="text-2xl font-extrabold text-lime-dark">{item.score}%</span>
              </button>
            </li>
          ))}
        </ul>
      )}
      <Button className="mt-6" onClick={resetDraft}>
        Start another case
      </Button>
    </div>
  );
}
