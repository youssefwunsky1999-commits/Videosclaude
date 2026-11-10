import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Chip, Entrance, GlitchText, Scene, Stage, WordReveal, useBreathe, useSpring } from "../components/Motion";
import { ArrowUp, Bank, Person } from "../components/Icons";
import { Sfx } from "../components/Sfx";
import { Escena, at } from "../timeline";
import { clamp, theme } from "../theme";

const C = theme.colors;
const fmt = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
type P = { e: Escena };

// 6 — Giro
export const Giro: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const push = interpolate(frame, [0, e.d], [1, 1.1], { ...clamp, easing: theme.ease.inOut });
  return (
    <Scene d={e.d} exit={6}>
      <Sfx at={0} n="glitch" v={0.8} lead={0} />
      <Sfx at={e.d - 46} n="riser" v={0.7} lead={0} />
      <Stage style={{ transform: `scale(${push})` }}>
        <GlitchText at={1}>
          <WordReveal text="PERO AQUÍ VIENE LO INTERESANTE…" per={3} size={138} hero={["INTERESANTE…"]} />
        </GlitchText>
      </Stage>
    </Scene>
  );
};

const Card: React.FC<{ title: string; amount: string; color: string; hero?: boolean; sub: string }> = ({ title, amount, color, hero, sub }) => (
  <div
    style={{
      width: 430, padding: "34px 30px", borderRadius: 30, background: hero ? C.primarySoft : C.surface,
      border: `3px solid ${hero ? C.primary : color + "66"}`, boxShadow: hero ? `0 0 70px ${C.glow}` : "0 40px 80px -30px rgba(0,0,0,0.7)",
      display: "flex", flexDirection: "column", gap: 14,
    }}
  >
    <div style={{ fontFamily: theme.fonts.mono, fontSize: 28, letterSpacing: "0.14em", color: hero ? C.primary : color }}>{title}</div>
    <div style={{ fontFamily: theme.fonts.display, fontSize: 84, color: C.text, letterSpacing: "-0.03em", fontVariantNumeric: "tabular-nums" }}>{amount}</div>
    <div style={{ fontFamily: theme.fonts.body, fontSize: 30, color: C.textDim }}>{sub}</div>
  </div>
);

// 7 — Bancos crean depósitos al prestar
export const Bancos: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tPrest = at(e, "prestamos");
  const tCrear = at(e, "crear");
  const tDep = at(e, "depositos");
  const bank = useSpring(0, theme.spring.bouncy);
  const loan = useSpring(tPrest, theme.spring.smooth);
  const dep = useSpring(tCrear, theme.spring.bouncy);
  const b = useBreathe();
  const amount = Math.round(interpolate(useSpring(tCrear + 4, { damping: 30, stiffness: 60, mass: 1 }), [0, 1], [0, 10000]));
  return (
    <Scene d={e.d}>
      <Sfx at={0} n="whoosh" v={0.5} lead={0} />
      <Sfx at={tPrest} n="whoosh" v={0.6} />
      <Sfx at={tCrear} n="pop" v={0.8} />
      <Sfx at={tDep} n="ding" v={0.7} />
      <Stage>
        <div style={{ opacity: bank, transform: `translateY(${interpolate(bank, [0, 1], [80, 0]) + b.y}px) scale(${interpolate(bank, [0, 1], [0.7, 1])})` }}>
          <Bank size={360} />
        </div>
        <Entrance delay={4} y={20}>
          <Chip style={{ marginTop: 26 }}>Banco</Chip>
        </Entrance>
        <div style={{ display: "flex", gap: 40, marginTop: 70, position: "relative" }}>
          {/* chispas de dinero nuevo */}
          {Array.from({ length: 10 }).map((_, i) => {
            const k = frame - tCrear - i * 2;
            if (k < 0 || k > 30) return null;
            const ang = (i / 10) * Math.PI * 2;
            const r = interpolate(k, [0, 30], [40, 260], { ...clamp, easing: theme.ease.out });
            return (
              <div key={i} style={{ position: "absolute", left: 470 + 215 + Math.cos(ang) * r, top: 110 + Math.sin(ang) * r * 0.7, fontFamily: theme.fonts.display, fontSize: 40, color: C.accent, opacity: interpolate(k, [0, 30], [1, 0], clamp) }}>
                €
              </div>
            );
          })}
          <div style={{ opacity: interpolate(loan, [0, 0.4], [0, 1], clamp), transform: `translate(${interpolate(loan, [0, 1], [240, 0])}px, ${interpolate(loan, [0, 1], [-200, 0])}px) scale(${interpolate(loan, [0, 1], [0.5, 1])})` }}>
            <Card title="PRÉSTAMO" amount="10.000 €" color={C.accent} sub="Te lo conceden" />
          </div>
          <div style={{ opacity: interpolate(dep, [0, 0.4], [0, 1], clamp), transform: `translate(${interpolate(dep, [0, 1], [-240, 0])}px, ${interpolate(dep, [0, 1], [-200, 0])}px) scale(${interpolate(dep, [0, 1], [0.5, 1])})` }}>
            <Card title="DEPÓSITO" amount={`+${fmt(amount)} €`} color={C.accent} hero={frame >= tDep} sub="Dinero nuevo" />
          </div>
        </div>
      </Stage>
    </Scene>
  );
};

const Bar: React.FC<{ h: number; color: string; label: string; hero?: boolean }> = ({ h, color, label, hero }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 250 }}>
    <div style={{ height: 600, display: "flex", alignItems: "flex-end" }}>
      <div style={{ width: 170, height: h, borderRadius: "22px 22px 6px 6px", background: `linear-gradient(180deg, ${color}, ${color}33)`, boxShadow: hero ? `0 0 60px ${C.glow}` : undefined }} />
    </div>
    <div style={{ marginTop: 24, fontFamily: theme.fonts.mono, fontSize: 30, letterSpacing: "0.1em", color: C.text }}>{label}</div>
  </div>
);

// 8 — Más dinero, misma producción → precios
export const Precios: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tAum = at(e, "aumenta");
  const tProd = at(e, "produccion");
  const tPrec = at(e, "precios");
  const tSub = at(e, "subir");
  const money = useSpring(tAum, theme.spring.smooth);
  const prod = useSpring(tProd, theme.spring.smooth);
  const prices = useSpring(tPrec, theme.spring.bouncy);
  const intro = useSpring(0, theme.spring.snappy);
  const pulse = frame > tSub ? 1 + Math.sin((frame - tSub) / 5) * 0.02 : 1;
  return (
    <Scene d={e.d}>
      <Sfx at={tAum} n="riser" v={0.35} lead={0} />
      <Sfx at={tProd} n="tick" v={0.8} />
      <Sfx at={tPrec} n="hit" v={0.9} />
      <Stage>
        <div style={{ display: "flex", gap: 30, alignItems: "flex-end", opacity: intro, transform: `translateY(${interpolate(intro, [0, 1], [60, 0])}px)` }}>
          <Bar h={interpolate(money, [0, 1], [110, 560])} color={C.accent} label="DINERO" />
          <Bar h={interpolate(prod, [0, 1], [110, 170])} color={C.textDim} label="PRODUCCIÓN" />
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 250 }}>
            <div style={{ height: 600, display: "flex", alignItems: "flex-end", opacity: interpolate(prices, [0, 0.3], [0, 1], clamp), filter: `drop-shadow(0 0 40px ${C.glow})`, transform: `scale(${pulse})` }}>
              <ArrowUp h={interpolate(prices, [0, 1], [0, 420])} w={170} />
            </div>
            <div style={{ marginTop: 24, fontFamily: theme.fonts.mono, fontSize: 30, letterSpacing: "0.1em", color: C.primary, opacity: interpolate(prices, [0, 0.5], [0, 1], clamp) }}>PRECIOS</div>
          </div>
        </div>
        <div style={{ width: 860, height: 4, background: C.line, marginTop: -56, marginBottom: 52 }} />
      </Stage>
    </Scene>
  );
};

// 9 — ¿Quién lo nota primero?
export const Quien: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tNo = at(e, "no");
  const tMas = at(e, "mas");
  const heights = [250, 200, 280, 215, 240];
  const stacks = [1, 2, 6, 1, 3]; // monedas por persona
  const target = 1; // el foco cae en alguien con poco dinero
  const fx = interpolate(frame, [tNo - 20, tNo + 4, tMas], [0, 4, target], { ...clamp, easing: theme.ease.inOut });
  const spotOn = useSpring(tNo - 22, theme.spring.smooth);
  return (
    <Scene d={e.d}>
      <Sfx at={0} n="whoosh" v={0.5} lead={0} />
      <Sfx at={tMas} n="pop" v={0.8} />
      <Stage style={{ justifyContent: "flex-start", paddingTop: 10 }}>
        <WordReveal text="¿QUIÉN LO NOTA PRIMERO?" per={3} size={112} />
        <div style={{ position: "relative", display: "flex", gap: 34, alignItems: "flex-end", marginTop: 90, height: 470 }}>
          <div
            style={{
              position: "absolute", bottom: -20, width: 260, height: 560, left: fx * (124 + 34) + 62 - 130,
              background: `linear-gradient(180deg, transparent, ${C.primarySoft} 40%, rgba(232,176,75,0.32))`,
              clipPath: "polygon(38% 0, 62% 0, 100% 100%, 0 100%)", opacity: spotOn,
            }}
          />
          {heights.map((h, i) => {
            const p = useSpring(4 + i * 4, theme.spring.snappy);
            const lit = Math.max(0, 1 - Math.abs(fx - i));
            return (
              <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10, width: 124, opacity: p, transform: `translateY(${interpolate(p, [0, 1], [50, 0])}px)` }}>
                <div style={{ display: "flex", flexDirection: "column-reverse", gap: 4 }}>
                  {Array.from({ length: stacks[i] }).map((_, k) => (
                    <div key={k} style={{ width: 70, height: 16, borderRadius: 8, background: C.textDim, opacity: 0.6 }} />
                  ))}
                </div>
                <Person h={h} color={lit > 0.5 && frame > tNo ? C.primary : C.textDim} />
              </div>
            );
          })}
        </div>
      </Stage>
    </Scene>
  );
};

// 10 — Ahorros vs precios
export const Ahorros: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tSuben = at(e, "suben");
  const tPoder = at(e, "poder");
  const tDism = at(e, "disminuye");
  const card = useSpring(0, theme.spring.bouncy);
  const items = 12;
  const quedan = 7;
  const bar = interpolate(frame, [tPoder, tDism + 14], [1, quedan / items], { ...clamp, easing: theme.ease.inOut });
  return (
    <Scene d={e.d}>
      <Sfx at={0} n="pop" v={0.7} lead={0} />
      <Sfx at={tSuben} n="tick" v={0.8} />
      <Sfx at={tDism} n="down" v={0.9} />
      <Stage>
        <div style={{ opacity: card, transform: `translateY(${interpolate(card, [0, 1], [60, 0])}px) scale(${interpolate(card, [0, 1], [0.85, 1])})`, padding: "30px 56px", borderRadius: 30, background: C.surface, border: `3px solid ${C.line}`, textAlign: "center" }}>
          <div style={{ fontFamily: theme.fonts.mono, fontSize: 28, letterSpacing: "0.14em", color: C.textDim }}>TUS AHORROS</div>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 120, color: C.text, letterSpacing: "-0.03em" }}>1.000 €</div>
          <div style={{ fontFamily: theme.fonts.body, fontSize: 30, color: C.textDim }}>los mismos billetes…</div>
        </div>
        <Entrance delay={8} y={20}>
          <div style={{ marginTop: 56, fontFamily: theme.fonts.mono, fontSize: 28, letterSpacing: "0.14em", color: C.textDim, textAlign: "center" }}>…PERO COMPRAN MENOS</div>
        </Entrance>
        <div style={{ marginTop: 26, display: "grid", gridTemplateColumns: "repeat(6, 110px)", gap: 18 }}>
          {Array.from({ length: items }).map((_, i) => {
            const p = useSpring(10 + i * 2, theme.spring.snappy);
            const gone = i >= quedan ? interpolate(frame, [tDism + (items - 1 - i) * 3, tDism + (items - 1 - i) * 3 + 8], [0, 1], { ...clamp, easing: theme.ease.in }) : 0;
            const tag = useSpring(tSuben + (i % 6) * 2, theme.spring.snappy);
            return (
              <div key={i} style={{ position: "relative", width: 110, height: 110, borderRadius: 22, background: C.accentSoft, border: `3px solid ${C.accent}55`, opacity: p * (1 - gone), transform: `scale(${interpolate(p, [0, 1], [0.6, 1]) * (1 - gone * 0.4)}) translateY(${gone * 40}px)` }}>
                <div style={{ position: "absolute", inset: 30, borderRadius: i % 3 === 0 ? "50%" : 10, background: `${C.accent}66` }} />
                <div style={{ position: "absolute", right: -10, top: -14, fontFamily: theme.fonts.display, fontSize: 30, color: C.danger, opacity: tag, transform: `translateY(${interpolate(tag, [0, 1], [10, 0])}px)` }}>↑</div>
              </div>
            );
          })}
        </div>
        <div style={{ marginTop: 50, width: 800 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: theme.fonts.mono, fontSize: 28, letterSpacing: "0.1em", color: frame >= tPoder ? C.danger : C.textDim }}>
            <span>PODER ADQUISITIVO</span>
            <span>{frame >= tDism ? "↓" : ""}</span>
          </div>
          <div style={{ marginTop: 14, height: 26, borderRadius: 13, background: C.line, overflow: "hidden" }}>
            <div style={{ width: `${bar * 100}%`, height: "100%", borderRadius: 13, background: `linear-gradient(90deg, ${C.danger}, #FF8A6B)` }} />
          </div>
        </div>
      </Stage>
    </Scene>
  );
};
