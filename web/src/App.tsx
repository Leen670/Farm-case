import { GameProvider, useGame } from "./state/game";
import { Shell } from "./components/Shell";
import { Welcome } from "./pages/Welcome";

export function App() {
  return (
    <GameProvider>
      <Stage />
    </GameProvider>
  );
}

function Stage() {
  const { screen } = useGame();
  if (screen === "welcome") {
    return (
      <Shell tone="hero">
        <Welcome />
      </Shell>
    );
  }
  return (
    <Shell>
      <p className="text-2xl font-extrabold text-navy">Farm Case</p>
    </Shell>
  );
}