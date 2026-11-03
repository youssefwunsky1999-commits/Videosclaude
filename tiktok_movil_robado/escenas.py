# --- Escenas del TikTok «Imagínate que te roban el móvil: los primeros 10 minutos» ---
POSES.update({
    "movil_mira": dict(rodilla=(4, 95), pie=(2, 190), cuello=(4, -150), cabeza=(12, -194), codo=(30, -96), mano=(54, -120),
                       codo2=(26, -90), mano2=(50, -116)),
    "susto": dict(rodilla=(4, 95), pie=(2, 190), cuello=(-4, -148), cabeza=(-10, -192), codo=(-40, -150), mano=(-20, -200),
                  codo2=(40, -150), mano2=(20, -200)),
    "teclea": dict(rodilla=(70, 0), pie=(72, 85), cuello=(4, -118), cabeza=(14, -158), codo=(40, -60), mano=(84, -66),
                   codo2=(36, -56), mano2=(80, -62)),
})
FONDO_C = (232, 236, 244)


def movil(L, x, y, s=1.0, a=1.0, pantalla=(30, 34, 46)):
    rect(L, x - 14 * s, y - 26 * s, x + 14 * s, y + 26 * s, (20, 20, 24), a=a, r=5 * s)
    rect(L, x - 11 * s, y - 22 * s, x + 11 * s, y + 22 * s, pantalla, a=a, r=3 * s)


def ventana_ui(L, x0, y0, x1, y1, titulo, a=1.0):
    rect(L, x0, y0, x1, y1, BLANCO, a=a, r=14)
    rect(L, x0, y0, x1, y0 + 40, (220, 224, 232), a=a, r=14)
    rect(L, x0, y0 + 26, x1, y0 + 40, (220, 224, 232), a=a)
    for k, c in enumerate(((255, 96, 86), (255, 189, 46), (40, 200, 64))):
        circ(L, x0 + 22 + k * 20, y0 + 20, 6, fill=c, a=a)
    texto(L, titulo, (x0 + x1) / 2, y0 + 20, 14, (60, 60, 70), a=a, fuente="black", sombra=False)


def boton(L, x, y, txt, q, col=(40, 120, 230), pulsado=0.0):
    if q <= 0:
        return
    w = ancho(txt, 18) + 40
    s = 1 - 0.06 * pulsado
    rect(L, x - w / 2 * s, y - 22 * s, x + w / 2 * s, y + 22 * s, col, a=q, r=22)
    texto(L, txt, x, y, 18 * s, BLANCO, a=q, fuente="black", sombra=False)


def esc_gancho(L, e, t, D, T, st):
    calle(L, T)
    tirón = prog(t, 0.0, 0.5)
    huye = prog(t, 0.6, D - 0.6)
    persona(L, 230, SUELO - 20 - 190 * 0.85, "susto" if tirón >= 1 else "movil_mira", 0.85, ropa=PROTA, pelo=(60, 36, 24),
            ojos=1.8 if tirón >= 1 else 1, boca=0.7 if tirón >= 1 else 0)
    xl = lerp(330, 640, eio(huye))
    info = seguidor(L, xl, SUELO - 24, t * 1.6, s=0.85, pose=camina(t * 1.6, 12) if huye > 0 else "de_pie")
    mx, my = info["mano"]
    movil(L, mx, my, 0.9, pantalla=(90, 160, 255))
    st["cam"] = (1.2 - 0.1 * eio(t / D), 300, 560)
    st["alarma"] = t
    st["luces"] = [(110, SUELO - 250, 190, 1.0, (255, 220, 160)), (400, SUELO - 250, 190, 1.0, (255, 220, 160)),
                   (270, 600, 160, 0.35, (255, 230, 200))]
    st["shake"] = 4 if t < 0.5 else 0
    st["overlay"].append(("titular", t, "TE ROBAN EL MÓVIL", "LOS PRIMEROS 10 MIN", 1.0))
    st["sin_cabecera"] = True


def icono(L, tipo, x, y, s=1.0, a=1.0):
    if tipo == "correo":
        rect(L, x - 40 * s, y - 28 * s, x + 40 * s, y + 28 * s, BLANCO, a=a, r=6)
        linea(L, [(x - 40 * s, y - 28 * s), (x, y + 4 * s), (x + 40 * s, y - 28 * s)], (200, 60, 60), w=4, a=a)
    elif tipo == "banco":
        poly(L, [(x - 44 * s, y - 14 * s), (x, y - 44 * s), (x + 44 * s, y - 14 * s)], (240, 200, 80), a)
        for k in range(4):
            rect(L, x - 34 * s + k * 22 * s, y - 10 * s, x - 26 * s + k * 22 * s, y + 26 * s, (240, 200, 80), a=a)
        rect(L, x - 44 * s, y + 26 * s, x + 44 * s, y + 34 * s, (240, 200, 80), a=a)
    else:   # mensaje con código
        rect(L, x - 44 * s, y - 30 * s, x + 44 * s, y + 24 * s, (60, 200, 110), a=a, r=14)
        poly(L, [(x - 20 * s, y + 22 * s), (x - 30 * s, y + 40 * s), (x, y + 22 * s)], (60, 200, 110), a)
        texto(L, "4821", x, y - 4 * s, 22 * s, BLANCO, a=a, fuente="black", sombra=False)


def esc_porque(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (24, 28, 40))
    rect(L, 150, 330, 390, 830, (16, 16, 20), r=36)
    rect(L, 166, 350, 374, 810, (40, 46, 66), r=26)
    for j, (pal, tipo, lab) in enumerate((("correo", "correo", "CORREO"), ("banco", "banco", "BANCO"),
                                          ("códigos", "codigo", "CÓDIGOS"))):
        q = prog(t, wt(e, pal) - 0.3, 0.3)
        if q > 0:
            y = 440 + j * 130
            icono(L, tipo, 270, y, eob(q), a=q)
            texto(L, lab, 270, y + 52, 15, BLANCO, a=q, fuente="black", sombra=False)
    st["paso"] = ("!", "QUÉ HAY EN JUEGO")


def esc_uno(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, FONDO_C)
    ventana_ui(L, 40, 320, 500, 820, "Buscar  ·  Encontrar mi dispositivo")
    # mapa
    rect(L, 56, 366, 484, 640, (214, 230, 214))
    for k in range(6):
        linea(L, [(56, 400 + k * 44), (484, 380 + k * 50)], (250, 250, 250), w=6)
    linea(L, [(200, 366), (260, 640)], (250, 250, 250), w=8)
    py = 500 - 10 * abs(math.sin(T * 3))
    circ(L, 300, py, 18, fill=ROJO)
    poly(L, [(286, py + 8), (314, py + 8), (300, py + 34)], ROJO)
    circ(L, 300, py, 7, fill=BLANCO)
    qp = prog(t, wt(e, "perdido") - 0.3, 0.3)
    ql = prog(t, wt(e, "bloquéalo") - 0.3, 0.3)
    boton(L, 270, 690, "MARCAR COMO PERDIDO", prog(t, wt(e, "Buscar") - 0.2, 0.3), pulsado=qp)
    boton(L, 270, 760, "BLOQUEAR", prog(t, wt(e, "Encontrar") - 0.2, 0.3), col=ROJO, pulsado=ql)
    if qp > 0:
        texto(L, "✓", 470, 690, 30, VERDE, a=qp, fuente="sym")
    if ql > 0:
        texto(L, "✓", 470, 760, 30, VERDE, a=ql, fuente="sym")
    st["overlay"].append(("fuente", prog(t, wt(e, "bloquéalo") + 0.2, 0.4), "Borrarlo en remoto, solo si das el móvil por perdido"))
    st["paso"] = (1, "LOCALIZA Y BLOQUEA")


def sim(L, x, y, s=1.0, a=1.0, bloqueada=0.0):
    poly(L, [(x - 50 * s, y - 70 * s), (x + 26 * s, y - 70 * s), (x + 50 * s, y - 46 * s), (x + 50 * s, y + 70 * s),
             (x - 50 * s, y + 70 * s)], (230, 232, 240), a)
    rect(L, x - 30 * s, y - 30 * s, x + 30 * s, y + 34 * s, (214, 176, 90), a=a, r=6)
    for k in range(3):
        linea(L, [(x - 30 * s, y - 14 * s + k * 18 * s), (x + 30 * s, y - 14 * s + k * 18 * s)], (170, 130, 60), w=2, a=a)
    if bloqueada > 0:
        q = bloqueada
        rect(L, x - 30, y + 30, x + 30, y + 80, ROJO, a=q, r=8)
        L.d.arc(P(x - 20, y + 2, x + 20, y + 46), 180, 360, fill=L.c(ROJO, q), width=7 * K)
        circ(L, x, y + 54, 6, fill=BLANCO, a=q)


def esc_dos(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, FONDO_C)
    persona(L, 120, 860 - 190 * 0.9, "movil_oreja", 0.9, ropa=PROTA, pelo=(60, 36, 24))
    qb = prog(t, wt(e, "bloqueen") - 0.3, 0.4)
    sim(L, 360, 520, 1.3, bloqueada=qb)
    qs = prog(t, wt(e, "SMS") - 0.3, 0.3)
    if qs > 0:
        rect(L, 260, 680, 480, 740, (60, 200, 110), a=qs, r=16)
        texto(L, "SMS del banco", 370, 710, 18, BLANCO, a=qs, fuente="black", sombra=False)
        linea(L, [(270, 690), (470, 730)], ROJO, w=6, a=qs)
    st["paso"] = (2, "BLOQUEA LA SIM")


def esc_like(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, FONDO_C)
    st["tinte"] = ((0, 0, 0), 0.55)
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    st["sin_cabecera"] = True


def esc_tres(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, FONDO_C)
    ventana_ui(L, 60, 330, 480, 620, "Correo · Cambiar contraseña")
    icono(L, "correo", 140, 420, 0.7)
    rect(L, 90, 470, 450, 520, (240, 242, 248), r=10, outline=(200, 204, 214), w=2)
    n = int(14 * prog(t, wt(e, "contraseña") - 0.3, 1.2))
    texto(L, "•" * n, 106, 495, 22, (40, 40, 50), fuente="sym", anchor="lm", sombra=False)
    qok = prog(t, wt(e, "todo") - 0.3, 0.3)
    boton(L, 270, 570, "GUARDAR", prog(t, wt(e, "contraseña"), 0.3), col=VERDE, pulsado=qok)
    qb = prog(t, wt(e, "banco") - 0.3, 0.3)
    if qb > 0:
        icono(L, "banco", 270, 730, eob(qb), a=qb)
        texto(L, "AVISA A TU BANCO", 270, 800, 20, (40, 40, 50), a=qb, fuente="black", sombra=False)
    st["paso"] = (3, "CORREO Y BANCO")


def esc_cuatro(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, FONDO_C)
    q = prog(t, wt(e, "denuncia") - 0.4, 0.4)
    if q > 0:
        s = eob(q)
        rect(L, 150, 340, 390, 680, BLANCO, a=q, r=8)
        texto(L, "DENUNCIA", 270, 380, 24 * s, (40, 40, 50), a=q, fuente="black", sombra=False)
        for k in range(5):
            rect(L, 176, 420 + k * 24, 364 - (k % 2) * 40, 430 + k * 24, (210, 214, 224), a=q)
        qi = prog(t, wt(e, "IMEI") - 0.3, 0.3)
        if qi > 0:
            rect(L, 170, 560, 370, 610, (255, 240, 180), a=qi, r=6)
            texto(L, "IMEI 35 209 4…", 270, 585, 16, (40, 40, 50), a=qi, fuente="mono", sombra=False)
    qb = prog(t, wt(e, "bloquear") - 0.3, 0.4)
    if qb > 0:
        movil(L, 270, 790, 2.2, a=qb, pantalla=(30, 30, 36))
        circ(L, 270, 790, 34, outline=ROJO, w=8, a=qb)
        linea(L, [(246, 766), (294, 814)], ROJO, w=8, a=qb)
        texto(L, "YA NO SIRVE", 270, 880, 24, ROJO, a=qb, fuente="black")
    st["paso"] = (4, "DENUNCIA CON EL IMEI")


def esc_truco(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (24, 28, 40))
    rect(L, 140, 320, 400, 880, (16, 16, 20), r=36)
    rect(L, 156, 340, 384, 860, (240, 242, 248), r=26)
    teclas = [("asterisco", "*"), ("almohadilla", "#"), ("cero", "0"), ("seis", "6"), ("almohadilla", "#")]
    marcado = ""
    cuenta = {}
    for pal, ch in teclas:
        n = cuenta.get(pal, 0)
        cuenta[pal] = n + 1
        if t >= wt(e, pal, n) - 0.1:
            marcado += ch
    texto(L, marcado, 270, 420, 44, (30, 30, 40), fuente="black", sombra=False)
    for k, ch in enumerate("123456789*0#"):
        x = 200 + (k % 3) * 70
        y = 520 + (k // 3) * 70
        activa = marcado and marcado[-1] == ch and (t - 0.0) % 1 < 1
        circ(L, x, y, 28, fill=(220, 224, 232) if not activa else AMARILLO)
        texto(L, ch, x, y, 22, (30, 30, 40), fuente="black", sombra=False)
    qi = prog(t, wt(e, "apunta") - 0.3, 0.4)
    if qi > 0:
        rect(L, 60, 600, 480, 740, (0, 0, 0), a=0.82 * qi, r=18)
        texto(L, "IMEI", 270, 630, 18, (180, 180, 190), a=qi, fuente="black", sombra=False)
        texto(L, "35 209411 482193 7", 270, 680, 26, BLANCO, a=qi, fuente="mono", sombra=False)
        texto(L, "(ejemplo)", 270, 716, 13, (160, 160, 170), a=qi, fuente="bold", sombra=False)
    if prog(t, wt(e, "IMEI") - 0.3, 0.3) > 0:
        st["overlay"].append(("sello", "APÚNTALO HOY", prog(t, wt(e, "IMEI") - 0.3, 0.3), 800, AMARILLO))
    st["paso"] = ("★", "TRUCO")


def esc_final(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, FONDO_C)
    persona(L, 200, 860 - 190 * 0.9, "movil_mira", 0.9, ropa=PROTA, pelo=(60, 36, 24), boca=0.3)
    movil(L, 254, 860 - 190 * 0.9 - 120 * 0.9, 0.9, pantalla=(90, 160, 255))
    st["tinte"] = ((0, 0, 0), 0.4)
    st["overlay"].append(("final", t, prog(t, wt(e, "Guarda") - 0.2, 0.3), prog(t, wt(e, "mándaselo") - 0.2, 0.3),
                          prog(t, wt(e, "sígueme") - 0.2, 0.3)))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "porque": esc_porque, "uno": esc_uno, "dos": esc_dos, "like": esc_like, "tres": esc_tres,
         "cuatro": esc_cuatro, "truco": esc_truco, "final": esc_final}


def efectos(fx, E):
    g = E["gancho"]
    colocar(fx, whoosh(2, 0.5), 0.0, 0.8)
    colocar(fx, pasos(g["dur"], 0.22, 10, vol=0.6), 0.6, 1.0)
    colocar(fx, braam(), g["t0"] + wt(g, "diez") - 0.3, 0.6)
    t_ = 0.0
    while t_ < g["dur"]:
        colocar(fx, latido(0.9), t_, 0.5)
        t_ += 0.6
    p = E["porque"]
    for pal in ("correo", "banco", "códigos"):
        colocar(fx, pop(), p["t0"] + wt(p, pal) - 0.3, 0.5)
    u = E["uno"]
    for pal in ("perdido", "bloquéalo"):
        colocar(fx, tic(), u["t0"] + wt(u, pal) - 0.3, 0.6)
        colocar(fx, pop(), u["t0"] + wt(u, pal) - 0.25, 0.4)
    d = E["dos"]
    colocar(fx, tono(2), d["t0"] + 0.3, 0.4)
    colocar(fx, golpe() * 0.5, d["t0"] + wt(d, "bloqueen") - 0.3, 0.5)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.6)
    tr = E["tres"]
    for k in range(14):
        colocar(fx, tic() * 0.6, tr["t0"] + wt(tr, "contraseña") - 0.3 + k * 1.2 / 14, 0.5)
    c = E["cuatro"]
    colocar(fx, golpe() * 0.6, c["t0"] + wt(c, "bloquear") - 0.3, 0.6)
    tu = E["truco"]
    for pal, n in (("asterisco", 0), ("almohadilla", 0), ("cero", 0), ("seis", 0), ("almohadilla", 1)):
        colocar(fx, tono_tecla(), tu["t0"] + wt(tu, pal, n) - 0.1, 0.5)
    colocar(fx, dingdong(), tu["t0"] + wt(tu, "apunta") - 0.3, 0.5)


def tono_tecla():
    m = int(0.12 * SR)
    u = np.arange(m) / SR
    return ((np.sin(2 * np.pi * 852 * u) + np.sin(2 * np.pi * 1336 * u)) * 0.12 * np.clip((0.12 - u) / 0.02, 0, 1)).astype(np.float32)
