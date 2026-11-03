"""Guion del TikTok «¿Sabías que en un incendio mata más el humo que el fuego?» (consejos generales de seguridad)."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+10%"
TONO = "-5Hz"
PAUSA = 0.22

SALIDA = "humo_tiktok.mp4"
CABECERA = "SI HAY FUEGO EN CASA"
MUSICA_LUZ = "detector"
AMBIENTE = 0.07
EXTRA = {"gancho": 0.4, "porque": 0.5, "agachate": 0.6, "puerta": 0.7, "like": 0.5, "cierra": 0.6, "atrapado": 0.8,
         "detector": 0.6, "final": 1.6}
CLAVE = ["sabías", "humo", "fuego", "llamas", "tóxico", "sube", "inconsciente", "agáchate", "gatas", "suelo", "limpio",
         "dorso", "quema", "abras", "like", "cierras", "frena", "ascensor", "toallas", "ventana", "112", "detector",
         "euros", "guarda", "mándaselo", "sígueme"]
FUSIONES = ((["uno", "uno", "dos"], "112"),)

SEGMENTOS = [
    {"escena": "gancho", "texto": "¿Sabías que en un incendio en casa mata más el humo que el fuego? La mayoría de las víctimas mueren por respirar humo, no por las llamas."},
    {"escena": "porque", "texto": "El humo es caliente, tóxico, y sube. Unas pocas bocanadas pueden dejarte inconsciente."},
    {"escena": "agachate", "texto": "Por eso, si hay humo, agáchate o ve a gatas. Cerca del suelo, el aire es más limpio."},
    {"escena": "puerta", "texto": "Antes de abrir una puerta, toca la puerta y el pomo con el dorso de la mano. Si quema, no la abras: el fuego está al otro lado."},
    {"escena": "like", "texto": "Si esto te parece útil, dale like para que le llegue a más gente."},
    {"escena": "cierra", "texto": "Cada puerta que cierras detrás de ti frena el humo. Y nunca uses el ascensor."},
    {"escena": "atrapado", "texto": "Si no puedes salir, enciérrate en una habitación, tapa las rendijas con toallas mojadas, asómate a la ventana y llama al uno uno dos."},
    {"escena": "detector", "texto": "Y lo más importante: un detector de humo cuesta unos pocos euros, y te despierta antes de que sea tarde."},
    {"escena": "final", "texto": "Guarda este vídeo y mándaselo a tu familia. Y sígueme para más."},
]
