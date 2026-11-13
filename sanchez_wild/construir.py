"""«¿Es Sánchez tan malo como dicen?» (basado en si_gana_psoe). Antes: «¿Y si gobiernan PP y Vox?» en estilo explicativo con dibujos (personajes vectoriales planos, fondos con rayos,
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

FONDOS = {"gancho": ("#5a0a10", "#b0141f"), "abalos": ("#4a0810", "#9c1220"), "amigos": ("#5a0a10", "#c21b26"),
          "zapatero": ("#4a1506", "#a8360d"), "ceuta": ("#3e070c", "#8a0f19"), "zasca": ("#141519", "#2c2e38"), "final": ("#5a0a10", "#c21b26")}

PP, VX, PS = "#1d6fe0", "#2fa84f", "#e3262a"

CSS = """
#root { position: absolute; inset: 0; overflow: hidden; background: var(--a); font-family: Inter; }
.rays { position: absolute; left: -50%; top: -30%; width: 200%; height: 160%;
        background: repeating-conic-gradient(from 0deg at 50% 50%, rgba(255,255,255,.07) 0deg 7deg, transparent 7deg 18deg); }
.vig { position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 30%, rgba(0,0,0,.55) 100%); }
.pill { position: absolute; left: 0; right: 0; text-align: center; }
.pill span { display: inline-block; font-weight: 900; font-size: 48px; padding: 14px 36px; border-radius: 60px; box-shadow: 0 10px 0 rgba(0,0,0,.25); }
.am span { background: #ffd43b; color: #1a1d33; } .ro span { background: #ff3b47; color: #fff; } .bl span { background: #fff; color: #1a1d33; }
.big { position: absolute; left: 0; right: 0; text-align: center; font-weight: 900; color: #ffd43b; text-shadow: 0 10px 0 rgba(0,0,0,.3); line-height: 1; }
.big small { display: block; font-size: 40px; color: #fff; margin-top: 10px; text-shadow: none; }
.card { position: absolute; left: 70px; right: 70px; background: #fbf7ee; border-radius: 24px; box-shadow: 0 14px 0 rgba(0,0,0,.25);
        color: #1a1d33; padding: 22px 30px; display: flex; align-items: center; gap: 24px; font-weight: 800; font-size: 40px; line-height: 1.15; }
.tag { flex: none; font-weight: 900; font-size: 34px; color: #fff; border-radius: 14px; padding: 8px 18px; }
.nombre { position: absolute; text-align: center; }
.nombre span { display: inline-block; font-weight: 900; font-size: 36px; padding: 8px 26px; border-radius: 40px; color: #fff; box-shadow: 0 8px 0 rgba(0,0,0,.25); }
.pj { position: absolute; }
.sello { position: absolute; font-weight: 900; color: #e5323e; border: 10px solid #e5323e; border-radius: 16px; padding: 6px 26px; text-align: center;
         background: rgba(251,247,238,.9); line-height: 1.05; }
.titulo { position: absolute; left: 0; right: 0; text-align: center; font-weight: 900; line-height: 1; }
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


def personaje_feijoo(pid):
    s = ('<path d="M10 480 C25 385 110 352 200 348 C290 352 375 385 390 480 Z" fill="#1c2a4f"/>'
         '<path d="M160 350 L200 420 L240 350 Z" fill="#fff"/><path d="M190 368 L210 368 L216 460 L200 476 L184 460 Z" fill="#2f7be0"/>'
         + _cabeza("#f2c6a3", "#e4b28e") +
         '<path d="M108 210 C100 140 118 104 140 96 C130 130 132 160 138 186 Z" fill="#e8e8ea"/>'
         '<path d="M292 210 C300 140 282 104 260 96 C270 130 268 160 262 186 Z" fill="#e8e8ea"/>'
         '<path d="M140 100 C170 80 232 80 262 100 C240 92 160 92 140 100 Z" fill="#e8e8ea"/>'
         '<path d="M150 128 Q200 118 250 128" stroke="#e0aa86" stroke-width="4" fill="none"/>'
         '<path d="M180 262 Q200 274 220 262" stroke="#7a3a2a" stroke-width="5" fill="none" stroke-linecap="round"/>'
         + _cara(pid, "#b9babd"))
    return f'<svg id="{pid}" class="pj" viewBox="0 0 400 480">{s}</svg>'


def personaje_sanchez(pid):
    c = ('<path d="M10 480 C25 385 110 352 200 348 C290 352 375 385 390 480 Z" fill="#1b2340"/>'
         '<path d="M156 350 L200 418 L244 350 Z" fill="#fff"/><path d="M178 352 L200 386 L222 352" stroke="#d9dbe3" stroke-width="5" fill="none"/>'
         + _cabeza("#e9b994", "#dba783") +
         '<path d="M108 186 C102 96 150 62 206 64 C266 66 302 100 294 186 C288 140 270 112 246 104 C214 94 170 98 148 112 C124 128 114 156 108 186 Z" fill="#2b2522"/>'
         '<path d="M108 186 C106 168 108 150 114 138 L122 196 Z" fill="#8c8580"/><path d="M294 186 C296 168 294 150 288 138 L280 196 Z" fill="#8c8580"/>'
         '<path d="M178 262 Q200 276 222 262" stroke="#7a3a2a" stroke-width="5" fill="none" stroke-linecap="round"/>'
         + _cara(pid, "#2b2522"))
    return f'<svg id="{pid}" class="pj" viewBox="0 0 400 480">{c}</svg>'


def solo(eid):
    return (personaje_sanchez(f"{eid}-ps").replace('class="pj"', 'class="pj" style="left:280px;top:1210px;width:520px"') +
            f'<div class="nombre" style="left:0;right:0;top:1700px"><span style="background:#fff;color:{PS}">SÁNCHEZ · PSOE</span></div>')


def tarjeta(cid, texto, top):
    return f'<div id="{cid}" class="card" style="top:{top}px"><span class="tag" style="background:{PS}">PSOE</span><span>{texto}</span></div>'


def perfil(eid, titulo, big, big_pie, big_t, items):
    cuerpo = [f'<div id="{eid}-tit" class="pill am" style="top:420px"><span>{titulo}</span></div>',
              f'<div id="{eid}-big" class="big" style="top:540px;font-size:{150 if len(big) <= 9 else 104}px">{big}<small>{big_pie}</small></div>']
    tws = [pop(f"#{eid}-tit", 0.05, 0.5), pop(f"#{eid}-big", big_t, 0.3)]
    for k, (texto, pal) in enumerate(items):
        cid = f"{eid}-c{k}"
        cuerpo.append(tarjeta(cid, texto, 800 + k * 200))
        tws.append(sube(f"#{cid}", pal, 80))
    cuerpo.append(solo(eid))
    return escena(eid, "\n".join(cuerpo), tws)


NEGRO = "#111318"


def duo(eid):
    return (personaje_sanchez(f"{eid}-ps").replace('class="pj"', 'class="pj" style="left:30px;top:1290px;width:470px"') +
            personaje("jordi", f"{eid}-jw").replace('class="pj"', 'class="pj" style="left:580px;top:1290px;width:470px"') +
            f'<div class="nombre" style="left:30px;width:470px;top:1720px"><span style="background:#fff;color:{PS}">SÁNCHEZ</span></div>'
            f'<div class="nombre" style="left:580px;width:470px;top:1720px"><span style="background:{NEGRO}">JORDI WILD</span></div>')


def cita(cid, quien, texto, top, size=50):
    col = PS if quien == "SÁNCHEZ" else (NEGRO if quien == "WILD" else "#7a3cc9")
    return (f'<div id="{cid}" class="card" style="top:{top}px;display:block;padding:26px 34px 30px">'
            f'<span class="tag" style="background:{col};font-size:30px">{quien}</span>'
            f'<div style="margin-top:14px;font-weight:900;font-size:{size}px;line-height:1.12">«{texto}»</div></div>')


def num(eid, txt):
    return f'<div id="{eid}-n" class="pill am" style="top:440px"><span style="font-size:58px">{txt}</span></div>'


CSS += "mark { background: #ffd43b; color: #1a1d33; padding: 0 8px; border-radius: 8px; }\n"


def escenas():
    o = {}
    o["gancho"] = escena("gancho", f"""
    <div id="g-t" class="titulo" style="top:430px"><div style="font-size:100px;color:#fff">SÁNCHEZ</div>
      <div style="font-size:70px;margin-top:6px;color:#fff">ANTE</div><div style="font-size:120px;margin-top:6px;color:#ffd43b">JORDI WILD</div></div>
    <div id="g-5" class="pill bl" style="top:850px"><span>5 FRASES QUE VAN A DAR QUE HABLAR</span></div>
    <div id="g-u" class="pill ro" style="top:970px"><span>ATENTO A LA ÚLTIMA</span></div>
    {duo("gancho")}
""", [pop("#g-t", 0.0, 0.9), pop("#g-5", t("gancho", "cinco"), 0.4), pop("#g-u", t("gancho", "última"), 0.4, 3)])

    o["abalos"] = escena("abalos", f"""
    {num("abalos", "1 · ÁBALOS")}
    {cita("ab-1", "SÁNCHEZ", "Yo no sabía que Ábalos consumía <mark>prostitución</mark>", 580, 56)}
    {cita("ab-2", "SÁNCHEZ", "Era muy brillante, pero tenía una <mark>cara B</mark> que no conocía", 900, 46)}
    {solo("abalos")}
""", [pop("#abalos-n", 0.05, 0.5), sube("#ab-1", t("abalos", "sabía")), sube("#ab-2", t("abalos", "brillante"))])

    o["amigos"] = escena("amigos", f"""
    {num("amigos", "2 · ÁBALOS Y CERDÁN")}
    {cita("am-1", "SÁNCHEZ", "<mark>Creía</mark> que eran amigos", 600, 70)}
    {cita("am-2", "SÁNCHEZ", "¿Tú no has conocido a gente que te haya <mark>decepcionado</mark>?", 920, 48)}
    {solo("amigos")}
""", [pop("#amigos-n", 0.05, 0.5), sube("#am-1", t("amigos", "creía")), sube("#am-2", t("amigos", "Tú"))])

    o["zapatero"] = escena("zapatero", f"""
    {num("zapatero", "3 · ZAPATERO")}
    {cita("za-1", "SÁNCHEZ", "Pongo la <mark>mano en el fuego</mark> por él", 620, 78)}
    <svg id="za-f" viewBox="0 0 120 160" style="position:absolute;left:820px;top:520px;width:170px">
      <path d="M60 4 C70 40 110 60 110 104 A50 50 0 0 1 10 104 C10 76 30 64 34 40 C44 56 52 60 56 72 C62 52 60 26 60 4 Z" fill="#ff7a1a"/>
      <path d="M60 60 C66 80 88 92 88 116 A28 28 0 0 1 32 116 C32 100 44 92 48 80 C54 90 58 92 60 98 Z" fill="#ffd43b"/></svg>
    {solo("zapatero")}
""", [pop("#zapatero-n", 0.05, 0.5), sube("#za-1", t("zapatero", "pongo")), pop("#za-f", t("zapatero", "fuego"), 0.2, 8)])

    o["ceuta"] = escena("ceuta", f"""
    {num("ceuta", "4 · CEUTA")}
    {cita("ce-1", "WILD", "No puedo entender que durante la crisis te vayas de <mark>vacaciones</mark>", 560, 44)}
    {cita("ce-2", "SÁNCHEZ", "No tengo información para acusar a <mark>Marruecos</mark>", 830, 44)}
    {cita("ce-3", "COLAU, ESA MAÑANA", "70.000 personas no se mueven sin que se dé cuenta el gobierno de Marruecos", 1080, 34)}
    {duo("ceuta")}
""", [pop("#ceuta-n", 0.05, 0.5), sube("#ce-1", t("ceuta", "entender")), sube("#ce-2", t("ceuta", "información")),
      pop("#ce-3", t("ceuta", "contrario"), 0.5, -2)])

    o["zasca"] = escena("zasca", f"""
    {num("zasca", "5 · EL ZASCA")}
    {cita("zs-1", "SÁNCHEZ", "Se ha cruzado una línea", 600, 60)}
    <div id="zs-2" class="sello" style="left:90px;right:90px;top:830px;font-size:78px;color:{NEGRO};border-color:{NEGRO}">«LOS DOS LA<br>HABÉIS CRUZADO»</div>
    <div id="zs-w" class="pill" style="top:1110px"><span style="background:{NEGRO};color:#fff">— JORDI WILD</span></div>
    {duo("zasca")}
""", [pop("#zasca-n", 0.05, 0.5), sube("#zs-1", t("zasca", "línea", d=-0.5)), sello_cae("#zs-2", t("zasca", "dos"), -3),
      pop("#zs-w", t("zasca", "cruzado", 2) if len([w for w in ESC["zasca"]["palabras"] if w["w"] == "cruzado"]) > 1 else t("zasca", "dos") + 0.6, 0.4)])

    o["final"] = escena("final", f"""
    <div id="f-q" class="titulo" style="top:440px;font-size:96px;color:#fff">¿QUIÉN GANÓ<br>LA ENTREVISTA?</div>
    <div id="f-a" class="sello" style="left:90px;top:700px;font-size:66px;color:{PS};border-color:{PS}">SÁNCHEZ</div>
    <div id="f-b" class="sello" style="left:580px;top:720px;font-size:66px;color:{NEGRO};border-color:{NEGRO}">WILD</div>
    <div id="f-com" class="pill bl" style="top:920px"><span>TE LEO EN COMENTARIOS</span></div>
    <div id="f-sig" class="pill" style="top:1040px"><span style="background:#111;color:#fff">SÍGUEME · ESTO VA A SER UNA LOCURA</span></div>
    {duo("final")}
""", [pop("#f-q", 0.05, 0.6), sello_cae("#f-a", t("final", "Sánchez"), -6), sello_cae("#f-b", t("final", "Wild"), 6),
      pop("#f-com", t("final", "comentarios"), 0.4), pop("#f-sig", t("final", "sígueme"), 0.4)])
    return o


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
    idx = base.index(DATOS).replace("<title>Abascal planta a Jordi Wild</title>", "<title>Sánchez ante Jordi Wild</title>")
    open(os.path.join(HF, "index.html"), "w", encoding="utf-8").write(idx)
    print("hf/ listo:", DATOS["total"], "s")


if __name__ == "__main__":
    main()
