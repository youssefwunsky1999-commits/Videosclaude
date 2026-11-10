"""«GTA VI sale en menos de 10 días»: vídeo de hype con datos reales y anuncio de sorteo (TikTok vertical).

Datos (prensa, consultada el 10-11-2026):
  - Lanzamiento el 19-11-2026 en PS5 y Xbox Series X|S; sin versión de PC anunciada (Infobae, 25-10-2026).
  - Escenario: estado de Leonida, Vice City; protagonistas Lucía Caminos y Jason Duval (Infobae).
  - Reservas: descarga anticipada desde el 12-11, se juega desde el lanzamiento (Infobae).
  - Retrasado dos veces: de 2025 al 26-5-2026 y de ahí al 19-11-2026; Take-Two mantiene la fecha (Infobae, 5-2-2026).
  - Primer tráiler (dic. 2023): 90.421.491 visualizaciones en 24 h en YouTube, récord Guinness (eldiario.com, RPP).
  - Segundo tráiler (mayo 2025): 475 millones de visualizaciones en 24 h sumando plataformas, según Rockstar (Claro Sports).
  - GTA V salió en septiembre de 2013: 13 años de espera.
Sorteo (compromiso del autor de la cuenta): si el vídeo llega a 10.000 likes, 1 copia de GTA VI (PS5 o Xbox a elegir)
entre quienes den like y comenten «GTA6». Ganador: 19-11-2026.

Tipos de tarjeta: "grande" (sello), "dato" (cifra que cuenta hasta su valor), por defecto (texto)."""

VOZ = "es-MX-JorgeNeural"
VELOCIDAD = "+14%"
TONO = "-4Hz"
PAUSA = 0.14

SEGMENTOS = [
    {"escena": "gancho", "etiqueta": "LA ESPERA SE ACABA",
     "texto": "Trece años esperando. Y en menos de diez días, se acaba la espera. Esto es todo lo que tienes que saber de GTA seis.",
     "tarjetas": [
         {"texto": "13 AÑOS", "en": "Trece", "grande": True},
         {"texto": "MENOS DE 10 DÍAS", "en": "diez", "grande": True},
     ]},
    {"escena": "fecha", "etiqueta": "FECHA",
     "texto": "Diecinueve de noviembre. En PlayStation cinco y Xbox Series. Y ojo: en PC no sale el primer día.",
     "tarjetas": [
         {"texto": "19 NOV 2026", "en": "Diecinueve", "grande": True},
         {"texto": "PS5 · XBOX SERIES X|S", "en": "PlayStation"},
         {"texto": "PC: NO EN EL LANZAMIENTO", "en": "PC", "tachado": True},
     ]},
    {"escena": "mundo", "etiqueta": "EL MAPA",
     "texto": "Volvemos a Vice City, en el estado de Leonida. Y esta vez, dos protagonistas: Lucía y Jason.",
     "tarjetas": [
         {"texto": "VICE CITY", "en": "Vice", "grande": True},
         {"texto": "Estado de LEONIDA", "en": "Leonida"},
         {"texto": "LUCÍA  +  JASON", "en": "Lucía", "grande": True},
     ]},
    {"escena": "hype", "etiqueta": "EL HYPE",
     "texto": "El primer tráiler hizo noventa millones de visitas en veinticuatro horas. Récord Guinness. Y el segundo, cuatrocientos setenta y cinco millones, según Rockstar.",
     "tarjetas": [
         {"texto": "90.421.491", "pie": "visitas en 24 h · 1.er tráiler · récord Guinness", "en": "noventa", "dato": 90421491},
         {"texto": "475.000.000", "pie": "visitas en 24 h · 2.º tráiler · todas las plataformas", "en": "cuatrocientos", "dato": 475000000},
     ]},
    {"escena": "fomo", "etiqueta": "NO TE QUEDES FUERA",
     "texto": "Si lo reservas, lo descargas desde el doce de noviembre y juegas desde el primer minuto. Ya lo retrasaron dos veces. Esta vez, Take-Two insiste: la fecha se mantiene.",
     "tarjetas": [
         {"texto": "DESCARGA ANTICIPADA: 12 NOV", "en": "doce"},
         {"texto": "2 RETRASOS", "en": "retrasaron", "grande": True},
         {"texto": "«La fecha se mantiene»", "en": "mantiene"},
     ]},
    {"escena": "sorteo", "etiqueta": "SORTEO",
     "texto": "Y ahora lo bueno. Si este vídeo llega a diez mil likes, sorteo una copia de GTA seis entre quienes den like y comenten GTA seis. El ganador, el diecinueve de noviembre. Comenta ya.",
     "tarjetas": [
         {"texto": "10.000 LIKES", "en": "diez", "grande": True},
         {"texto": "1 COPIA DE GTA VI · PS5 o Xbox", "en": "copia"},
         {"texto": "Like + comenta «GTA6»", "en": "comenten"},
         {"texto": "GANADOR: 19 NOV", "en": "ganador", "grande": True},
     ]},
]
