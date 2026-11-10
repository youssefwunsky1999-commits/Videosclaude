import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { clamp, theme } from "../theme";

const C = theme.colors;

/** Moneda de euro que gira (falso 3D con scaleX) */
export const Coin: React.FC<{ size?: number; spin?: number; glow?: boolean }> = ({ size = 340, spin = 0, glow = true }) => {
  const sx = Math.cos(spin);
  const edge = Math.max(0.08, Math.abs(sx));
  return (
    <div style={{ width: size, height: size, position: "relative", transform: `scaleX(${edge})`, filter: glow ? `drop-shadow(0 0 ${size * 0.18}px ${C.glow})` : undefined }}>
      <div
        style={{
          position: "absolute", inset: 0, borderRadius: "50%",
          background: `radial-gradient(circle at 35% 30%, ${C.goldA}, ${C.goldB} 45%, ${C.goldC} 100%)`,
          boxShadow: `inset 0 0 0 ${size * 0.035}px ${C.goldC}, inset 0 0 ${size * 0.08}px rgba(0,0,0,0.35)`,
        }}
      />
      <div style={{ position: "absolute", inset: size * 0.1, borderRadius: "50%", border: `${size * 0.018}px dashed rgba(120,80,20,0.55)` }} />
      <div
        style={{
          position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
          fontFamily: theme.fonts.display, fontSize: size * 0.52, color: "rgba(110,70,15,0.85)",
          textShadow: `0 ${size * 0.008}px 0 rgba(255,240,200,0.6)`,
        }}
      >
        €
      </div>
    </div>
  );
};

/** Ojo que se abre: open 0..1, irisScale para dilatar */
export const Eye: React.FC<{ width?: number; open: number; iris?: number; glow?: boolean; look?: number }> = ({ width = 640, open, iris = 1, glow = true, look = 0 }) => {
  const h = width / 2;
  const o = Math.max(0.02, open);
  const shape = `M20 150 Q300 ${150 - 150 * o * 1.25} 580 150 Q300 ${150 + 150 * o * 1.25} 20 150Z`;
  return (
    <svg width={width} height={h} viewBox="0 0 600 300" style={{ overflow: "visible", filter: glow ? `drop-shadow(0 0 40px ${C.glow})` : undefined }}>
      <defs>
        <clipPath id="eyeclip">
          <path d={shape} />
        </clipPath>
        <radialGradient id="iris" cx="50%" cy="45%" r="55%">
          <stop offset="0%" stopColor={C.goldA} />
          <stop offset="55%" stopColor={C.goldB} />
          <stop offset="100%" stopColor={C.goldC} />
        </radialGradient>
      </defs>
      <path d={shape} fill="rgba(255,255,255,0.06)" />
      <g clipPath="url(#eyeclip)">
        <g transform={`translate(${300 + look * 60} 150) scale(${iris})`}>
          <circle r="92" fill="url(#iris)" />
          {Array.from({ length: 24 }).map((_, i) => (
            <line key={i} x1="0" y1="34" x2="0" y2="86" stroke="rgba(110,70,15,0.45)" strokeWidth="3" transform={`rotate(${i * 15})`} />
          ))}
          <circle r="34" fill={C.bg} />
          <circle cx="-26" cy="-30" r="14" fill="rgba(255,255,255,0.85)" />
        </g>
      </g>
      <path d={shape} fill="none" stroke={C.text} strokeWidth="9" strokeLinejoin="round" />
    </svg>
  );
};

/** Lingote de oro (trapecio en SVG). fill 0..1 = cuánto oro "queda" (de abajo a arriba) */
export const GoldBar: React.FC<{ w?: number; fill?: number; id: string }> = ({ w = 250, fill = 1, id }) => {
  const h = w * 0.42;
  const pts = `${w * 0.14},0 ${w * 0.86},0 ${w},${h} 0,${h}`;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ overflow: "visible" }}>
      <defs>
        <linearGradient id={`g${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={C.goldA} />
          <stop offset="45%" stopColor={C.goldB} />
          <stop offset="100%" stopColor={C.goldC} />
        </linearGradient>
        <clipPath id={`c${id}`}>
          <rect x="-5" y={h * (1 - fill)} width={w + 10} height={h * fill + 5} />
        </clipPath>
      </defs>
      <polygon points={pts} fill={`url(#g${id})`} clipPath={`url(#c${id})`} />
      <polygon points={`${w * 0.2},${h * 0.18} ${w * 0.8},${h * 0.18} ${w * 0.84},${h * 0.32} ${w * 0.16},${h * 0.32}`} fill="rgba(255,250,230,0.35)" clipPath={`url(#c${id})`} />
      <polygon points={pts} fill="none" stroke={fill < 0.98 ? C.textDim : C.goldC} strokeWidth="3" strokeDasharray={fill < 0.98 ? "10 8" : undefined} />
    </svg>
  );
};

/** Banco clásico */
export const Bank: React.FC<{ size?: number; color?: string }> = ({ size = 360, color = C.accent }) => (
  <svg width={size} height={size * 0.82} viewBox="0 0 200 164" fill="none" stroke={color} strokeWidth="6" strokeLinejoin="round">
    <path d="M10 52 L100 8 L190 52 Z" fill={`${color}22`} />
    <path d="M22 62 H178" />
    {[42, 80, 120, 158].map((x) => (
      <path key={x} d={`M${x} 70 V128`} strokeWidth="10" />
    ))}
    <path d="M16 136 H184 M8 154 H192" />
    <text x="100" y="44" textAnchor="middle" fill={color} stroke="none" fontFamily={theme.fonts.display} fontSize="26">
      €
    </text>
  </svg>
);

/** Persona (silueta) */
export const Person: React.FC<{ h?: number; color?: string }> = ({ h = 220, color = C.textDim }) => (
  <svg width={h * 0.62} height={h} viewBox="0 0 62 100">
    <circle cx="31" cy="24" r="17" fill={color} />
    <path d="M2 100 C2 64 12 50 31 50 C50 50 60 64 60 100 Z" fill={color} />
  </svg>
);

export const IconFactory: React.FC<{ s?: number; color?: string }> = ({ s = 96, color = C.accent }) => (
  <svg width={s} height={s} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth="3.2" strokeLinejoin="round">
    <path d="M4 42 V22 L16 28 V22 L28 28 V22 L40 28 V8 H44 V42 Z" fill={`${color}22`} />
    <path d="M12 36 h6 M24 36 h6" />
  </svg>
);
export const IconHouse: React.FC<{ s?: number; color?: string }> = ({ s = 96, color = C.accent }) => (
  <svg width={s} height={s} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth="3.2" strokeLinejoin="round">
    <path d="M6 22 L24 7 L42 22 V42 H6 Z" fill={`${color}22`} />
    <path d="M19 42 V30 H29 V42" />
  </svg>
);
export const IconChart: React.FC<{ s?: number; color?: string }> = ({ s = 96, color = C.accent }) => (
  <svg width={s} height={s} viewBox="0 0 48 48" fill="none" stroke={color} strokeWidth="3.2" strokeLinejoin="round">
    <path d="M10 14 V30 M10 34 V40" /><rect x="7" y="18" width="6" height="12" fill={`${color}33`} />
    <path d="M24 8 V16 M24 30 V36" /><rect x="21" y="16" width="6" height="14" fill={`${color}33`} />
    <path d="M38 4 V10 M38 24 V30" /><rect x="35" y="10" width="6" height="14" fill={`${color}33`} />
  </svg>
);

/** Línea ascendente que se dibuja (p 0..1) */
export const Spark: React.FC<{ w?: number; h?: number; p: number; color?: string; seed?: number }> = ({ w = 260, h = 90, p, color = C.accent, seed = 1 }) => {
  const n = 8;
  const pts = Array.from({ length: n }).map((_, i) => {
    const x = (i / (n - 1)) * w;
    const wob = Math.sin(i * 2.1 + seed) * 0.16;
    const y = h - (i / (n - 1)) * h * 0.85 - wob * h + h * 0.08;
    return [x, Math.max(4, Math.min(h - 4, y))];
  });
  const d = pts.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
  const len = w * 1.5;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ overflow: "visible" }}>
      <path d={d} fill="none" stroke={color} strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - p)} />
      {p > 0.97 && <circle cx={pts[n - 1][0]} cy={pts[n - 1][1]} r="10" fill={color} />}
    </svg>
  );
};

/** Flecha hacia arriba */
export const ArrowUp: React.FC<{ h: number; w?: number; color?: string }> = ({ h, w = 140, color = C.primary }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
    <div style={{ width: 0, height: 0, borderLeft: `${w / 2}px solid transparent`, borderRight: `${w / 2}px solid transparent`, borderBottom: `${w * 0.7}px solid ${color}` }} />
    <div style={{ width: w * 0.38, height: Math.max(0, h), background: `linear-gradient(180deg, ${color}, ${color}00)` }} />
  </div>
);

/** Tilde de verificación que se dibuja */
export const Check: React.FC<{ p: number; s?: number; color?: string }> = ({ p, s = 56, color = C.accent }) => (
  <svg width={s} height={s} viewBox="0 0 40 40">
    <circle cx="20" cy="20" r="18" fill={`${color}22`} stroke={color} strokeWidth="3" />
    <path d="M11 21 L18 28 L30 13" fill="none" stroke={color} strokeWidth="4.5" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="40" strokeDashoffset={40 * (1 - interpolate(p, [0, 1], [0, 1], clamp))} />
  </svg>
);
