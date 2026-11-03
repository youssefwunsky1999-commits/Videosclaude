"""Guion del TikTok «Imagínate que te quedas encerrado en un ascensor» (información general de seguridad)."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+10%"
TONO = "-5Hz"
PAUSA = 0.22

SALIDA = "ascensor_tiktok.mp4"
CABECERA = "SI TE QUEDAS ENCERRADO"
MUSICA_LUZ = "alarma"          # la música pasa a modo mayor (calma) desde esta escena
AMBIENTE = 0.06
EXTRA = {"gancho": 0.4, "cables": 0.5, "freno": 0.6, "aire": 0.4, "like": 0.5, "alarma": 0.6, "puertas": 0.6,
         "movil": 0.5, "final": 1.6}
CLAVE = ["imagínate", "encerrado", "caer", "nunca", "cables", "acero", "solo", "freno", "emergencia", "raíles", "aire",
         "herméticos", "like", "alarma", "campana", "segundos", "sacarte", "salir", "forzar", "puertas", "hueco", "112",
         "dirección", "guarda", "mándaselo", "sígueme"]
FUSIONES = ((["uno", "uno", "dos"], "112"),)

SEGMENTOS = [
    {"escena": "gancho", "texto": "Imagínate que te quedas encerrado en un ascensor. Lo primero que piensas es que se va a caer."},
    {"escena": "cables", "texto": "Tranquilo: es muy difícil. Cuelga de varios cables de acero, y cada uno podría sostenerlo solo."},
    {"escena": "freno", "texto": "Y si aun así empezara a bajar demasiado rápido, salta un freno de emergencia que lo clava a los raíles."},
    {"escena": "aire", "texto": "Tampoco te vas a quedar sin aire: los ascensores no son herméticos."},
    {"escena": "like", "texto": "Si esto te ha quitado un poco de miedo, dale like."},
    {"escena": "alarma", "texto": "Lo que tienes que hacer: pulsa el botón de alarma, el de la campana, y mantenlo unos segundos. Te pone en contacto con alguien que vendrá a sacarte."},
    {"escena": "puertas", "texto": "Y nunca intentes salir tú solo ni forzar las puertas. Si estás entre dos plantas, podrías caer al hueco."},
    {"escena": "movil", "texto": "Si nadie responde, llama al uno uno dos y di la dirección del edificio."},
    {"escena": "final", "texto": "Guarda este vídeo y mándaselo a quien le dan miedo los ascensores. Y sígueme para más."},
]
