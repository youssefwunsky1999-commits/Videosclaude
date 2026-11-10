import voz from "./voz.json";

export const FPS = 30;
const LEAD = 0.25; // s antes de la primera palabra
const COLA = 2.2; // s después de la última frase

export type Escena = {
  id: string;
  audio: string;
  from: number; // fotograma de inicio en el vídeo
  d: number; // duración de la escena (hasta la siguiente)
  voz: number; // fotogramas con voz
  words: string[];
  w: number[]; // fotograma (relativo a la escena) en que empieza cada palabra
};

const segs = voz.segmentos;
let t = LEAD;
const inicios = segs.map((s) => {
  const ini = t;
  t += s.dur + voz.hueco;
  return ini;
});

export const ESCENAS: Escena[] = segs.map((s, i) => {
  const from = Math.round(inicios[i] * FPS);
  const fin = i < segs.length - 1 ? Math.round(inicios[i + 1] * FPS) : Math.round((inicios[i] + s.dur + COLA) * FPS);
  return {
    id: s.escena,
    audio: s.audio,
    from,
    d: fin - from,
    voz: Math.round(s.dur * FPS),
    words: s.palabras.map((p) => p.w),
    w: s.palabras.map((p) => Math.round(p.t * FPS)),
  };
});

export const DURACION = ESCENAS[ESCENAS.length - 1].from + ESCENAS[ESCENAS.length - 1].d;

/** fotograma (relativo) de la primera palabra que empieza por `pref` (insensible a mayúsculas/acentos) */
const norm = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]/g, "");
export const at = (e: Escena, pref: string, nth = 0) => {
  const p = norm(pref);
  for (const exact of [true, false]) {
    let k = 0;
    for (let i = 0; i < e.words.length; i++) {
      const w = norm(e.words[i]);
      if (exact ? w === p : w.startsWith(p)) {
        if (k === nth) return e.w[i];
        k++;
      }
    }
  }
  throw new Error(`palabra «${pref}» no encontrada en ${e.id}`);
};
