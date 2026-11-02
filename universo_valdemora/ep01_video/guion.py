"""Valdemora · Ep. 01 «Las 3:17» — guion de voces (ficción original). Ver ../ep01_las_317.md."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+17%"
TONO = "-8Hz"
PAUSA = 0.26

ABUELA = {"voz": "es-ES-ElviraNeural", "velocidad": "-2%", "tono": "-14Hz"}
LEO = {"voz": "es-ES-AlvaroNeural", "velocidad": "+8%", "tono": "+24Hz"}
DOBLE = {"voz": "es-ES-AlvaroNeural", "velocidad": "-8%", "tono": "+22Hz"}
COMPI = {"voz": "es-ES-XimenaNeural", "velocidad": "+6%", "tono": "+4Hz"}

SEGMENTOS = [
    {"escena": "regla", "texto": "Si alguien llama a tu puerta a las 3:17… no abras. En Valdemora, todos conocen esa regla."},
    {"escena": "advertencia", "texto": "Leo acaba de mudarse a Valdemora con su abuela. Y la primera noche, ella le advierte:"},
    dict(ABUELA, escena="abuela1", texto="Pase lo que pase… a las 3:17 no se abre la puerta."),
    {"escena": "pupitre", "texto": "Pensó que era una superstición. Hasta que vio un pupitre vacío en clase… y nadie recordaba quién se sentaba allí."},
    {"escena": "golpes", "texto": "Esa noche, a las 3:17, alguien llamó. Tres golpes. Lentos."},
    {"escena": "mirilla", "texto": "Leo miró por la mirilla. Al otro lado había un chico con su misma ropa… su misma cara. Y sonreía."},
    dict(DOBLE, escena="doble1", texto="Ábreme, Leo. Ya casi nadie se acuerda de ti."),
    {"escena": "foto", "texto": "Su abuela, temblando, le enseñó una foto de 1979. Su abuelo Julián… y a su lado, otro chico idéntico a él."},
    dict(ABUELA, escena="abuela2", texto="Tu abuelo abrió. Y tardé cuarenta años en recordar su nombre."),
    {"escena": "silencio", "texto": "Los golpes pararon. Silencio. Y entonces, tres golpes más. Pero no venían de la puerta."},
    {"escena": "armario", "texto": "Venían de dentro de su armario."},
    dict(DOBLE, escena="doble2", texto="Leo… ya estoy dentro."),
]
