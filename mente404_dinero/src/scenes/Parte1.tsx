import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Chip, Entrance, GlitchText, Scene, Stage, WordReveal, useBreathe, useSpring } from "../components/Motion";
import { Coin, Eye, GoldBar } from "../components/Icons";
import { Sfx } from "../components/Sfx";
import { Escena, at } from "../timeline";
import { clamp, theme } from "../theme";

const C = theme.colors;
type P = { e: Escena };

// 1 — Gancho: moneda que gira + pregunta
export const Gancho: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const coinIn = useSpring(0, theme.spring.bouncy);
  const b = useBreathe();
  const tTrab = at(e, "trabajando");
  const tSin = at(e, "sin");
  const spin = interpolate(coinIn, [0, 1], [-Math.PI * 2, 0]) + frame / 18;
  const swap = interpolate(frame, [tSin - 4, tSin + 4], [0, 1], { ...clamp, easing: theme.ease.inOut });
  return (
    <Scene d={e.d}>
      <Sfx at={0} n="hit" v={0.9} lead={0} />
      <Sfx at={tTrab} n="whoosh" v={0.6} />
      <Sfx at={tSin} n="glitch" v={0.7} />
      <Stage style={{ justifyContent: "flex-start", paddingTop: 30 }}>
        <Entrance delay={2} y={-30}>
          <Chip>Expediente · Dinero</Chip>
        </Entrance>
        <div
          style={{
            marginTop: 70, opacity: coinIn,
            transform: `translateY(${interpolate(coinIn, [0, 1], [120, 0]) + b.y}px) scale(${interpolate(coinIn, [0, 1], [0.4, 1]) * b.s})`,
          }}
        >
          <Coin size={330} spin={spin} />
        </div>
        <div style={{ position: "relative", marginTop: 90, height: 260, width: "100%" }}>
          <div style={{ position: "absolute", inset: 0, opacity: 1 - swap, transform: `translateY(${-swap * 40}px)` }}>
            <WordReveal text="TRABAJANDO POR DINERO" delay={tTrab} size={104} />
          </div>
          {frame >= tSin - 4 && (
            <div style={{ position: "absolute", inset: 0, opacity: swap, transform: `translateY(${(1 - swap) * 40}px)` }}>
              <GlitchText at={tSin} style={{ fontFamily: theme.fonts.display, fontSize: 104, lineHeight: 1.02, letterSpacing: "-0.035em", color: C.text, textAlign: "center" }}>
                ¿SABES CÓMO FUNCIONA?
              </GlitchText>
            </div>
          )}
        </div>
      </Stage>
    </Scene>
  );
};

// 2 — Abre los ojos
export const Ojos: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const open = useSpring(3, theme.spring.snappy);
  const iris = interpolate(frame, [3, 20], [1.25, 1], { ...clamp, easing: theme.ease.out });
  const flash = interpolate(frame, [3, 6, 16], [0, 0.55, 0], clamp);
  const rays = useSpring(6, theme.spring.smooth);
  return (
    <Scene d={e.d} exit={7}>
      <Sfx at={4} n="hit" v={1} />
      <Stage>
        <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center" }}>
          {Array.from({ length: 14 }).map((_, i) => {
            const pr = interpolate(rays, [0, 1], [0, 1], clamp) * (0.6 + 0.4 * Math.sin(i * 1.7) ** 2);
            return (
              <div
                key={i}
                style={{
                  position: "absolute", width: 6, height: 260 * pr, left: "50%", top: "50%",
                  background: `linear-gradient(180deg, ${C.accent}88, transparent)`, borderRadius: 4,
                  transformOrigin: "50% 0%", transform: `translateX(-50%) rotate(${(360 / 14) * i + frame * 0.4}deg) translateY(200px)`,
                  opacity: 0.6,
                }}
              />
            );
          })}
          <Eye width={720} open={open} iris={iris} />
        </div>
        <div style={{ marginTop: 110 }}>
          <WordReveal text="ABRE LOS OJOS" delay={e.w[0]} per={4} size={128} />
        </div>
      </Stage>
      <div style={{ position: "absolute", inset: 0, background: C.text, opacity: flash, pointerEvents: "none" }} />
    </Scene>
  );
};

// 3 — Sin montaña de oro
export const Oro: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tResp = at(e, "respaldado");
  const tMont = at(e, "montana");
  const drain = interpolate(frame, [tResp, tResp + 26], [1, 0], { ...clamp, easing: theme.ease.inOut });
  const stamp = useSpring(tMont, theme.spring.bouncy);
  const rows = [[0, 1, 2], [3, 4], [5]];
  return (
    <Scene d={e.d}>
      <Sfx at={tResp} n="down" v={0.8} />
      <Sfx at={tMont} n="hit" v={0.9} />
      <Stage>
        <Entrance delay={0}>
          <Chip color={C.textDim}>¿Qué respalda tu dinero?</Chip>
        </Entrance>
        <div style={{ position: "relative", marginTop: 90, display: "flex", flexDirection: "column-reverse", alignItems: "center", gap: 14 }}>
          {rows.map((row, r) => (
            <div key={r} style={{ display: "flex", gap: 14 }}>
              {row.map((k) => {
                const p = useSpring(4 + k * 4, theme.spring.bouncy);
                return (
                  <div key={k} style={{ opacity: interpolate(p, [0, 0.4], [0, 1], clamp), transform: `translateY(${interpolate(p, [0, 1], [-260, 0])}px) rotate(${interpolate(p, [0, 1], [k % 2 ? 8 : -8, 0])}deg)` }}>
                    <GoldBar id={`b${k}`} w={250} fill={interpolate(drain, [0, 1], [0, 1], clamp) ** (1 + (5 - k) * 0.12)} />
                  </div>
                );
              })}
            </div>
          ))}
          <div
            style={{
              position: "absolute", left: "50%", top: "50%",
              transform: `translate(-50%, -50%) rotate(-9deg) scale(${interpolate(stamp, [0, 1], [2.2, 1])})`,
              opacity: interpolate(stamp, [0, 0.3], [0, 1], clamp),
              fontFamily: theme.fonts.display, fontSize: 70, color: C.danger, letterSpacing: "0.02em",
              border: `10px solid ${C.danger}`, borderRadius: 18, padding: "10px 34px", whiteSpace: "nowrap",
              background: "rgba(6,7,11,0.72)", lineHeight: 1,
            }}
          >
            SIN ORO DETRÁS
          </div>
        </div>
      </Stage>
    </Scene>
  );
};

// 4 — 1971: la cadena dólar–oro se rompe
export const Anio1971: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const t71 = at(e, "1971");
  const tConv = at(e, "convertibilidad");
  const year = Math.round(interpolate(frame, [6, t71], [1944, 1971], { ...clamp, easing: theme.ease.inOut }));
  const brk = useSpring(t71, theme.spring.snappy);
  const yearHit = useSpring(t71, theme.spring.bouncy);
  const nodes = useSpring(0, theme.spring.smooth);
  const label = useSpring(tConv, theme.spring.snappy);
  const shake = frame >= t71 && frame < t71 + 8 ? Math.sin(frame * 3) * (t71 + 8 - frame) * 2 : 0;
  const ticks = Array.from({ length: 13 }).map((_, i) => Math.round(interpolate(i / 13, [0, 1], [8, t71 - 2])));
  const linkW = 250;
  return (
    <Scene d={e.d}>
      {ticks.map((t, i) => (
        <Sfx key={i} at={t} n="tick" v={0.45} lead={0} />
      ))}
      <Sfx at={t71} n="hit" v={1} />
      <Sfx at={t71} n="glitch" v={0.5} />
      <Stage style={{ transform: `translateX(${shake}px)` }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", opacity: nodes, transform: `scale(${interpolate(nodes, [0, 1], [0.85, 1])})` }}>
          <div style={{ width: 190, height: 190, borderRadius: "50%", border: `8px solid ${C.accent}`, background: C.accentSoft, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: theme.fonts.display, fontSize: 130, color: C.accent, transform: `translateX(${-brk * 20}px) rotate(${-brk * 10}deg)` }}>
            $
          </div>
          <div style={{ width: linkW, height: 40, position: "relative" }}>
            {[0, 1].map((half) => (
              <div
                key={half}
                style={{
                  position: "absolute", top: 14, height: 12, width: linkW / 2 - 6, left: half ? linkW / 2 + 6 : 0,
                  background: `repeating-linear-gradient(90deg, ${C.text} 0 34px, transparent 34px 46px)`, borderRadius: 6,
                  transformOrigin: half ? "100% 50%" : "0% 50%",
                  transform: `translate(${(half ? 1 : -1) * brk * 30}px, ${brk * 70}px) rotate(${(half ? -1 : 1) * brk * 38}deg)`,
                  opacity: 1 - brk * 0.6,
                }}
              />
            ))}
          </div>
          <div style={{ transform: `translateX(${brk * 20}px) rotate(${brk * 10}deg)` }}>
            <GoldBar id="b71" w={220} />
          </div>
        </div>
        <div style={{ marginTop: 40, height: 70, opacity: interpolate(label, [0, 0.5], [0, 1], clamp), transform: `translateY(${interpolate(label, [0, 1], [20, 0])}px)` }}>
          <Chip color={frame >= t71 ? C.danger : C.textDim}>{frame >= t71 ? "Convertibilidad: fin" : "Convertibilidad dólar ⇄ oro"}</Chip>
        </div>
        <div
          style={{
            marginTop: 70, fontFamily: theme.fonts.display, fontSize: 290, letterSpacing: "-0.05em", lineHeight: 1,
            fontVariantNumeric: "tabular-nums",
            color: frame >= t71 ? C.primary : C.text,
            textShadow: frame >= t71 ? `0 0 70px ${C.glow}, 0 0 140px ${C.primarySoft}` : "none",
            transform: `scale(${frame >= t71 ? interpolate(yearHit, [0, 1], [1.25, 1]) : 1})`,
          }}
        >
          {year}
        </div>
        <Entrance delay={t71 + 8} y={30}>
          <div style={{ fontFamily: theme.fonts.body, fontSize: 40, color: C.textDim, letterSpacing: "0.04em" }}>EE. UU. corta el vínculo del dólar con el oro</div>
        </Entrance>
      </Stage>
    </Scene>
  );
};

// 5 — Pilares: confianza, instituciones, capacidad económica
export const Pilares: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tiempos = [at(e, "confianza"), at(e, "instituciones"), at(e, "capacidad")];
  const labels = ["CONFIANZA", "INSTITUCIONES", "ECONOMÍA"];
  const slab = useSpring(2, theme.spring.smooth);
  const settled = interpolate(frame, [tiempos[2], tiempos[2] + 14], [1, 0], clamp);
  const wobble = Math.sin(frame / 5) * 5 * settled;
  const b = useBreathe(26, 0.008);
  const sinkY = interpolate(frame, [2, tiempos[0]], [0, 26], { ...clamp, easing: theme.ease.in }) * settled;
  return (
    <Scene d={e.d}>
      <Sfx at={2} n="whoosh" v={0.5} />
      {tiempos.map((t, i) => (
        <Sfx key={i} at={t} n="hit" v={0.55} />
      ))}
      <Stage>
        <div style={{ transform: `scale(${b.s})`, display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div
            style={{
              width: 900, height: 150, transform: `translateY(${interpolate(slab, [0, 1], [-200, 0]) + sinkY}px) rotate(${wobble}deg)`, opacity: slab,
              clipPath: "polygon(50% 0, 100% 62%, 100% 100%, 0 100%, 0 62%)",
              background: `linear-gradient(180deg, ${C.bgAlt}, #1A1D29)`, display: "flex", alignItems: "flex-end", justifyContent: "center", paddingBottom: 14,
              boxShadow: `inset 0 -6px 0 ${C.line}`,
            }}
          >
            <div style={{ fontFamily: theme.fonts.mono, fontSize: 34, letterSpacing: "0.18em", color: C.text }}>SISTEMA MONETARIO</div>
          </div>
          <div style={{ display: "flex", gap: 70, height: 470, alignItems: "flex-end", marginTop: 10 }}>
            {labels.map((l, i) => {
              const p = useSpring(tiempos[i], theme.spring.bouncy);
              const hero = i === 0;
              const col = hero ? C.primary : C.accent;
              return (
                <div key={l} style={{ width: 190, height: 470 * interpolate(p, [0, 1], [0, 1], clamp), overflow: "hidden", display: "flex", flexDirection: "column", alignItems: "center" }}>
                  <div style={{ width: 190, height: 30, background: col, borderRadius: 6, flexShrink: 0 }} />
                  <div
                    style={{
                      width: 150, flex: 1, position: "relative",
                      background: `repeating-linear-gradient(90deg, ${col}33 0 18px, ${col}14 18px 30px)`,
                      borderLeft: `3px solid ${col}88`, borderRight: `3px solid ${col}88`,
                      boxShadow: hero ? `0 0 60px ${C.glow}` : undefined,
                    }}
                  >
                    <div
                      style={{
                        position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%) rotate(-90deg)",
                        fontFamily: theme.fonts.display, fontSize: l.length > 10 ? 50 : 58, color: hero ? C.primary : C.text, whiteSpace: "nowrap", letterSpacing: "0.02em",
                        textShadow: hero ? `0 0 30px ${C.glow}` : undefined,
                      }}
                    >
                      {l}
                    </div>
                  </div>
                  <div style={{ width: 190, height: 26, background: col, borderRadius: 6, flexShrink: 0 }} />
                </div>
              );
            })}
          </div>
          <div style={{ width: 900, height: 34, marginTop: 4, background: `linear-gradient(180deg, #1A1D29, ${C.bgAlt})`, borderRadius: 6 }} />
        </div>
      </Stage>
    </Scene>
  );
};
