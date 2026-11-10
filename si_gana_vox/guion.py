"""«¿Qué pasaría en España si gana Abascal?»: lo que prometió en La Revuelta (RTVE, 9-11-2026). TikTok vertical, >1 min.

Solo promesas que hizo en la entrevista, según la prensa del 9 y 10 de noviembre de 2026:
  - Deportar a todos los extranjeros que cometan delitos; sin regularizaciones ni ayudas a inmigrantes irregulares
    (Europa Press en Diario de Pontevedra; Última Hora).
  - Derogar la Ley de Memoria Histórica si llega al Gobierno (Europa Press).
  - Revisar la ley de violencia de género, que llama «ineficaz»; que los violadores «no salgan de prisión» (Europa Press).
  - Eliminar impuestos a la primera vivienda y construir más vivienda pública (Europa Press).
  - Rechazar las normativas de transición ecológica por su impacto económico (Europa Press; Última Hora).
Audiencia: 4.815.000 espectadores, más que Pedro Sánchez (4.387.000), aunque sin batir su récord de share del 33,9 %
(Libertad Digital, 10-11-2026).
NO hay encuestas que muestren que Vox haya ganado votos por la entrevista: por eso el vídeo lo plantea como pregunta.
Fotos: capturas de la entrevista aportadas por el autor (Imagen: RTVE / La Revuelta)."""

VOZ_ELEVENLABS = "Rie0luvrYhyKLba1lK3c"   # Mateo – News & Digital Stories

B, A = "BRONCANO", "ABASCAL"

SEGMENTOS = [
    {"escena": "gancho", "foto": "abascal_marruecos", "etiqueta": "ELECCIONES 29N",
     "texto": "¿Qué pasaría en España si gana Abascal? Esto es lo que él mismo prometió en La Revuelta, delante de casi cinco millones de personas.",
     "tarjetas": [
         {"quien": "", "texto": "¿Y SI GANA VOX?", "en": "gana", "grande": True},
         {"quien": "", "texto": "4,8 MILLONES LO VIERON", "en": "millones", "grande": True},
     ]},
    {"escena": "m1", "foto": "abascal", "etiqueta": "1 · INMIGRACIÓN",
     "texto": "Uno. Inmigración. Deportar a todos los extranjeros que cometan delitos. Y nada de regularizaciones ni ayudas para los que estén en situación irregular.",
     "tarjetas": [
         {"quien": "", "texto": "DEPORTAR A LOS QUE DELINCAN", "en": "Deportar", "grande": True},
         {"quien": A, "texto": "Sin regularizaciones ni ayudas a irregulares", "en": "regularizaciones"},
     ]},
    {"escena": "m2", "foto": "abascal_escucha", "etiqueta": "2 · MEMORIA HISTÓRICA",
     "texto": "Dos. Derogar la Ley de Memoria Histórica si llega al Gobierno.",
     "tarjetas": [
         {"quien": "", "texto": "DEROGAR LA LEY DE MEMORIA", "en": "Derogar", "grande": True},
     ]},
    {"escena": "m3", "foto": "abascal_marruecos", "etiqueta": "3 · VIOLENCIA DE GÉNERO",
     "texto": "Tres. Cambiar la ley de violencia de género, que él llama ineficaz. Y que los violadores no salgan de prisión.",
     "tarjetas": [
         {"quien": A, "texto": "La ley actual es «ineficaz»", "en": "ineficaz"},
         {"quien": A, "texto": "Los violadores «no deben salir de la prisión»", "en": "violadores"},
     ]},
    {"escena": "m4", "foto": "abascal", "etiqueta": "4 · VIVIENDA Y CLIMA",
     "texto": "Cuatro. Quitar los impuestos a la primera vivienda y construir más vivienda pública. Y frenar las normas de transición ecológica.",
     "tarjetas": [
         {"quien": "", "texto": "0 IMPUESTOS A LA 1.ª VIVIENDA", "en": "impuestos", "grande": True},
         {"quien": A, "texto": "Frenar las normas de transición ecológica", "en": "transición"},
     ]},
    {"escena": "m5", "foto": "broncano", "etiqueta": "EL EFECTO BRONCANO",
     "texto": "Y un dato: Broncano le dio a Abascal más audiencia que a Pedro Sánchez. Cuatro millones ochocientos mil espectadores. ¿Le habrá dado también votos?",
     "tarjetas": [
         {"quien": "", "texto": "ABASCAL 4,8 M · SÁNCHEZ 4,4 M", "en": "audiencia", "grande": True},
         {"quien": "", "texto": "¿Y VOTOS?", "en": "votos", "grande": True},
     ]},
    {"escena": "final", "foto": "broncano_genocidio", "etiqueta": "TU VOTO",
     "texto": "Ahora te toca a ti: ¿debería ganar Vox? Sí o no, en comentarios. Y sígueme, que cada día te explico la campaña del veintinueve de noviembre en un minuto.",
     "tarjetas": [
         {"quien": "", "texto": "¿DEBERÍA GANAR VOX?", "en": "ganar", "grande": True},
         {"quien": "", "texto": "SÍGUEME · CADA DÍA UN VÍDEO", "en": "sígueme", "grande": True},
     ]},
]
