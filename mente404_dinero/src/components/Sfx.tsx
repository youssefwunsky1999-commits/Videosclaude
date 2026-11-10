import React from "react";
import { Audio, Sequence, staticFile } from "remotion";
import { theme } from "../theme";

export type SfxName = "whoosh" | "hit" | "tick" | "pop" | "riser" | "glitch" | "ding" | "down";

/** Efecto que arranca `lead` fotogramas ANTES del golpe visual (se percibe sincronizado) */
export const Sfx: React.FC<{ at: number; n: SfxName; v?: number; lead?: number }> = ({ at, n, v = 1, lead = 2 }) => (
  <Sequence from={Math.max(0, at - lead)} durationInFrames={90} layout="none">
    <Audio src={staticFile(`sfx/${n}.wav`)} volume={theme.audio.sfx * v} />
  </Sequence>
);
