"""Guion del TikTok «Imagínate que te roban el móvil: los primeros 10 minutos» (consejos generales)."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+10%"
TONO = "-5Hz"
PAUSA = 0.2

SALIDA = "movil_robado_tiktok.mp4"
CABECERA = "SI TE ROBAN EL MÓVIL"
MUSICA_LUZ = "truco"
AMBIENTE = 0.07
EXTRA = {"gancho": 0.4, "porque": 0.5, "uno": 0.7, "dos": 0.6, "like": 0.5, "tres": 0.6, "cuatro": 0.6,
         "truco": 1.0, "final": 1.6}
CLAVE = ["imagínate", "roban", "diez", "minutos", "correo", "banco", "códigos", "buscar", "encontrar", "perdido",
         "bloquéalo", "sim", "sms", "like", "contraseña", "todo", "denuncia", "imei", "sirva", "*#06#", "guarda",
         "mándaselo", "sígueme"]
FUSIONES = ((["asterisco,", "almohadilla,", "cero,", "seis,", "almohadilla,"], "*#06#,"),
            (["asterisco", "almohadilla", "cero", "seis", "almohadilla"], "*#06#"))

SEGMENTOS = [
    {"escena": "gancho", "texto": "Imagínate que te roban el móvil. Lo que hagas en los primeros diez minutos importa más que el propio móvil."},
    {"escena": "porque", "texto": "Porque ahí dentro tienes tu correo, tu banco y los mensajes con los códigos de seguridad."},
    {"escena": "uno", "texto": "Primero: desde otro móvil u ordenador, entra en Buscar, si es un iPhone, o en Encontrar mi dispositivo, si es Android. Márcalo como perdido y bloquéalo."},
    {"escena": "dos", "texto": "Segundo: llama a tu compañía y pide que bloqueen tu tarjeta SIM. Así nadie recibe tus SMS del banco."},
    {"escena": "like", "texto": "Si esto te puede servir, dale like."},
    {"escena": "tres", "texto": "Tercero: cambia la contraseña de tu correo, porque con él se puede recuperar casi todo. Y avisa a tu banco."},
    {"escena": "cuatro", "texto": "Y por último, pon una denuncia con el IMEI. Con ella, tu operadora puede bloquear el móvil para que no sirva."},
    {"escena": "truco", "texto": "Truco: marca asterisco, almohadilla, cero, seis, almohadilla, y apunta ahora ese número. Es tu IMEI."},
    {"escena": "final", "texto": "Guarda este vídeo y mándaselo a quien siempre pierde el móvil. Y sígueme para más."},
]
