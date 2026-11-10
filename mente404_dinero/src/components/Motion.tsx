import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { clamp, theme } from "../theme";

type SpringCfg = { damping: number; stiffness: number; mass: number };

export const useSpring = (delay: number, config: SpringCfg = theme.spring.smooth) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config });
};

/** Entrada premium: opacidad + subida + escala */
export const Entrance: React.FC<{
  delay?: number; y?: number; scale?: number; x?: number;
  config?: SpringCfg; style?: React.CSSProperties; children: React.ReactNode;
}> = ({ delay = 0, y = 50, x = 0, scale = 0.92, config = theme.spring.smooth, style, children }) => {
  const p = useSpring(delay, config);
  return (
    <div
      style={{
        opacity: interpolate(p, [0, 0.6], [0, 1], clamp),
        transform: `translate(${interpolate(p, [0, 1], [x, 0])}px, ${interpolate(p, [0, 1], [y, 0])}px) scale(${interpolate(p, [0, 1], [scale, 1])})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Envoltorio de escena: entrada rápida y salida más rápida (escala + desenfoque + fundido) */
export const Scene: React.FC<{ d: number; children: React.ReactNode; exit?: number }> = ({ d, children, exit = 9 }) => {
  const frame = useCurrentFrame();
  const inP = interpolate(frame, [0, 10], [0, 1], { ...clamp, easing: theme.ease.out });
  const outP = interpolate(frame, [d - exit, d], [0, 1], { ...clamp, easing: theme.ease.in });
  return (
    <AbsoluteFill
      style={{
        opacity: Math.min(inP, 1 - outP),
        transform: `scale(${interpolate(inP, [0, 1], [1.06, 1]) * interpolate(outP, [0, 1], [1, 0.94])})`,
        filter: `blur(${(1 - inP) * 10 + outP * 14}px)`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

/** Escenario centrado en la zona segura superior */
export const Stage: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      position: "absolute", left: 70, right: 70, top: theme.layout.stageTop, height: theme.layout.stageH,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", ...style,
    }}
  >
    {children}
  </div>
);

/** Respiración idle */
export const useBreathe = (speed = 22, amt = 0.015) => {
  const frame = useCurrentFrame();
  return { s: 1 + Math.sin(frame / speed) * amt, y: Math.sin(frame / (speed * 1.4)) * 5 };
};

/** Titular palabra a palabra; cada palabra con escala+subida+opacidad, escalonadas */
export const WordReveal: React.FC<{
  text: string; delay?: number; per?: number; size?: number; color?: string;
  hero?: string[]; style?: React.CSSProperties; font?: string; gap?: number; strike?: { word: string; at: number };
}> = ({ text, delay = 0, per = 3, size = 110, color = theme.colors.text, hero = [], style, font = theme.fonts.display, gap, strike }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: gap ?? size * 0.26, rowGap: size * 0.02,
        fontFamily: font, fontSize: size, lineHeight: 1.02, letterSpacing: "-0.035em", textAlign: "center",
        ...style,
      }}
    >
      {text.split(" ").map((word, i) => {
        const p = spring({ frame: frame - delay - i * per, fps, config: theme.spring.snappy });
        const isHero = hero.includes(word);
        const sp = strike && word === strike.word ? interpolate(frame, [strike.at, strike.at + 8], [0, 1], { ...clamp, easing: theme.ease.out }) : 0;
        return (
          <span
            key={i}
            style={{
              display: "inline-block", position: "relative",
              opacity: interpolate(p, [0, 0.5], [0, 1], clamp),
              transform: `translateY(${interpolate(p, [0, 1], [size * 0.45, 0])}px) scale(${interpolate(p, [0, 1], [0.85, 1])})`,
              color: isHero ? theme.colors.primary : sp > 0.4 ? theme.colors.textDim : color,
              textShadow: isHero ? `0 0 50px ${theme.colors.glow}, 0 0 110px ${theme.colors.primarySoft}` : "0 6px 30px rgba(0,0,0,0.5)",
            }}
          >
            {word}
            {sp > 0 && (
              <span
                style={{
                  position: "absolute", left: -8, right: -8, top: "52%", height: size * 0.09,
                  background: theme.colors.danger, transformOrigin: "0 50%", transform: `scaleX(${sp}) rotate(-3deg)`,
                  borderRadius: 6,
                }}
              />
            )}
          </span>
        );
      })}
    </div>
  );
};

/** Desplazamiento RGB breve (glitch) alrededor de un fotograma */
export const useGlitch = (at: number, len = 7) => {
  const frame = useCurrentFrame();
  const k = frame - at;
  if (k < 0 || k > len) return { x: 0, on: false, k };
  const j = [14, -10, 18, -6, 9, -14, 4, 0][k % 8];
  return { x: j, on: true, k };
};

export const GlitchText: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ at, children, style }) => {
  const g = useGlitch(at, 8);
  return (
    <div style={{ position: "relative", ...style }}>
      {g.on && (
        <>
          <div style={{ position: "absolute", inset: 0, color: theme.colors.accent, transform: `translateX(${g.x}px)`, opacity: 0.8, mixBlendMode: "screen" }}>{children}</div>
          <div style={{ position: "absolute", inset: 0, color: theme.colors.danger, transform: `translateX(${-g.x}px)`, opacity: 0.8, mixBlendMode: "screen" }}>{children}</div>
        </>
      )}
      <div style={{ position: "relative", clipPath: g.on ? `inset(${(g.k * 13) % 60}% 0 ${(g.k * 7) % 30}% 0)` : undefined }}>{children}</div>
      {g.on && <div style={{ position: "absolute", inset: 0, transform: `translateX(${g.x * 1.6}px)`, clipPath: `inset(0 0 ${100 - ((g.k * 13) % 60)}% 0)` }}>{children}</div>}
    </div>
  );
};

/** Etiqueta pequeña tipo "chip" */
export const Chip: React.FC<{ children: React.ReactNode; color?: string; style?: React.CSSProperties }> = ({ children, color = theme.colors.accent, style }) => (
  <div
    style={{
      fontFamily: theme.fonts.mono, fontSize: 30, letterSpacing: "0.14em", textTransform: "uppercase",
      color, padding: "12px 24px", border: `2px solid ${color}55`, borderRadius: 999, background: `${color}14`,
      ...style,
    }}
  >
    {children}
  </div>
);
