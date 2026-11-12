"""Paso 3: genera el proyecto HyperFrames (1920x1080) en hf/: una composición por escena, subtítulos karaoke y mezcla.

    python3 construir.py   -> hf/index.html, hf/compositions/*.html, hf/assets/mezcla.wav

Fondo común de neón retro (cielo de atardecer, sol a franjas, palmeras, carretera de rejilla) hecho solo con CSS, con
la paleta de cada capítulo; encima, dibujo a la izquierda y tarjetas a la derecha (o cifra, barras, línea de tiempo,
cita, mapa, precios). Cada elemento entra cuando la voz dice su palabra. La fuente de cada dato va abajo."""
import html
import json
import os
import re
import shutil

import dibujos as D
from guion import CAPITULOS, SEGMENTOS, TITULO

AQUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(AQUI, "build")
HF = os.path.join(AQUI, "hf")
W, H = 1920, 1080

PALETAS = {  # cielo arriba, cielo medio, horizonte, acento
    "intro": ("#12062a", "#5b1a7a", "#ff5e7e", "#ff2e88"),
    "c1": ("#0a0a2e", "#3a1a7a", "#ff2e88", "#00e5ff"),
    "c2": ("#1a0418", "#6a0f3a", "#ff8c42", "#ff2e88"),
    "c3": ("#04142e", "#0f4a6a", "#ff8c42", "#ffd166"),
    "c4": ("#1a0b2e", "#7b2ff7", "#ff2e88", "#ffd166"),
    "c5": ("#07021a", "#1f2a7a", "#00b3ff", "#00e5ff"),
    "c6": ("#1a0b2e", "#6a1a5a", "#ffd166", "#ffd166"),
    "c7": ("#1a0410", "#5a0a2a", "#ff2e4d", "#ff8c42"),
    "c8": ("#05121e", "#0f3a5a", "#00e5c0", "#00e5ff"),
    "cierre": ("#12062a", "#5b1a7a", "#ffd166", "#ff2e88"),
}
NUM_CAP = {c["id"]: i for i, c in enumerate(CAPITULOS)}

PALMERA = """<svg viewBox="0 0 300 900" class="palm {cls}" preserveAspectRatio="xMidYMax meet"><g fill="#0b0414">
<path d="M150 900 C 140 700, 170 520, 150 300 L 162 300 C 184 520, 156 700, 168 900 Z"/>
<path d="M156 300 C 90 240, 30 260, 0 320 C 50 270, 100 270, 156 312 Z"/>
<path d="M156 300 C 230 230, 280 250, 300 310 C 250 265, 210 268, 156 314 Z"/>
<path d="M156 298 C 110 200, 60 170, 20 180 C 80 200, 120 240, 150 310 Z"/>
<path d="M156 298 C 200 190, 250 170, 290 190 C 230 205, 190 245, 162 312 Z"/>
<path d="M156 300 C 150 220, 160 160, 190 120 C 175 180, 168 240, 162 306 Z"/>
<path d="M156 300 C 120 300, 80 340, 60 400 C 100 350, 130 330, 156 316 Z"/>
<path d="M156 300 C 200 305, 240 345, 255 405 C 220 355, 190 335, 158 318 Z"/>
</g></svg>"""

CSS = """
#root { position: absolute; inset: 0; overflow: hidden; font-family: Inter; color: #fff; }
.cielo { position: absolute; inset: 0; background: linear-gradient(180deg, var(--c0) 0%, var(--c1) 45%, var(--c2) 66%, #12062a 66.2%, #07020f 100%); }
.estrellas { position: absolute; left: 0; right: 0; top: 0; height: 600px; opacity: .55;
  background-image: radial-gradient(2px 2px at 10% 20%, #fff 50%, transparent 51%), radial-gradient(2px 2px at 30% 8%, #fff 50%, transparent 51%),
  radial-gradient(1.5px 1.5px at 55% 15%, #fff 50%, transparent 51%), radial-gradient(2px 2px at 75% 25%, #fff 50%, transparent 51%),
  radial-gradient(1.5px 1.5px at 90% 10%, #fff 50%, transparent 51%), radial-gradient(1.5px 1.5px at 42% 30%, #fff 50%, transparent 51%),
  radial-gradient(2px 2px at 65% 5%, #fff 50%, transparent 51%), radial-gradient(1.5px 1.5px at 20% 35%, #fff 50%, transparent 51%); }
.sol { position: absolute; left: 660px; top: 120px; width: 600px; height: 600px; border-radius: 50%;
  background: linear-gradient(180deg, #ffd166 0%, #ff8c42 45%, #ff2e88 100%);
  -webkit-mask: linear-gradient(180deg, #000 0 52%, transparent 52%) , repeating-linear-gradient(180deg, #000 0 30px, transparent 30px 42px);
  -webkit-mask-composite: source-over; mask: linear-gradient(180deg, #000 0 52%, transparent 52%), repeating-linear-gradient(180deg, #000 0 30px, transparent 30px 42px);
  box-shadow: 0 0 140px rgba(255,46,136,.55); }
.rejilla-cont { position: absolute; inset: 0; perspective: 380px; perspective-origin: 50% 712px; overflow: hidden; }
.rejilla { position: absolute; left: -1400px; right: -1400px; top: 712px; height: 1400px; transform-origin: 50% 0; transform: rotateX(74deg);
  background-image: linear-gradient(var(--grid) 3px, transparent 3px), linear-gradient(90deg, var(--grid) 3px, transparent 3px); background-size: 110px 110px; }
.horiz { position: absolute; left: 0; right: 0; top: 708px; height: 6px; background: var(--c2); box-shadow: 0 0 30px var(--c2); }
.palm { position: absolute; bottom: 0; height: 900px; width: 300px; }
.palm.izq { left: -90px; } .palm.der { right: -100px; height: 760px; }
.velo { position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 45%, rgba(8,2,20,.25) 30%, rgba(8,2,20,.62) 100%); }
.bandasub { position: absolute; left: 0; right: 0; top: 820px; bottom: 0; background: linear-gradient(180deg, rgba(5,1,14,0) 0%, rgba(5,1,14,.78) 30%, rgba(5,1,14,.9) 100%); }
.cab { position: absolute; left: 56px; top: 40px; display: flex; align-items: center; gap: 22px; }
.logo { font-family: "League Gothic"; font-size: 64px; line-height: 1; letter-spacing: 3px; color: #fff; text-shadow: 0 0 14px #ff2e88, 0 0 34px #ff2e88, 0 4px 0 #7b2ff7; }
.logo b { font-weight: 400; color: #ffd166; text-shadow: 0 0 14px #ff8c42, 0 0 34px #ff8c42, 0 4px 0 #7b2ff7; }
.pillcap { font-family: "League Gothic"; font-size: 44px; letter-spacing: 2px; color: #12062a; background: var(--ac); padding: 2px 26px; border-radius: 10px; box-shadow: 0 0 24px var(--ac); }
.prog { position: absolute; right: 56px; top: 62px; display: flex; gap: 8px; }
.prog i { display: block; width: 46px; height: 10px; border-radius: 5px; background: rgba(255,255,255,.22); }
.prog i.on { background: var(--ac); box-shadow: 0 0 12px var(--ac); } .prog i.hecho { background: rgba(255,255,255,.6); }
.fuente { position: absolute; left: 56px; right: 56px; top: 1036px; font-weight: 700; font-size: 21px; color: rgba(255,255,255,.62); }
.panel { position: absolute; left: 110px; top: 150px; width: 700px; height: 650px; display: flex; align-items: center; justify-content: center; }
.dib { width: 660px; height: 616px; overflow: visible; filter: drop-shadow(0 18px 0 rgba(0,0,0,.28)); }
.pila { position: absolute; left: 880px; right: 110px; top: 150px; height: 650px; display: flex; flex-direction: column; justify-content: center; gap: 26px; }
.pila.sola { left: 260px; right: 260px; }
.tj { position: relative; background: rgba(10,4,24,.82); border: 4px solid var(--ac); border-radius: 18px; padding: 16px 30px;
  box-shadow: 0 0 22px color-mix(in srgb, var(--ac) 55%, transparent), inset 0 0 18px color-mix(in srgb, var(--ac) 25%, transparent);
  font-weight: 900; font-size: 46px; line-height: 1.1; }
.tj.g { background: #ff2e88; border-color: #ff2e88; font-family: "League Gothic"; font-weight: 400; font-size: 92px; letter-spacing: 2px; line-height: 1;
  text-align: center; box-shadow: 0 0 36px rgba(255,46,136,.7), 0 12px 0 #7b2ff7; padding: 10px 30px; }
.tj.x i { position: absolute; left: 22px; right: 22px; top: 50%; height: 9px; margin-top: -4px; background: #ff3b4d; border-radius: 5px; transform-origin: 0 50%; box-shadow: 0 0 14px #ff3b4d; }
.tj.x { color: rgba(255,255,255,.75); border-color: #ff3b4d; }
.tj.r { border-color: #ff8c42; border-style: dashed; background: rgba(40,10,4,.85); padding-right: 210px; }
.tj.r b.sello { position: absolute; right: 18px; top: 50%; margin-top: -30px; font-family: "League Gothic"; font-weight: 400; font-size: 46px; line-height: 52px;
  color: #ff8c42; border: 5px solid #ff8c42; border-radius: 10px; padding: 0 14px; transform: rotate(-8deg); letter-spacing: 3px; }
.tj.ok { border-color: #3ccf6e; background: rgba(4,30,14,.85); padding-left: 100px; }
.tj.ok b.tick { position: absolute; left: 22px; top: 50%; margin-top: -30px; width: 60px; height: 60px; border-radius: 50%; background: #3ccf6e; color: #fff;
  text-align: center; line-height: 60px; font-size: 40px; }
.cifra { position: absolute; left: 0; right: 0; top: 230px; text-align: center; }
.cifra .n { font-family: "League Gothic"; font-size: 300px; line-height: 1; color: #ffd166; text-shadow: 0 0 30px #ff8c42, 0 0 80px #ff8c42, 0 10px 0 #7b2ff7; }
.cifra .pie { margin-top: 18px; font-weight: 900; font-size: 44px; text-shadow: 0 3px 12px rgba(0,0,0,.8); }
.btit { position: absolute; left: 0; right: 0; top: 150px; text-align: center; font-family: "League Gothic"; font-size: 70px; letter-spacing: 3px;
  text-shadow: 0 0 20px var(--ac); }
.barras { position: absolute; left: 120px; right: 160px; top: 290px; display: flex; flex-direction: column; gap: 34px; }
.bar { display: grid; grid-template-columns: 640px 1fr; align-items: center; gap: 26px; }
.bar .et { font-weight: 900; font-size: 36px; text-align: right; line-height: 1.1; }
.bar .tr { position: relative; height: 84px; }
.bar .rel { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 14px; background: linear-gradient(90deg, #ff2e88, #ffd166); transform-origin: 0 50%;
  box-shadow: 0 0 22px rgba(255,46,136,.6); }
.bar.x .rel { background: linear-gradient(90deg, #5b6075, #9aa3b5); box-shadow: none; }
.bar .v { position: absolute; top: 50%; margin-top: -40px; font-family: "League Gothic"; font-size: 80px; line-height: 80px; white-space: nowrap; }
.nota { position: absolute; left: 0; right: 0; top: 700px; text-align: center; }
.nota span { display: inline-block; font-weight: 900; font-size: 40px; background: rgba(10,4,24,.85); border: 4px solid var(--ac); border-radius: 50px; padding: 10px 34px; }
.linea { position: absolute; left: 110px; right: 110px; top: 300px; height: 500px; }
.linea .eje { position: absolute; left: 40px; right: 40px; top: 190px; height: 10px; border-radius: 5px; background: var(--ac); box-shadow: 0 0 20px var(--ac); transform-origin: 0 50%; }
.hito { position: absolute; top: 0; width: 540px; margin-left: -270px; text-align: center; }
.hito .f { display: inline-block; font-family: "League Gothic"; font-size: 84px; letter-spacing: 2px; background: #12062a; border: 4px solid var(--ac); border-radius: 14px; padding: 2px 22px; }
.hito .pt { display: block; margin: 30px auto 34px; width: 54px; height: 54px; border-radius: 50%; background: #ffd166; box-shadow: 0 0 24px #ffd166; }
.hito .d { position: relative; display: inline-block; font-weight: 900; font-size: 50px; line-height: 1.15; background: rgba(10,4,24,.85); border-radius: 16px; padding: 14px 22px; }
.hito.x .d { color: rgba(255,255,255,.7); } .hito.x .d i { position: absolute; left: 14px; right: 14px; top: 50%; height: 8px; margin-top: -4px; background: #ff3b4d; border-radius: 4px; transform-origin: 0 50%; }
.hito.x .pt { background: #ff3b4d; box-shadow: 0 0 24px #ff3b4d; } .hito.ok .pt { background: #3ccf6e; box-shadow: 0 0 30px #3ccf6e; }
.hito.ok .d { border: 4px solid #3ccf6e; }
.cita { position: absolute; left: 230px; right: 230px; top: 210px; background: #fbf7ee; color: #1a1d33; border-radius: 30px; padding: 60px 80px 50px; box-shadow: 0 18px 0 rgba(0,0,0,.3); }
.cita .q { position: absolute; left: 34px; top: -70px; font-family: "League Gothic"; font-size: 260px; line-height: 1; color: var(--ac); text-shadow: 0 6px 0 rgba(0,0,0,.25); }
.cita .tx { font-weight: 900; font-size: 58px; line-height: 1.18; }
.cita .au { margin-top: 30px; font-weight: 800; font-size: 32px; color: #6b6f80; }
.mapa { position: absolute; left: 90px; top: 140px; width: 860px; height: 669px; filter: drop-shadow(0 16px 0 rgba(0,0,0,.3)); }
.etq { position: absolute; font-family: "League Gothic"; font-size: 46px; letter-spacing: 2px; background: #12062a; border: 3px solid #ffd166; color: #ffd166;
  border-radius: 10px; padding: 0 14px; white-space: nowrap; transform: translate(-50%, -50%); }
.etq.vc { border-color: #ff2e88; color: #fff; background: #ff2e88; font-size: 64px; box-shadow: 0 0 24px #ff2e88; }
.etq.le { border: none; background: none; color: rgba(255,255,255,.9); font-size: 90px; letter-spacing: 10px; text-shadow: 0 4px 0 rgba(0,0,0,.4); }
.lista { position: absolute; left: 1010px; right: 110px; top: 170px; height: 620px; display: flex; flex-direction: column; justify-content: center; gap: 18px; }
.lista .tj { font-size: 42px; padding: 12px 26px; }
.precios { position: absolute; left: 0; right: 0; top: 200px; display: flex; justify-content: center; gap: 90px; }
.precio { width: 560px; height: 520px; border-radius: 30px; background: rgba(10,4,24,.85); border: 6px solid var(--ac); text-align: center; padding-top: 50px;
  box-shadow: 0 0 40px color-mix(in srgb, var(--ac) 50%, transparent); }
.precio.u { border-color: #ff2e88; box-shadow: 0 0 40px rgba(255,46,136,.6); }
.precio .ed { font-family: "League Gothic"; font-size: 84px; letter-spacing: 4px; }
.precio .p { font-family: "League Gothic"; font-size: 210px; line-height: 1.05; color: #ffd166; text-shadow: 0 0 30px #ff8c42, 0 8px 0 #7b2ff7; }
.precio .pl { font-weight: 800; font-size: 32px; color: rgba(255,255,255,.75); }
.port { position: absolute; left: 0; right: 0; top: 230px; text-align: center; }
.port .k { font-family: "League Gothic"; font-size: 90px; letter-spacing: 16px; color: var(--ac); text-shadow: 0 0 24px var(--ac); }
.port .num { font-family: "League Gothic"; font-size: 330px; line-height: .9; color: #fff; text-shadow: 0 0 30px #ff2e88, 0 0 80px #ff2e88, 0 12px 0 #7b2ff7; }
.port .tt { display: inline-block; margin-top: 10px; font-family: "League Gothic"; font-size: 110px; letter-spacing: 4px; color: #12062a; background: #ffd166;
  padding: 4px 46px; border-radius: 18px; box-shadow: 0 0 40px rgba(255,209,102,.6), 0 12px 0 #ff2e88; }
.gtit { position: absolute; left: 0; right: 0; top: 150px; text-align: center; }
.gtit .lg { font-family: "League Gothic"; font-size: 330px; line-height: .9; letter-spacing: 8px; color: #fff; text-shadow: 0 0 26px #ff2e88, 0 0 70px #ff2e88, 0 12px 0 #7b2ff7; }
.gtit .lg b { font-weight: 400; color: #ffd166; text-shadow: 0 0 26px #ff8c42, 0 0 70px #ff8c42, 0 12px 0 #7b2ff7; }
.gtit .fe { font-family: "League Gothic"; font-size: 90px; letter-spacing: 12px; color: #00e5ff; text-shadow: 0 0 20px #00b3ff, 0 0 50px #00b3ff; }
.sellos { position: absolute; left: 120px; right: 120px; top: 640px; display: flex; justify-content: space-between; }
.sellos span { font-family: "League Gothic"; font-size: 76px; letter-spacing: 3px; background: #ff2e88; padding: 4px 30px; border-radius: 16px; box-shadow: 0 0 30px rgba(255,46,136,.7), 0 10px 0 #7b2ff7; }
.chips { position: absolute; left: 180px; right: 180px; top: 260px; display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; }
.chips .tj { font-size: 60px; padding: 18px 42px; }
.chips .tj.r { padding-right: 230px; } .chips .tj.ok { padding-left: 110px; }
.chips.nombres .tj { font-family: "League Gothic"; font-weight: 400; font-size: 84px; letter-spacing: 3px; }
.chips-tit { position: absolute; left: 0; right: 0; top: 150px; text-align: center; font-family: "League Gothic"; font-size: 70px; letter-spacing: 3px; text-shadow: 0 0 20px var(--ac); }
.subs { position: absolute; left: 0; right: 0; top: 260px; display: flex; justify-content: center; gap: 80px; }
.btn { font-family: "League Gothic"; font-size: 120px; letter-spacing: 4px; padding: 20px 70px; border-radius: 30px; }
.btn.lk { background: #fff; color: #12062a; box-shadow: 0 14px 0 #7b2ff7; }
.btn.su { background: #ff3b4d; color: #fff; box-shadow: 0 0 50px rgba(255,59,77,.7), 0 14px 0 #7a0a1a; }
.mano { position: absolute; left: 1220px; top: 420px; width: 150px; }
"""


def t_palabra(e, clave):
    palabra, n = (clave.split("#") + ["1"])[:2]
    hits = [w for w in e["palabras"] if w["w"].lower() == palabra.lower()]
    if len(hits) < int(n):
        raise SystemExit(f"[{e['escena']}] la voz no dice «{palabra}» ({n}.ª vez)")
    return max(0.15, round(hits[int(n) - 1]["t"] - e["ini"] - 0.1, 3))


def esc(s):
    return html.escape(s)


def tarjeta(i, it):
    k = it.get("k", "")
    extra = {"x": "<i></i>", "r": '<b class="sello">RUMOR</b>', "ok": '<b class="tick">✓</b>'}.get(k, "")
    return f'<div id="{i}" class="tj {k}">{esc(it["t"])}{extra}</div>'


def entra_tarjeta(i, it, t, k, tws, desde=900):
    if it.get("k") == "g":
        tws.append(f'tl.fromTo("#{i}", {{ scale: 2.4, opacity: 0, rotation: {-6 if k % 2 else 6} }}, {{ scale: 1, opacity: 1, rotation: {-1.5 if k % 2 else 1.5}, duration: 0.22, ease: "power4.in" }}, {t});')
    else:
        tws.append(f'tl.fromTo("#{i}", {{ x: {desde}, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.32, ease: "power3.out" }}, {t});')
    if it.get("k") == "x":
        tws.append(f'tl.fromTo("#{i} i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power2.out" }}, {t + 0.45:.3f});')
    if it.get("k") == "r":
        tws.append(f'tl.fromTo("#{i} .sello", {{ scale: 2.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "power4.in" }}, {t + 0.3:.3f});')


def anim_dibujo(dib, p, D_, t0, tws):
    """Pequeñas animaciones propias de cada dibujo (además de la entrada y el balanceo)."""
    a = {
        "calendario": [f'tl.to("#{p}-circ", {{ strokeDashoffset: 0, duration: 0.7, ease: "power2.inOut" }}, {t0 + 0.3});'],
        "pc": [f'tl.fromTo("#{p}-x", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)" }}, {t0 + 0.2});'],
        "regla": [f'tl.fromTo("#{p}-q", {{ scale: 0 }}, {{ scale: 1, duration: 0.4, ease: "back.out(2.5)" }}, {t0 + 0.2});',
                  f'tl.to("#{p}-q", {{ rotation: 8, duration: 0.6, yoyo: true, repeat: {max(1, int(D_ / 0.6) - 2)}, ease: "sine.inOut" }}, {t0 + 0.6});'],
        "movil": [f'tl.fromTo("#{p}-h{i}", {{ y: 40, opacity: 0 }}, {{ y: -30, opacity: 1, duration: 0.8, ease: "power2.out" }}, {t0 + 0.4 + i * 0.5});' for i in (1, 2, 3)],
        "cartel": [f'tl.fromTo("#{p}-sign", {{ y: -260 }}, {{ y: 0, duration: 1.4, ease: "power2.out" }}, {t0});',
                   f'tl.fromTo("#{p}-heli", {{ x: 0, y: 0 }}, {{ x: -60, y: 20, duration: {D_}, ease: "none" }}, 0);',
                   f'tl.fromTo("#{p}-sign text", {{ opacity: 0.4 }}, {{ opacity: 1, duration: 0.12, repeat: 6, yoyo: true }}, {t0 + 1.4});'],
        "tele": [f'tl.fromTo("#{p}-barra", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {D_}, ease: "none" }}, 0);'],
        "musica": [f'tl.fromTo("#{p}-disco", {{ rotation: 0 }}, {{ rotation: {int(D_ * 120)}, duration: {D_}, ease: "none" }}, 0);',
                   f'tl.fromTo("#{p}-n1", {{ y: 0 }}, {{ y: -24, duration: 0.5, yoyo: true, repeat: {max(1, int(D_ / 0.5) - 1)}, ease: "sine.inOut" }}, 0);',
                   f'tl.fromTo("#{p}-n2", {{ y: 0 }}, {{ y: -18, duration: 0.6, yoyo: true, repeat: {max(1, int(D_ / 0.6) - 1)}, ease: "sine.inOut" }}, 0.2);'],
        "coche": [f'tl.fromTo("#{p}-car", {{ x: -700 }}, {{ x: 0, duration: 0.8, ease: "power3.out" }}, {t0});',
                  f'tl.fromTo("#{p}-yate", {{ x: 0 }}, {{ x: 30, duration: 1.6, yoyo: true, repeat: {max(1, int(D_ / 1.6) - 1)}, ease: "sine.inOut" }}, 0);'],
        "regalo": [f'tl.fromTo("#{p}-lazo", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.5, ease: "back.out(3)" }}, {t0 + 0.3});'],
        "caja": [f'tl.fromTo("#{p}-disco", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2)" }}, {t0 + 0.3});',
                 f'tl.fromTo("#{p}-cod", {{ y: 200, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power3.out" }}, {t0 + 1.0});'],
        "grafica": [f'tl.fromTo("#{p}-b{i}", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.4, ease: "power3.out" }}, {t0 + 0.1 + i * 0.12});' for i in range(5)]
                   + [f'tl.to("#{p}-fl", {{ strokeDashoffset: 0, duration: 0.9, ease: "power2.inOut" }}, {t0 + 0.6});'],
        "check": [f'tl.fromTo("#{p}-ok", {{ scale: 0, rotation: -20 }}, {{ scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2.5)" }}, {t0 + 0.1});'],
        "online": [f'tl.fromTo("#{p}-q", {{ scale: 0 }}, {{ scale: 1, duration: 0.4, ease: "back.out(2.5)" }}, {t0 + 0.4});']
                  + [f'tl.fromTo("#{p}-u{i}", {{ scale: 0 }}, {{ scale: 1, duration: 0.3, ease: "back.out(2.5)" }}, {t0 + 0.1 + i * 0.15});' for i in range(4)],
        "fps": [f'tl.fromTo("#{p}-aguja", {{ rotation: -90 }}, {{ rotation: 0, duration: 1.0, ease: "elastic.out(1, 0.5)" }}, {t0 + 0.3});'],
        "lupa": [f'tl.fromTo("#{p}-lupa", {{ x: -180 }}, {{ x: 40, duration: 2.2, yoyo: true, repeat: {max(1, int(D_ / 2.2) - 1)}, ease: "sine.inOut" }}, 0);'],
        "descarga": [f'(() => {{ const o = {{ v: 0 }}, el = document.getElementById("{p}-pct"); tl.fromTo("#{p}-prog", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {max(1, D_ - 1)}, ease: "power1.inOut" }}, 0.3); tl.fromTo(o, {{ v: 0 }}, {{ v: 100, duration: {max(1, D_ - 1)}, ease: "power1.inOut", onUpdate: () => {{ el.textContent = Math.round(o.v) + " %"; }} }}, 0.3); }})();'],
        "reloj": [f'tl.fromTo("#{p}-min", {{ rotation: -300 }}, {{ rotation: 0, duration: 1.6, ease: "power3.out" }}, {t0});',
                  f'tl.fromTo("#{p}-hor", {{ rotation: -25 }}, {{ rotation: 0, duration: 1.6, ease: "power3.out" }}, {t0});'],
        "poster": [f'tl.fromTo("#{p}-reg", {{ scale: 0 }}, {{ scale: 1, duration: 0.4, ease: "back.out(2.5)" }}, {t0 + 0.6});'],
        "despidos": [f'tl.fromTo("#{p}-sobre", {{ y: -300, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "bounce.out" }}, {t0 + 0.4});'],
        "consolas": [f'tl.fromTo("#{p}-c1", {{ y: 400, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.45, ease: "back.out(1.6)" }}, {t0});',
                     f'tl.fromTo("#{p}-c2", {{ y: 400, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.45, ease: "back.out(1.6)" }}, {t0 + 0.25});',
                     f'tl.fromTo("#{p}-mando", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, {t0 + 0.6});'],
    }.get(dib, [])
    tws.extend(a)


def cuerpo_escena(e, seg):
    """HTML + tweens del contenido de una escena según su tipo."""
    p, tipo, its = seg["escena"], seg["tipo"], seg.get("items", [])
    Dd = e["dur"]
    h, tws = [], []
    if tipo == "portada":
        cap = next(c for c in CAPITULOS if c["id"] == seg["cap"])
        h.append(f'<div class="port"><div id="{p}-k" class="k">CAPÍTULO</div><div id="{p}-n" class="num">{seg["num"]}</div>'
                 f'<div id="{p}-t" class="tt">{esc(cap["titulo"])}</div></div>')
        tws += [f'tl.fromTo("#{p}-k", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power3.out" }}, 0.05);',
                f'tl.fromTo("#{p}-n", {{ scale: 3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "power4.in" }}, 0.2);',
                f'tl.fromTo("#{p}-t", {{ scaleX: 0, opacity: 0 }}, {{ scaleX: 1, opacity: 1, duration: 0.4, ease: "back.out(1.8)" }}, 0.75);']
    elif tipo == "titulo":
        h.append(f'<div class="gtit"><div id="{p}-lg" class="lg">GTA <b>VI</b></div><div id="{p}-fe" class="fe">19 · 11 · 2026</div></div>')
        h.append('<div class="sellos">' + "".join(f'<span id="{p}-s{k}">{esc(it["t"])}</span>' for k, it in enumerate(its)) + '</div>')
        tws += [f'tl.fromTo("#{p}-lg", {{ scale: 1.25, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "power3.out" }}, 0);',
                f'tl.fromTo("#{p}-fe", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power3.out" }}, 0.25);']
        for k, it in enumerate(its):
            tws.append(f'tl.fromTo("#{p}-s{k}", {{ scale: 2.6, opacity: 0, rotation: {-10 if k % 2 else 10} }}, {{ scale: 1, opacity: 1, rotation: {-3 if k % 2 else 3}, duration: 0.2, ease: "power4.in" }}, {t_palabra(e, it["en"])});')
    elif tipo == "indice":
        nombres = seg["escena"] == "c4f"
        if nombres:
            h.append('<div class="chips-tit">PERSONAJES SECUNDARIOS</div>')
        h.append(f'<div class="chips{" nombres" if nombres else ""}">' + "".join(tarjeta(f"{p}-i{k}", it) for k, it in enumerate(its)) + '</div>')
        for k, it in enumerate(its):
            tws.append(f'tl.fromTo("#{p}-i{k}", {{ scale: 0.3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.4)" }}, {t_palabra(e, it["en"])});')
            if it.get("k") == "r":
                tws.append(f'tl.fromTo("#{p}-i{k} .sello", {{ scale: 2.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "power4.in" }}, {t_palabra(e, it["en"]) + 0.3:.3f});')
    elif tipo == "tarjetas":
        dib = seg.get("dib")
        if dib:
            h.append(f'<div class="panel" id="{p}-panel">{D.DIBUJOS[dib](p)}</div>')
            tws.append(f'tl.fromTo("#{p}-panel", {{ x: -500, opacity: 0, rotation: -6 }}, {{ x: 0, opacity: 1, rotation: 0, duration: 0.5, ease: "back.out(1.4)" }}, 0.02);')
            tws.append(f'tl.fromTo("#{p}-dib", {{ y: 0 }}, {{ y: -12, duration: 1.1, yoyo: true, repeat: {max(1, int(Dd / 1.1) - 1)}, ease: "sine.inOut" }}, 0.5);')
            anim_dibujo(dib, p, Dd, 0.3, tws)
        h.append(f'<div class="pila{"" if dib else " sola"}">' + "".join(tarjeta(f"{p}-t{k}", it) for k, it in enumerate(its)) + '</div>')
        for k, it in enumerate(its):
            entra_tarjeta(f"{p}-t{k}", it, t_palabra(e, it["en"]), k, tws)
    elif tipo == "cifra":
        it = its[0]
        h.append(f'<div class="cifra"><div id="{p}-n" class="n">0</div><div id="{p}-pie" class="pie">{esc(it["pie"])}</div></div>')
        t = t_palabra(e, it["en"])
        suf = json.dumps(it.get("suf", ""))
        tws += [f'tl.fromTo("#{p}-n", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }}, {t});',
                f'(() => {{ const o = {{ v: 0 }}, el = document.getElementById("{p}-n"); tl.fromTo(o, {{ v: 0 }}, {{ v: {it["n"]}, duration: 1.6, ease: "power3.out", onUpdate: () => {{ el.textContent = Math.round(o.v).toLocaleString("es-ES") + {suf}; }} }}, {t}); }})();',
                f'tl.fromTo("#{p}-pie", {{ y: 50, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power3.out" }}, {t + 0.5:.3f});']
    elif tipo == "barras":
        mx = max(it["n"] for it in its)
        h.append(f'<div class="btit">{esc(seg["titulo"])}</div><div class="barras">')
        for k, it in enumerate(its):
            pct = 0.86 * it["n"] / mx
            h.append(f'<div class="bar {it.get("k", "")}"><div class="et">{esc(it["t"])}</div><div class="tr">'
                     f'<div id="{p}-r{k}" class="rel" style="width:{pct * 100:.1f}%"></div>'
                     f'<div id="{p}-v{k}" class="v" style="left:calc({pct * 100:.1f}% + 20px)">0</div></div></div>')
        h.append('</div>')
        if seg.get("nota"):
            h.append(f'<div class="nota" id="{p}-nota"><span>{esc(seg["nota"]["t"])}</span></div>')
            tws.append(f'tl.fromTo("#{p}-nota", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power3.out" }}, {t_palabra(e, seg["nota"]["en"])});')
        for k, it in enumerate(its):
            t = t_palabra(e, it["en"]) + (0.25 * k if its[0]["en"] == it["en"] else 0)
            dec = 1 if it["n"] != int(it["n"]) else 0
            suf = json.dumps(it.get("suf", ""))
            tws += [f'tl.fromTo("#{p}-r{k}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.9, ease: "power3.out" }}, {t:.3f});',
                    f'(() => {{ const o = {{ v: 0 }}, el = document.getElementById("{p}-v{k}"); tl.fromTo(o, {{ v: 0 }}, {{ v: {it["n"]}, duration: 0.9, ease: "power3.out", onUpdate: () => {{ el.textContent = o.v.toLocaleString("es-ES", {{ minimumFractionDigits: {dec}, maximumFractionDigits: {dec} }}) + {suf}; }} }}, {t:.3f}); }})();',
                    f'tl.fromTo("#{p}-v{k}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {t:.3f});']
    elif tipo == "linea":
        n = len(its)
        h.append(f'<div class="linea"><div id="{p}-eje" class="eje"></div>')
        for k, it in enumerate(its):
            x = (k + 0.5) / n * 100
            hk = it.get("k", "")
            h.append(f'<div id="{p}-h{k}" class="hito {hk}" style="left:{x:.1f}%"><span class="f">{esc(it["f"])}</span><i class="pt"></i>'
                     f'<span class="d">{esc(it["t"])}{"<i></i>" if hk == "x" else ""}</span></div>')
        h.append('</div>')
        tws.append(f'tl.fromTo("#{p}-eje", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.8, ease: "power2.inOut" }}, 0.05);')
        for k, it in enumerate(its):
            t = t_palabra(e, it["en"])
            tws.append(f'tl.fromTo("#{p}-h{k}", {{ y: 80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "back.out(1.8)" }}, {t});')
            if it.get("k") == "x":
                # se tacha cuando llega el siguiente hito (o un poco después si es el último)
                tx = t_palabra(e, its[k + 1]["en"]) if k + 1 < n else t + 1.2
                tws.append(f'tl.fromTo("#{p}-h{k} .d i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power2.out" }}, {tx:.3f});')
    elif tipo == "cita":
        h.append(f'<div class="cita" id="{p}-cita"><div class="q">“</div><div class="tx">{esc(seg["cita"])}</div><div class="au">— {esc(seg["autor"])}</div></div>')
        tws.append(f'tl.fromTo("#{p}-cita", {{ y: 120, opacity: 0, rotation: -2 }}, {{ y: 0, opacity: 1, rotation: 0, duration: 0.5, ease: "back.out(1.5)" }}, 0.1);')
        tws.append(f'tl.fromTo("#{p}-cita .tx", {{ opacity: 0.25 }}, {{ opacity: 1, duration: 0.6 }}, {t_palabra(e, seg["en"])});')
    elif tipo == "mapa":
        fase = seg["fase"]
        h.append(f'<div id="{p}-mw" style="position:absolute;inset:0">{D.mapa(p)}')
        etqs = ([("LEONIDA", "le"), ("VICE CITY", "vc")] if fase == 1 else
                [("LEONIDA", "le"), ("VICE CITY", "vc")] + [(it["t"], "") for it in its])
        for k, (nombre, cls) in enumerate(etqs):
            x, y = D.POS_MAPA[nombre]
            h.append(f'<div id="{p}-e{k}" class="etq {cls}" style="left:{90 + x * 860 / 900:.0f}px;top:{140 + y * 669 / 700:.0f}px">{esc(nombre)}</div>')
        h.append('</div>')
        if fase == 2:
            h.append('<div class="lista">' + "".join(tarjeta(f"{p}-t{k}", it) for k, it in enumerate(its)) + '</div>')
        tws.append(f'tl.fromTo("#{p}-mapa", {{ scale: {0.8 if fase == 1 else 1}, opacity: {0 if fase == 1 else 1} }}, {{ scale: 1, opacity: 1, duration: 0.6, ease: "power3.out" }}, 0.02);')
        if fase == 1:
            for k, it in enumerate(its):
                tws.append(f'tl.fromTo("#{p}-e{k}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.5)" }}, {t_palabra(e, it["en"])});')
            tws.append(f'tl.fromTo("#{p}-vc", {{ scale: 0 }}, {{ scale: 1, duration: 0.4, ease: "back.out(3)", transformOrigin: "680px 470px" }}, {t_palabra(e, "Vice")});')
            tws.append(f'tl.fromTo("#{p}-tierra", {{ opacity: 0.4 }}, {{ opacity: 1, duration: 0.5 }}, {t_palabra(e, "Leonida")});')
        else:
            for k, it in enumerate(its):
                t = t_palabra(e, it["en"])
                tws.append(f'tl.fromTo("#{p}-e{k + 2}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.5)" }}, {t});')
                tws.append(f'tl.fromTo("#{p}-p{k + 1}", {{ scale: 0 }}, {{ scale: 1, duration: 0.35, ease: "back.out(3)", transformOrigin: "center" }}, {t});')
                tws.append(f'tl.fromTo("#{p}-t{k}", {{ x: 500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3, ease: "power3.out" }}, {t});')
        if fase == 1:
            for k in range(1, 6):
                tws.append(f'tl.set("#{p}-p{k}", {{ opacity: 0 }}, 0);')
        tws.append(f'tl.fromTo("#{p}-mw", {{ scale: 1 }}, {{ scale: 1.03, duration: {Dd}, ease: "none", transformOrigin: "30% 50%" }}, 0);')
    elif tipo == "precios":
        h.append('<div class="precios">' + "".join(
            f'<div id="{p}-p{k}" class="precio{" u" if k else ""}"><div class="ed">{esc(it["t"])}</div><div class="p">{esc(it["p"])}</div>'
            f'<div class="pl">PS5 · XBOX SERIES X|S</div></div>' for k, it in enumerate(its)) + '</div>')
        for k, it in enumerate(its):
            tws.append(f'tl.fromTo("#{p}-p{k}", {{ y: 300, opacity: 0, rotation: {-8 if k else 8} }}, {{ y: 0, opacity: 1, rotation: {2 if k else -2}, duration: 0.45, ease: "back.out(1.7)" }}, {t_palabra(e, it["en"])});')
    elif tipo == "suscribir":
        h.append(f'<div class="gtit" style="top:120px"><div class="lg" style="font-size:200px">GTA <b>VI</b></div></div>')
        h.append(f'<div class="subs" style="top:470px"><div id="{p}-b0" class="btn lk">👍 {esc(its[0]["t"])}</div><div id="{p}-b1" class="btn su">🔔 {esc(its[1]["t"])}</div></div>')
        h.append(f'<div class="nota" style="top:720px" id="{p}-vc"><span>NOS VEMOS EN VICE CITY</span></div>')
        tws += [f'tl.fromTo("#{p}-b0", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.5)" }}, {t_palabra(e, its[0]["en"])});',
                f'tl.fromTo("#{p}-b1", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.5)" }}, {t_palabra(e, its[1]["en"])});',
                f'tl.to("#{p}-b1", {{ scale: 1.08, duration: 0.4, yoyo: true, repeat: 7, ease: "sine.inOut" }}, {t_palabra(e, its[1]["en"]) + 0.4:.3f});',
                f'tl.fromTo("#{p}-vc", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power3.out" }}, {t_palabra(e, "Vice")});']
    # balanceo y parpadeo de los personajes
    tws.append(f'document.querySelectorAll("#root [id$=\'-ojos\']").forEach((el, i) => {{ for (let s = 1.0 + i * 0.7; s < {Dd} - 0.3; s += 2.7) tl.fromTo(el, {{ scaleY: 1 }}, {{ scaleY: 0.1, duration: 0.07, yoyo: true, repeat: 1 }}, s); }});')
    return "\n    ".join(h), tws


def escena_html(e, seg):
    eid, Dd, cap = e["escena"], e["dur"], seg["cap"]
    c0, c1, c2, ac = PALETAS[cap]
    cuerpo, tws = cuerpo_escena(e, seg)
    ncap = NUM_CAP[cap]
    cab = ""
    if cap not in ("intro",) and seg["tipo"] != "portada":
        titulo = next(c["titulo"] for c in CAPITULOS if c["id"] == cap)
        lbl = f"{ncap} · {titulo}" if cap != "cierre" else titulo
        cab = f'<div class="cab"><span class="logo">GTA <b>VI</b></span><span class="pillcap">{esc(lbl)}</span></div>'
        prog = "".join(f'<i class="{"on" if k == ncap else ("hecho" if k < ncap else "")}"></i>' for k in range(1, 9))
        cab += f'<div class="prog">{prog}</div>'
    fuente = f'<div class="fuente">Fuente: {esc(seg["fuente"])}</div>' if seg.get("fuente") else ""
    sol_op = 1 if seg["tipo"] in ("portada", "titulo", "suscribir") else 0.75
    return f"""<template>
  <style>{CSS}</style>
  <div id="root" data-composition-id="{eid}" data-width="{W}" data-height="{H}" style="--c0:{c0};--c1:{c1};--c2:{c2};--ac:{ac};--grid:{c2}cc">
    <div class="cielo"></div><div class="estrellas"></div>
    <div class="sol" id="{eid}-sol" style="opacity:{sol_op}"></div>
    <div class="rejilla-cont"><div class="rejilla" id="{eid}-rej"></div></div>
    <div class="horiz"></div>
    {PALMERA.replace("{cls}", "izq")}
    {PALMERA.replace("{cls}", "der")}
    <div class="velo"></div>
    <div class="bandasub"></div>
    {cab}
    {cuerpo}
    {fuente}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.to({{}}, {{ duration: {Dd} }}, 0);
      tl.fromTo("#{eid}-rej", {{ backgroundPosition: "0px 0px" }}, {{ backgroundPosition: "0px " + (110 * Math.round({Dd} * 2.5)) + "px", duration: {Dd}, ease: "none" }}, 0);
      tl.fromTo("#{eid}-sol", {{ y: 30 }}, {{ y: -10, duration: {Dd}, ease: "none" }}, 0);
      {(chr(10) + "      ").join(tws)}
      window.__timelines["{eid}"] = tl;
    }})();
  </script>
</template>
"""


def grupos(escena, maximo=7):
    """Frases de subtítulo de hasta `maximo` palabras; un signo de puntuación fuerte cierra el grupo."""
    tokens = escena["texto"].split()
    limpio = lambda s: re.sub(r"[^\wáéíóúñü'-]", "", s.lower())
    palabras, j = [], 0
    for w in escena["palabras"]:
        while j < len(tokens) and not limpio(tokens[j]).startswith(limpio(w["w"])[:3]):
            j += 1
        tok = tokens[j] if j < len(tokens) else ""
        palabras.append(dict(w, fin=bool(re.search(r"[.:;…!?]$", tok)), coma=tok.endswith(","), vis=tok or w["w"]))
        j += 1
    out, g = [], []
    for w in palabras:
        g.append(w)
        if w["fin"] or len(g) == maximo or (w["coma"] and len(g) >= 4):
            out.append(g)
            g = []
    if g:
        out.append(g)
    return out


def subtitulos(datos):
    total = datos["total"]
    gs = [g for e in datos["escenas"] for g in grupos(e)]
    filas, tw = [], []
    for i, g in enumerate(gs):
        t0 = g[0]["t"] - 0.06
        fin = gs[i + 1][0]["t"] - 0.06 if i + 1 < len(gs) else total
        fin = min(fin, g[-1]["t"] + g[-1]["d"] + 0.7)
        spans = " ".join(f'<span id="sb-{i}-{k}" class="sb-w">{html.escape(w["vis"])}</span>' for k, w in enumerate(g))
        filas.append(f'    <div id="sb-{i}" class="sb-g clip" data-start="{t0:.3f}" data-duration="{max(0.2, fin - t0):.3f}">{spans}</div>')
        tw.append(f'      tl.fromTo("#sb-{i}", {{ y: 14, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.12, ease: "power2.out" }}, {t0:.3f});')
        for k, w in enumerate(g):
            col = "#ffd166" if len(re.sub(r"\W", "", w["w"])) >= 7 or any(ch.isdigit() for ch in w["w"]) else "#ffffff"
            tw.append(f'      tl.fromTo("#sb-{i}-{k}", {{ color: "rgba(255,255,255,0.38)" }}, {{ color: "{col}", duration: 0.01 }}, {w["t"]:.3f});')
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .sb-g {{ position: absolute; left: 160px; right: 160px; top: 884px; text-align: center; }}
    .sb-w {{ display: inline-block; margin: 0 8px; font-family: Inter; font-weight: 900; font-size: 54px; line-height: 1.15;
            color: rgba(255,255,255,0.38); text-shadow: 0 4px 14px rgba(0,0,0,.7); }}
  </style>
  <div id="root" data-composition-id="subtitulos" data-width="{W}" data-height="{H}">
{chr(10).join(filas)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.to({{}}, {{ duration: {total} }}, 0);
{chr(10).join(tw)}
      window.__timelines["subtitulos"] = tl;
    }})();
  </script>
</template>
"""


def index(datos, titulo=TITULO):
    total = datos["total"]
    hosts = []
    for k, e in enumerate(datos["escenas"]):
        hosts.append(f'''      <div id="{e['escena']}" data-composition-id="{e['escena']}" data-composition-src="compositions/{e['escena']}.html"
        data-start="{e['ini']:.3f}" data-duration="{e['dur']:.3f}" data-track-index="{k % 2 + 1}" data-track-kind="graphics"
        data-width="{W}" data-height="{H}" style="z-index: 1"></div>''')
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{html.escape(titulo)}</title>
    <script src="assets/lib/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #0d0d12; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
{chr(10).join(hosts)}
      <div id="subtitulos" data-composition-id="subtitulos" data-composition-src="compositions/subtitulos.html"
        data-start="0" data-duration="{total}" data-track-index="10" data-track-kind="captions"
        data-width="{W}" data-height="{H}" style="z-index: 20"></div>
      <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{total}" data-track-index="20" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def main():
    datos = json.load(open(os.path.join(BUILD, "tiempos.json"), encoding="utf-8"))
    comp = os.path.join(HF, "compositions")
    shutil.rmtree(comp, ignore_errors=True)
    os.makedirs(comp)
    os.makedirs(os.path.join(HF, "assets", "lib"), exist_ok=True)
    lib = os.path.join(AQUI, "..", "gta6", "hf", "assets", "lib", "gsap.min.js")
    shutil.copy(lib, os.path.join(HF, "assets", "lib", "gsap.min.js"))
    for f in ("package.json", "hyperframes.json"):
        shutil.copy(os.path.join(AQUI, "..", "gta6", "hf", f), os.path.join(HF, f))
    for e, seg in zip(datos["escenas"], SEGMENTOS):
        assert e["escena"] == seg["escena"], (e["escena"], seg["escena"])
        open(os.path.join(comp, e["escena"] + ".html"), "w", encoding="utf-8").write(escena_html(e, seg))
    open(os.path.join(comp, "subtitulos.html"), "w", encoding="utf-8").write(subtitulos(datos))
    open(os.path.join(HF, "index.html"), "w", encoding="utf-8").write(index(datos))
    mez = os.path.join(BUILD, "mezcla.wav")
    if os.path.exists(mez):
        shutil.copy(mez, os.path.join(HF, "assets", "mezcla.wav"))
    print("hf/ listo:", len(datos["escenas"]), "escenas,", datos["total"], "s")


if __name__ == "__main__":
    main()
