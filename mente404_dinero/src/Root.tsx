import React from "react";
import { Composition } from "remotion";
import { Main } from "./Main";
import { DURACION, FPS } from "./timeline";
import { theme } from "./theme";

export const Root: React.FC = () => (
  <Composition id="Mente404Dinero" component={Main} durationInFrames={DURACION} fps={FPS} width={theme.layout.w} height={theme.layout.h} />
);
