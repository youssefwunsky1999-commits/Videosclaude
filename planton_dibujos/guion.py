"""«Abascal planta a Jordi Wild»: Vox suspende la entrevista en The Wild Project y culpa a La Revuelta (11-11-2026).

Fuentes: comunicado de VOX del 11-11-2026 (captura aportada por el autor) y Cadena SER, «Vox acusa a 'La Revuelta' de
incumplir su acuerdo sobre la visita de Abascal a Broncano y cancela la entrevista con Jordi Wild» (11-11-2026, 12:39).
Del comunicado: «Ante los graves incumplimientos de La Revuelta…»; El Terrat y TVE «se niegan a entregar a VOX o hacer
pública la grabación íntegra de la entrevista, incluidos los 40 minutos suprimidos»; «el ente público está secuestrando
40 minutos de respuestas de nuestro candidato»; Abascal no acudirá a programas que pretendan «un control en exclusiva de
las respuestas»; se suspende la entrevista en The Wild Project «prevista para hoy día 11 de noviembre, sin que ello
suponga, en modo alguno, atribución a Jordi Wild de incumplimiento ninguno»."""

VOZ_ELEVENLABS = "Rie0luvrYhyKLba1lK3c"   # Mateo – News & Digital Stories

V = "VOX"

SEGMENTOS = [
    {"escena": "gancho", "foto": "abascal_tapa", "etiqueta": "ÚLTIMA HORA · 11 NOV",
     "texto": "Abascal acaba de plantar a Jordi Wild. Y según Vox, la culpa es de La Revuelta.",
     "tarjetas": [
         {"quien": "", "texto": "¿LA CULPA? LA REVUELTA", "en": "culpa", "grande": True},
     ]},
    {"escena": "m1", "foto": "comunicado", "etiqueta": "1 · EL COMUNICADO",
     "texto": "Vox ha suspendido la entrevista en The Wild Project, que se iba a grabar hoy mismo. En un comunicado, habla de graves incumplimientos de La Revuelta.",
     "tarjetas": [
         {"quien": "", "texto": "ENTREVISTA SUSPENDIDA", "en": "suspendido", "grande": True},
         {"quien": V, "texto": "«Graves incumplimientos de La Revuelta»", "en": "incumplimientos"},
     ]},
    {"escena": "m2", "foto": "abascal_marruecos", "etiqueta": "2 · LOS 40 MINUTOS",
     "texto": "¿Qué denuncia? Que TVE y El Terrat no le entregan la grabación completa, con cuarenta minutos que no se emitieron. Y lo dice así: el ente público está secuestrando cuarenta minutos de respuestas de nuestro candidato.",
     "tarjetas": [
         {"quien": "", "texto": "40 MINUTOS CORTADOS", "en": "emitieron", "grande": True},
         {"quien": V, "texto": "«El ente público está secuestrando 40 minutos de respuestas»", "en": "secuestrando"},
     ]},
    {"escena": "m3", "foto": "plato_efe", "etiqueta": "3 · SUS NUEVAS CONDICIONES",
     "texto": "Y pone condiciones: Abascal no irá a ningún programa que se reserve el control en exclusiva de sus respuestas, sin que Vox tenga el mismo derecho sobre la imagen y el contenido.",
     "tarjetas": [
         {"quien": "", "texto": "SOLO SI CONTROLA SUS RESPUESTAS", "en": "exclusiva", "grande": True},
     ]},
    {"escena": "m4", "foto": "titular_ser", "etiqueta": "4 · ¿Y JORDI WILD?",
     "texto": "Eso sí: Vox aclara que no culpa de nada a Jordi Wild. Dice que solo quiere proteger su reputación en plena campaña.",
     "tarjetas": [
         {"quien": V, "texto": "Sin «atribución a Jordi Wild de incumplimiento ninguno»", "en": "Wild"},
         {"quien": "", "texto": "«PROTEGER SU REPUTACIÓN»", "en": "reputación", "grande": True},
     ]},
    {"escena": "final", "foto": "abascal_corta", "etiqueta": "¿Y TÚ?",
     "texto": "¿Queja justa contra La Revuelta, o miedo a otra entrevista incómoda? Te leo en comentarios. Y sígueme, que esto no ha acabado.",
     "tarjetas": [
         {"quien": "", "texto": "¿QUEJA JUSTA O MIEDO?", "en": "miedo", "grande": True},
         {"quien": "", "texto": "SÍGUEME · ESTO NO ACABA AQUÍ", "en": "sígueme", "grande": True},
     ]},
]
