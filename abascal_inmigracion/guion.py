"""«Inmigración y Gaza: lo que dijo Abascal en La Revuelta» (RTVE, 9-11-2026). TikTok vertical.

Todas las afirmaciones salen de la prensa del 9 y 10 de noviembre de 2026:
  - Defendió el término «cazar inmigrantes» (dicho por José María Figaredo) «en un contexto de invasión» de Ceuta
    (Europa Press en Diario de Pontevedra; Última Hora).
  - «Entraron 100.000 personas en una ciudad de 80.000» (Última Hora). Broncano no compartió el término «invasión» (Infobae).
  - «El problema de la vivienda es la inmigración» (Europa Press); «casi seis millones de personas en cinco años» (Infobae).
  - Pidió deportar a todos los extranjeros que cometan delitos (Europa Press; Última Hora).
  - Gaza: Broncano le reprochó no haber condenado ante Israel los bombardeos y la muerte de niños: «No has tenido huevos a
    decírselo» (Infobae; Europa Press). Abascal culpó a Hamás y dijo «Es mi posición y no voy a cambiarla» (Infobae).
    Ojo: según Europa Press también dijo que le parecía «terrorífico»; por eso el vídeo no dice que le diera igual.
«Marruecos ha sido más inteligente que España» (Abascal) y «…de las tres conversaciones que hayas tenido con Israel y en
    ninguna se haya mencionado el terrorífico genocidio que han hecho contra miles y miles de personas en Palestina»
    (Broncano): subtítulos de las capturas de la emisión aportadas por el autor.
Fotos: capturas de la entrevista aportadas por el autor (Imagen: RTVE / La Revuelta)."""

VOZ_ELEVENLABS = "Rie0luvrYhyKLba1lK3c"   # Mateo – News & Digital Stories

B, A = "BRONCANO", "ABASCAL"

SEGMENTOS = [
    {"escena": "gancho", "foto": "abascal_marruecos", "etiqueta": "LA REVUELTA · 9 NOV",
     "texto": "En la televisión pública, Abascal defendió la expresión «cazar inmigrantes». Y no fue lo más fuerte de la noche.",
     "tarjetas": [
         {"quien": "", "texto": "«CAZAR INMIGRANTES»", "en": "cazar", "grande": True},
         {"quien": "", "texto": "Y NO FUE LO MÁS FUERTE", "en": "fuerte", "grande": True},
     ]},
    {"escena": "m1", "foto": "broncano_marruecos", "etiqueta": "1 · CEUTA Y MARRUECOS",
     "texto": "Sobre Ceuta, habló de invasión: entraron cien mil personas en una ciudad de ochenta mil. Y soltó: Marruecos ha sido más inteligente que España.",
     "tarjetas": [
         {"quien": A, "texto": "«Entraron 100.000 personas en una ciudad de 80.000»", "en": "entraron"},
         {"quien": A, "texto": "«Marruecos ha sido más inteligente que España»", "en": "inteligente"},
     ]},
    {"escena": "m2", "foto": "broncano_fondos", "etiqueta": "2 · VIVIENDA E INMIGRACIÓN",
     "texto": "Para él, el problema de la vivienda es la inmigración: casi seis millones de personas en cinco años, dijo. Y propone deportar a todos los extranjeros que cometan delitos.",
     "tarjetas": [
         {"quien": A, "texto": "«El problema de la vivienda es la inmigración»", "en": "problema"},
         {"quien": "", "texto": "DEPORTAR A TODOS LOS QUE DELINCAN", "en": "deportar", "grande": True},
     ]},
    {"escena": "m3", "foto": "broncano_israel", "etiqueta": "3 · GAZA",
     "texto": "Y luego, Gaza. Broncano le reprochó que en sus tres conversaciones con Israel no mencionara el terrorífico genocidio contra miles y miles de personas en Palestina. No has tenido huevos a decírselo.",
     "tarjetas": [
         {"quien": B, "texto": "«…en ninguna se haya mencionado el terrorífico genocidio»", "en": "genocidio"},
         {"quien": B, "texto": "«No has tenido huevos a decírselo»", "en": "huevos"},
     ]},
    {"escena": "m4", "foto": "abascal_escucha", "etiqueta": "4 · LA RESPUESTA",
     "texto": "La respuesta de Abascal: la responsabilidad es de Hamás. Y sentenció: es mi posición y no voy a cambiarla.",
     "tarjetas": [
         {"quien": A, "texto": "La culpa es de Hamás", "en": "Hamás"},
         {"quien": A, "texto": "«Es mi posición y no voy a cambiarla»", "en": "posición"},
     ]},
    {"escena": "final", "foto": "broncano_genocidio", "etiqueta": "¿Y TÚ?",
     "texto": "Inmigración y Gaza: dos respuestas que no dejaron indiferente a nadie. ¿Con quién estás tú? Te leo en comentarios.",
     "tarjetas": [
         {"quien": "", "texto": "¿CON QUIÉN ESTÁS?", "en": "estás", "grande": True},
     ]},
]
