// theme.ts — única fuente de colores, curvas y muelles. Nunca hex ni easings sueltos en componentes.
import { Easing } from "remotion";

export const theme = {
  colors: {
    bg: "#06070B",
    bgAlt: "#0F1119",
    surface: "rgba(255,255,255,0.045)",
    line: "rgba(255,255,255,0.10)",
    primary: "#E8B04B", // ORO — color héroe, máx. un elemento por fotograma
    primarySoft: "rgba(232,176,75,0.18)",
    accent: "#45C8C1", // frío: sistema, bancos, datos
    accentSoft: "rgba(69,200,193,0.16)",
    danger: "#FF5A4E", // solo semántico: pérdida
    text: "#F3F0E8",
    textDim: "#8E8B95",
    glow: "rgba(232,176,75,0.45)",
    goldA: "#FFE2A0",
    goldB: "#E8B04B",
    goldC: "#9A6A1E",
  },
  fonts: {
    display: "MDisplay", // Inter Display Black (public/fonts)
    displayBold: "MDisplayBold",
    body: "MBody",
    mono: "MMono",
  },
  ease: {
    out: Easing.bezier(0.16, 1, 0.3, 1),
    inOut: Easing.bezier(0.83, 0, 0.17, 1),
    in: Easing.bezier(0.7, 0, 0.84, 0),
    soft: Easing.bezier(0.33, 1, 0.68, 1),
  },
  spring: {
    snappy: { damping: 14, stiffness: 160, mass: 0.6 },
    smooth: { damping: 20, stiffness: 90, mass: 1 },
    bouncy: { damping: 11, stiffness: 170, mass: 0.7 },
  },
  // composición 9:16 — zonas seguras
  layout: {
    w: 1080,
    h: 1920,
    stageTop: 390, // zona del gráfico
    stageH: 860,
    captionY: 1400, // centro de los subtítulos
  },
  audio: { music: 0.16, voice: 1, sfx: 0.5 },
} as const;

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
