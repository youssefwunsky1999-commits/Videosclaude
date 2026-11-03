"""Guion del TikTok «Si caes al agua fría, NO nades» (choque por frío; consejos generales tipo «flota para vivir»)."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+10%"
TONO = "-5Hz"
PAUSA = 0.22

SALIDA = "agua_fria_tiktok.mp4"
CABECERA = "SI CAES AL AGUA FRÍA"
MUSICA_LUZ = "flota"
AMBIENTE = 0.08
EXTRA = {"gancho": 0.4, "choque": 0.6, "minuto": 0.8, "flota": 0.8, "like": 0.5, "despues": 0.6, "otro": 0.7,
         "grados": 0.6, "final": 1.6}
CLAVE = ["no", "nades", "instinto", "choque", "jadeas", "corazón", "pánico", "tragas", "minuto", "aguantar", "boca",
         "arriba", "estrella", "despacio", "like", "ayuda", "agarrarte", "tires", "112", "flote", "quince", "grados",
         "guarda", "mándaselo", "sígueme"]
FUSIONES = ((["uno", "uno", "dos"], "112"), (["quince", "grados"], "15 °C"))

SEGMENTOS = [
    {"escena": "gancho", "texto": "Si caes al agua fría, no nades. Aunque sepas nadar. Tu instinto te va a pedir justo lo contrario."},
    {"escena": "choque", "texto": "Al caer, el frío provoca un choque: jadeas sin control, el corazón se dispara y llega el pánico. Si tragas agua en ese momento, es muy peligroso."},
    {"escena": "minuto", "texto": "Pero ese choque pasa en un minuto, más o menos. Solo tienes que aguantar ese minuto."},
    {"escena": "flota", "texto": "Así que túmbate boca arriba, con la cabeza hacia atrás y los brazos y las piernas abiertos, como una estrella. Mueve un poco las manos y respira despacio."},
    {"escena": "like", "texto": "Si no lo sabías, dale like. Le puede salvar la vida a alguien."},
    {"escena": "despues", "texto": "Cuando controles la respiración, pide ayuda a gritos, o nada hacia algo a lo que agarrarte."},
    {"escena": "otro", "texto": "Y si ves a alguien caer, no te tires tú. Llama al uno uno dos y lánzale algo que flote."},
    {"escena": "grados", "texto": "Ojo: no hace falta que sea invierno. Por debajo de quince grados, el agua ya puede provocar este choque."},
    {"escena": "final", "texto": "Guarda este vídeo y mándaselo a quien va a la playa o al río. Y sígueme para más."},
]
