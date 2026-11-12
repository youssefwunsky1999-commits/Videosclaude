"""Dibujos vectoriales originales (SVG plano, estilo explicativo con toques de neón). Nada de logos ni arte de Rockstar.

Cada función devuelve un <svg> con viewBox 0 0 600 560 que se coloca en el panel izquierdo de la escena. Las piezas
que se animan llevan un id con el prefijo de la escena (p)."""

import re

NEGRO = "#120822"
ROSA = "#ff2e88"
CIAN = "#00e5ff"
AMAR = "#ffd166"
NARAN = "#ff8c42"
VIOL = "#7b2ff7"
CREMA = "#fbf7ee"
ROJO = "#ff3b4d"
VERDE = "#3ccf6e"


_ENVOLVER = re.compile(r'<g id="([^"]+)"([^>]*?) transform="([^"]+)"([^>]*)>((?:(?!<g).)*?)</g>', re.S)


def _svg(cuerpo, p, extra=""):
    # GSAP sustituye el atributo transform al animar x/y/scale: el id va en un <g> exterior y el translate en uno interior
    cuerpo = _ENVOLVER.sub(lambda m: f'<g id="{m[1]}"{m[2]}{m[4]}><g transform="{m[3]}">{m[5]}</g></g>', cuerpo)
    return f'<svg class="dib" id="{p}-dib" viewBox="0 0 600 560" {extra}>{cuerpo}</svg>'


def _ojos(pid, x1, x2, y, r=8):
    return (f'<g id="{pid}-ojos" style="transform-origin:{(x1 + x2) / 2}px {y}px">'
            f'<circle cx="{x1}" cy="{y}" r="{r}" fill="#1b1b1b"/><circle cx="{x2}" cy="{y}" r="{r}" fill="#1b1b1b"/></g>')


def lucia(pid, x=0, y=0, s=1.0):
    """Mujer joven: pelo largo oscuro recogido en coleta, aros, camiseta de tirantes."""
    return f'''<g id="{pid}" class="pj" transform="translate({x} {y}) scale({s})">
  <path d="M60 470 C70 380 130 350 200 346 C270 350 330 380 340 470 Z" fill="{ROSA}"/>
  <path d="M150 352 C170 380 230 380 250 352 L262 470 L138 470 Z" fill="#c21d68"/>
  <rect x="172" y="290" width="56" height="70" rx="18" fill="#c98a5e"/>
  <path d="M104 190 C96 100 150 58 204 58 C262 58 306 102 296 196 C300 260 306 300 330 330 C290 336 270 300 266 270 Z" fill="#2a160e"/>
  <ellipse cx="200" cy="186" rx="80" ry="100" fill="#d79b6c"/>
  <path d="M118 170 C120 110 160 82 206 82 C250 84 282 112 284 168 C262 132 226 116 190 120 C160 124 136 140 118 170 Z" fill="#2a160e"/>
  <circle cx="122" cy="214" r="13" fill="none" stroke="{AMAR}" stroke-width="5"/><circle cx="278" cy="214" r="13" fill="none" stroke="{AMAR}" stroke-width="5"/>
  <rect x="150" y="158" width="38" height="7" rx="3" fill="#2a160e" transform="rotate(-6 169 161)"/><rect x="212" y="158" width="38" height="7" rx="3" fill="#2a160e" transform="rotate(6 231 161)"/>
  {_ojos(pid, 170, 230, 186)}
  <path d="M200 194 L191 224 Q200 230 209 224 Z" fill="#c4865a"/>
  <path d="M180 248 Q200 260 220 248" stroke="#8a2a3a" stroke-width="6" fill="none" stroke-linecap="round"/>
</g>'''


def jason(pid, x=0, y=0, s=1.0):
    """Hombre de unos treinta: pelo corto castaño, barba de pocos días, camisa abierta sobre camiseta."""
    return f'''<g id="{pid}" class="pj" transform="translate({x} {y}) scale({s})">
  <path d="M40 470 C55 380 120 350 200 346 C280 350 345 380 360 470 Z" fill="#2b6cb0"/>
  <path d="M160 350 L200 470 L240 350 Z" fill="#e8e3d6"/>
  <path d="M160 350 L140 470 L118 470 L140 360 Z M240 350 L260 470 L282 470 L260 360 Z" fill="#1f4f86"/>
  <rect x="166" y="286" width="68" height="74" rx="20" fill="#d9a77f"/>
  <ellipse cx="112" cy="196" rx="17" ry="26" fill="#d9a77f"/><ellipse cx="288" cy="196" rx="17" ry="26" fill="#d9a77f"/>
  <ellipse cx="200" cy="186" rx="88" ry="106" fill="#e6b48c"/>
  <path d="M110 170 C104 90 152 62 206 64 C262 66 300 98 292 172 C282 128 258 108 230 104 C200 98 160 104 140 118 C122 132 114 150 110 170 Z" fill="#5a3a22"/>
  <path d="M114 200 C118 276 160 304 200 306 C240 304 282 276 286 200 C276 236 262 256 240 262 C222 250 178 250 160 262 C138 256 124 236 114 200 Z" fill="#7a5236" opacity=".55"/>
  <rect x="146" y="152" width="44" height="9" rx="4" fill="#5a3a22"/><rect x="210" y="152" width="44" height="9" rx="4" fill="#5a3a22"/>
  {_ojos(pid, 170, 230, 184)}
  <path d="M200 190 L189 226 Q200 233 211 226 Z" fill="#cf9a72"/>
  <path d="M182 258 Q200 266 218 258" stroke="#6a2f22" stroke-width="6" fill="none" stroke-linecap="round"/>
</g>'''


def calendario(p):
    return _svg(f'''
  <rect x="90" y="70" width="420" height="420" rx="36" fill="{CREMA}"/>
  <rect x="90" y="70" width="420" height="120" rx="36" fill="{ROSA}"/><rect x="90" y="150" width="420" height="40" fill="{ROSA}"/>
  <rect x="170" y="40" width="26" height="70" rx="13" fill="{NEGRO}"/><rect x="404" y="40" width="26" height="70" rx="13" fill="{NEGRO}"/>
  <text x="300" y="160" text-anchor="middle" font-family="League Gothic" font-size="92" fill="#fff" letter-spacing="6">NOVIEMBRE</text>
  <text id="{p}-dia" x="300" y="402" text-anchor="middle" font-family="League Gothic" font-size="210" fill="{NEGRO}">19</text>
  <text x="300" y="470" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="#6b6f80">JUEVES · 2026</text>
  <circle id="{p}-circ" cx="300" cy="330" r="112" fill="none" stroke="{ROSA}" stroke-width="10" stroke-dasharray="710" stroke-dashoffset="710" stroke-linecap="round"/>''', p)


def consolas(p):
    return _svg(f'''
  <ellipse cx="300" cy="500" rx="260" ry="26" fill="#000" opacity=".35"/>
  <g id="{p}-c1"><path d="M110 120 C150 100 200 100 230 120 L240 490 L100 490 Z" fill="#f2f2f5"/>
    <path d="M150 112 L170 112 L178 490 L146 490 Z" fill="{NEGRO}"/>
    <rect x="200" y="140" width="10" height="320" rx="5" fill="{CIAN}" opacity=".7"/></g>
  <g id="{p}-c2"><rect x="340" y="150" width="180" height="340" rx="18" fill="#1d1d24"/>
    <circle cx="430" cy="190" r="22" fill="#2c2c36"/><circle cx="430" cy="190" r="12" fill="{VERDE}"/>
    <rect x="360" y="440" width="140" height="10" rx="5" fill="#2c2c36"/></g>
  <g id="{p}-mando"><path d="M210 300 C240 280 360 280 390 300 C420 320 430 380 410 400 C390 420 370 400 350 380 L250 380 C230 400 210 420 190 400 C170 380 180 320 210 300 Z" fill="{VIOL}"/>
    <circle cx="250" cy="330" r="14" fill="#fff" opacity=".8"/><circle cx="350" cy="320" r="8" fill="{AMAR}"/><circle cx="370" cy="340" r="8" fill="{ROSA}"/></g>''', p)


def pc(p):
    return _svg(f'''
  <rect x="70" y="70" width="460" height="300" rx="22" fill="#23233a" stroke="{CIAN}" stroke-width="8"/>
  <rect x="96" y="96" width="408" height="248" rx="8" fill="#0d0d1d"/>
  <text x="300" y="240" text-anchor="middle" font-family="League Gothic" font-size="110" fill="#3a3a5c">PC</text>
  <rect x="260" y="370" width="80" height="70" fill="#23233a"/><rect x="180" y="440" width="240" height="22" rx="11" fill="#23233a"/>
  <rect x="120" y="480" width="360" height="40" rx="10" fill="#2c2c46"/>
  <g id="{p}-x" style="transform-origin:300px 220px"><path d="M170 110 L430 330 M430 110 L170 330" stroke="{ROJO}" stroke-width="30" stroke-linecap="round"/></g>''', p)


def despidos(p):
    return _svg(f'''
  <rect x="120" y="60" width="360" height="430" rx="18" fill="#2a2140"/>
  <rect x="150" y="90" width="300" height="370" rx="8" fill="#3b2f5c"/>
  <circle cx="420" cy="290" r="12" fill="{AMAR}"/>
  <g id="{p}-caja"><path d="M150 360 L450 360 L430 500 L170 500 Z" fill="#c8915a"/><path d="M150 360 L450 360 L470 330 L130 330 Z" fill="#e0aa70"/>
    <rect x="200" y="290" width="40" height="70" rx="6" fill="{CIAN}"/><rect x="260" y="270" width="70" height="90" rx="8" fill="{VERDE}"/>
    <circle cx="370" cy="320" r="34" fill="{ROSA}"/></g>
  <g id="{p}-sobre" transform="translate(300 160)"><rect x="-120" y="-60" width="240" height="140" rx="14" fill="{CREMA}"/>
    <path d="M-120 -60 L0 20 L120 -60" stroke="#c9c2b0" stroke-width="8" fill="none"/>
    <text x="0" y="62" text-anchor="middle" font-family="Inter" font-weight="900" font-size="28" fill="{ROJO}">CONFIDENCIAL</text></g>''', p)


def regla(p):
    marcas = "".join(f'<rect x="{90 + i * 42}" y="410" width="6" height="{40 if i % 2 == 0 else 24}" fill="{NEGRO}"/>' for i in range(11))
    return _svg(f'''
  <path d="M150 90 C220 70 300 80 360 110 C420 150 440 220 470 300 L380 320 C350 260 300 220 240 200 C190 180 150 150 150 90 Z" fill="#1fa37a" opacity=".85"/>
  <rect x="70" y="400" width="460" height="90" rx="12" fill="{AMAR}"/>{marcas}
  <g id="{p}-q" style="transform-origin:300px 220px"><circle cx="300" cy="220" r="120" fill="{ROSA}"/>
    <text x="300" y="285" text-anchor="middle" font-family="League Gothic" font-size="200" fill="#fff">?</text></g>''', p)


def movil(p):
    return _svg(f'''
  <rect x="170" y="40" width="260" height="480" rx="40" fill="#1d1d24" stroke="{ROSA}" stroke-width="8"/>
  <rect x="192" y="80" width="216" height="400" rx="12" fill="#2a1840"/>
  <rect x="210" y="100" width="180" height="120" rx="10" fill="{NARAN}"/><circle cx="350" cy="140" r="22" fill="{AMAR}"/>
  <rect x="210" y="236" width="140" height="14" rx="7" fill="#fff" opacity=".7"/><rect x="210" y="260" width="100" height="14" rx="7" fill="#fff" opacity=".4"/>
  <g id="{p}-h1" transform="translate(110 200)"><path d="M0 20 C0 -10 40 -10 40 20 C40 -10 80 -10 80 20 C80 50 40 70 40 80 C40 70 0 50 0 20 Z" fill="{ROJO}"/></g>
  <g id="{p}-h2" transform="translate(430 300)"><path d="M0 20 C0 -10 40 -10 40 20 C40 -10 80 -10 80 20 C80 50 40 70 40 80 C40 70 0 50 0 20 Z" fill="{ROSA}"/></g>
  <g id="{p}-h3" transform="translate(220 320)"><rect x="0" y="0" width="160" height="56" rx="28" fill="{CIAN}"/>
    <text x="80" y="38" text-anchor="middle" font-family="Inter" font-weight="900" font-size="26" fill="{NEGRO}">+10 MIL</text></g>''', p)


def cartel(p):
    letras = "WELCOME TO VICE CITY"
    return _svg(f'''
  <ellipse cx="300" cy="470" rx="290" ry="40" fill="#000" opacity=".35"/>
  <path d="M40 470 L40 330 C120 270 480 270 560 330 L560 470 Z" fill="#2a2140"/>
  <path d="M40 330 C120 270 480 270 560 330 L560 350 C480 292 120 292 40 350 Z" fill="{CIAN}" opacity=".6"/>
  {"".join(f'<rect x="{70 + i * 58}" y="370" width="34" height="80" rx="4" fill="{AMAR}" opacity=".55"/>' for i in range(8))}
  <g id="{p}-sign"><rect x="30" y="150" width="540" height="110" rx="14" fill="#160a2a" stroke="{ROSA}" stroke-width="6"/>
    <text x="300" y="228" text-anchor="middle" font-family="League Gothic" font-size="60" fill="#fff" letter-spacing="2"
      style="filter: drop-shadow(0 0 10px {ROSA}) drop-shadow(0 0 22px {ROSA})">{letras}</text>
    <rect x="140" y="260" width="10" height="40" fill="#555"/><rect x="450" y="260" width="10" height="40" fill="#555"/></g>
  <g id="{p}-heli" transform="translate(470 70)"><ellipse cx="0" cy="0" rx="46" ry="22" fill="#3a3a5c"/><rect x="30" y="-6" width="70" height="10" fill="#3a3a5c"/>
    <rect x="-70" y="-34" width="140" height="6" rx="3" fill="#aaa"/><line x1="0" y1="22" x2="0" y2="80" stroke="#aaa" stroke-width="3"/></g>''', p)


def pareja(p):
    return _svg(f'''
  <ellipse cx="300" cy="520" rx="280" ry="30" fill="#000" opacity=".35"/>
  {lucia(p + "-lu", -30, 60, 0.98)}
  {jason(p + "-ja", 230, 50, 1.0)}''', p)


def solo(p, quien):
    f = lucia if quien == "lucia" else jason
    return _svg(f'''<ellipse cx="300" cy="520" rx="220" ry="28" fill="#000" opacity=".35"/>{f(p + "-pj", 70, 40, 1.15)}''', p)


def tele(p):
    return _svg(f'''
  <rect x="50" y="70" width="500" height="320" rx="26" fill="#161625" stroke="{VIOL}" stroke-width="10"/>
  <rect x="78" y="96" width="444" height="268" rx="12" fill="#2a0f2f"/>
  <circle cx="300" cy="230" r="70" fill="{ROJO}"/><path d="M280 195 L335 230 L280 265 Z" fill="#fff"/>
  <rect x="96" y="330" width="408" height="10" rx="5" fill="#fff" opacity=".25"/><rect id="{p}-barra" x="96" y="330" width="408" height="10" rx="5" fill="{ROJO}" style="transform-origin:96px 335px"/>
  <rect x="250" y="390" width="100" height="60" fill="#161625"/><rect x="170" y="450" width="260" height="20" rx="10" fill="#161625"/>
  <g id="{p}-pop" transform="translate(470 420)"><path d="M-50 -40 L50 -40 L36 80 L-36 80 Z" fill="{CREMA}"/><path d="M-50 -40 L-36 80 L-22 80 L-30 -40 Z M-6 -40 L-2 80 L10 80 L14 -40 Z M30 -40 L22 80 L36 80 L50 -40 Z" fill="{ROJO}"/>
    {"".join(f'<circle cx="{cx}" cy="{cy}" r="16" fill="#fff6d8"/>' for cx, cy in ((-30, -46), (0, -56), (28, -46), (-12, -66), (14, -70)))}</g>''', p)


def musica(p):
    return _svg(f'''
  <g id="{p}-disco" style="transform-origin:280px 290px"><circle cx="280" cy="290" r="210" fill="#141414"/>
    {"".join(f'<circle cx="280" cy="290" r="{r}" fill="none" stroke="#2b2b2b" stroke-width="3"/>' for r in (190, 170, 150, 130, 110))}
    <circle cx="280" cy="290" r="70" fill="{ROSA}"/><circle cx="280" cy="290" r="10" fill="{NEGRO}"/>
    <path d="M200 160 A150 150 0 0 1 330 140" stroke="#fff" stroke-width="6" fill="none" opacity=".35"/></g>
  <g id="{p}-n1" transform="translate(470 120)"><ellipse cx="0" cy="60" rx="26" ry="20" fill="{CIAN}"/><rect x="20" y="-20" width="8" height="80" fill="{CIAN}"/><path d="M28 -20 C60 -10 60 20 40 30" stroke="{CIAN}" stroke-width="8" fill="none"/></g>
  <g id="{p}-n2" transform="translate(520 330)"><ellipse cx="0" cy="40" rx="20" ry="15" fill="{AMAR}"/><rect x="14" y="-30" width="7" height="70" fill="{AMAR}"/></g>''', p)


def coche(p):
    return _svg(f'''
  <ellipse cx="300" cy="430" rx="280" ry="26" fill="#000" opacity=".4"/>
  <g id="{p}-car"><path d="M40 380 L60 320 C120 300 170 250 250 240 C330 232 380 250 430 300 C500 306 550 320 560 360 L560 390 L40 390 Z" fill="{ROSA}"/>
    <path d="M200 300 C230 262 290 252 340 258 C370 262 390 280 410 300 Z" fill="#3a1d5c"/>
    <rect x="60" y="350" width="500" height="10" fill="#fff" opacity=".35"/>
    <circle cx="150" cy="392" r="46" fill="{NEGRO}"/><circle cx="150" cy="392" r="20" fill="#bbb"/>
    <circle cx="450" cy="392" r="46" fill="{NEGRO}"/><circle cx="450" cy="392" r="20" fill="#bbb"/>
    <rect x="530" y="340" width="26" height="14" rx="4" fill="{AMAR}"/></g>
  <g id="{p}-yate" transform="translate(110 90)"><path d="M0 70 L260 70 L220 120 L30 120 Z" fill="{CREMA}"/><path d="M60 70 L90 20 L200 20 L220 70 Z" fill="#e8e3d6"/>
    <rect x="100" y="34" width="90" height="20" rx="4" fill="{CIAN}" opacity=".8"/><path d="M-20 130 Q60 115 130 130 T280 130" stroke="{CIAN}" stroke-width="6" fill="none"/></g>''', p)


def regalo(p):
    return _svg(f'''
  <g id="{p}-caja"><rect x="130" y="250" width="340" height="250" rx="16" fill="{VIOL}"/>
    <rect x="110" y="200" width="380" height="80" rx="14" fill="#9b5cff"/>
    <rect x="275" y="200" width="50" height="300" fill="{AMAR}"/></g>
  <g id="{p}-lazo" style="transform-origin:300px 200px"><path d="M300 200 C240 120 170 140 200 190 C215 215 260 210 300 200 Z" fill="{AMAR}"/>
    <path d="M300 200 C360 120 430 140 400 190 C385 215 340 210 300 200 Z" fill="{AMAR}"/></g>
  <g id="{p}-et" transform="translate(470 150) rotate(12)"><rect x="-80" y="-30" width="160" height="60" rx="10" fill="{CREMA}"/>
    <text x="0" y="12" text-anchor="middle" font-family="League Gothic" font-size="40" fill="{ROSA}">20 NOV</text></g>''', p)


def caja(p):
    return _svg(f'''
  <g id="{p}-caja"><rect x="120" y="60" width="270" height="400" rx="16" fill="#1d4f9a"/>
    <rect x="140" y="90" width="230" height="300" rx="8" fill="#24164a"/>
    <circle cx="255" cy="200" r="70" fill="{NARAN}"/><rect x="140" y="250" width="230" height="140" fill="#3a1d5c"/>
    <text x="255" y="430" text-anchor="middle" font-family="League Gothic" font-size="40" fill="#fff">EDICIÓN FÍSICA</text></g>
  <g id="{p}-disco" transform="translate(470 180)"><circle r="90" fill="#d9dbe6"/><circle r="30" fill="#24164a"/>
    <path d="M-80 -80 L80 80" stroke="{ROJO}" stroke-width="22" stroke-linecap="round"/></g>
  <g id="{p}-cod" transform="translate(465 350) rotate(-8)"><rect x="-130" y="-50" width="260" height="100" rx="12" fill="{CREMA}"/>
    <text x="0" y="16" text-anchor="middle" font-family="Inter" font-weight="900" font-size="34" fill="{NEGRO}" letter-spacing="2">XXXX-XXXX</text></g>''', p)


def grafica(p):
    barras = "".join(f'<rect id="{p}-b{i}" x="{110 + i * 90}" y="{460 - h}" width="60" height="{h}" rx="8" fill="{c}" style="transform-origin:{140 + i * 90}px 460px"/>'
                     for i, (h, c) in enumerate(((90, VIOL), (150, VIOL), (210, ROSA), (300, ROSA), (390, AMAR))))
    return _svg(f'''<rect x="80" y="460" width="460" height="8" rx="4" fill="#fff" opacity=".6"/>{barras}
  <path id="{p}-fl" d="M130 380 L230 330 L320 260 L410 170 L500 70" stroke="{CIAN}" stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="520" stroke-dashoffset="520"/>
  <path d="M500 70 L470 76 M500 70 L494 100" stroke="{CIAN}" stroke-width="10" stroke-linecap="round"/>''', p)


def check(p):
    return _svg(f'''
  <g id="{p}-ok" style="transform-origin:300px 270px"><path d="M300 40 L500 110 V260 C500 380 420 450 300 500 C180 450 100 380 100 260 V110 Z" fill="{VERDE}"/>
    <path d="M200 270 L270 340 L410 190" stroke="#fff" stroke-width="40" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>''', p)


def online(p):
    return _svg(f'''
  <circle cx="300" cy="260" r="200" fill="#1b2a5a" stroke="{CIAN}" stroke-width="8"/>
  <ellipse cx="300" cy="260" rx="90" ry="200" fill="none" stroke="{CIAN}" stroke-width="5" opacity=".6"/>
  <path d="M100 260 H500 M130 160 H470 M130 360 H470" stroke="{CIAN}" stroke-width="5" opacity=".6"/>
  {"".join(f'<g id="{p}-u{i}" transform="translate({x} {y})"><circle r="26" fill="{c}"/><circle cy="-6" r="10" fill="#fff"/><path d="M-14 16 C-10 2 10 2 14 16" fill="#fff"/></g>' for i, (x, y, c) in enumerate(((150, 140, ROSA), (460, 160, AMAR), (170, 400, VERDE), (440, 390, NARAN))))}
  <g id="{p}-q" style="transform-origin:300px 260px"><circle cx="300" cy="260" r="80" fill="{ROSA}"/>
    <text x="300" y="312" text-anchor="middle" font-family="League Gothic" font-size="150" fill="#fff">?</text></g>''', p)


def fps(p):
    return _svg(f'''
  <path d="M90 380 A210 210 0 0 1 510 380" stroke="#2c2c46" stroke-width="44" fill="none" stroke-linecap="round"/>
  <path d="M90 380 A210 210 0 0 1 300 170" stroke="{AMAR}" stroke-width="44" fill="none" stroke-linecap="round"/>
  <path d="M300 170 A210 210 0 0 1 510 380" stroke="{CIAN}" stroke-width="44" fill="none" stroke-linecap="round" stroke-dasharray="14 18" opacity=".55"/>
  <g id="{p}-aguja" style="transform-origin:300px 380px"><path d="M292 380 L300 200 L308 380 Z" fill="#fff"/></g>
  <circle cx="300" cy="380" r="22" fill="#fff"/>
  <text x="300" y="480" text-anchor="middle" font-family="League Gothic" font-size="110" fill="#fff">30 FPS</text>
  <text x="525" y="440" text-anchor="middle" font-family="League Gothic" font-size="56" fill="{CIAN}" opacity=".8">¿60?</text>''', p)


def lupa(p):
    film = "".join(f'<rect x="{70 + i * 96}" y="160" width="80" height="60" rx="6" fill="#3b2f5c"/>' for i in range(5))
    return _svg(f'''
  <rect x="50" y="130" width="500" height="200" rx="10" fill="#1d1d24"/>{film}
  {"".join(f'<rect x="{70 + i * 48}" y="140" width="22" height="12" rx="2" fill="#fff" opacity=".5"/><rect x="{70 + i * 48}" y="306" width="22" height="12" rx="2" fill="#fff" opacity=".5"/>' for i in range(10))}
  <rect x="70" y="236" width="460" height="56" rx="6" fill="#3b2f5c"/>
  <g id="{p}-lupa"><circle cx="330" cy="240" r="120" fill="{CIAN}" fill-opacity=".18" stroke="#fff" stroke-width="22"/>
    <path d="M420 330 L520 450" stroke="#fff" stroke-width="40" stroke-linecap="round"/>
    <text x="330" y="270" text-anchor="middle" font-family="League Gothic" font-size="100" fill="{ROSA}">¿?</text></g>''', p)


def descarga(p):
    return _svg(f'''
  <rect x="70" y="90" width="460" height="290" rx="22" fill="#161625" stroke="{CIAN}" stroke-width="8"/>
  <path d="M300 140 L300 260 M250 215 L300 265 L350 215" stroke="#fff" stroke-width="22" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="130" y="300" width="340" height="34" rx="17" fill="#2c2c46"/>
  <rect id="{p}-prog" x="130" y="300" width="340" height="34" rx="17" fill="{VERDE}" style="transform-origin:130px 317px"/>
  <text id="{p}-pct" x="300" y="440" text-anchor="middle" font-family="League Gothic" font-size="80" fill="#fff">0 %</text>''', p)


def reloj(p):
    marcas = "".join(f'<rect x="296" y="76" width="8" height="30" rx="4" fill="{NEGRO}" transform="rotate({i * 30} 300 280)"/>' for i in range(12))
    return _svg(f'''
  <circle cx="300" cy="280" r="230" fill="{CREMA}" stroke="{ROSA}" stroke-width="18"/>{marcas}
  <g id="{p}-hor" style="transform-origin:300px 280px"><rect x="290" y="150" width="20" height="140" rx="10" fill="{NEGRO}"/></g>
  <g id="{p}-min" style="transform-origin:300px 280px"><rect x="294" y="100" width="12" height="190" rx="6" fill="{ROSA}"/></g>
  <circle cx="300" cy="280" r="18" fill="{NEGRO}"/>
  <text x="300" y="420" text-anchor="middle" font-family="League Gothic" font-size="64" fill="{NEGRO}">00:00</text>''', p)


def poster(p):
    return _svg(f'''
  <g id="{p}-pos" transform="rotate(-5 300 280)"><rect x="110" y="40" width="380" height="460" rx="10" fill="{CREMA}"/>
    <rect x="130" y="60" width="340" height="420" rx="6" fill="#1fa37a"/>
    <path d="M220 100 C300 90 380 120 400 200 C420 280 380 330 400 420 L330 440 C320 380 280 340 260 290 C240 240 200 200 220 100 Z" fill="#7ed6a8"/>
    <circle cx="350" cy="380" r="12" fill="{ROSA}"/>
    <text x="300" y="470" text-anchor="middle" font-family="League Gothic" font-size="44" fill="#fff" letter-spacing="4">LEONIDA</text></g>
  <g id="{p}-reg" transform="translate(490 430)"><rect x="-70" y="-50" width="140" height="100" rx="12" fill="{VIOL}"/><rect x="-12" y="-50" width="24" height="100" fill="{AMAR}"/>
    <text x="0" y="90" text-anchor="middle" font-family="League Gothic" font-size="40" fill="{AMAR}">GRATIS</text></g>''', p)


def mapa(p):
    """Leonida dibujada a mano: península tipo Florida, ciudad al sureste, cayos al sur, pantanos, norte con montaña."""
    return f'''<svg class="mapa" id="{p}-mapa" viewBox="0 0 900 700">
  <rect x="0" y="0" width="900" height="700" rx="30" fill="#0b2a4a" opacity=".85"/>
  {"".join(f'<path d="M{20 + i * 70} {60 + (i % 3) * 200} q20 -10 40 0 t40 0" stroke="{CIAN}" stroke-width="3" fill="none" opacity=".35"/>' for i in range(12))}
  <path id="{p}-tierra" d="M40 70 L560 60 C600 62 620 90 610 130 C600 200 640 260 670 330 C700 400 720 470 700 540 C690 580 650 600 620 590
     C590 580 570 540 540 500 C510 450 470 400 440 340 C420 300 380 270 330 240 C280 210 210 180 150 170 C100 162 60 150 40 140 Z"
     fill="#1fa37a" stroke="#7ed6a8" stroke-width="6"/>
  <path d="M470 380 C500 420 560 450 600 520 L560 540 C530 480 480 450 450 410 Z" fill="#2c7a54" opacity=".8"/>
  <path d="M120 120 L160 80 L200 120 Z M170 120 L210 70 L250 120 Z" fill="#cfe9dc"/>
  {"".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1fa37a" stroke="#7ed6a8" stroke-width="3"/>' for x, y, r in ((610, 620, 12), (575, 640, 10), (535, 655, 9), (495, 665, 8), (455, 670, 7)))}
  <g id="{p}-vc"><circle cx="680" cy="470" r="26" fill="{ROSA}"/><circle cx="680" cy="470" r="46" fill="none" stroke="{ROSA}" stroke-width="5"/></g>
  <circle id="{p}-p1" cx="540" cy="655" r="14" fill="{AMAR}"/>
  <circle id="{p}-p2" cx="520" cy="440" r="14" fill="{AMAR}"/>
  <circle id="{p}-p3" cx="120" cy="150" r="14" fill="{AMAR}"/>
  <circle id="{p}-p4" cx="430" cy="140" r="14" fill="{AMAR}"/>
  <circle id="{p}-p5" cx="185" cy="105" r="14" fill="{AMAR}"/>
</svg>'''


POS_MAPA = {  # posición (en px del viewBox 900x700) de cada etiqueta del mapa
    "LEONIDA": (330, 300), "VICE CITY": (690, 400), "CAYOS DE LEONIDA": (560, 610), "GRASSRIVERS": (470, 470),
    "PORT GELLHORN": (150, 215), "AMBROSIA": (470, 200), "MONTE KALAGA": (200, 45),
}

DIBUJOS = {"calendario": calendario, "consolas": consolas, "pc": pc, "despidos": despidos, "regla": regla, "movil": movil,
           "cartel": cartel, "pareja": pareja, "lucia": lambda p: solo(p, "lucia"), "jason": lambda p: solo(p, "jason"),
           "tele": tele, "musica": musica, "coche": coche, "regalo": regalo, "caja": caja, "grafica": grafica,
           "check": check, "online": online, "fps": fps, "lupa": lupa, "descarga": descarga, "reloj": reloj, "poster": poster}
