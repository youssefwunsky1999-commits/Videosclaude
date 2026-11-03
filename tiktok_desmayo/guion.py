"""Guion del TikTok «Imagínate que alguien se desmaya delante de ti» (primeros auxilios: información general)."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+10%"
TONO = "-5Hz"
PAUSA = 0.22

SALIDA = "desmayo_tiktok.mp4"
CABECERA = "SI ALGUIEN SE DESMAYA"
MUSICA_LUZ = "tu"
AMBIENTE = 0.06
EXTRA = {"gancho": 0.4, "tumba": 0.7, "piernas": 0.7, "aire": 0.5, "like": 0.5, "minuto": 0.7, "lateral": 0.8,
         "nada": 0.6, "tu": 0.7, "final": 1.6}
CLAVE = ["imagínate", "desmaya", "sabrías", "boca", "arriba", "piernas", "treinta", "cerebro", "afloja", "aire",
         "like", "minuto", "respira", "112", "lado", "lateral", "agua", "golpe", "siéntate", "túmbate", "guarda",
         "mándaselo", "sígueme"]
FUSIONES = ((["uno", "uno", "dos."], "112."), (["uno", "uno", "dos"], "112"), (["treinta", "centímetros"], "30 cm"))

SEGMENTOS = [
    {"escena": "gancho", "texto": "Imagínate que alguien se desmaya delante de ti. ¿Sabrías qué hacer?"},
    {"escena": "tumba", "texto": "Primero, que no se golpee: túmbalo boca arriba, en el suelo."},
    {"escena": "piernas", "texto": "Y levántale las piernas, unos treinta centímetros. Así la sangre vuelve antes al cerebro, y muchas veces se despierta en segundos."},
    {"escena": "aire", "texto": "Aflójale la ropa que apriete, y que le dé el aire."},
    {"escena": "like", "texto": "Si no lo sabías, dale like para que le llegue a más gente."},
    {"escena": "minuto", "texto": "Si en un minuto no se despierta, o no respira con normalidad, llama al uno uno dos."},
    {"escena": "lateral", "texto": "Si respira pero no despierta, ponlo de lado, en posición lateral de seguridad, para que no se ahogue."},
    {"escena": "nada", "texto": "Y cuando despierte, no le des agua ni lo levantes de golpe: que se quede tumbado unos minutos."},
    {"escena": "tu", "texto": "Y si eres tú quien nota que se va a desmayar, con mareo o la vista borrosa: siéntate o túmbate antes de caer."},
    {"escena": "final", "texto": "Guarda este vídeo y mándaselo a quien quieras. Y sígueme para más."},
]
