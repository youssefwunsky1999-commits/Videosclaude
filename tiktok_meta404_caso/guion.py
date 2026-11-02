"""Guion del TikTok «MENTE404 · El caso del cartel robado» (whodunit; el público adivina en comentarios).

SOLUCIÓN (para la parte 2, no se dice en el vídeo): Lola miente. Dice que a las 3 estaba regando sus flores,
pero aquella noche llovía (pista 3). La flor violeta aplastada junto a la caja es de su jardín. Usó la llave de
repuesto que Tito guarda bajo la maceta que ella le regaló, y pisó la harina del saco que Paco deja fuera.
"""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+14%"
TONO = "-4Hz"
PAUSA = 0.24

SEGMENTOS = [
    {"escena": "gancho",
     "texto": "Uno de estos tres vecinos es un ladrón. Y al final del vídeo, tú vas a decidir quién."},
    {"escena": "recap",
     "texto": "Hace unos días, alguien apagó las luces de Mente cuatro cero cuatro y robó el cartel de la ciudad."},
    {"escena": "detective",
     "texto": "Así que llamamos al mejor detective del pueblo: el detective Bloque."},
    {"escena": "pista1",
     "texto": "Primera pista: la caja de la luz no estaba rota. La abrieron con llave."},
    {"escena": "pista2",
     "texto": "Segunda pista: junto a los postes, una huella llena de harina."},
    {"escena": "pista3",
     "texto": "Y tercera: una flor violeta, aplastada en el barro. Aquella noche llovió."},
    {"escena": "like",
     "texto": "Si ya tienes un sospechoso, dale like. Ahora toca interrogar."},
    {"escena": "tito", "voz": "es-MX-JorgeNeural", "velocidad": "+12%", "tono": "+0Hz",
     "texto": "Soy Tito, el electricista. Sí, tengo la única llave de la caja… pero a las tres estaba durmiendo."},
    {"escena": "paco", "voz": "es-AR-TomasNeural", "velocidad": "+12%", "tono": "-2Hz",
     "texto": "Soy Paco, el panadero. La harina es mía, claro. Pero a esa hora, la panadería estaba cerrada."},
    {"escena": "lola", "voz": "es-ES-ElviraNeural", "velocidad": "+12%", "tono": "+2Hz",
     "texto": "Soy Lola, la jardinera. ¿Yo? A las tres estaba regando mis flores, como cada noche."},
    {"escena": "pregunta",
     "texto": "Uno de los tres miente. ¿Quién robó el cartel? Fíjate bien en las pistas."},
    {"escena": "final",
     "texto": "Comenta tu sospechoso. Si aciertas, saldrás en la parte dos… como ayudante del detective."},
]
