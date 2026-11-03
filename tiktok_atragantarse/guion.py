"""Guion del TikTok «Imagínate que te atragantas y estás solo en casa» (primeros auxilios: información general)."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+10%"
TONO = "-5Hz"
PAUSA = 0.22

SALIDA = "atragantarse_tiktok.mp4"
CABECERA = "SI TE ATRAGANTAS SOLO"
MUSICA_LUZ = "medico"
AMBIENTE = 0.04
EXTRA = {"gancho": 0.4, "toser": 0.5, "llamar": 0.6, "like": 0.5, "puno": 0.8, "silla": 0.8, "senal": 0.6,
         "medico": 0.6, "final": 1.6}
CLAVE = ["imagínate", "solo", "garganta", "respirar", "toser", "tose", "fuerzas", "112", "abierta", "like", "puño",
         "ombligo", "arriba", "silla", "encimera", "peso", "golpe", "cuello", "señal", "médico", "daño", "guarda",
         "mándaselo", "sígueme"]
FUSIONES = ((["uno", "uno", "dos"], "112"),)

SEGMENTOS = [
    {"escena": "gancho", "texto": "Imagínate que estás solo en casa, comiendo, y de repente algo se te queda en la garganta. No puedes respirar."},
    {"escena": "toser", "texto": "Si todavía puedes toser, tose con todas tus fuerzas. Es lo que mejor funciona."},
    {"escena": "llamar", "texto": "Si no puedes toser ni hablar, llama al uno uno dos y deja la llamada abierta, aunque no puedas decir nada."},
    {"escena": "like", "texto": "Esto le puede salvar la vida a alguien. Dale like para que llegue a más gente."},
    {"escena": "puno", "texto": "Ahora, tú mismo: pon el puño justo encima del ombligo, cúbrelo con la otra mano y empuja fuerte hacia dentro y hacia arriba. Varias veces."},
    {"escena": "silla", "texto": "Si no tienes fuerza, apóyate en el respaldo de una silla o en el borde de la encimera, y deja caer tu peso sobre la tripa, de golpe."},
    {"escena": "senal", "texto": "Y si hay alguien cerca, llévate las manos al cuello. Es la señal de que te estás atragantando."},
    {"escena": "medico", "texto": "Aunque consigas expulsarlo, ve al médico: esas compresiones pueden hacer daño por dentro."},
    {"escena": "final", "texto": "Guarda este vídeo y mándaselo a quien vive solo. Y sígueme para más."},
]
