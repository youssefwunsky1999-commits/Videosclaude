"""«5 errores de Broncano que Abascal supo aprovechar» + el zasca de las preguntas clásicas. TikTok, >1 min.

Guion del autor (opinión), con los hechos verificados:
  - El equipo de Abascal gestionó el público a través de una agencia y Broncano lo admitió (Público; elDiario.es);
    al final del programa lamentó haber aceptado (Público). El público aplaudió reiteradamente a Abascal (Última Hora).
  - Broncano «visiblemente nervioso» (Última Hora); pidió perdón por las formas tras «no has tenido huevos» (Infobae).
  - Acordaron una entrevista «con menos chistecitos» (Infobae).
  - Zasca: Broncano: «¿Y relaciones sexuales en el último mes?»; Abascal: «Deja, corta el rollo ese» (subtítulos de
    la emisión en las capturas aportadas por el autor; imágenes cedidas por La Revuelta-TVE).
Errores 2, 3 y 5 son valoraciones (opinión), y el vídeo lo indica en pantalla."""

VOZ_ELEVENLABS = "Rie0luvrYhyKLba1lK3c"   # Mateo – News & Digital Stories

B, A = "BRONCANO", "ABASCAL"

SEGMENTOS = [
    {"escena": "gancho", "foto": "abascal_tapa", "etiqueta": "LA REVUELTA · 9 NOV",
     "texto": "¿Fue Abascal quien le ganó el pulso a Broncano? Estos son los cinco errores de Broncano que Abascal supo aprovechar.",
     "tarjetas": [
         {"quien": "", "texto": "¿QUIÉN GANÓ EL PULSO?", "en": "pulso", "grande": True},
     ]},
    {"escena": "e1", "foto": "abascal_escucha", "etiqueta": "ERROR 1 · EL PÚBLICO",
     "texto": "Error uno: dejar que el equipo de Abascal gestionara el público. El resultado: un plató que aplaudía a Abascal una y otra vez. Y el propio Broncano terminó lamentando haber aceptado.",
     "tarjetas": [
         {"quien": "", "texto": "EL PÚBLICO LO GESTIONÓ VOX", "en": "gestionara", "grande": True},
         {"quien": B, "texto": "Acabó lamentando haber aceptado", "en": "lamentando"},
     ]},
    {"escena": "e2", "foto": "broncano", "etiqueta": "ERROR 2 · SU NATURALIDAD",
     "texto": "Error dos: perder su naturalidad. Broncano suele dominar el escenario con humor. Esta vez se le vio incómodo, con intervenciones largas y titubeos.",
     "tarjetas": [
         {"quien": "", "texto": "SIN SU HUMOR", "en": "naturalidad", "grande": True},
         {"quien": "", "texto": "«Visiblemente nervioso» — Última Hora", "en": "incómodo"},
     ]},
    {"escena": "e3", "foto": "abascal_marruecos", "etiqueta": "ERROR 3 · LAS EVASIVAS",
     "texto": "Error tres: no cortar las respuestas evasivas. Abascal llevó varias respuestas a su terreno. Y un buen entrevistador no solo pregunta: insiste cuando no le responden.",
     "tarjetas": [
         {"quien": "", "texto": "RESPUESTAS A SU TERRENO", "en": "terreno", "grande": True},
     ]},
    {"escena": "e4", "foto": "broncano_israel", "etiqueta": "ERROR 4 · EL CONTROL",
     "texto": "Error cuatro: no controlar el debate. La conversación acabó en un cruce de reproches, y Broncano terminó pidiendo perdón por las formas.",
     "tarjetas": [
         {"quien": "", "texto": "CRUCE DE REPROCHES", "en": "reproches", "grande": True},
         {"quien": B, "texto": "Pidió perdón por las formas", "en": "perdón"},
     ]},
    {"escena": "e5", "foto": "bandera", "etiqueta": "ERROR 5 · LA SORPRESA",
     "texto": "Error cinco: perder el factor sorpresa. Abascal llegó preparado para una entrevista seria. Y Broncano, sin su formato de siempre, no consiguió imponer su ritmo.",
     "tarjetas": [
         {"quien": "", "texto": "ABASCAL LLEGÓ PREPARADO", "en": "preparado", "grande": True},
     ]},
    {"escena": "zasca", "foto": "broncano_clasicas", "etiqueta": "EL ZASCA DE LA NOCHE",
     "texto": "Y el zasca de la noche. Broncano tiró de sus preguntas clásicas: ¿y relaciones sexuales en el último mes?",
     "tarjetas": [
         {"quien": B, "texto": "«¿Y relaciones sexuales en el último mes?»", "en": "relaciones"},
     ]},
    {"escena": "zasca2", "foto": "abascal_corta", "etiqueta": "EL ZASCA DE LA NOCHE",
     "texto": "Abascal le cortó en seco: deja, corta el rollo ese.",
     "tarjetas": [
         {"quien": A, "texto": "«Deja, corta el rollo ese»", "en": "corta"},
         {"quien": "", "texto": "ZASCA", "en": "rollo", "grande": True},
     ]},
    {"escena": "final", "foto": "broncano_genocidio", "etiqueta": "¿Y TÚ?",
     "texto": "¿Significa esto que Abascal tenía razón en todo? No. Pero queda una pregunta incómoda: ¿estuvo Broncano a la altura? ¿Quién ganó de verdad? Te leo en comentarios. Y sígueme, que cada día hay más.",
     "tarjetas": [
         {"quien": "", "texto": "¿QUIÉN GANÓ DE VERDAD?", "en": "ganó", "grande": True},
         {"quien": "", "texto": "SÍGUEME · CADA DÍA MÁS", "en": "sígueme", "grande": True},
     ]},
]
