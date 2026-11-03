"""Guion del reel «Cómo distinguimos los sabores» (formato «Mitos y verdades del cuerpo», estilo ilustración pintada).

Base: 5 sabores básicos (dulce, salado, ácido, amargo, umami); botones gustativos en las papilas; el «mapa de la
lengua» viene de un estudio de Hänig (1901) mal interpretado (Boring, 1942): toda la lengua nota los cinco, con
pequeñas diferencias de sensibilidad; los aromas llegan a la nariz por detrás de la boca (vía retronasal); con la nariz
tapada cuesta mucho distinguir alimentos de sabor básico parecido (prueba de la manzana y la cebolla); el cerebro
integra gusto, olfato, textura, temperatura y vista; el picante activa el receptor del calor (TRPV1): es dolor."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+8%"
TONO = "-4Hz"
PAUSA = 0.24

SALIDA = "sabores_reel.mp4"
EXTRA = {"gancho": 0.4, "cinco": 0.2, "lista": 0.5, "botones": 0.5, "mito": 0.6, "nariz": 0.5, "cerebro": 0.5,
         "resfriado": 0.4, "picante": 0.5, "cierre": 0.5, "cta": 1.4}
CLAVE = ["nariz", "manzana", "cebolla", "cinco", "dulce", "salado", "ácido", "amargo", "umami", "botones", "mito",
         "1901", "aromas", "cerebro", "sabor", "resfriado", "nada", "picante", "dolor", "calor", "envíaselo"]
FUSIONES = ((["mil", "novecientos", "uno"], "1901"),)

SEGMENTOS = [
    {"escena": "gancho", "texto": "Tápate la nariz, cierra los ojos y muerde una manzana. Luego, una cebolla cruda. Te va a costar muchísimo saber cuál es cuál."},
    {"escena": "cinco", "texto": "No es un truco. Tu lengua, sola, solo distingue cinco sabores:"},
    {"escena": "lista", "texto": "dulce, salado, ácido, amargo, y umami, el sabor del caldo o del queso curado."},
    {"escena": "botones", "texto": "Los detectan unos miles de botones gustativos, escondidos en los bultitos de tu lengua. Y se renuevan sin parar: por eso te recuperas cuando te quemas."},
    {"escena": "mito", "texto": "¿Y el mapa de la lengua del colegio, con lo dulce en la punta? Es un mito. Salió de un estudio de mil novecientos uno mal interpretado. Toda la lengua nota los cinco."},
    {"escena": "nariz", "texto": "Entonces, ¿cómo sabes que algo sabe a fresa o a café? Por la nariz. Al masticar, los aromas suben por detrás de la boca hasta ella."},
    {"escena": "cerebro", "texto": "Y tu cerebro lo junta todo: lengua, olfato, textura, temperatura y hasta el color. A esa mezcla la llamamos sabor."},
    {"escena": "resfriado", "texto": "Por eso, cuando estás resfriado, la comida no sabe a nada."},
    {"escena": "picante", "texto": "Y el picante ni siquiera es un sabor: es dolor. Tu boca siente la guindilla como si fuera calor de verdad."},
    {"escena": "cierre", "texto": "Así que la próxima vez que algo te encante, dale las gracias a tu nariz."},
    {"escena": "cta", "texto": "Envíaselo a alguien que todavía no lo sabía."},
]
