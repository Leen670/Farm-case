import { GameProvider, useGame } from "./state/game";
import { Shell } from "./components/Shell";
import { Welcome } from "./pages/Welcome";
import { FarmerProfile } from "./pages/FarmerProfile";
import { FarmMap } from "./pages/FarmMap";
import { EvidenceBoard } from "./pages/EvidenceBoard";
import { Investigation } from "./pages/Investigation";
import { Results } from "./pages/Results";
import { CaseFiles } from "./pages/CaseFiles";
import { FarmData } from "./pages/FarmData";
import { Assistant } from "./pages/Assistant";

export function App() {
  return (
    <GameProvider>
      <Stage />
    </GameProvider>
  );
}

function Stage() {
  const { screen } = useGame();
  if (screen === "welcome") return <Welcome />;
  if (screen === "farmer") return <FarmerProfile />;
  if (screen === "map") return <FarmMap />;
  if (screen === "investigation") return <Investigation />;
  if (screen === "results") return <Results />;
  if (screen === "files") return <CaseFiles />;
  if (screen === "data") return <FarmData />;
  if (screen === "assistant") return <Assistant />;
  return <Shell>{screen === "board" && <EvidenceBoard />}</Shell>;
}
