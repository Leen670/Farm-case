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
  const dark = screen === "investigation";
  return (
    <Shell tone={dark ? "dark" : "cream"}>
      {screen === "farmer" && <FarmerProfile />}
      {screen === "map" && <FarmMap />}
      {screen === "board" && <EvidenceBoard />}
      {screen === "investigation" && <Investigation />}
      {screen === "results" && <Results />}
      {screen === "files" && <CaseFiles />}
      {screen === "data" && <FarmData />}
    </Shell>
  );
}
