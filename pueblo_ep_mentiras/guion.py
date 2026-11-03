"""«En este pueblo, si mientes… te crece la cabeza» (ficción original, tono alegre). Narrador en primera persona: Nico."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+14%"
TONO = "+8Hz"
PAUSA = 0.2

NINO = {"voz": "es-ES-XimenaNeural", "velocidad": "+14%", "tono": "+30Hz"}
ALCALDE = {"voz": "es-ES-AlvaroNeural", "velocidad": "-4%", "tono": "-16Hz"}
VECINOS = {"voz": "es-ES-ElviraNeural", "velocidad": "+4%", "tono": "+2Hz"}

SEGMENTOS = [
    {"escena": "gancho", "texto": "En este pueblo, si mientes… te crece la cabeza."},
    dict(NINO, escena="demo", texto="¡Yo no me he comido la tarta!"),
    {"escena": "nadie", "texto": "Por eso aquí nadie miente. Ni un poquito. Mi vecina le dice a su marido que el jersey le queda fatal… y él le da las gracias."},
    {"escena": "yo", "texto": "Me llamo Nico, y llegué al pueblo hace un año. Y lo primero que me llamó la atención fue el alcalde."},
    {"escena": "sombrero", "texto": "Siempre llevaba un sombrero enorme. Nunca se lo quitaba. Ni para dormir. Ni en agosto."},
    {"escena": "viento", "texto": "Hasta que una tarde, en mitad de la plaza, el viento se lo llevó."},
    {"escena": "cabeza", "texto": "Y todo el pueblo lo vio: tenía la cabeza más grande que habíamos visto nunca."},
    {"escena": "like", "texto": "Había mentido muchísimo. Si quieres saber sobre qué, dale like."},
    {"escena": "pregunta", "texto": "Le preguntamos. Y por primera vez, dijo la verdad:"},
    dict(ALCALDE, escena="confesion", texto="Hace treinta años dije que este era el pueblo más feliz del mundo… para que nadie se fuera."),
    {"escena": "encoge", "texto": "Al decirlo, su cabeza volvió a la normalidad. Y los vecinos le contestaron:"},
    dict(VECINOS, escena="vecinos", texto="Pues ahora sí lo es."),
    {"escena": "final", "texto": "Y ninguna cabeza creció. Por cierto… yo dije que este vídeo duraba un minuto."},
]
