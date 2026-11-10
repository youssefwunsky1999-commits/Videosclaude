"""«Broncano vs. Abascal en La Revuelta»: resumen neutral de la entrevista (RTVE, 9-11-2026) para TikTok.

Todas las citas son textuales y salen de la prensa del 9 y 10 de noviembre de 2026:
  - Infobae: «Ocho momentos clave de Santiago Abascal en 'La Revuelta' con David Broncano»
  - Diario de Pontevedra / Europa Press: «Abascal y Broncano debaten de todo en una tensa edición de 'La Revuelta'»
  - Última Hora: «Abascal y Broncano protagonizan un tenso debate en 'La Revuelta'»
No se atribuye a nadie nada que no conste en esas crónicas, y el vídeo no toma partido.

Cada tarjeta aparece cuando la voz dice la palabra «en» (primera vez dentro de su escena; «palabra#2» = segunda)."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+14%"
TONO = "+0Hz"
PAUSA = 0.16

B, A = "BRONCANO", "ABASCAL"

SEGMENTOS = [
    {"escena": "gancho", "etiqueta": "ANOCHE EN LA REVUELTA",
     "texto": "Broncano dejó de hacer chistes. Y Abascal se despidió diciéndole que había perdido la gracia. Esto es lo que pasó anoche en La Revuelta, en cinco momentos.",
     "tarjetas": [
         {"quien": "", "texto": "SIN CHISTES", "en": "chistes", "grande": True},
         {"quien": A, "texto": "«Me sale el punto cómico que tú has perdido»", "en": "gracia"},
         {"quien": "", "texto": "5 MOMENTOS", "en": "cinco", "grande": True},
     ]},
    {"escena": "m1", "etiqueta": "1 · EL REGALO",
     "texto": "Uno. Abascal llegó con un regalo: una bandera de Ceuta. Te pediría que la pusieras. Broncano: comprometido con todos los territorios. Y pactaron una entrevista con menos chistecitos.",
     "tarjetas": [
         {"quien": "", "texto": "BANDERA DE CEUTA", "en": "bandera", "grande": True},
         {"quien": A, "texto": "«Te pediría que la pusieras»", "en": "pediría"},
         {"quien": B, "texto": "«Comprometido con todos los territorios»", "en": "comprometido"},
         {"quien": "", "texto": "«MENOS CHISTECITOS»", "en": "chistecitos", "grande": True},
     ]},
    {"escena": "m2", "etiqueta": "2 · VIVIENDA",
     "texto": "Dos: vivienda. Abascal: el problema de la vivienda es la inmigración. Y sobre los fondos buitre: el principal fondo buitre es el Gobierno.",
     "tarjetas": [
         {"quien": A, "texto": "«El problema de la vivienda es la inmigración»", "en": "problema"},
         {"quien": A, "texto": "«El principal fondo buitre es el Gobierno»", "en": "principal"},
     ]},
    {"escena": "m3", "etiqueta": "3 · EL MOMENTO MÁS TENSO",
     "texto": "Tres, el momento más tenso: Israel y Gaza. Broncano: no has tenido huevos a decírselo. Abascal culpó a Hamás: es mi posición y no voy a cambiarla. Y Broncano acabó pidiendo perdón por las formas.",
     "tarjetas": [
         {"quien": B, "texto": "«No has tenido huevos a decírselo»", "en": "huevos"},
         {"quien": A, "texto": "«Es mi posición y no voy a cambiarla»", "en": "posición"},
         {"quien": "", "texto": "BRONCANO PIDE PERDÓN POR LAS FORMAS", "en": "perdón", "grande": True},
     ]},
    {"escena": "m4", "etiqueta": "4 · EN TRES FRASES",
     "texto": "Cuatro, a toda velocidad. Violencia de género: la ley es ineficaz. Cambio climático: el clima ha cambiado siempre. Franquismo: Vox no tiene una posición.",
     "tarjetas": [
         {"quien": A, "texto": "Ley de violencia de género: «ineficaz»", "en": "ineficaz"},
         {"quien": A, "texto": "«El clima ha cambiado siempre»", "en": "clima"},
         {"quien": A, "texto": "Franquismo: «Vox no tiene una posición»", "en": "Vox"},
     ]},
    {"escena": "m5", "etiqueta": "5 · LA DESPEDIDA",
     "texto": "Y cinco, la despedida. Broncano no le deseó suerte. Abascal: yo sí, porque vas a necesitarla. A menos de tres semanas del veintinueve de noviembre. ¿Quién crees que salió ganando? Te leo en comentarios.",
     "tarjetas": [
         {"quien": B, "texto": "No le desea suerte", "en": "suerte"},
         {"quien": A, "texto": "«Yo sí, porque vas a necesitarla»", "en": "necesitarla"},
         {"quien": "", "texto": "¿QUIÉN GANÓ?", "en": "ganando", "grande": True},
     ]},
]
