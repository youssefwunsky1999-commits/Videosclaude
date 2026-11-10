import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { BgMesh, Grade, Grain, Scan, Vignette } from "./components/Layers";
import { Captions } from "./components/Captions";
import { DURACION, ESCENAS, Escena } from "./timeline";
import { clamp, theme } from "./theme";
import { cargarFuentes } from "./fonts";
import { Anio1971, Gancho, Ojos, Oro, Pilares } from "./scenes/Parte1";
import { Ahorros, Bancos, Giro, Precios, Quien } from "./scenes/Parte2";
import { Activos, Contraste, Final, Millonario, Pregunta, Realidad } from "./scenes/Parte3";

cargarFuentes();

const MAPA: Record<string, { C: React.FC<{ e: Escena }>; subs: boolean }> = {
  gancho: { C: Gancho, subs: true },
  ojos: { C: Ojos, subs: false },
  oro: { C: Oro, subs: true },
  "1971": { C: Anio1971, subs: true },
  pilares: { C: Pilares, subs: true },
  giro: { C: Giro, subs: false },
  bancos: { C: Bancos, subs: true },
  precios: { C: Precios, subs: true },
  quien: { C: Quien, subs: true },
  ahorros: { C: Ahorros, subs: true },
  activos: { C: Activos, subs: true },
  realidad: { C: Realidad, subs: true },
  millonario: { C: Millonario, subs: false },
  contraste: { C: Contraste, subs: true },
  pregunta: { C: Pregunta, subs: false },
  final: { C: Final, subs: false },
};

/** Barra de progreso + marca, arriba (fuera de la UI de la plataforma) */
const Top: React.FC = () => {
  const frame = useCurrentFrame();
  const fin = ESCENAS[ESCENAS.length - 1].from;
  const o = interpolate(frame, [4, 20, fin - 6, fin], [0, 1, 1, 0], clamp);
  return (
    <div style={{ position: "absolute", top: 228, left: 90, right: 90, opacity: o }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontFamily: theme.fonts.mono, fontSize: 24, letterSpacing: "0.2em", color: theme.colors.textDim }}>
        <span>MENTE<span style={{ color: theme.colors.text }}>404</span></span>
        <span>EL SISTEMA</span>
      </div>
      <div style={{ marginTop: 14, height: 4, borderRadius: 2, background: theme.colors.line }}>
        <div style={{ width: `${(frame / DURACION) * 100}%`, height: "100%", borderRadius: 2, background: theme.colors.text, opacity: 0.6 }} />
      </div>
    </div>
  );
};

export const Main: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: theme.colors.bg }}>
    <BgMesh />
    {ESCENAS.map((e) => {
      const { C, subs } = MAPA[e.id];
      return (
        <Sequence key={e.id} from={e.from} durationInFrames={e.d} name={e.id}>
          <C e={e} />
          {subs && <Captions e={e} />}
          <Audio src={staticFile(e.audio)} volume={theme.audio.voice} />
        </Sequence>
      );
    })}
    <Top />
    <Grade />
    <Scan />
    <Grain />
    <Vignette />
    <Audio
      src={staticFile("sfx/musica.wav")}
      volume={(f) => theme.audio.music * interpolate(f, [DURACION - 60, DURACION], [1, 0], clamp)}
    />
  </AbsoluteFill>
);
