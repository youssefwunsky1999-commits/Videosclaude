"""«La peor noche de Broncano»: vídeo de opinión sobre la entrevista a Abascal en La Revuelta (RTVE, 9-11-2026).

Es opinión («la peor noche»), pero cada hecho es real y sale de la prensa:
  - «menos chistecitos»: acordaron una entrevista con menos humor tras el momento Ceuta (Infobae, 9-11-2026).
  - El público lo gestionó el equipo de Abascal a través de una agencia; lo admitió Broncano: «Había un cierto temor a
    que el público habitual dificultase el ritmo de la entrevista» (Público, 9-11-2026). El público aplaudió a Abascal
    (Infobae; Última Hora).
  - «No has tenido huevos a decírselo» y después pidió perdón por las formas (Infobae; Europa Press).
  - «Visiblemente nervioso» (Última Hora, 10-11-2026).
  - «Me sale el punto cómico que tú has perdido en esta entrevista» (Abascal, despedida; Infobae).
  - Al final del programa lamentó haber aceptado la petición sobre el público (Público).
Huecos «clip»: momentos del programa que pondrá el autor (Imágenes: RTVE / La Revuelta)."""

VOZ_ELEVENLABS = "Rie0luvrYhyKLba1lK3c"   # Mateo – News & Digital Stories

B, A = "BRONCANO", "ABASCAL"

SEGMENTOS = [
    {"escena": "gancho", "etiqueta": "LA PEOR NOCHE DE BRONCANO",
     "texto": "Un humorista. En su propio programa. Sin chistes, sin su público… y pidiendo perdón. Así fue la peor noche de Broncano.",
     "clip": "despedida (Abascal: «me sale el punto cómico que tú has perdido»)",
     "tarjetas": [
         {"quien": "", "texto": "SIN CHISTES", "en": "chistes", "grande": True},
         {"quien": "", "texto": "SIN SU PÚBLICO", "en": "público", "grande": True},
         {"quien": "", "texto": "PIDIENDO PERDÓN", "en": "perdón", "grande": True},
     ]},
    {"escena": "m1", "etiqueta": "1 · RENUNCIÓ AL HUMOR",
     "texto": "Uno. Renunció a lo suyo: aceptó una entrevista con menos chistecitos. Un programa de humor… sin humor.",
     "clip": "momento de la bandera de Ceuta y el pacto de «menos chistecitos»",
     "tarjetas": [
         {"quien": "", "texto": "«MENOS CHISTECITOS»", "en": "chistecitos", "grande": True},
         {"quien": "", "texto": "Un programa de humor… sin humor", "en": "humor#2", "quien_libre": True},
     ]},
    {"escena": "m2", "etiqueta": "2 · LE CAMBIARON EL PÚBLICO",
     "texto": "Dos. Dejó que el equipo de Abascal gestionara el público, a través de una agencia. Resultado: aplausos para Abascal… en su propio plató.",
     "clip": "Broncano explicando lo del público",
     "tarjetas": [
         {"quien": B, "texto": "«Había un cierto temor a que el público habitual dificultase el ritmo»", "en": "agencia"},
         {"quien": "", "texto": "APLAUSOS PARA ABASCAL", "en": "aplausos", "grande": True},
     ]},
    {"escena": "m3", "etiqueta": "3 · PERDIÓ LOS PAPELES",
     "texto": "Tres. Perdió los papeles: le soltó «no has tenido huevos»… y acabó pidiéndole perdón por las formas. Última Hora lo describe visiblemente nervioso.",
     "clip": "«no has tenido huevos» y la disculpa",
     "tarjetas": [
         {"quien": B, "texto": "«No has tenido huevos a decírselo»", "en": "huevos"},
         {"quien": "", "texto": "PIDE PERDÓN POR LAS FORMAS", "en": "perdón", "grande": True},
         {"quien": "", "texto": "«Visiblemente nervioso» — Última Hora", "en": "nervioso", "quien_libre": True},
     ]},
    {"escena": "m4", "etiqueta": "4 · EL REMATE",
     "texto": "Y el remate. Broncano no le deseó suerte. Y Abascal le contestó: me sale el punto cómico que tú has perdido en esta entrevista.",
     "clip": "la despedida completa",
     "tarjetas": [
         {"quien": A, "texto": "«Me sale el punto cómico que tú has perdido en esta entrevista»", "en": "cómico"},
     ]},
    {"escena": "final", "etiqueta": "¿LA PEOR DE SU CARRERA?",
     "texto": "Al final del programa, el propio Broncano lamentó haber cedido con el público. ¿Fue la peor entrevista de su carrera? Te leo en comentarios.",
     "clip": None,
     "tarjetas": [
         {"quien": "", "texto": "BRONCANO SE ARREPIENTE", "en": "lamentó", "grande": True},
         {"quien": "", "texto": "¿LA PEOR DE SU CARRERA?", "en": "peor", "grande": True},
     ]},
]
