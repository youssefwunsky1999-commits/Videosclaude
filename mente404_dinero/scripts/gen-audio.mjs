// Sintetiza la música de fondo y el kit de efectos como WAV de 16 bits -> public/sfx/.
// Determinista (PRNG con semilla), sin descargas.
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "public", "sfx");
mkdirSync(OUT, { recursive: true });
const SR = 44100;

let seed = 404;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;

function wav(name, L, R = L) {
  const n = L.length;
  const buf = Buffer.alloc(44 + n * 4);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * 4, 4); buf.write("WAVE", 8);
  buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34);
  buf.write("data", 36); buf.writeUInt32LE(n * 4, 40);
  let peak = 0;
  for (let i = 0; i < n; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  const g = peak > 0.98 ? 0.98 / peak : 1;
  for (let i = 0; i < n; i++) {
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[i] * g)) * 32767), 44 + i * 4);
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[i] * g)) * 32767), 46 + i * 4);
  }
  writeFileSync(join(OUT, name), buf);
  console.log(name, (n / SR).toFixed(2) + "s");
}
const arr = (s) => new Float32Array(Math.round(s * SR));

// One-pole low-pass, in place
function lp(x, cutoff) {
  const a = 1 - Math.exp((-2 * Math.PI * cutoff) / SR);
  let y = 0;
  for (let i = 0; i < x.length; i++) x[i] = y += a * (x[i] - y);
  return x;
}

// ---------- SFX ----------
{ // whoosh: filtered noise, swelling and sweeping
  const d = 0.55, x = arr(d); let y = 0;
  for (let i = 0; i < x.length; i++) {
    const t = i / x.length, env = Math.sin(Math.PI * Math.pow(t, 0.7)) ** 2;
    const a = 1 - Math.exp((-2 * Math.PI * (300 + 3500 * Math.sin(Math.PI * t))) / SR);
    y += a * (rnd() - y); x[i] = y * env * 0.9;
  }
  wav("whoosh.wav", x);
}
{ // hit: sub boom with pitch drop + click
  const d = 1.4, x = arr(d); let ph = 0;
  for (let i = 0; i < x.length; i++) {
    const t = i / SR, f = 38 + 90 * Math.exp(-t * 18);
    ph += (2 * Math.PI * f) / SR;
    x[i] = Math.sin(ph) * Math.exp(-t * 2.6) + (t < 0.01 ? rnd() * (1 - t / 0.01) * 0.5 : 0);
  }
  wav("hit.wav", x);
}
{ // tick
  const x = arr(0.06);
  for (let i = 0; i < x.length; i++) { const t = i / SR; x[i] = Math.sin(2 * Math.PI * 2400 * t) * Math.exp(-t * 120) * 0.6; }
  wav("tick.wav", x);
}
{ // pop: pitch drop sine
  const x = arr(0.18); let ph = 0;
  for (let i = 0; i < x.length; i++) { const t = i / SR; ph += (2 * Math.PI * (900 * Math.exp(-t * 25) + 180)) / SR; x[i] = Math.sin(ph) * Math.exp(-t * 28) * 0.8; }
  wav("pop.wav", x);
}
{ // riser: noise + rising sine, 1.6s
  const d = 1.6, x = arr(d); let ph = 0, y = 0;
  for (let i = 0; i < x.length; i++) {
    const t = i / x.length; ph += (2 * Math.PI * (120 + 900 * t * t)) / SR;
    y += 0.08 * (rnd() - y);
    x[i] = (Math.sin(ph) * 0.35 + y * 1.4) * t * t * (t > 0.97 ? (1 - t) / 0.03 : 1);
  }
  wav("riser.wav", x);
}
{ // glitch: chopped digital noise bursts
  const x = arr(0.35);
  for (let i = 0; i < x.length; i++) {
    const t = i / SR, gate = Math.floor(t * 60) % 3 !== 1 ? 1 : 0;
    const sq = Math.sign(Math.sin(2 * Math.PI * (200 + 1800 * ((Math.floor(t * 60) * 7) % 5) / 5) * t));
    x[i] = gate * (sq * 0.25 + rnd() * 0.25) * Math.exp(-t * 5);
  }
  wav("glitch.wav", x);
}
{ // ding: coin-like metallic partials
  const d = 1.3, x = arr(d), parts = [[2093, 1], [3136, 0.5], [5274, 0.3], [6645, 0.15]];
  for (let i = 0; i < x.length; i++) {
    const t = i / SR; let s = 0;
    for (const [f, a] of parts) s += Math.sin(2 * Math.PI * f * t) * a * Math.exp(-t * (3 + f / 1500));
    x[i] = s * 0.5;
  }
  wav("ding.wav", x);
}
{ // down: falling tone (pérdida de valor)
  const d = 0.9, x = arr(d); let ph = 0;
  for (let i = 0; i < x.length; i++) { const t = i / SR; ph += (2 * Math.PI * (520 * Math.exp(-t * 2.2) + 60)) / SR; x[i] = (Math.sin(ph) + 0.3 * Math.sin(ph * 2.01)) * Math.exp(-t * 2.5) * 0.5; }
  wav("down.wav", x);
}

// ---------- Música: pulso oscuro 96 BPM, La menor ----------
{
  const BPM = 96, beat = 60 / BPM, d = 100, L = arr(d), R = arr(d);
  const chords = [[110, 130.81, 164.81], [87.31, 110, 130.81], [98, 123.47, 146.83], [82.41, 103.83, 123.47]]; // Am F G E
  const bar = beat * 4;
  for (let i = 0; i < L.length; i++) {
    const t = i / SR;
    const ci = Math.floor(t / (bar * 2)) % chords.length;
    const tc = (t % (bar * 2)) / (bar * 2);
    const xf = Math.min(1, tc * 12, (1 - tc) * 12); // micro crossfade between chords
    let padL = 0, padR = 0;
    for (const f of chords[ci]) {
      padL += Math.sin(2 * Math.PI * f * 2 * t) + Math.sin(2 * Math.PI * f * 2.006 * t) * 0.7;
      padR += Math.sin(2 * Math.PI * f * 2 * 0.996 * t) + Math.sin(2 * Math.PI * f * 2.012 * t) * 0.7;
    }
    const lfo = 0.75 + 0.25 * Math.sin(2 * Math.PI * t / (bar * 2));
    // kick on every beat (half-time feel: louder on 1 and 3)
    const tb = t % beat, bi = Math.floor(t / beat) % 4;
    const kick = Math.sin(2 * Math.PI * (45 + 80 * Math.exp(-tb * 30)) * tb) * Math.exp(-tb * 7) * (bi % 2 === 0 ? 1 : 0.45);
    // sub bass following chord root, sidechained by the kick
    const duck = 1 - 0.7 * Math.exp(-tb * 8);
    const bass = Math.sin(2 * Math.PI * chords[ci][0] / 2 * t) * duck;
    // soft hats on off-beats
    const th = (t + beat / 2) % beat, hat = rnd() * Math.exp(-th * 90) * 0.12;
    const fadeIn = Math.min(1, t / 1.5), fadeOut = Math.min(1, (d - t) / 3);
    const m = fadeIn * fadeOut;
    L[i] = (padL * 0.035 * lfo * xf * duck + kick * 0.55 + bass * 0.22 + hat) * m;
    R[i] = (padR * 0.035 * lfo * xf * duck + kick * 0.55 + bass * 0.22 + hat * 0.8) * m;
  }
  lp(L, 6000); lp(R, 6000);
  wav("musica.wav", L, R);
}
