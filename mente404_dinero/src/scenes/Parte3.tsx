import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Chip, Entrance, GlitchText, Scene, Stage, WordReveal, useBreathe, useSpring } from "../components/Motion";
import { Check, Eye, IconChart, IconFactory, IconHouse, Spark } from "../components/Icons";
import { Sfx } from "../components/Sfx";
import { Escena, at } from "../timeline";
import { clamp, theme } from "../theme";

const C = theme.colors;
type P = { e: Escena };

// 11 — Activos
export const Activos: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tAct = at(e, "activos");
  const ts = [at(e, "empresas"), at(e, "inmuebles"), at(e, "acciones")];
  const tBen = at(e, "beneficiarse");
  const tSub = at(e, "subidas");
  const items = [
    { l: "EMPRESAS", I: IconFactory },
    { l: "INMUEBLES", I: IconHouse },
    { l: "ACCIONES", I: IconChart },
  ];
  const chip = useSpring(tAct, theme.spring.snappy);
  const ben = useSpring(tBen, theme.spring.bouncy);
  return (
    <Scene d={e.d}>
      <Sfx at={tAct} n="pop" v={0.7} />
      {ts.map((t, i) => (
        <Sfx key={i} at={t} n="whoosh" v={0.5} />
      ))}
      <Sfx at={tBen} n="ding" v={0.7} />
      <Stage>
        <div style={{ opacity: chip, transform: `scale(${interpolate(chip, [0, 1], [0.7, 1])})`, marginBottom: 50 }}>
          <Chip color={C.text}>Quien posee activos</Chip>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 30 }}>
          {items.map(({ l, I }, i) => {
            const p = useSpring(ts[i], theme.spring.smooth);
            const draw = interpolate(frame, [tBen + i * 5, tBen + i * 5 + 28], [0, 1], { ...clamp, easing: theme.ease.out });
            const fl = Math.sin((frame + i * 20) / 26) * 4;
            return (
              <div
                key={l}
                style={{
                  width: 920, height: 170, borderRadius: 30, background: C.surface, border: `3px solid ${C.line}`,
                  display: "flex", alignItems: "center", padding: "0 40px", gap: 34,
                  opacity: interpolate(p, [0, 0.4], [0, 1], clamp),
                  transform: `translateX(${interpolate(p, [0, 1], [-160, 0])}px) scale(${interpolate(p, [0, 1], [0.9, 1])}) translateY(${fl}px)`,
                }}
              >
                <I s={96} />
                <div style={{ flex: 1, fontFamily: theme.fonts.display, fontSize: 64, color: C.text, letterSpacing: "-0.02em" }}>{l}</div>
                <Spark w={220} h={90} p={draw} seed={i * 2} />
              </div>
            );
          })}
        </div>
        <div style={{ marginTop: 56, height: 90, opacity: interpolate(ben, [0, 0.4], [0, 1], clamp), transform: `translateY(${interpolate(ben, [0, 1], [30, 0])}px) scale(${interpolate(ben, [0, 1], [0.8, 1])})` }}>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 64, color: C.primary, textShadow: `0 0 50px ${C.glow}`, letterSpacing: "-0.02em" }}>
            {frame >= tSub ? "SUBEN CON LOS PRECIOS" : "PUEDEN BENEFICIARSE"}
          </div>
        </div>
      </Stage>
    </Scene>
  );
};

// 12 — La realidad que nadie explica (expediente censurado)
export const Realidad: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tReal = at(e, "realidad");
  const tExp = at(e, "explica");
  const doc = useSpring(0, theme.spring.smooth);
  const lines = [0.92, 0.7, 0.84, 0.55];
  return (
    <Scene d={e.d}>
      <Sfx at={0} n="whoosh" v={0.5} lead={0} />
      <Sfx at={tReal} n="glitch" v={0.7} />
      <Stage>
        <div style={{ width: 900, padding: 56, borderRadius: 26, background: "#E9E4D8", color: "#121212", transform: `rotate(${interpolate(doc, [0, 1], [6, -2])}deg) translateY(${interpolate(doc, [0, 1], [180, 0])}px)`, opacity: doc, boxShadow: "0 50px 100px -30px rgba(0,0,0,0.8)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: theme.fonts.mono, fontSize: 28, letterSpacing: "0.14em", color: "#7A1F18" }}>
            <span>EXPEDIENTE 404</span>
            <span>CONFIDENCIAL</span>
          </div>
          <div style={{ marginTop: 40, position: "relative" }}>
            <div style={{ fontFamily: theme.fonts.display, fontSize: 104, lineHeight: 1, letterSpacing: "-0.04em" }}>LA OTRA REALIDAD</div>
            <div style={{ position: "absolute", inset: "-6px -10px", background: "#121212", transformOrigin: "100% 50%", transform: `scaleX(${interpolate(frame, [tReal, tReal + 10], [1, 0], { ...clamp, easing: theme.ease.inOut })})` }} />
          </div>
          <div style={{ marginTop: 44, display: "flex", flexDirection: "column", gap: 20 }}>
            {lines.map((w, i) => (
              <div key={i} style={{ height: 34, width: `${w * 100}%`, background: "#121212", borderRadius: 4, transformOrigin: "0 50%", transform: `scaleX(${interpolate(frame, [6 + i * 4, 18 + i * 4], [0, 1], { ...clamp, easing: theme.ease.out })})` }} />
            ))}
          </div>
          <div style={{ marginTop: 40, fontFamily: theme.fonts.mono, fontSize: 30, color: "#7A1F18", opacity: interpolate(frame, [tExp, tExp + 8], [0, 1], clamp) }}>
            → casi nadie te lo explica
          </div>
        </div>
      </Stage>
    </Scene>
  );
};

// 13 — No necesitas ser millonario
export const Millonario: React.FC<P> = ({ e }) => {
  const tPara = at(e, "para");
  const tPero = at(e, "pero");
  const tEnt = at(e, "entender");
  return (
    <Scene d={e.d}>
      <Sfx at={tPara} n="whoosh" v={0.5} />
      <Sfx at={tEnt} n="hit" v={0.8} />
      <Stage>
        <WordReveal text="NO NECESITAS SER MILLONARIO" per={3} size={104} strike={{ word: "MILLONARIO", at: tPara }} />
        <Entrance delay={tPara + 4} y={20}>
          <div style={{ marginTop: 34, fontFamily: theme.fonts.mono, fontSize: 32, letterSpacing: "0.08em", color: C.textDim, textAlign: "center" }}>PARA PARTICIPAR EN EL SISTEMA FINANCIERO</div>
        </Entrance>
        <div style={{ width: 120, height: 6, borderRadius: 3, background: C.line, margin: "70px 0" }} />
        <WordReveal text="PERO SÍ NECESITAS" delay={tPero} per={3} size={104} />
        <div style={{ marginTop: 10 }}>
          <WordReveal text="ENTENDERLO" delay={tEnt} size={150} hero={["ENTENDERLO"]} />
        </div>
      </Stage>
    </Scene>
  );
};

// 14 — Unos trabajan por dinero, otros estudian el dinero
export const Contraste: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tUnos = at(e, "unos");
  const tOtros = at(e, "otros");
  const ts = [at(e, "funciona"), at(e, "mueve"), at(e, "invierte")];
  const left = useSpring(tUnos - 4, theme.spring.smooth);
  const right = useSpring(tOtros, theme.spring.smooth);
  const dim = interpolate(frame, [tOtros, tOtros + 12], [1, 0.4], clamp);
  const b = useBreathe();
  const labels = ["CÓMO FUNCIONA", "CÓMO SE MUEVE", "CÓMO SE INVIERTE"];
  return (
    <Scene d={e.d}>
      <Sfx at={tUnos} n="whoosh" v={0.5} />
      <Sfx at={tOtros} n="whoosh" v={0.5} />
      {ts.map((t, i) => (
        <Sfx key={i} at={t} n="pop" v={0.7} />
      ))}
      <Stage>
        <div style={{ display: "flex", gap: 40, alignItems: "stretch" }}>
          <div style={{ width: 440, height: 760, borderRadius: 34, background: C.surface, border: `3px solid ${C.line}`, padding: 40, display: "flex", flexDirection: "column", alignItems: "center", opacity: left * dim, transform: `translateX(${interpolate(left, [0, 1], [-120, 0])}px)` }}>
            <div style={{ fontFamily: theme.fonts.mono, fontSize: 30, letterSpacing: "0.18em", color: C.textDim }}>UNOS</div>
            <div style={{ marginTop: 60, position: "relative", width: 260, height: 260 }}>
              <svg width="260" height="260" viewBox="0 0 100 100" style={{ position: "absolute", inset: 0, transform: `rotate(${frame * 4}deg)` }}>
                <circle cx="50" cy="50" r="42" fill="none" stroke={C.textDim} strokeWidth="5" strokeDasharray="200 64" strokeLinecap="round" />
                <path d="M86 30 L92 46 L76 42 Z" fill={C.textDim} />
              </svg>
              <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: theme.fonts.display, fontSize: 110, color: C.text }}>€</div>
            </div>
            <div style={{ marginTop: 70, fontFamily: theme.fonts.display, fontSize: 58, lineHeight: 1.05, color: C.text, textAlign: "center", letterSpacing: "-0.02em" }}>
              TRABAJAN<br />POR DINERO
            </div>
          </div>
          <div style={{ width: 440, height: 760, borderRadius: 34, background: C.primarySoft, border: `3px solid ${C.primary}`, boxShadow: `0 0 70px ${C.glow}`, padding: 40, display: "flex", flexDirection: "column", alignItems: "center", opacity: right, transform: `translateX(${interpolate(right, [0, 1], [120, 0])}px) translateY(${b.y}px)` }}>
            <div style={{ fontFamily: theme.fonts.mono, fontSize: 30, letterSpacing: "0.18em", color: C.primary }}>OTROS</div>
            <div style={{ marginTop: 40, fontFamily: theme.fonts.display, fontSize: 58, lineHeight: 1.05, color: C.text, textAlign: "center", letterSpacing: "-0.02em" }}>
              ESTUDIAN<br />EL DINERO
            </div>
            <div style={{ marginTop: 60, display: "flex", flexDirection: "column", gap: 36, alignSelf: "stretch" }}>
              {labels.map((l, i) => {
                const p = useSpring(ts[i], theme.spring.snappy);
                return (
                  <div key={l} style={{ display: "flex", alignItems: "center", gap: 20, opacity: interpolate(p, [0, 0.4], [0, 1], clamp), transform: `translateX(${interpolate(p, [0, 1], [40, 0])}px)` }}>
                    <Check p={p} s={58} color={C.text} />
                    <div style={{ fontFamily: theme.fonts.displayBold, fontSize: 36, color: C.text }}>{l}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </Stage>
    </Scene>
  );
};

// 15 — ¿Cuánto ganas? → ¿Cuánto entiendes?
export const Pregunta: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const tGan = at(e, "cuanto");
  const tP2 = at(e, "pregunta", 1);
  const tEnt = at(e, "cuanto", 1);
  const tSis = at(e, "sistema");
  const g = useSpring(Math.min(tGan, 8), theme.spring.bouncy);
  const shrink = interpolate(frame, [tP2, tP2 + 14], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const strike = interpolate(frame, [tP2 - 6, tP2 + 2], [0, 1], { ...clamp, easing: theme.ease.out });
  const en = useSpring(tEnt, theme.spring.bouncy);
  return (
    <Scene d={e.d}>
      <Sfx at={Math.min(tGan, 8)} n="pop" v={0.7} />
      <Sfx at={tP2 - 6} n="whoosh" v={0.5} />
      <Sfx at={tEnt} n="hit" v={1} />
      <Stage>
        <Entrance delay={0} y={-20}>
          <Chip color={C.textDim}>La pregunta</Chip>
        </Entrance>
        <div style={{ marginTop: 60, position: "relative", opacity: interpolate(g, [0, 0.4], [0, 1], clamp) * interpolate(shrink, [0, 1], [1, 0.45]), transform: `scale(${interpolate(g, [0, 1], [0.7, 1]) * interpolate(shrink, [0, 1], [1, 0.62])}) translateY(${shrink * -30}px)` }}>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 108, color: C.text, letterSpacing: "-0.04em", whiteSpace: "nowrap" }}>¿CUÁNTO GANAS?</div>
          <div style={{ position: "absolute", left: -10, right: -10, top: "50%", height: 14, background: C.danger, borderRadius: 7, transformOrigin: "0 50%", transform: `scaleX(${strike}) rotate(-2deg)` }} />
        </div>
        <div style={{ marginTop: 40, opacity: interpolate(en, [0, 0.3], [0, 1], clamp), transform: `translateY(${interpolate(en, [0, 1], [80, 0])}px) scale(${interpolate(en, [0, 1], [0.6, 1])})`, textAlign: "center" }}>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 132, color: C.text, letterSpacing: "-0.04em", lineHeight: 1 }}>¿CUÁNTO</div>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 150, color: C.primary, letterSpacing: "-0.04em", lineHeight: 1.05, textShadow: `0 0 60px ${C.glow}, 0 0 130px ${C.primarySoft}` }}>ENTIENDES?</div>
        </div>
        <Entrance delay={tSis} y={24}>
          <div style={{ marginTop: 40, fontFamily: theme.fonts.mono, fontSize: 34, letterSpacing: "0.1em", color: C.textDim }}>DEL SISTEMA EN EL QUE VIVES</div>
        </Entrance>
      </Stage>
    </Scene>
  );
};

// 16 — Cierre MENTE404
export const Final: React.FC<P> = ({ e }) => {
  const frame = useCurrentFrame();
  const ts = [at(e, "despierta"), at(e, "cuestiona"), at(e, "comprende")];
  const open = useSpring(2, theme.spring.snappy);
  const logo = useSpring(4, theme.spring.bouncy);
  const b = useBreathe(24, 0.012);
  const words = ["DESPIERTA.", "CUESTIONA.", "COMPRENDE."];
  return (
    <Scene d={e.d} exit={14}>
      <Sfx at={2} n="hit" v={1} />
      <Sfx at={4} n="glitch" v={0.6} />
      {ts.map((t, i) => (
        <Sfx key={i} at={t} n="hit" v={0.55} />
      ))}
      <Stage style={{ transform: `scale(${b.s})` }}>
        <Eye width={420} open={open} glow={false} look={Math.sin(frame / 40) * 0.4} />
        <div style={{ marginTop: 50, opacity: interpolate(logo, [0, 0.3], [0, 1], clamp), transform: `scale(${interpolate(logo, [0, 1], [1.4, 1])})` }}>
          <GlitchText at={4} style={{ fontFamily: theme.fonts.display, fontSize: 160, letterSpacing: "-0.05em", lineHeight: 1, color: C.text, whiteSpace: "nowrap" }}>
            <>
              MENTE<span style={{ color: C.primary, textShadow: `0 0 60px ${C.glow}` }}>404</span>
            </>
          </GlitchText>
        </div>
        <div style={{ marginTop: 80, display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
          {words.map((w, i) => {
            const p = useSpring(ts[i], theme.spring.snappy);
            return (
              <div key={w} style={{ fontFamily: theme.fonts.display, fontSize: 92, letterSpacing: "0.02em", color: C.text, opacity: interpolate(p, [0, 0.4], [0, 1], clamp), transform: `translateY(${interpolate(p, [0, 1], [40, 0])}px) scale(${interpolate(p, [0, 1], [0.8, 1])})` }}>
                {w}
              </div>
            );
          })}
        </div>
      </Stage>
    </Scene>
  );
};
