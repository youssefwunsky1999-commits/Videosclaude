# --- Escenas del TikTok «Imagínate que alguien se desmaya delante de ti» ---
VICTIMA = ((90, 150, 210), (70, 120, 180), (50, 50, 60), (40, 40, 50))
PELO_V = (150, 100, 50)
PISO = 820
POSES.update({
    "mareo": dict(rodilla=(10, 94), pie=(4, 190), cuello=(-10, -146), cabeza=(-20, -188), codo=(30, -110), mano=(18, -170),
                  codo2=(-30, -76), mano2=(-30, -20)),
    "tumbado": dict(rodilla=(-80, 2), pie=(-160, 6), cuello=(110, -2), cabeza=(152, -6), codo=(40, 10), mano=(-10, 16),
                    codo2=(46, 8), mano2=(0, 14)),
    "piernas_arriba": dict(rodilla=(-60, -48), pie=(-110, -100), cuello=(110, -2), cabeza=(152, -6), codo=(40, 10),
                           mano=(-10, 16), codo2=(46, 8), mano2=(0, 14)),
    "lateral": dict(rodilla=(-56, -44), pie=(-120, -10), cuello=(110, -8), cabeza=(150, -2), codo=(150, 26), mano=(184, 12),
                    codo2=(70, -50), mano2=(110, -64)),
    "sujeta": dict(rodilla=(10, 94), pie=(4, 190), cuello=(-34, -140), cabeza=(-52, -178), codo=(-52, -50), mano=(-66, 52),
                   codo2=(-48, -46), mano2=(-62, 56)),
    "sentado_mareo": dict(rodilla=(70, 0), pie=(72, 85), cuello=(4, -116), cabeza=(14, -152), codo=(40, -80), mano=(22, -150),
                          codo2=(24, -52), mano2=(66, -40)),
})


def fondo(L, T):
    rect(L, 0, 0, W, PISO, (226, 222, 236))
    rect(L, 0, PISO, W, H, (150, 120, 96))
    for k in range(6):
        linea(L, [(0, PISO + 10 + k * k * 5), (W, PISO + 10 + k * k * 5)], (126, 100, 80), w=1.2)
    rect(L, 330, 360, 500, 540, (120, 90, 60), r=4)
    rect(L, 340, 370, 490, 530, (170, 214, 240))
    linea(L, [(415, 370), (415, 530)], (120, 90, 60), w=4)
    rect(L, 40, 420, 150, 560, (90, 110, 90), r=6)


def victima(L, pose, x=230, y=None, ojos=0.1, a=1.0):
    if isinstance(pose, dict) or pose in ("tumbado", "piernas_arriba", "lateral"):
        y = PISO - 22 if y is None else y
        return persona(L, x, y, pose, 0.9, ropa=VICTIMA, pelo=PELO_V, ojos=ojos, a=a)
    y = PISO + 10 if y is None else y
    return persona(L, x, y - 190 * 0.9, pose, 0.9, ropa=VICTIMA, pelo=PELO_V, ojos=ojos, a=a)


def espiral(L, x, y, T, r=16, a=1.0):
    pts = []
    for k in range(40):
        ang = k * 0.45 + T * 6
        rr = r * k / 40
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    linea(L, pts, (120, 90, 200), w=2.5, a=a)


def esc_gancho(L, e, t, D, T, st):
    fondo(L, T)
    cae = prog(t, 1.0, 0.35)
    if cae < 1:
        info = victima(L, "mareo", x=270 + 12 * math.sin(T * 5), ojos=1.0)
        cx, cy = info["cabeza"]
        espiral(L, cx - 40, cy - 40, T)
        espiral(L, cx + 40, cy - 50, T + 1)
    else:
        victima(L, "tumbado", x=280)
        for k in range(3):
            texto(L, "z", 470 + k * 14, 760 - k * 18 - 6 * math.sin(T * 3 + k), 18 + k * 4, (120, 120, 160), fuente="black")
    st["shake"] = 6 * (1 - prog(t, 1.35, 0.4)) if cae >= 1 else 0
    st["cam"] = (1.18 - 0.08 * eio(t / D), 270, 600)
    st["alarma"] = t
    st["overlay"].append(("titular", t, "SE DESMAYA DELANTE DE TI", "¿SABRÍAS QUÉ HACER?", 1.0))
    st["sin_cabecera"] = True


def esc_tumba(L, e, t, D, T, st):
    fondo(L, T)
    persona(L, 450, PISO - 62, "agachado", 0.9, ropa=PROTA, pelo=(60, 36, 24), flip=True)
    victima(L, "tumbado", x=260)
    st["overlay"].append(("chip", "BOCA ARRIBA, EN EL SUELO", 0, prog(t, wt(e, "boca") - 0.3, 0.3)))
    st["paso"] = (1, "TÚMBALO")


def esc_piernas(L, e, t, D, T, st):
    fondo(L, T)
    sube = eio(prog(t, wt(e, "levántale") - 0.2, 0.8))
    pose = pose_mix("tumbado", "piernas_arriba", sube)
    info = victima(L, pose, x=300)
    persona(L, 150, PISO + 10 - 190 * 0.9, "sujeta" if sube > 0.3 else "de_pie", 0.9, ropa=PROTA, pelo=(60, 36, 24), flip=True)
    q30 = prog(t, wt(e, "treinta") - 0.3, 0.3)
    if q30 > 0:
        x = 150
        linea(L, [(x - 40, PISO - 20), (x - 40, PISO - 110)], AMARILLO, w=4, a=q30)
        texto(L, "30 cm", x - 50, PISO - 65, 22, AMARILLO, a=q30, fuente="black", anchor="rm")
    qc = prog(t, wt(e, "cerebro") - 0.6, 0.4)
    if qc > 0:
        hx, hy = info["cabeza"]
        for k in range(8):
            u = (t * 0.7 + k / 8) % 1
            x = lerp(200, hx, u)
            y = lerp(PISO - 80, hy, u)
            circ(L, x, y, 6, fill=ROJO, a=qc * math.sin(u * math.pi))
        texto(L, "SANGRE AL CEREBRO", hx - 20, hy - 70, 18, ROJO, a=qc, fuente="black")
    qs = prog(t, wt(e, "segundos") - 0.3, 0.3)
    if qs > 0:
        st["overlay"].append(("sello", "SE SUELE DESPERTAR", qs, 400, VERDE))
    st["paso"] = (2, "PIERNAS ARRIBA")


def esc_aire(L, e, t, D, T, st):
    fondo(L, T)
    persona(L, 470, PISO - 62, "agachado", 0.9, ropa=PROTA, pelo=(60, 36, 24), flip=True)
    victima(L, "piernas_arriba", x=280)
    q = prog(t, wt(e, "aire") - 0.4, 0.5)
    for k in range(6):
        u = (t * 0.6 + k / 6) % 1
        y = 420 + k * 22
        x = lerp(330, 140, u)
        linea(L, [(x, y), (x - 20, y + 8), (x - 40, y)], (120, 200, 255), w=3, a=q * math.sin(u * math.pi))
    st["overlay"].append(("chip", "AFLOJA LA ROPA", 0, prog(t, wt(e, "Aflójale") - 0.3, 0.3)))
    st["overlay"].append(("chip", "QUE LE DÉ EL AIRE", 1, q))
    st["paso"] = (3, "AIRE")


def esc_like(L, e, t, D, T, st):
    fondo(L, T)
    st["tinte"] = ((0, 0, 0), 0.5)
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    st["sin_cabecera"] = True


def esc_minuto(L, e, t, D, T, st):
    fondo(L, T)
    victima(L, "tumbado", x=300)
    q = prog(t, wt(e, "minuto") - 0.3, 0.3)
    if q > 0:
        seg = int(60 * prog(t, wt(e, "minuto") - 0.3, 2.5))
        cx, cy, r = 160, 440, 70
        circ(L, cx, cy, r + 8, fill=BLANCO, a=q)
        circ(L, cx, cy, r, fill=(30, 34, 46), a=q)
        L.d.pieslice(P(cx - r, cy - r, cx + r, cy + r), -90, -90 + 6 * seg, fill=L.c(ROJO, q))
        circ(L, cx, cy, r * 0.68, fill=(30, 34, 46), a=q)
        texto(L, f"{seg} s", cx, cy, 30, BLANCO, a=q, fuente="black")
    q1 = prog(t, wt(e, "uno") - 0.3, 0.3)
    if q1 > 0:
        st["overlay"].append(("numero", "112", "LLAMA", q1, 470))
    st["paso"] = (4, "SI NO DESPIERTA")


def esc_lateral(L, e, t, D, T, st):
    fondo(L, T)
    gira = eio(prog(t, wt(e, "lado") - 0.4, 0.8))
    persona(L, 200, PISO - 70, "agachado", 0.9, ropa=PROTA, pelo=(60, 36, 24))
    victima(L, pose_mix("tumbado", "lateral", gira), x=280)
    if gira > 0.8:
        texto(L, "↻", 300, 600, 60, AMARILLO, fuente="sym")
    st["overlay"].append(("chip", "DE LADO", 0, prog(t, wt(e, "lado") - 0.3, 0.3)))
    st["overlay"].append(("chip", "POSICIÓN LATERAL DE SEGURIDAD", 1, prog(t, wt(e, "lateral") - 0.3, 0.3)))
    st["paso"] = (5, "SI RESPIRA PERO NO DESPIERTA")


def esc_nada(L, e, t, D, T, st):
    fondo(L, T)
    victima(L, "piernas_arriba", x=300, ojos=1.0)
    st["overlay"].append(("regla", "NO LE DES AGUA", 0, prog(t, wt(e, "agua") - 0.3, 0.3), False))
    st["overlay"].append(("regla", "NO LO LEVANTES DE GOLPE", 1, prog(t, wt(e, "golpe") - 0.3, 0.3), False))
    st["overlay"].append(("regla", "TUMBADO UNOS MINUTOS", 2, prog(t, wt(e, "tumbado") - 0.3, 0.3), True))
    st["paso"] = (6, "CUANDO DESPIERTE")


def esc_tu(L, e, t, D, T, st):
    fondo(L, T)
    sienta = prog(t, wt(e, "siéntate") - 0.3, 0.5)
    sx = 240
    if sienta <= 0:
        info = persona(L, sx + 8 * math.sin(T * 5), PISO + 10 - 190 * 0.95, "mareo", 0.95, ropa=PROTA, pelo=(60, 36, 24))
        cx, cy = info["cabeza"]
        espiral(L, cx - 40, cy - 40, T)
        espiral(L, cx + 40, cy - 50, T + 1)
        st["tinte"] = ((255, 255, 255), 0.18 * prog(t, wt(e, "borrosa") - 0.3, 0.4))
    else:
        silla(L, sx, PISO - 90)
        persona(L, sx, PISO - 90, "sentado_mareo", 1.0, ropa=PROTA, pelo=(60, 36, 24))
        st["overlay"].append(("sello", "SIÉNTATE O TÚMBATE", sienta, 400, VERDE))
    st["overlay"].append(("regla", "MAREO", 0, prog(t, wt(e, "mareo") - 0.3, 0.3) * (1 - sienta), False))
    st["overlay"].append(("regla", "VISTA BORROSA", 1, prog(t, wt(e, "borrosa") - 0.3, 0.3) * (1 - sienta), False))
    st["paso"] = ("!", "SI ERES TÚ")


def esc_final(L, e, t, D, T, st):
    fondo(L, T)
    victima(L, "de_pie", x=330, ojos=1.0)
    persona(L, 180, PISO + 10 - 190 * 0.9, "de_pie", 0.9, ropa=PROTA, pelo=(60, 36, 24), boca=0.3)
    st["tinte"] = ((0, 0, 0), 0.4)
    st["overlay"].append(("final", t, prog(t, wt(e, "Guarda") - 0.2, 0.3), prog(t, wt(e, "mándaselo") - 0.2, 0.3),
                          prog(t, wt(e, "sígueme") - 0.2, 0.3)))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "tumba": esc_tumba, "piernas": esc_piernas, "aire": esc_aire, "like": esc_like,
         "minuto": esc_minuto, "lateral": esc_lateral, "nada": esc_nada, "tu": esc_tu, "final": esc_final}


def efectos(fx, E):
    g = E["gancho"]
    t_ = 0.0
    while t_ < g["dur"]:
        colocar(fx, latido(0.9), t_, 0.5)
        t_ += 0.6
    colocar(fx, golpe(), g["t0"] + 1.3, 0.9)
    colocar(fx, braam(), g["t0"] + wt(g, "Sabrías") - 0.3, 0.6)
    tb = E["tumba"]
    colocar(fx, pop(), tb["t0"] + wt(tb, "boca") - 0.3, 0.5)
    p = E["piernas"]
    colocar(fx, whoosh(3, 0.6), p["t0"] + wt(p, "levántale") - 0.2, 0.5)
    colocar(fx, pop(), p["t0"] + wt(p, "treinta") - 0.3, 0.5)
    colocar(fx, dingdong(), p["t0"] + wt(p, "segundos") - 0.3, 0.5)
    a = E["aire"]
    colocar(fx, ruido_filtrado(int(a["dur"] * SR), 60, 5) * 0.12, a["t0"], 0.5)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.6)
    m = E["minuto"]
    for k in range(6):
        colocar(fx, tic(), m["t0"] + wt(m, "minuto") - 0.3 + k * 0.42, 0.4)
    colocar(fx, tono(2), m["t0"] + wt(m, "uno") - 0.2, 0.5)
    la = E["lateral"]
    colocar(fx, whoosh(6, 0.6), la["t0"] + wt(la, "lado") - 0.4, 0.5)
    n = E["nada"]
    for pal in ("agua", "golpe", "tumbado"):
        colocar(fx, pop(), n["t0"] + wt(n, pal) - 0.3, 0.5)
    tu = E["tu"]
    colocar(fx, golpe() * 0.4, tu["t0"] + wt(tu, "siéntate") - 0.3, 0.5)
