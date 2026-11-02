# --- Escenas del TikTok «Si alguien te sigue por la calle de noche» (se insertan en video.py al montarlo) ---

POSES.update({
    "camina1": dict(rodilla=(26, 92), pie=(36, 188), cuello=(6, -150), cabeza=(12, -196), codo=(-16, -76), mano=(-26, -14),
                    codo2=(18, -76), mano2=(32, -16)),
    "camina2": dict(rodilla=(-12, 94), pie=(-30, 188), cuello=(6, -150), cabeza=(12, -196), codo=(18, -76), mano=(32, -16),
                    codo2=(-16, -76), mano2=(-26, -14)),
    "corre1": dict(rodilla=(40, 72), pie=(22, 172), cuello=(18, -146), cabeza=(30, -190), codo=(-28, -92), mano=(-46, -48),
                   codo2=(40, -96), mano2=(60, -130)),
    "corre2": dict(rodilla=(-18, 90), pie=(-62, 166), cuello=(18, -146), cabeza=(30, -190), codo=(34, -94), mano=(58, -126),
                   codo2=(-26, -92), mano2=(-44, -50)),
    "grita": dict(rodilla=(10, 94), pie=(14, 190), cuello=(8, -150), cabeza=(16, -196), codo=(50, -150), mano=(100, -176),
                  codo2=(-10, -80), mano2=(-4, -20)),
    "movil_oreja": dict(rodilla=(4, 95), pie=(2, 190), cuello=(2, -150), cabeza=(6, -196), codo=(34, -140), mano=(14, -190),
                        codo2=(-8, -74), mano2=(-4, -10)),
    "mira_atras": dict(rodilla=(10, 94), pie=(4, 190), cuello=(-6, -150), cabeza=(-16, -194), codo=(-16, -76), mano=(-26, -14),
                       codo2=(18, -76), mano2=(32, -16)),
})

PROTA = ((235, 128, 70), (205, 104, 52), (62, 86, 150), (48, 68, 122))     # chaqueta naranja y vaqueros
TESTIGO = ((210, 50, 50), (170, 36, 36), (60, 60, 70), (46, 46, 56))     # chaqueta roja
CABECERA = "QUÉ HACER SI TE SIGUEN"
SUELO = 760


def camina(t, vel=8):
    return pose_mix("camina1", "camina2", 0.5 + 0.5 * math.sin(t * vel))


def seguidor(L, x, y, t, s=0.62, anda=True, pose=None):
    """Perseguidor: figura oscura con capucha (siempre igual)."""
    p = pose or (camina(t + 0.6) if anda else "de_pie")
    info = persona(L, x, y - 190 * s, p, s, tipo="captor")
    cx, cy = info["cabeza"]
    r = 34 * s
    L.d.pieslice(P(cx - r * 1.25, cy - r * 1.35, cx + r * 1.25, cy + r * 1.1), 180, 360, fill=L.c((14, 14, 18)))
    return info


def prota(L, x, y, t, s=0.62, pose=None, ojos=1.0, boca=0.0, flip=False):
    return persona(L, x, y - 190 * s, pose or camina(t), s, ropa=PROTA, pelo=(60, 36, 24), ojos=ojos, boca=boca, flip=flip)


def calle(L, T, desplaza=0.0, lamparas=(110, 400), escaparate=None):
    rect(L, 0, 0, W, H, (8, 10, 20))
    # edificios del fondo con paralaje
    rs = random.Random(3)
    x = -((desplaza * 0.4) % 160) - 40
    k = 0
    while x < W + 40:
        w = 70 + (k * 37) % 50
        h = 220 + (k * 53) % 180
        rect(L, x, SUELO - 60 - h, x + w, SUELO - 60, (22, 24, 38))
        for wy in range(int(SUELO - 60 - h + 14), SUELO - 70, 26):
            for wx in range(int(x + 8), int(x + w - 12), 18):
                if random.Random(k * 1000 + wy * 7 + wx).random() < 0.25:
                    rect(L, wx, wy, wx + 9, wy + 12, (255, 210, 120))
        x += w + 6
        k += 1
    _ = rs
    # acera lejana, calzada y acera cercana
    rect(L, 0, SUELO - 60, W, SUELO, (70, 70, 80))
    rect(L, 0, SUELO, W, 880, (36, 38, 46))
    off = -(desplaza % 90)
    for xx in range(int(off) - 90, W + 90, 90):
        rect(L, xx, 816, xx + 46, 822, (200, 190, 120))
    rect(L, 0, 880, W, H, (70, 70, 80))
    for lx in lamparas:
        lx2 = lx - desplaza % (W + 200) if desplaza else lx
        rect(L, lx2 - 3, SUELO - 260, lx2 + 3, SUELO - 60, (40, 40, 46))
        rect(L, lx2 - 16, SUELO - 270, lx2 + 16, SUELO - 256, (50, 50, 56), r=3)
        circ(L, lx2, SUELO - 252, 7, fill=(255, 236, 180))
    if escaparate:
        ex, nombre, col = escaparate
        rect(L, ex, SUELO - 260, ex + 220, SUELO - 60, (40, 40, 50))
        rect(L, ex + 14, SUELO - 210, ex + 206, SUELO - 70, (255, 236, 190))
        rect(L, ex + 90, SUELO - 140, ex + 130, SUELO - 60, (200, 220, 230))
        rect(L, ex + 20, SUELO - 250, ex + 200, SUELO - 216, col, r=4)
        texto(L, nombre, ex + 110, SUELO - 233, 16, BLANCO, fuente="black", sombra=False)
        if nombre == "FARMACIA":
            cx_, cy_ = ex + 236, SUELO - 236
            rect(L, cx_ - 14, cy_ - 5, cx_ + 14, cy_ + 5, (60, 220, 110))
            rect(L, cx_ - 5, cy_ - 14, cx_ + 5, cy_ + 14, (60, 220, 110))


def mapa_luz(T, fuentes, ambiente=0.22, parpadeo=None):
    """fuentes: lista de (x, y, radio, intensidad, color)."""
    sw, sh = IW // 12, IH // 12
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    acc = np.ones((sh, sw, 3), np.float32) * ambiente * np.array([0.7, 0.78, 1.0], np.float32)
    for (x, y, r, k, col) in fuentes:
        ux, uy = x / W * sw, y / H * sh
        d2 = ((xx - ux) ** 2 + (yy - uy) ** 2) / (r / W * sw) ** 2
        acc += np.exp(-d2)[..., None] * k * np.array(col, np.float32)[None, None, :] / 255
    return Image.fromarray(np.clip(acc * 255, 0, 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    calle(L, T, desplaza=T * 60)
    x = 330
    mira = wt(e, "sigue") - 0.2 < t < wt(e, "sigue") + 1.0
    prota(L, x, SUELO - 20, t, pose="mira_atras" if mira else None, ojos=1.6 if mira else 1.0)
    seguidor(L, 110 + 6 * math.sin(t), SUELO - 24, t)
    st["luces"] = [(110 - (T * 60) % (W + 200), SUELO - 250, 150, 0.8, (255, 220, 160)),
                   (400 - (T * 60) % (W + 200), SUELO - 250, 150, 0.8, (255, 220, 160)), (330, 600, 120, 0.25, (255, 230, 200))]
    q = prog(t, wt(e, "casa") - 0.3, 0.3)
    st["overlay"].append(("titular", t, q))


def esc_porque(L, e, t, D, T, st):
    calle(L, T)
    # portal de su casa
    rect(L, 340, SUELO - 300, 520, SUELO - 60, (60, 50, 46))
    rect(L, 400, SUELO - 200, 470, SUELO - 60, (90, 64, 44))
    circ(L, 460, SUELO - 130, 4, fill=(220, 190, 110))
    rect(L, 360, SUELO - 280, 500, SUELO - 236, (240, 220, 160))
    texto(L, "Nº 14", 430, SUELO - 258, 18, (40, 30, 20), fuente="black", sombra=False)
    u = eio(prog(t, 0, 2.0))
    prota(L, lerp(230, 360, u), SUELO - 20, t, pose=None if u < 1 else "de_pie")
    seguidor(L, 80, SUELO - 24, t, anda=False)
    st["luces"] = [(430, SUELO - 240, 140, 0.7, (255, 220, 160)), (110, SUELO - 250, 150, 0.6, (255, 220, 160))]
    q = prog(t, wt(e, "vives") - 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("pin", q, t))
    qe = prog(t, wt(e, "expertos") - 0.3, 0.4)
    if qe > 0:
        st["overlay"].append(("fuente", qe))


def esc_comprobar(L, e, t, D, T, st):
    calle(L, T)
    tc = wt(e, "Cruza") - 0.2
    ts = wt(e, "mismo") - 0.6
    u1 = eio(prog(t, tc, 1.4))
    u2 = eio(prog(t, ts, 1.4))
    # cruzar: de la acera lejana a la cercana (más grande por la perspectiva)
    y1 = lerp(SUELO - 20, 930, u1)
    s1 = lerp(0.62, 0.8, u1)
    prota(L, lerp(300, 330, u1), y1, t, s=s1, pose="mira_atras" if t > ts + 1.0 else None, ojos=1.7 if t > ts + 1 else 1)
    y2 = lerp(SUELO - 24, 930, u2)
    s2 = lerp(0.62, 0.8, u2)
    seguidor(L, lerp(110, 150, u2), y2, t, s=s2)
    st["luces"] = [(110, SUELO - 250, 150, 0.7, (255, 220, 160)), (400, SUELO - 250, 150, 0.7, (255, 220, 160))]
    qa = prog(t, wt(e, "casualidad") - 0.4, 0.3)
    if qa > 0:
        st["overlay"].append(("alerta", qa, t))
    st["latido"] = True


def esc_luz(L, e, t, D, T, st):
    calle(L, T, escaparate=(300, "FARMACIA", (40, 160, 90)), lamparas=(110,))
    te = wt(e, "Entra") - 0.2
    u = eio(prog(t, 0.3, te - 0.3))
    if t < te + 0.5:
        prota(L, lerp(120, 400, u), SUELO - 20, t, pose=None if u < 1 else "de_pie")
    sx = lerp(20, 140, u)
    seguidor(L, sx, SUELO - 24, t, anda=u < 1, pose=None if u < 1 else "de_pie")
    st["luces"] = [(410, SUELO - 160, 230, 1.1, (230, 255, 230)), (110, SUELO - 250, 150, 0.5, (255, 220, 160))]
    sitios = [("bar", "BAR"), ("tienda", "TIENDA"), ("farmacia", "FARMACIA")]
    for j, (pal, txt) in enumerate(sitios):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("chip", txt, j, q))


def esc_llamar(L, e, t, D, T, st):
    # dentro de la farmacia, a salvo junto al mostrador
    rect(L, 0, 0, W, H, (220, 236, 226))
    rect(L, 0, 300, W, 760, (236, 246, 240))
    for k in range(4):
        rect(L, 20, 340 + k * 70, 240, 346 + k * 70, (180, 200, 190))
        for j in range(6):
            rect(L, 30 + j * 34, 310 + k * 70, 52 + j * 34, 340 + k * 70, [(200, 80, 80), (80, 140, 200), (240, 200, 80)][(j + k) % 3])
    rect(L, 0, 760, W, H, (200, 210, 206))
    rect(L, 260, 640, 540, 760, (140, 180, 160))
    prota(L, 160, SUELO, t, s=0.8, pose="movil_oreja")
    st["luces"] = None
    st["overlay"].append(("telefono", t, e))


def esc_like(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (40, 12, 16))
    st["luces"] = None
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))


def esc_grita(L, e, t, D, T, st):
    calle(L, T, lamparas=(110, 420))
    tg = wt(e, "Grita") - 0.2
    tt = wt(e, "Tú") - 0.2
    huye = eio(prog(t, tt + 1.4, 1.2))
    prota(L, 240, SUELO - 20, t, pose="grita" if t > tg else "de_pie", ojos=1.5, boca=1.0 if t > tg else 0)
    if huye <= 0:
        seguidor(L, 120, SUELO - 24, t, anda=False)
    else:
        seguidor(L, lerp(120, -120, huye), SUELO - 24, t * 1.8, pose=pose_mix("corre1", "corre2", 0.5 + 0.5 * math.sin(t * 14)))
    # testigo con chaqueta roja que se gira y llama
    gira = t > tt + 0.6
    persona(L, 440, SUELO - 20 - 190 * 0.62, "movil_oreja" if gira else "de_pie", 0.62, ropa=TESTIGO, pelo=(30, 30, 30),
            flip=gira, ojos=1.4 if gira else 1.0)
    st["luces"] = [(110, SUELO - 250, 150, 0.7, (255, 220, 160)), (420, SUELO - 250, 150, 0.8, (255, 220, 160)),
                   (240, 600, 120, 0.3, (255, 230, 200))]
    if t > tt:
        st["overlay"].append(("bocadillo", prog(t, tt, 0.25)))
    if t > tg and t < tt:
        st["overlay"].append(("ruido", prog(t, tg, 0.2), t))
    qr = prog(t, wt(e, "reacciona") - 0.3, 0.4)
    if qr > 0:
        st["overlay"].append(("efecto", qr))


def esc_prevencion(L, e, t, D, T, st):
    calle(L, T, desplaza=T * 50)
    prota(L, 270, SUELO - 20, t, s=0.7)
    st["luces"] = [(110 - (T * 50) % (W + 200), SUELO - 250, 150, 0.8, (255, 220, 160)),
                   (400 - (T * 50) % (W + 200), SUELO - 250, 150, 0.8, (255, 220, 160)), (270, 600, 140, 0.35, (255, 230, 200))]
    for j, (pal, txt, ok) in enumerate([("seguridad", "CAMINA SEGURO", True), ("cascos", "SIN CASCOS", False),
                                        ("móvil", "SIN MIRAR EL MÓVIL", False)]):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("regla", txt, j, q))
    qm = prog(t, wt(e, "objetivo") - 0.3, 0.4)
    if qm > 0:
        st["overlay"].append(("sello", "MAL OBJETIVO", qm))


def esc_final(L, e, t, D, T, st):
    calle(L, T)
    prota(L, 270, SUELO - 20, t, pose="de_pie")
    st["luces"] = [(110, SUELO - 250, 150, 0.7, (255, 220, 160)), (400, SUELO - 250, 150, 0.7, (255, 220, 160))]
    st["overlay"].append(("final", t, prog(t, wt(e, "Guarda") - 0.2, 0.3), prog(t, wt(e, "mándaselo") - 0.2, 0.3),
                          prog(t, wt(e, "sígueme") - 0.2, 0.3)))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "porque": esc_porque, "comprobar": esc_comprobar, "luz": esc_luz, "llamar": esc_llamar,
         "like": esc_like, "grita": esc_grita, "prevencion": esc_prevencion, "final": esc_final}


def corazon(O, x, y, r, col, a=1.0):
    if r <= 1:
        return
    circ(O, x - r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    circ(O, x + r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    poly(O, [(x - r * 1.02, y - r * 0.05), (x + r * 1.02, y - r * 0.05), (x, y + r * 0.95)], col, a=a)


def sello_t(O, txt, x, y, q, col=ROJO, size=34):
    if q <= 0:
        return
    s = 1 + 1.3 * (1 - eo3(q))
    w = ancho(txt, size * s) + 30 * s
    rect(O, x - w / 2, y - size * 0.75 * s, x + w / 2, y + size * 0.75 * s, (0, 0, 0), a=0.55 * q, r=10)
    rect(O, x - w / 2, y - size * 0.75 * s, x + w / 2, y + size * 0.75 * s, None, a=q, r=10, outline=col, w=5 * s)
    texto(O, txt, x, y, size * s, col, a=q, fuente="black", sombra=False)


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "titular":
            _, t, q = it
            s = 1 + 0.35 * math.exp(-t * 9)
            texto(O, "SI TE SIGUEN DE NOCHE", 270, 340, 30 * s, BLANCO, fuente="black")
            if q > 0:
                sello_t(O, "NUNCA VAYAS A CASA", 270, 410, q, size=30)
        elif tipo == "pin":
            _, q, t = it
            x, y = 430, 400 - 8 * math.sin(t * 3)
            s = eob(q)
            circ(O, x, y, 26 * s, fill=ROJO, a=q)
            poly(O, [(x - 18 * s, y + 10 * s), (x + 18 * s, y + 10 * s), (x, y + 44 * s)], ROJO, a=q)
            circ(O, x, y, 9 * s, fill=BLANCO, a=q)
            texto(O, "TU CASA", x, y + 66, 18, BLANCO, a=q, fuente="black")
            linea(O, [(140, 470), (400, 420)], ROJO, w=3, a=q * 0.7)
        elif tipo == "fuente":
            q = it[1]
            rect(O, 80, 860, 460, 900, (0, 0, 0), a=0.6 * q, r=20)
            texto(O, "Consejos generales de seguridad", 270, 880, 15, (220, 220, 230), a=q, fuente="bold", sombra=False)
        elif tipo == "alerta":
            _, q, t = it
            texto(O, "!", 160, 520 - 10 * math.sin(t * 10), 90 * eob(q) + 1, ROJO, a=q, fuente="black")
            sello_t(O, "NO ES CASUALIDAD", 270, 380, q, size=28)
        elif tipo == "chip":
            _, txt, j, q = it
            y = 360 + j * 54
            w = ancho(txt, 22) + 70
            rect(O, 270 - w / 2, y - 22, 270 + w / 2, y + 22, (40, 160, 90), a=q, r=22)
            circ(O, 270 - w / 2 + 24, y, 12, fill=BLANCO, a=q)
            linea(O, [(270 - w / 2 + 18, y), (270 - w / 2 + 23, y + 5), (270 - w / 2 + 31, y - 6)], (40, 160, 90), w=3, a=q)
            texto(O, txt, 270 + 14, y, 22, BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "telefono":
            _, t, e = it
            x0, y0 = 300, 330
            rect(O, x0, y0, x0 + 210, y0 + 380, (16, 16, 20), r=24)
            rect(O, x0 + 10, y0 + 14, x0 + 200, y0 + 366, (30, 120, 70), r=18)
            texto(O, "112", x0 + 105, y0 + 70, 40, BLANCO, fuente="black", sombra=False)
            seg = int(t)
            texto(O, f"00:{seg:02d}", x0 + 105, y0 + 110, 16, BLANCO, fuente="mono", sombra=False)
            items = [("dónde", "Dónde estás"), ("describe", "Cómo es"), ("cuelgues", "No cuelgues")]
            for j, (pal, txt) in enumerate(items):
                q = prog(t, wt(e, pal) - 0.2, 0.3)
                if q > 0:
                    y = y0 + 170 + j * 56
                    rect(O, x0 + 20, y - 20, x0 + 190, y + 20, BLANCO, a=q, r=12)
                    texto(O, "✓ " + txt, x0 + 30, y, 15, (30, 120, 70), a=q, fuente="sym", anchor="lm", sombra=False)
        elif tipo == "like":
            _, t, tl = it
            q = prog(t, tl, 0.35)
            s = eob(q) * (1 + 0.08 * math.sin(t * 8))
            corazon(O, 270, 560, 110 * s, (254, 44, 85), a=cl(q * 1.5))
            texto(O, "DALE LIKE", 270, 740, 46 * (0.8 + 0.2 * eob(q)), BLANCO, a=q, fuente="black")
            texto(O, "y compártelo", 270, 790, 22, (230, 200, 200), a=q, fuente="semi")
        elif tipo == "bocadillo":
            q = it[1]
            s = eob(q)
            rect(O, 60, 340, 480, 430, BLANCO, a=q, r=20)
            poly(O, [(220, 428), (250, 428), (230, 460)], BLANCO, a=q)
            texto(O, "¡TÚ, EL DE LA CHAQUETA ROJA,", 270, 370, 18 * s, (30, 30, 30), a=q, fuente="black", sombra=False)
            texto(O, "LLAMA A LA POLICÍA!", 270, 402, 22 * s, ROJO, a=q, fuente="black", sombra=False)
        elif tipo == "ruido":
            _, q, t = it
            for k in range(3):
                u = (t * 2 + k / 3) % 1
                O.d.arc(P(330 - 40 - 60 * u, 560 - 40 - 60 * u, 330 + 40 + 60 * u, 560 + 40 + 60 * u), 300, 60,
                        fill=O.c(AMARILLO, q * (1 - u)), width=3 * K)
        elif tipo == "efecto":
            q = it[1]
            rect(O, 70, 860, 470, 902, (0, 0, 0), a=0.6 * q, r=20)
            texto(O, "Pedir ayuda a alguien concreto funciona", 270, 881, 15, BLANCO, a=q, fuente="bold", sombra=False)
        elif tipo == "regla":
            _, txt, j, q = it
            y = 360 + j * 56
            col = VERDE if j == 0 else ROJO
            w = ancho(txt, 22) + 70
            rect(O, 270 - w / 2, y - 22, 270 + w / 2, y + 22, (0, 0, 0), a=0.65 * q, r=22)
            texto(O, ("✓ " if j == 0 else "✗ ") + txt, 270, y, 22, col, a=q, fuente="sym", sombra=False)
        elif tipo == "sello":
            _, txt, q = it
            sello_t(O, txt, 270, 560, q, col=VERDE, size=34)
        elif tipo == "final":
            _, t, qg, qm, qs = it
            if qg > 0:
                cx, cy, s = 150, 420, eob(qg)
                w, h = 46 * s, 60 * s
                poly(O, [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2),
                         (cx, cy + h / 2 - 17 * s), (cx - w / 2, cy + h / 2)], AMARILLO, a=qg)
                texto(O, "GUÁRDALO", cx, cy + 56, 16, BLANCO, a=qg, fuente="black")
            if qm > 0:
                texto(O, "↗", 390, 420, 60 * eob(qm) + 1, (40, 160, 230), a=qm, fuente="sym")
                texto(O, "MÁNDASELO", 390, 476, 16, BLANCO, a=qm, fuente="black")
            if qs > 0:
                rect(O, 130, 560, 410, 620, (254, 44, 85), a=qs, r=30)
                texto(O, "+ SEGUIR", 270, 590, 26, BLANCO, a=qs, fuente="black", sombra=False)


def cabecera(O, st):
    if st.get("sin_cabecera"):
        return
    w = ancho(CABECERA, 15) + 30
    rect(O, 270 - w / 2, 148, 270 + w / 2, 180, (180, 30, 30), a=0.92, r=16)
    texto(O, CABECERA, 270, 164, 15, BLANCO, fuente="black", sombra=False)
