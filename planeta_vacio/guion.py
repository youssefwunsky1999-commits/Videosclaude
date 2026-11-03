"""«En este planeta no hay nadie. Solo yo.» (ficción) — vídeo de arranque para una cuenta nueva: cada seguidor
aparece en el planeta. Narrador en primera persona: Nico."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+12%"
TONO = "+8Hz"
PAUSA = 0.22

ECO = {"voz": "es-ES-AlvaroNeural", "velocidad": "-10%", "tono": "+10Hz"}

SEGMENTOS = [
    {"escena": "gancho", "texto": "En este planeta no hay nadie. Solo yo."},
    {"escena": "estadio", "texto": "Tengo una casa, un banco… y un estadio enorme. Pero las gradas están vacías."},
    {"escena": "saludo", "texto": "Cada mañana grito:"},
    dict(ECO, escena="eco", texto="¡Hola!"),
    {"escena": "nadie", "texto": "Y nadie me contesta."},
    {"escena": "descubre", "texto": "Pero he descubierto algo. Cada vez que alguien sigue esta cuenta… aparece una persona nueva en el planeta."},
    {"escena": "llega", "texto": "Mira. Así es como llegaría el primero."},
    {"escena": "nombre", "texto": "Si me sigues, tú puedes ser ese primero. Y si comentas tu nombre, tu personaje lo llevará."},
    {"escena": "amigo", "texto": "Y si compartes este vídeo, traerás a un amigo contigo."},
    {"escena": "metas", "texto": "Cuando seamos cien, llenaremos el estadio. Y cuando seamos mil… construiremos una ciudad entera."},
    {"escena": "final", "texto": "Hoy somos cero. ¿Quieres ser el primero?"},
]
