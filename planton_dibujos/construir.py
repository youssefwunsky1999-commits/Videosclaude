"""«Abascal planta a Jordi Wild» en estilo explicativo con dibujos (personajes vectoriales planos, fondos con rayos,
subtítulos karaoke arriba, píldoras y tarjetas). Reutiliza la narración de Mateo y la mezcla de planton_wild/.

    python3 construir.py   -> hf/index.html + hf/compositions/*.html

Los personajes son caricaturas simples y amables con su nombre debajo; los datos salen del comunicado de VOX (11-11-2026)
y de la Cadena SER (ver guion.py)."""
import importlib.util
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
HF = os.path.join(AQUI, "hf")
DATOS = json.load(open(os.path.join(AQUI, "build", "tiempos.json"), encoding="utf-8"))
ESC = {e["escena"]: e for e in DATOS["escenas"]}

# funciones de subtítulos e index del proyecto base
_spec = importlib.util.spec_from_file_location("base", os.path.join(AQUI, "..", "planton_wild", "construir.py"))
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def t(esc, palabra, n=1, d=-0.08):
    e = ESC[esc]
    hits = [w for w in e["palabras"] if w["w"] == palabra]
    return round(hits[n - 1]["t"] - e["ini"] + d, 3)


# ---------------------------------------------------------------- personajes (SVG, viewBox 400x480)
def _cabeza(piel, oreja):
    return (f'<ellipse cx="112" cy="205" rx="18" ry="28" fill="{oreja}"/><ellipse cx="288" cy="205" rx="18" ry="28" fill="{oreja}"/>'
            f'<rect x="168" y="290" width="64" height="72" rx="20" fill="{oreja}"/>'
            f'<ellipse cx="200" cy="192" rx="88" ry="108" fill="{piel}"/>')


def _cara(pid, cejas, boca="#7a3a2a"):
    return (f'<rect x="148" y="158" width="42" height="9" rx="4" fill="{cejas}"/><rect x="210" y="158" width="42" height="9" rx="4" fill="{cejas}"/>'
            f'<g id="{pid}-ojos" style="transform-origin:200px 188px"><circle cx="170" cy="188" r="8" fill="#1b1b1b"/><circle cx="230" cy="188" r="8" fill="#1b1b1b"/></g>'
            f'<path d="M200 192 L189 228 Q200 235 211 228 Z" fill="#e0a986"/>')


def personaje(tipo, pid):
    if tipo == "abascal":
        s = ('<path d="M10 480 C25 385 110 352 200 348 C290 352 375 385 390 480 Z" fill="#1f2a44"/>'
             '<path d="M150 352 L200 425 L250 352 L238 346 L200 398 L162 346 Z" fill="#4f7396"/>'
             + _cabeza("#f0c4a0", "#e3b08c") +
             '<path d="M112 178 C106 100 150 70 205 72 C262 72 298 106 290 178 C284 140 268 118 244 110 C214 100 168 102 148 118 C126 134 117 152 112 178 Z" fill="#8e9196"/>'
             '<path d="M114 205 C117 282 160 316 200 318 C240 316 283 282 286 205 C276 242 262 264 240 270 C224 256 176 256 160 270 C138 264 124 242 114 205 Z" fill="#a7a8ac"/>'
             '<path d="M166 250 C182 237 218 237 234 250 C220 257 180 257 166 250 Z" fill="#8a8b8f"/>'
             '<path d="M184 264 Q200 271 216 264" stroke="#7a3a2a" stroke-width="5" fill="none" stroke-linecap="round"/>'
             + _cara(pid, "#5f6166"))
    elif tipo == "jordi":
        s = ('<path d="M10 480 C25 385 110 352 200 348 C290 352 375 385 390 480 Z" fill="#161616"/>'
             + _cabeza("#e9b893", "#dba783") +
             '<ellipse cx="200" cy="120" rx="80" ry="40" fill="#c99876" opacity=".35"/>'
             '<path d="M112 200 C110 300 150 372 200 378 C250 372 290 300 288 200 C278 246 262 268 238 272 C222 258 178 258 162 272 C138 268 122 246 112 200 Z" fill="#3d2a1e"/>'
             '<path d="M164 250 C182 236 218 236 236 250 C220 258 180 258 164 250 Z" fill="#2f2017"/>'
             '<path d="M186 266 Q200 272 214 266" stroke="#e9b893" stroke-width="5" fill="none" stroke-linecap="round"/>'
             + _cara(pid, "#3d2a1e"))
    else:  # broncano
        s = ('<path d="M10 480 C25 385 110 352 200 348 C290 352 375 385 390 480 Z" fill="#1c2340"/>'
             '<path d="M160 350 L200 410 L240 350 Z" fill="#0f0f14"/>'
             + _cabeza("#efc19c", "#e0ad88") +
             '<path d="M110 182 C104 96 152 66 206 68 C264 70 300 104 292 182 C286 138 262 114 236 108 C206 100 168 104 148 116 C126 132 116 154 110 182 Z" fill="#2e211a"/>'
             '<path d="M116 210 C120 274 160 304 200 306 C240 304 280 274 284 210 C276 240 262 258 242 262 C226 252 174 252 158 262 C138 258 124 240 116 210 Z" fill="#3a2a20" opacity=".9"/>'
             '<path d="M184 262 Q200 270 216 262" stroke="#7a3a2a" stroke-width="5" fill="none" stroke-linecap="round"/>'
             + _cara(pid, "#2e211a"))
    return f'<svg id="{pid}" class="pj" viewBox="0 0 400 480">{s}</svg>'


SILLA = ('<svg viewBox="0 0 300 360" class="silla"><rect x="40" y="20" width="220" height="190" rx="40" fill="#3a3f55"/>'
         '<rect x="20" y="190" width="260" height="60" rx="26" fill="#4a5070"/><rect x="138" y="250" width="24" height="70" fill="#2b2f42"/>'
         '<rect x="70" y="315" width="160" height="18" rx="9" fill="#2b2f42"/></svg>')
MICRO = ('<svg viewBox="0 0 120 260" class="micro"><rect x="35" y="0" width="50" height="110" rx="25" fill="#c7cad6"/>'
         '<g stroke="#8d91a3" stroke-width="4"><line x1="40" y1="30" x2="80" y2="30"/><line x1="40" y1="50" x2="80" y2="50"/><line x1="40" y1="70" x2="80" y2="70"/></g>'
         '<rect x="54" y="110" width="12" height="130" fill="#5b6075"/><rect x="20" y="236" width="80" height="16" rx="8" fill="#5b6075"/></svg>')
CANDADO = ('<svg viewBox="0 0 120 140" class="ico"><path d="M30 60 V40 a30 30 0 0 1 60 0 V60" stroke="#ffd43b" stroke-width="14" fill="none"/>'
           '<rect x="14" y="58" width="92" height="76" rx="14" fill="#ffd43b"/><circle cx="60" cy="92" r="10" fill="#1a1d33"/></svg>')
TIJERA = ('<svg viewBox="0 0 160 120" class="ico"><circle cx="30" cy="30" r="22" stroke="#ff4d5a" stroke-width="10" fill="none"/>'
          '<circle cx="30" cy="90" r="22" stroke="#ff4d5a" stroke-width="10" fill="none"/>'
          '<path d="M48 42 L150 96 M48 78 L150 24" stroke="#e8ebf5" stroke-width="10" stroke-linecap="round"/></svg>')
ESCUDO = ('<svg viewBox="0 0 140 160" class="ico"><path d="M70 6 L130 28 V78 C130 118 104 142 70 154 C36 142 10 118 10 78 V28 Z" fill="#3ccf6e"/>'
          '<path d="M44 80 L64 100 L100 60" stroke="#fff" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')

FONDOS = {"gancho": ("#141a3d", "#2a3480"), "m1": ("#2a0f4a", "#5b2a9a"), "m2": ("#0b1430", "#163a6b"),
          "m3": ("#3a0c18", "#7a1f33"), "m4": ("#0e2236", "#1f4e74"), "final": ("#2a0f4a", "#5b2a9a")}

CSS = """
#root { position: absolute; inset: 0; overflow: hidden; background: var(--a); font-family: Inter; }
.rays { position: absolute; left: -50%; top: -30%; width: 200%; height: 160%;
        background: repeating-conic-gradient(from 0deg at 50% 50%, rgba(255,255,255,.07) 0deg 7deg, transparent 7deg 18deg); }
.vig { position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 30%, rgba(0,0,0,.55) 100%); }
.pill { position: absolute; left: 0; right: 0; text-align: center; }
.pill span { display: inline-block; font-weight: 900; font-size: 46px; letter-spacing: .5px; padding: 14px 34px; border-radius: 60px;
             box-shadow: 0 10px 0 rgba(0,0,0,.25); }
.am span { background: #ffd43b; color: #1a1d33; } .ro span { background: #ff3b47; color: #fff; }
.bl span { background: #fff; color: #1a1d33; } .az span { background: #2f6bff; color: #fff; } .ve span { background: #3ccf6e; color: #fff; }
.nombre { position: absolute; text-align: center; }
.nombre span { display: inline-block; font-weight: 900; font-size: 38px; padding: 10px 28px; border-radius: 40px; background: #fff; color: #1a1d33;
               box-shadow: 0 8px 0 rgba(0,0,0,.25); }
.pj { position: absolute; }
.card { position: absolute; background: #fbf7ee; border-radius: 26px; box-shadow: 0 16px 0 rgba(0,0,0,.25); color: #1a1d33; }
.sello { position: absolute; font-weight: 900; color: #e5323e; border: 10px solid #e5323e; border-radius: 16px; padding: 6px 26px; text-align: center;
         background: rgba(251,247,238,.85); line-height: 1.05; }
.silla, .micro, .ico { position: absolute; }
.big { position: absolute; left: 0; right: 0; text-align: center; font-weight: 900; color: #ffd43b; text-shadow: 0 10px 0 rgba(0,0,0,.3); }
"""


def escena(eid, cuerpo, tws):
    a, b = FONDOS[eid]
    D = ESC[eid]["dur"]
    return f"""<template>
  <style>{CSS}</style>
  <div id="root" data-composition-id="{eid}" data-width="1080" data-height="1920" style="--a:{a}">
    <div id="{eid}-rays" class="rays" style="background-color:{b}"></div>
    <div class="vig"></div>
{cuerpo}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.to({{}}, {{ duration: {D} }}, 0);
      tl.fromTo("#{eid}-rays", {{ rotation: 0 }}, {{ rotation: {round(D * 4, 1)}, duration: {D}, ease: "none" }}, 0);
      document.querySelectorAll("#root .pj").forEach((el, i) => {{
        tl.fromTo(el, {{ y: 0 }}, {{ y: -10, duration: 0.9, yoyo: true, repeat: Math.max(1, Math.floor({D} / 0.9) - 1), ease: "sine.inOut" }}, i * 0.3);
      }});
      document.querySelectorAll("#root [id$='-ojos']").forEach((el, i) => {{
        for (let s = 1.2 + i * 0.7; s < {D} - 0.3; s += 2.6) tl.fromTo(el, {{ scaleY: 1 }}, {{ scaleY: 0.1, duration: 0.07, yoyo: true, repeat: 1 }}, s);
      }});
      {(chr(10) + '      ').join(tws)}
      window.__timelines["{eid}"] = tl;
    }})();
  </script>
</template>
"""


def pop(sel, t0, desde=0.2, rot=0, dur=0.35):
    return f'tl.fromTo("{sel}", {{ scale: {desde}, opacity: 0, rotation: {rot - 12 if rot else 0} }}, {{ scale: 1, opacity: 1, rotation: {rot}, duration: {dur}, ease: "back.out(2.2)" }}, {t0});'


def sube(sel, t0, dy=120):
    return f'tl.fromTo("{sel}", {{ y: {dy}, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.45, ease: "power3.out" }}, {t0});'


def sello_cae(sel, t0, rot=-8):
    return f'tl.fromTo("{sel}", {{ scale: 2.6, opacity: 0, rotation: {rot - 10} }}, {{ scale: 1, opacity: 1, rotation: {rot}, duration: 0.2, ease: "power4.in" }}, {t0});'


def escenas():
    out = {}
    # ------------------------------------------------ gancho: el estudio con la silla vacía
    out["gancho"] = escena("gancho", f"""
    <div id="g-pl" class="pill am" style="top:440px"><span>THE WILD PROJECT · HOY</span></div>
    <div id="g-silla" style="position:absolute;left:70px;top:820px;width:400px;height:480px">{SILLA.replace('class="silla"', 'class="silla" style="left:40px;top:60px;width:320px"')}</div>
    <div id="g-n1" class="nombre" style="left:90px;top:1330px;width:360px"><span>ABASCAL</span></div>
    <div id="g-x" class="sello" style="left:120px;top:960px;font-size:90px;border-width:12px">PLANTADO</div>
    <div style="position:absolute;left:470px;top:1000px;width:110px">{MICRO.replace('class="micro"', 'class="micro" style="width:110px"')}</div>
    {personaje('jordi', 'g-jw').replace('class="pj"', 'class="pj" style="left:560px;top:820px;width:460px"')}
    <div id="g-n2" class="nombre" style="left:580px;top:1330px;width:420px"><span>JORDI WILD</span></div>
    <div id="g-cul" class="pill ro" style="top:620px"><span>¿LA CULPA? LA REVUELTA</span></div>
""", [pop("#g-pl", 0.0, 0.8), sello_cae("#g-x", t("gancho", "plantar")), pop("#g-cul", t("gancho", "culpa"), 0.3, 0, 0.3)])

    # ------------------------------------------------ m1: el comunicado
    out["m1"] = escena("m1", f"""
    <div id="c-doc" class="card" style="left:150px;top:450px;width:780px;height:640px;padding:46px 56px">
      <div style="font-weight:900;font-size:64px;color:#1f7a45">COMUNICADO</div>
      <div style="font-weight:800;font-size:30px;color:#6b6f80;margin-top:6px">VOX · 11 DE NOVIEMBRE</div>
      <div style="margin-top:34px;display:flex;flex-direction:column;gap:22px">
        <i style="display:block;height:16px;border-radius:8px;background:#d9d4c7;width:92%"></i><i style="display:block;height:16px;border-radius:8px;background:#d9d4c7;width:80%"></i>
        <i style="display:block;height:16px;border-radius:8px;background:#d9d4c7;width:88%"></i><i style="display:block;height:16px;border-radius:8px;background:#d9d4c7;width:70%"></i>
        <i style="display:block;height:16px;border-radius:8px;background:#d9d4c7;width:84%"></i></div>
    </div>
    <div id="c-sello" class="sello" style="left:200px;top:780px;font-size:70px">ENTREVISTA<br>SUSPENDIDA</div>
    <div id="c-inc" class="pill am" style="top:1150px"><span>«GRAVES INCUMPLIMIENTOS»</span></div>
    {personaje('abascal', 'c-ab').replace('class="pj"', 'class="pj" style="left:300px;top:1280px;width:480px"')}
""", [sube("#c-doc", 0.05), sello_cae("#c-sello", t("m1", "suspendido")), pop("#c-inc", t("m1", "incumplimientos"), 0.3)])

    # ------------------------------------------------ m2: los 40 minutos
    out["m2"] = escena("m2", f"""
    <div id="t-tv" class="card" style="left:140px;top:440px;width:800px;height:470px;background:#1a1d33;border:14px solid #2c3152;padding:0">
      <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column">
        <div style="font-weight:900;font-size:40px;color:#9aa3d6;letter-spacing:3px">GRABACIÓN ÍNTEGRA</div>
        <div id="t-num" style="font-weight:900;font-size:190px;color:#fff;line-height:1">0</div>
        <div style="font-weight:900;font-size:56px;color:#ffd43b">MINUTOS SIN EMITIR</div></div>
    </div>
    <div id="t-tij" style="position:absolute;left:820px;top:380px;width:200px">{TIJERA.replace('class="ico"', 'class="ico" style="width:200px"')}</div>
    <div id="t-tve" class="pill bl" style="top:960px"><span>TVE + EL TERRAT</span></div>
    <div id="t-can" style="position:absolute;left:470px;top:1060px;width:140px">{CANDADO.replace('class="ico"', 'class="ico" style="width:140px"')}</div>
    <div id="t-sec" class="pill ro" style="top:1230px"><span>«ESTÁ SECUESTRANDO 40 MINUTOS»</span></div>
""", [sube("#t-tv", 0.05), pop("#t-tve", t("m2", "TVE"), 0.4),
      f'tl.fromTo("#t-tij", {{ x: 200, opacity: 0, rotation: 40 }}, {{ x: 0, opacity: 1, rotation: 0, duration: 0.4, ease: "back.out(2)" }}, {t("m2", "completa")});',
      f'(() => {{ const o = {{ v: 0 }}, el = document.getElementById("t-num"); tl.fromTo(o, {{ v: 0 }}, {{ v: 40, duration: 0.9, ease: "power2.out", onUpdate: () => {{ el.textContent = Math.round(o.v); }} }}, {t("m2", "cuarenta")}); }})();',
      pop("#t-can", t("m2", "secuestrando"), 0.2), pop("#t-sec", t("m2", "secuestrando", d=0.15), 0.3)])

    # ------------------------------------------------ m3: sus condiciones
    out["m3"] = escena("m3", f"""
    <div id="k-pl" class="pill am" style="top:440px"><span>SUS NUEVAS CONDICIONES</span></div>
    <div id="k-card" class="card" style="left:110px;top:570px;width:860px;padding:40px 50px">
      <div id="k-1" style="display:flex;align-items:center;gap:26px;font-weight:900;font-size:50px"><b style="flex:none;width:76px;height:76px;border-radius:50%;background:#3ccf6e;color:#fff;text-align:center;line-height:76px;font-size:48px">✓</b>Control de sus respuestas</div>
      <div id="k-2" style="display:flex;align-items:center;gap:26px;font-weight:900;font-size:50px;margin-top:30px"><b style="flex:none;width:76px;height:76px;border-radius:50%;background:#3ccf6e;color:#fff;text-align:center;line-height:76px;font-size:48px">✓</b>Mismo derecho sobre imagen y contenido</div>
    </div>
    <div id="k-no" class="sello" style="left:250px;top:1010px;font-size:58px">SI NO, NO VA</div>
    {personaje('abascal', 'k-ab').replace('class="pj"', 'class="pj" style="left:300px;top:1250px;width:480px"')}
""", [pop("#k-pl", t("m3", "condiciones"), 0.5), sube("#k-card", t("m3", "condiciones", d=0.1)),
      pop("#k-1", t("m3", "control"), 0.5), pop("#k-2", t("m3", "derecho"), 0.5), sello_cae("#k-no", t("m3", "ningún"), -5),
      'tl.set("#k-1", { opacity: 0 }, 0); tl.set("#k-2", { opacity: 0 }, 0);'])

    # ------------------------------------------------ m4: ¿y Jordi Wild?
    out["m4"] = escena("m4", f"""
    <div id="j-ok" class="pill ve" style="top:440px"><span>«NO CULPA DE NADA A JORDI WILD»</span></div>
    {personaje('jordi', 'j-jw').replace('class="pj"', 'class="pj" style="left:250px;top:600px;width:580px"')}
    <div id="j-n" class="nombre" style="left:0;right:0;top:1300px"><span>JORDI WILD</span></div>
    <div id="j-esc" style="position:absolute;left:800px;top:620px;width:190px">{ESCUDO.replace('class="ico"', 'class="ico" style="width:190px"')}</div>
    <div id="j-rep" class="pill am" style="top:1420px"><span>«PROTEGER SU REPUTACIÓN»</span></div>
""", [pop("#j-ok", t("m4", "nada"), 0.3), pop("#j-esc", t("m4", "reputación"), 0.2), pop("#j-rep", t("m4", "proteger"), 0.4)])

    # ------------------------------------------------ final: la pregunta
    out["final"] = escena("final", f"""
    <div id="f-q" class="card" style="left:110px;top:450px;width:860px;padding:34px 40px;text-align:center;font-weight:900;font-size:66px;line-height:1.1">¿QUEJA JUSTA<br>O MIEDO?</div>
    <div id="f-si" class="pill" style="top:720px;left:-420px"><span style="background:#3ccf6e;color:#fff">QUEJA JUSTA</span></div>
    <div id="f-no" class="pill" style="top:720px;left:520px"><span style="background:#ff3b47;color:#fff">MIEDO</span></div>
    {personaje('abascal', 'f-ab').replace('class="pj"', 'class="pj" style="left:20px;top:880px;width:460px"')}
    {personaje('broncano', 'f-br').replace('class="pj"', 'class="pj" style="left:600px;top:880px;width:460px"')}
    <div class="nombre" style="left:60px;top:1350px;width:380px"><span>ABASCAL</span></div>
    <div class="nombre" style="left:640px;top:1350px;width:380px"><span>BRONCANO</span></div>
    <div id="f-com" class="pill bl" style="top:1450px"><span>TE LEO EN COMENTARIOS</span></div>
    <div id="f-sig" class="pill ro" style="top:1560px"><span>SÍGUEME · ESTO NO HA ACABADO</span></div>
""", [pop("#f-q", 0.1, 0.5), pop("#f-si", t("final", "justa"), 0.3), pop("#f-no", t("final", "miedo"), 0.3),
      pop("#f-com", t("final", "comentarios"), 0.4), pop("#f-sig", t("final", "sígueme"), 0.4)])
    return out


def subtitulos_arriba():
    """Subtítulos karaoke arriba: la frase en gris y cada palabra se enciende al decirla (las largas, en amarillo)."""
    import inspect
    src = inspect.getsource(base.grupos).replace("len(g) == 3", "len(g) == 6")
    exec(src, base.__dict__)          # frases de hasta 6 palabras, como en la referencia
    s = base.subtitulos(DATOS)
    s = s.replace("top: 1215px;", "top: 236px;")
    s = s.replace('-webkit-text-stroke: 12px #0b0712; paint-order: stroke fill; text-shadow: 0 6px 18px rgba(0,0,0,.45);',
                  'text-shadow: 0 6px 16px rgba(0,0,0,.55);')
    s = s.replace('font-family: "Archivo Black"; font-size: 68px;', 'font-family: Inter; font-weight: 900; font-size: 64px;')
    import re
    # palabra dicha: blanca (o amarilla si es larga); pendiente: gris
    s = re.sub(r'tl\.fromTo\("(#sb-\d+-\d+)", \{ color: "#ffffff" \}, \{ color: "#ffd23f", duration: 0\.01 \}, ([\d.]+)\);',
               lambda m: f'tl.fromTo("{m.group(1)}", {{ color: "rgba(255,255,255,.35)" }}, {{ color: document.querySelector("{m.group(1)}").textContent.length >= 7 ? "#ffd43b" : "#ffffff", duration: 0.01 }}, {m.group(2)});', s)
    s = re.sub(r'\s*tl\.to\("#sb-\d+-\d+", \{ color: "#ffffff", duration: 0\.01 \}, [\d.]+\);', '', s)
    s = s.replace('line-height: 1.1; color: #fff;', 'line-height: 1.12; color: rgba(255,255,255,.35);')
    return s


def main():
    os.makedirs(os.path.join(HF, "compositions"), exist_ok=True)
    for eid, html_ in escenas().items():
        open(os.path.join(HF, "compositions", eid + ".html"), "w", encoding="utf-8").write(html_)
    open(os.path.join(HF, "compositions", "subtitulos.html"), "w", encoding="utf-8").write(subtitulos_arriba())
    idx = base.index(DATOS).replace("<title>Abascal planta a Jordi Wild</title>", "<title>Abascal planta a Jordi Wild (dibujos)</title>")
    open(os.path.join(HF, "index.html"), "w", encoding="utf-8").write(idx)
    print("hf/ listo:", DATOS["total"], "s")


if __name__ == "__main__":
    main()
