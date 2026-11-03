# --- Escenas del TikTok «Imagínate que te atragantas y estás solo en casa» ---
POSES.update({
    "garganta": dict(rodilla=(4, 95), pie=(2, 190), cuello=(2, -148), cabeza=(6, -192), codo=(40, -116), mano=(12, -150),
                     codo2=(-36, -114), mano2=(-8, -148)),
    "tose": dict(rodilla=(8, 94), pie=(4, 190), cuello=(20, -142), cabeza=(36, -180), codo=(40, -100), mano=(44, -150),
                 codo2=(-10, -76), mano2=(-4, -16)),
    "puno": dict(rodilla=(4, 95), pie=(2, 190), cuello=(6, -148), cabeza=(14, -192), codo=(44, -84), mano=(30, -52),
                 codo2=(40, -80), mano2=(26, -48)),
    "puno2": dict(rodilla=(4, 95), pie=(2, 190), cuello=(12, -144), cabeza=(22, -186), codo=(42, -96), mano=(24, -70),
                  codo2=(38, -92), mano2=(20, -66)),
    "dobla": dict(rodilla=(6, 95), pie=(2, 190), cuello=(80, -108), cabeza=(118, -130), codo=(90, -56), mano=(110, -6),
                  codo2=(84, -52), mano2=(104, -2)),
    "dobla2": dict(rodilla=(10, 95), pie=(2, 190), cuello=(86, -96), cabeza=(124, -112), codo=(96, -44), mano=(116, 6),
                   codo2=(90, -40), mano2=(110, 10)),
})
PARED = (236, 226, 206)
SUELO_M = (196, 156, 110)


def cocina(L, T, mesa=True):
    rect(L, 0, 0, W, 780, PARED)
    for x in range(0, W, 40):
        for y in (500, 540):
            rect(L, x + 2, y + 2, x + 38, y + 38, (250, 246, 236))
    rect(L, 0, 780, W, H, SUELO_M)
    for k in range(7):
        linea(L, [(0, 790 + k * k * 4), (W, 790 + k * k * 4)], (176, 138, 94), w=1.2)
    # ventana
    rect(L, 60, 330, 220, 470, (120, 90, 60), r=4)
    rect(L, 70, 340, 210, 460, (170, 214, 240))
    linea(L, [(140, 340), (140, 460)], (120, 90, 60), w=4)
    # encimera y muebles
    rect(L, 330, 580, W, 600, (90, 90, 100))
    rect(L, 340, 600, W, 780, (214, 196, 160))
    for x in (340, 440):
        rect(L, x + 6, 610, x + 94, 770, (226, 210, 176), r=4)
        rect(L, x + 70, 680, x + 78, 710, (120, 110, 90), r=2)
    rect(L, 360, 300, W, 420, (226, 210, 176))
    if mesa:
        rect(L, 40, 690, 260, 704, (150, 100, 60))
        rect(L, 60, 704, 72, 790, (120, 80, 48))
        rect(L, 228, 704, 240, 790, (120, 80, 48))
        L.d.ellipse(P(110, 676, 190, 696), fill=L.c(BLANCO))
        circ(L, 150, 684, 8, fill=(180, 110, 60))


def tachar(L, cx, cy, r, q):
    if q <= 0:
        return
    circ(L, cx, cy, r, outline=ROJO, w=6, a=q)
    linea(L, [(cx - r * 0.7, cy - r * 0.7), (cx + r * 0.7, cy + r * 0.7)], ROJO, w=6, a=q)


def esc_gancho(L, e, t, D, T, st):
    cocina(L, T)
    ahoga = prog(t, wt(e, "garganta") - 0.4, 0.3)
    pose = "garganta" if ahoga > 0 or t < 0.9 else "de_pie"
    tiembla = 3 * math.sin(T * 40) if pose == "garganta" else 0
    persona(L, 230 + tiembla, 860 - 190 * 1.0, pose, 1.0, ropa=PROTA, pelo=(60, 36, 24), ojos=1.8, boca=0.8)
    st["cam"] = (1.35 - 0.2 * eio(t / D), 250, 520)
    st["alarma"] = t
    st["shake"] = 2
    st["overlay"].append(("titular", t, "TE ATRAGANTAS Y ESTÁS SOLO", "NO PUEDES RESPIRAR", 1.0))
    st["sin_cabecera"] = True


def esc_toser(L, e, t, D, T, st):
    cocina(L, T)
    tos = (t * 2.2) % 1 < 0.45
    persona(L, 230, 860 - 190, "tose" if tos else "de_pie_inclina", 1.0, ropa=PROTA, pelo=(60, 36, 24), boca=0.9 if tos else 0.2)
    if tos:
        for k in range(4):
            u = (t * 2.2) % 1 / 0.45
            circ(L, 300 + 40 * u + k * 12, 470 - k * 8, 6 * (1 - u) + 2, fill=BLANCO, a=1 - u)
        texto(L, "¡COF!", 360, 480, 30, BLANCO, fuente="black")
    q = prog(t, wt(e, "toser") - 0.3, 0.3)
    st["overlay"].append(("chip", "TOSE CON FUERZA", 0, q))
    st["paso"] = (1, "SI PUEDES TOSER")


def telefono(L, x0, y0, t, s=1.0, a=1.0, segundos=None, extra=""):
    rect(L, x0, y0, x0 + 200 * s, y0 + 340 * s, (16, 16, 20), a=a, r=24)
    rect(L, x0 + 10 * s, y0 + 14 * s, x0 + 190 * s, y0 + 326 * s, (30, 120, 70), a=a, r=18)
    texto(L, "112", x0 + 100 * s, y0 + 80 * s, 46 * s, BLANCO, a=a, fuente="black", sombra=False)
    if segundos is not None:
        texto(L, f"00:{int(segundos):02d}", x0 + 100 * s, y0 + 126 * s, 18 * s, BLANCO, a=a, fuente="mono", sombra=False)
    if extra:
        texto(L, extra, x0 + 100 * s, y0 + 250 * s, 16 * s, BLANCO, a=a, fuente="black", sombra=False)


def esc_llamar(L, e, t, D, T, st):
    cocina(L, T)
    persona(L, 140, 860 - 190, "garganta", 1.0, ropa=PROTA, pelo=(60, 36, 24), ojos=1.6, boca=0.7)
    q = prog(t, wt(e, "llama") - 0.3, 0.4)
    if q > 0:
        telefono(L, 290, 380, t, s=eob(q), a=q, segundos=max(0, t - wt(e, "llama")),
                 extra="LLAMADA ABIERTA" if prog(t, wt(e, "abierta") - 0.3, 0.3) > 0 else "")
    qa = prog(t, wt(e, "abierta") - 0.3, 0.3)
    if qa > 0:
        for k in range(3):
            u = (t * 1.3 + k / 3) % 1
            L.d.arc(P(390 - 120 - 40 * u, 540 - 160 - 40 * u, 390 + 120 + 40 * u, 540 + 160 + 40 * u), 300, 60,
                    fill=L.c(AMARILLO, qa * (1 - u)), width=3 * K)
    st["overlay"].append(("fuente", prog(t, wt(e, "decir") - 0.3, 0.3), "Aunque no hables, te pueden localizar y enviar ayuda"))
    st["paso"] = (2, "SI NO PUEDES TOSER")


def esc_like(L, e, t, D, T, st):
    cocina(L, T)
    st["tinte"] = ((0, 0, 0), 0.45)
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    st["sin_cabecera"] = True


def esc_puno(L, e, t, D, T, st):
    # esquema grande del abdomen con el puño
    rect(L, 0, 0, W, H, (30, 34, 46))
    cx, cy = 270, 580
    L.d.ellipse(P(cx - 170, cy - 260, cx + 170, cy + 300), fill=L.c(PROTA[0]))
    L.d.ellipse(P(cx - 150, cy - 230, cx + 150, cy + 270), fill=L.c(PIEL), outline=L.c(PIEL_S), width=4 * K)
    # costillas
    for k in range(3):
        L.d.arc(P(cx - 130 + k * 6, cy - 220 + k * 34, cx + 130 - k * 6, cy - 60 + k * 34), 200, 340,
                fill=L.c(PIEL_S), width=3 * K)
    circ(L, cx, cy + 110, 9, fill=PIEL_S)
    texto(L, "OMBLIGO", cx + 70, cy + 112, 14, (120, 80, 60), fuente="black", anchor="lm", sombra=False)
    qo = prog(t, wt(e, "ombligo") - 0.4, 0.4)
    if qo > 0:
        empuja = 0.5 + 0.5 * math.sin(t * 8) if t > wt(e, "empuja") - 0.2 else 0
        fy = cy + 50 - 14 * empuja
        s = eob(qo)
        rect(L, cx - 46 * s, fy - 36 * s, cx + 46 * s, fy + 36 * s, (226, 170, 130), a=qo, r=24)
        for k in range(3):
            linea(L, [(cx - 30 + k * 26, fy - 32 * s), (cx - 30 + k * 26, fy - 6 * s)], PIEL_S, w=3, a=qo)
        qc = prog(t, wt(e, "cúbrelo") - 0.3, 0.3)
        if qc > 0:
            rect(L, cx - 60, fy - 10, cx + 60, fy + 50, (240, 196, 160), a=qc * 0.92, r=26)
            texto(L, "OTRA MANO", cx, fy + 66, 14, BLANCO, a=qc, fuente="black")
        qa = prog(t, wt(e, "dentro") - 0.3, 0.3)
        if qa > 0:
            for k, (dx, dy) in enumerate(((0, -1),)):
                y1 = fy - 60 - 20 * empuja
                linea(L, [(cx, fy - 40), (cx, y1 - 60)], AMARILLO, w=10, a=qa)
                poly(L, [(cx - 24, y1 - 50), (cx + 24, y1 - 50), (cx, y1 - 90)], AMARILLO, a=qa)
            texto(L, "DENTRO Y ARRIBA", cx, 905, 30, AMARILLO, a=qa, fuente="black")
    st["paso"] = (3, "COMPRESIONES")
    st["cam"] = (1.02, 270, 520)


def esc_silla(L, e, t, D, T, st):
    cocina(L, T, mesa=False)
    golpe_ = t > wt(e, "peso") - 0.4
    k = 0.5 + 0.5 * math.sin(t * 7) if golpe_ else 0
    sx = 330
    rect(L, sx - 10, 560, sx + 6, 860, (120, 80, 48))
    rect(L, sx - 10, 560, sx + 110, 576, (150, 100, 60))
    rect(L, sx - 10, 700, sx + 120, 716, (150, 100, 60))
    rect(L, sx + 104, 716, sx + 116, 860, (120, 80, 48))
    persona(L, 240, 860 - 190, pose_mix("dobla", "dobla2", k), 1.0, ropa=PROTA, pelo=(60, 36, 24), ojos=1.4, boca=0.6)
    q = prog(t, wt(e, "silla") - 0.3, 0.3)
    if q > 0:
        rotulo_ = "RESPALDO DE UNA SILLA"
        texto(L, rotulo_, 400, 440, 18, BLANCO, a=q, fuente="black")
        linea(L, [(420, 452), (400, 566)], BLANCO, w=2, a=q)
    if golpe_:
        texto(L, "↓", 300, 470 + 12 * k, 50, AMARILLO, fuente="sym")
    st["overlay"].append(("chip", "TU PESO, DE GOLPE", 0, prog(t, wt(e, "golpe") - 0.3, 0.3)))
    st["paso"] = (4, "SIN FUERZA: UNA SILLA")


def esc_senal(L, e, t, D, T, st):
    cocina(L, T)
    persona(L, 200, 860 - 190, "garganta", 1.0, ropa=PROTA, pelo=(60, 36, 24), ojos=1.6, boca=0.7)
    qv = prog(t, wt(e, "cuello") - 0.6, 0.6)
    persona(L, lerp(600, 420, eio(qv)), 860 - 190 * 0.95, camina(t) if qv < 1 else "de_pie", 0.95,
            ropa=((90, 150, 210), (70, 120, 180), (50, 50, 60), (40, 40, 50)), pelo=(150, 100, 50), flip=True, ojos=1.5)
    qs = prog(t, wt(e, "señal") - 0.3, 0.3)
    if qs > 0:
        texto(L, "!", 420, 400 - 8 * math.sin(t * 8), 80 * eob(qs) + 1, ROJO, a=qs, fuente="black")
        st["overlay"].append(("sello", "SEÑAL DE ATRAGANTAMIENTO", qs, 900, AMARILLO))
    st["paso"] = (5, "SI HAY ALGUIEN")


def esc_medico(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (226, 238, 246))
    rect(L, 0, 780, W, H, (190, 200, 210))
    rect(L, 300, 340, 500, 560, BLANCO, r=10)
    rect(L, 385, 380, 415, 520, ROJO)
    rect(L, 330, 435, 470, 465, ROJO)
    persona(L, 150, 860 - 190, camina(t) if t < 2 else "de_pie", 1.0, ropa=PROTA, pelo=(60, 36, 24))
    q = prog(t, wt(e, "médico") - 0.3, 0.3)
    st["overlay"].append(("chip", "VE AL MÉDICO", 0, q))
    st["overlay"].append(("fuente", prog(t, wt(e, "daño") - 0.3, 0.3), "Información general. No sustituye a un curso de primeros auxilios"))
    st["paso"] = (6, "DESPUÉS")


def esc_final(L, e, t, D, T, st):
    cocina(L, T)
    persona(L, 230, 860 - 190, "de_pie", 1.0, ropa=PROTA, pelo=(60, 36, 24), boca=0.3)
    st["tinte"] = ((0, 0, 0), 0.4)
    st["overlay"].append(("final", t, prog(t, wt(e, "Guarda") - 0.2, 0.3), prog(t, wt(e, "mándaselo") - 0.2, 0.3),
                          prog(t, wt(e, "sígueme") - 0.2, 0.3)))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "toser": esc_toser, "llamar": esc_llamar, "like": esc_like, "puno": esc_puno,
         "silla": esc_silla, "senal": esc_senal, "medico": esc_medico, "final": esc_final}


def efectos(fx, E):
    g = E["gancho"]
    t_ = 0.0
    per = 0.7
    while t_ < g["dur"] + 4:
        colocar(fx, latido(0.9), t_, 0.55)
        t_ += per
        per = max(0.45, per * 0.96)
    colocar(fx, braam(), g["t0"] + wt(g, "respirar") - 0.3, 0.7)
    to = E["toser"]
    for k in range(int(to["dur"] * 2.2)):
        colocar(fx, ruido_filtrado(int(0.25 * SR), 8, 40 + k) * np.exp(-np.arange(int(0.25 * SR)) / SR * 12) * 0.5,
                to["t0"] + k / 2.2, 0.5)
    ll = E["llamar"]
    colocar(fx, tono(3), ll["t0"] + wt(ll, "llama"), 0.5)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.6)
    p = E["puno"]
    for pal in ("puño", "cúbrelo", "dentro"):
        colocar(fx, pop(), p["t0"] + wt(p, pal) - 0.3, 0.5)
    s = E["silla"]
    for k in range(5):
        colocar(fx, golpe() * 0.35, s["t0"] + wt(s, "peso") - 0.2 + k * 0.9, 0.5)
    se = E["senal"]
    colocar(fx, golpe() * 0.5, se["t0"] + wt(se, "señal") - 0.3, 0.6)
    m = E["medico"]
    colocar(fx, dingdong(), m["t0"] + wt(m, "médico") - 0.3, 0.5)
