import { useRef, useState } from "react";
import { PixelButton } from "../components/PixelButton";
import { useGame, type Screen } from "../state/game";

const MENU: { screen: Screen; label: string }[] = [
  { screen: "files", label: "Case Files" },
  { screen: "data", label: "Farm Data" },
  { screen: "assistant", label: "AI Assistant" },
];

export function Welcome() {
  const { go } = useGame();
  const loopRef = useRef<HTMLVideoElement>(null);
  const [showMenu, setShowMenu] = useState(false);

  function revealMenu() {
    setShowMenu(true);
    void loopRef.current?.play().catch(() => undefined);
  }

  return (
    <div className="relative h-screen overflow-hidden bg-[#1d4d28]">
      <div className="absolute top-1/2 left-1/2 h-[max(100vh,56.25vw)] w-[max(100vw,177.78vh)] -translate-x-1/2 -translate-y-1/2">
        <video
          ref={loopRef}
          className="h-full w-full object-cover"
          src={`${import.meta.env.BASE_URL}backgrounds/farm_case_loop.mp4`}
          loop
          muted
          playsInline
          preload="auto"
        />
        {!showMenu && (
          <video
            className="absolute inset-0 z-20 h-full w-full object-cover"
            src={`${import.meta.env.BASE_URL}backgrounds/farm_case_cinematic_intro_short.mp4`}
            autoPlay
            muted
            playsInline
            onEnded={revealMenu}
            onError={revealMenu}
            onLoadedData={(event) => {
              void event.currentTarget.play().catch(revealMenu);
            }}
          />
        )}
        {showMenu && (
          <div className="absolute top-[62%] left-1/2 z-10 w-[9.6rem] -translate-x-1/2">
            <div className="flex flex-col gap-2">
              <PixelButton tone="green" onClick={() => go("farmer")}>
                Start Case
              </PixelButton>
              {MENU.map((item) => (
                <PixelButton key={item.screen} onClick={() => go(item.screen)}>
                  {item.label}
                </PixelButton>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

