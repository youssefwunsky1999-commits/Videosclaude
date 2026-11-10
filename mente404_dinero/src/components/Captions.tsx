import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Escena } from "../timeline";
import { clamp, theme } from "../theme";

type Page = { start: number; end: number; idx: number[] };

const paginar = (e: Escena): Page[] => {
  const pages: Page[] = [];
  let cur: number[] = [];
  const flush = (end: number) => {
    if (cur.length) pages.push({ start: e.w[cur[0]], end, idx: cur });
    cur = [];
  };
  e.words.forEach((w, i) => {
    const chars = cur.reduce((n, k) => n + e.words[k].length + 1, 0) + w.length;
    const gap = i > 0 ? e.w[i] - e.w[i - 1] : 0;
    if (cur.length && (cur.length >= 3 || chars > 17 || gap > 12)) flush(e.w[i]);
    cur.push(i);
  });
  flush(Math.min(e.d - 4, e.voz + 10));
  return pages;
};

/** Subtítulos sincronizados por palabra (2–3 palabras por página), dentro de la zona segura */
export const Captions: React.FC<{ e: Escena }> = ({ e }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pages = paginar(e);
  const page = pages.find((p) => frame >= p.start - 1 && frame < p.end);
  if (!page) return null;
  const pin = spring({ frame: frame - page.start + 1, fps, config: theme.spring.snappy });
  const out = interpolate(frame, [page.end - 4, page.end], [1, 0], clamp);
  return (
    <div
      style={{
        position: "absolute", left: 60, right: 60, top: theme.layout.captionY - 70,
        display: "flex", justifyContent: "center", flexWrap: "wrap", columnGap: 30,
        fontFamily: theme.fonts.display, fontSize: 76, letterSpacing: "-0.02em", textTransform: "uppercase",
        opacity: Math.min(interpolate(pin, [0, 0.5], [0, 1], clamp), out),
        transform: `translateY(${interpolate(pin, [0, 1], [24, 0])}px) scale(${interpolate(pin, [0, 1], [0.94, 1])})`,
      }}
    >
      {page.idx.map((k) => {
        const active = frame >= e.w[k];
        const pk = spring({ frame: frame - e.w[k], fps, config: theme.spring.snappy });
        return (
          <span
            key={k}
            style={{
              display: "inline-block",
              color: active ? theme.colors.text : "rgba(243,240,232,0.38)",
              transform: `scale(${active ? interpolate(pk, [0, 1], [1.12, 1]) : 1})`,
              textShadow: "0 4px 0 rgba(0,0,0,0.55), 0 0 40px rgba(0,0,0,0.8)",
              WebkitTextStroke: "2px rgba(0,0,0,0.35)",
            }}
          >
            {e.words[k]}
          </span>
        );
      })}
    </div>
  );
};
