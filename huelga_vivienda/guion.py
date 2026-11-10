"""«Mañana hay huelga general… y la apoya parte del Gobierno»: la huelga por la vivienda del 11N (TikTok, >1 min).

Datos (prensa del 3 al 9 de noviembre de 2026):
  - Huelga general de 24 h por la vivienda el miércoles 11-11-2026 en toda España; la impulsa el Sindicato de Inquilinas
    y se suman UGT y CCOO, que le dan la cobertura legal (Infobae, 7-10-2026; El Español, 9-11-2026).
  - El Congreso rechazó los dos decretos de vivienda del Gobierno con los votos de PP, Vox y Junts (El Constitucional,
    3-10-2026; El Español: la huelga nace por ese rechazo).
  - Yolanda Díaz: «Creo que va a ser la primera vez que no puedo ir de piquete. Bien que me gustaría» (Moncloa.com,
    8-11-2026); «¿Qué es una huelga si no es política?» (El Español).
  - El PSOE la sitúa contra la oposición que tumbó los decretos; Sordo (CCOO) y Álvarez (UGT): «nadie ha dicho que esta
    huelga se convoque contra la oposición» (El Español, 9-11-2026).
  - Feijóo: «No la hagan. No la hicieron en ocho años de Gobierno. No la hagan ahora». Garamendi (CEOE): «Esta huelga es
    parte de una campaña, es una huelga electoral» (El Español, 9-11-2026).
  - SocioMétrica: solo el 22,5 % de los trabajadores planea secundarla (El Español, 9-11-2026).
Fotos: manifestaciones por la vivienda en Madrid, aportadas por el autor."""

VOZ_ELEVENLABS = "Rie0luvrYhyKLba1lK3c"   # Mateo – News & Digital Stories

SEGMENTOS = [
    {"escena": "gancho", "foto": "granvia", "etiqueta": "11N · HUELGA GENERAL",
     "texto": "Mañana, España va a la huelga general. Y lo más raro de todo: la apoya parte del propio Gobierno.",
     "tarjetas": [
         {"quien": "", "texto": "HUELGA GENERAL", "en": "huelga", "grande": True},
         {"quien": "", "texto": "LA APOYA EL PROPIO GOBIERNO", "en": "Gobierno", "grande": True},
     ]},
    {"escena": "m1", "foto": "cibeles", "etiqueta": "1 · POR LA VIVIENDA",
     "texto": "Es una huelga por la vivienda. La impulsa el Sindicato de Inquilinas, y se han sumado UGT y Comisiones Obreras. Veinticuatro horas, en toda España.",
     "tarjetas": [
         {"quien": "", "texto": "POR LA VIVIENDA", "en": "vivienda", "grande": True},
         {"quien": "SINDICATOS", "texto": "Sindicato de Inquilinas + UGT + CCOO", "en": "Comisiones"},
     ]},
    {"escena": "m2", "foto": "estudiantes", "etiqueta": "2 · EL DETONANTE",
     "texto": "¿El detonante? El Congreso tumbó los dos decretos de vivienda del Gobierno, con los votos de PP, Vox y Junts.",
     "tarjetas": [
         {"quien": "", "texto": "DECRETOS TUMBADOS", "en": "tumbó", "grande": True},
         {"quien": "", "texto": "PP + VOX + JUNTS", "en": "Junts", "grande": True},
     ]},
    {"escena": "m3", "foto": "granvia", "etiqueta": "3 · EL LÍO DEL GOBIERNO",
     "texto": "Y aquí empieza el lío. Yolanda Díaz, vicepresidenta del Gobierno, anima a ir: dice que bien que le gustaría ir de piquete. El PSOE la presenta como una huelga contra la oposición. Pero los sindicatos lo niegan.",
     "tarjetas": [
         {"quien": "YOLANDA DÍAZ", "texto": "«Bien que me gustaría» ir de piquete", "en": "piquete"},
         {"quien": "SINDICATOS", "texto": "«Nadie ha dicho que se convoque contra la oposición»", "en": "niegan"},
     ]},
    {"escena": "m4", "foto": "cibeles", "etiqueta": "4 · LA OPOSICIÓN",
     "texto": "Feijóo pide que no se haga: no la hicieron en ocho años de Gobierno, no la hagan ahora. Y la patronal la llama huelga electoral.",
     "tarjetas": [
         {"quien": "FEIJÓO", "texto": "«No la hicieron en ocho años de Gobierno. No la hagan ahora»", "en": "ocho"},
         {"quien": "", "texto": "CEOE: «HUELGA ELECTORAL»", "en": "electoral", "grande": True},
     ]},
    {"escena": "m5", "foto": "estudiantes", "etiqueta": "EL DATO",
     "texto": "Y un dato: según una encuesta de SocioMétrica, solo el veintidós y medio por ciento de los trabajadores piensa secundarla.",
     "tarjetas": [
         {"quien": "", "texto": "SOLO EL 22,5 % LA SECUNDARÁ", "en": "veintidós", "grande": True},
     ]},
    {"escena": "final", "foto": "granvia", "etiqueta": "TU VOTO",
     "texto": "A menos de tres semanas de las elecciones: ¿esta huelga le hace daño al PSOE, o a la oposición? Te leo en comentarios. Y sígueme, que mañana te cuento cómo ha ido.",
     "tarjetas": [
         {"quien": "", "texto": "¿A QUIÉN LE HACE DAÑO?", "en": "daño", "grande": True},
         {"quien": "", "texto": "SÍGUEME · MAÑANA EL RESULTADO", "en": "sígueme", "grande": True},
     ]},
]
