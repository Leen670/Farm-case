import { GameProvider } from "./state/game";
import { Shell } from "./components/Shell";

export function App() {
  return (
    <GameProvider>
      <Shell>
        <p className="text-2xl font-extrabold text-navy">Farm Case</p>
      </Shell>
    </GameProvider>
  );
}