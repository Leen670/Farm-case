import { GameProvider, useGame } from "./state/game";
import { Shell } from "./components/Shell";
import { Welcome } from "./pages/Welcome";
import { FarmerProfile } from "./pages/FarmerProfile";
import { FarmMap } from "./pages/FarmMap";
import { EvidenceBoard } from "./pages/EvidenceBoard";

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
      {screen === "farmer" && <FarmerProfile />}
      {screen === "map" && <FarmMap />}
      {screen === "board" && <EvidenceBoard />}
    </Shell>
  );
}