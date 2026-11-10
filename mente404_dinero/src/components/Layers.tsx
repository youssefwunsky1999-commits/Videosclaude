import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { theme } from "../theme";

/** Fondo: malla de luz que respira + rejilla técnica muy tenue. Nunca un sólido plano. */
export const BgMesh: React.FC<{ tint?: string }> = ({ tint = theme.colors.accent }) => {
  const frame = useCurrentFrame();
  const d1 = Math.sin(frame / 70) * 60;
  const d2 = Math.cos(frame / 90) * 50;
  const gridShift = (frame * 0.4) % 90;
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      <div
        style={{
          position: "absolute", width: 1400, height: 1400, borderRadius: "50%",
          top: -520, left: -420 + d1, filter: "blur(60px)",
          background: `radial-gradient(circle, ${tint}2a, transparent 62%)`,
        }}
      />
      <div
        style={{
          position: "absolute", width: 1200, height: 1200, borderRadius: "50%",
          bottom: -520, right: -460 - d2, filter: "blur(80px)",
          background: `radial-gradient(circle, ${theme.colors.primary}1c, transparent 64%)`,
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${theme.colors.line} 1px, transparent 1px), linear-gradient(90deg, ${theme.colors.line} 1px, transparent 1px)`,
          backgroundSize: "90px 90px",
          backgroundPosition: `0px ${gridShift}px`,
          opacity: 0.22,
          maskImage: "radial-gradient(ellipse at 50% 42%, black 10%, transparent 70%)",
          WebkitMaskImage: "radial-gradient(ellipse at 50% 42%, black 10%, transparent 70%)",
        }}
      />
    </AbsoluteFill>
  );
};

export const Grade: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill style={{ backgroundColor: theme.colors.primary, mixBlendMode: "soft-light", opacity: 0.12 }} />
    <AbsoluteFill
      style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.35), transparent 22%, transparent 74%, rgba(0,0,0,0.45))" }}
    />
  </AbsoluteFill>
);

export const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  const noise = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.6'/%3E%3C/svg%3E")`;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none", backgroundImage: noise, backgroundSize: "220px",
        backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`,
        opacity: 0.09, mixBlendMode: "overlay",
      }}
    />
  );
};

export const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{ pointerEvents: "none", background: "radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.6) 100%)" }}
  />
);

/** Scanlines muy sutiles: firma visual de MENTE404 */
export const Scan: React.FC = () => {
  const frame = useCurrentFrame();
  const y = interpolate(frame % 240, [0, 240], [-200, 2120]);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill
        style={{
          backgroundImage: "repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 4px)",
        }}
      />
      <div
        style={{
          position: "absolute", left: 0, right: 0, top: y, height: 180,
          background: "linear-gradient(180deg, transparent, rgba(255,255,255,0.025), transparent)",
        }}
      />
    </AbsoluteFill>
  );
};
