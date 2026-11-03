"""Guion del TikTok «¿Sabías que el 112 sabe dónde estás?» (localización AML y otras curiosidades del 112)."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+10%"
TONO = "-5Hz"
PAUSA = 0.2

SALIDA = "112_tiktok.mp4"
CABECERA = "LO QUE NO SABÍAS DEL 112"
MUSICA_LUZ = "como"
AMBIENTE = 0.03
EXTRA = {"gancho": 0.4, "como": 0.6, "precision": 0.7, "gratis": 0.5, "like": 0.5, "bloqueado": 0.6, "red": 0.6,
         "europa": 0.6, "final": 1.6}
CLAVE = ["sabías", "112", "dónde", "estás", "aml", "gps", "wifi", "ubicación", "antena", "kilómetros", "metros",
         "apagada", "gratis", "datos", "like", "bloqueado", "emergencia", "saldo", "cobertura", "otra", "red", "europea",
         "mismo", "guarda", "mándaselo", "sígueme"]
FUSIONES = ((["uno", "uno", "dos,"], "112,"), (["uno", "uno", "dos"], "112"))

SEGMENTOS = [
    {"escena": "gancho", "texto": "¿Sabías que cuando llamas al uno uno dos, tu móvil les dice dónde estás? Aunque tú no lo sepas."},
    {"escena": "como", "texto": "Se llama AML. Al marcar, el móvil enciende solo el GPS y el wifi, y les envía tu ubicación en un mensaje que tú ni ves."},
    {"escena": "precision", "texto": "Antes, solo sabían qué antena estabas usando: una zona de kilómetros. Ahora, muchas veces, el margen es de unas decenas de metros."},
    {"escena": "gratis", "texto": "Funciona aunque tengas la ubicación apagada, es gratis y no gasta tus datos."},
    {"escena": "like", "texto": "Si no lo sabías, dale like."},
    {"escena": "bloqueado", "texto": "Más cosas: puedes llamar al uno uno dos con el móvil bloqueado, desde el botón de emergencia de la pantalla."},
    {"escena": "red", "texto": "Sin saldo, y aunque tu compañía no tenga cobertura: si hay otra red cerca, el móvil la usa para esa llamada."},
    {"escena": "europa", "texto": "Y es el mismo número en toda la Unión Europea."},
    {"escena": "final", "texto": "Guarda este vídeo y mándaselo a tus padres. Y sígueme para más."},
]
