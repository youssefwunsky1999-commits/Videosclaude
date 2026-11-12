"""«GTA VI: todo lo que sabemos antes del lanzamiento» — vídeo largo para YouTube (1920x1080, 8-12 min).

Estilo: el neón retro de gta6/ (atardecer, sol a franjas, palmeras, carretera de rejilla) con tarjetas, cifras que cuentan
y dibujos vectoriales tipo explicativo (planton_dibujos/). Original: sin logos, tipografías ni imágenes de Rockstar.

DATOS Y FUENTES (consultadas el 12-11-2026). Lo que es rumor o estimación se dice como tal en la voz y en pantalla.
  Fecha y plataformas
  - 19-11-2026 en PS5 y Xbox Series X|S; reconfirmada en el informe de Take-Two del 9-11-2026, el último antes del
    lanzamiento (StockTitan, 9-11-2026; TechRadar). Rockstar: «no habrá más retrasos» (Vandal, 25-6-2026).
  - Sin versión de PC anunciada; Zelnick (Take-Two): Rockstar va primero a consolas, donde está su público principal
    (Infobae, 22-6-2026). Exdesarrollador John Ricchio: más fácil hacerlo para consola y ampliarlo a PC (Vandal).
  - GTA V: consolas sep. 2013, PC abr. 2015 (~19 meses). RDR2: consolas oct. 2018, PC nov. 2019 (~13 meses).
  Retrasos e historia
  - 4-2-2022: Rockstar confirma que el desarrollo está «muy avanzado». Sep. 2022: filtración de vídeos en desarrollo
    por un joven hacker; Take-Two/Rockstar cifraron el coste en unos 5 millones de dólares (prensa; Wikipedia la recoge).
  - Tráiler 1 (dic. 2023) con ventana 2025. 2-5-2025: retraso al 26-5-2026. 6-11-2025: retraso al 19-11-2026, para
    terminarlo con el pulido que los fans «esperan y merecen» (3DJuegos, Geeknetic, Ámbito).
  - Oct. 2025: despido de más de 30 empleados por, según Rockstar, difundir información confidencial; el sindicato IWGB
    la acusó de castigar a quienes intentaban sindicarse (prensa; Wikipedia).
  Leonida y Vice City
  - Leonida (Florida ficticia), Vice City (Miami), Cayos de Leonida, Grassrivers (Everglades), Port Gellhorn, Ambrosia,
    parque nacional del monte Kalaga (web de Rockstar, mayo 2025). Tamaño: sin cifra oficial (estimaciones = rumor).
  - Cartel «Welcome to Vice City» en el Kaseya Center (Miami Heat), unos 975.000 $ al condado (Notebookcheck, Beebom,
    GamesRadar, sep. 2026).
  Lucía y Jason
  - Descripciones oficiales de Rockstar: Lucía Caminos (penitenciaría de Leonida por luchar por su familia; «solo
    movimientos inteligentes») y Jason Duval (creció entre timadores, ejército, los Cayos trabajando para traficantes);
    un golpe fácil sale mal y acaban en una conspiración criminal por todo Leonida. Secundarios: Cal Hampton, Boobie
    Ike, Dre'Quan Priest, Raul Bautista, Brian Heder (Rockstar).
  Tráileres
  - T1 (4-12-2023, adelantado por filtración): 90.421.491 vistas en YouTube en 24 h, récord Guinness (Infobae, Variety).
  - T2 (6-5-2025): 475 millones en 24 h sumando plataformas, según Rockstar (Claro Sports).
  - Mar. 2026: el tráiler de Spider-Man: Brand New Day supera los 718,6 millones en 24 h (HD Tecnología citando a IGN).
  - 27-8-2026: «An Extended Look» de 26 min, primero en Netflix (Netflix Tudum, What's on Netflix); 31 millones de
    espectadores en 4 días, según Zelnick (StockTitan, 9-11-2026).
  - 15-10-2026: tráiler de lanzamiento con música de Justice (Gematsu); en 3 días superó las vistas totales del tráiler
    de lanzamiento de GTA V (~34,6 M) (ixbt.games, 20-10-2026).
  Precio y ediciones
  - Reservas desde el 25-6-2026. Estándar 79,99 €; Ultimate 99,99 € (Vandal, Xataka). Ultimate: vehículos, armas, ropa
    y extras a lo largo de la historia (Grotti Cheetah de 1995, yate…). Reserva antes del 20-11: pack Vintage Vice City
    (Vapid Stanier de 1955 de dos tonos, garaje en Shore Court junto a Ocean Beach, ropa y peinados) (Vandal). Reservas
    digitales: 1 mes de GTA+ (StockTitan). Edición física sin disco: código en la caja (Vandal, VidaExtra).
  - Take-Two: reservas «muy por encima de nuestras expectativas iniciales», «niveles sin precedentes»; sin cifras
    (StockTitan, 9-11-2026). Las cifras de millones de reservas son estimaciones de analistas (Sensor Tower, etc.).
  Rumores (marcados como tales)
  - Modo online: Jason Schreier informó en 2020 de un gran componente online; Rockstar lo describe como experiencia para
    un jugador y no ha anunciado online (Vandal, StockTitan).
  - 30 fps: un youtuber invitado a Rockstar North contó que en desarrollo va a 30 fps en consola; sin ficha técnica
    oficial (VGC, GamesRadar, ago. 2026).
  - PC en 2027: fuentes del sector, sin confirmar (Infobae, Vandal).
  - CyberLeek: supuestas filtraciones (ago. 2026); Take-Two pidió citaciones a Discord y Microsoft (VGC, Push Square).
  - Historia por capítulos, como RDR2 (Vandal).
  Día de lanzamiento
  - Precarga desde el 10-11 en PS5 y Xbox; física desde el 12-11 (código antes de precargar); 212 GB; el 19-11 póster y
    mapa de Leonida en descarga gratuita (VidaExtra, 10-11-2026; El Diario de Madrid). En España, desde las 00:00 del
    19-11 hora local en las tiendas de PlayStation y Microsoft (HardZone, SomosXbox).

Estructura: CAPITULOS -> escenas. La voz se genera por capítulo (texto de sus escenas unido) y se alinea por escena.
Tipos de escena: portada, titulo, indice, tarjetas (con «dib» opcional), cifra, barras, linea, cita, mapa, precios.
Cada elemento aparece cuando la voz dice la palabra «en» (palabra#n para la n-ésima)."""

VOZ_ELEVENLABS = "Rie0luvrYhyKLba1lK3c"   # Mateo – News & Digital Stories
TITULO = "GTA VI: todo lo que sabemos antes del lanzamiento"

CAPITULOS = [
    {"id": "intro", "titulo": "", "escenas": [
        {"id": "gancho", "tipo": "titulo",
         "texto": "Dentro de siete días sale GTA seis. Trece años de espera, dos retrasos, y unos tráileres que pulverizaron los récords de YouTube.",
         "fuente": "Take-Two · Rockstar Games · Guinness World Records",
         "items": [{"t": "7 DÍAS", "en": "siete"}, {"t": "13 AÑOS", "en": "Trece"},
                   {"t": "2 RETRASOS", "en": "retrasos"}, {"t": "RÉCORDS", "en": "récords"}]},
        {"id": "indice", "tipo": "indice",
         "texto": "En este vídeo te cuento todo lo que sabemos antes del lanzamiento: la fecha, el mapa, los protagonistas, el precio, y qué es verdad y qué es solo rumor. Vamos allá.",
         "fuente": "Datos verificados en prensa · nov. 2026",
         "items": [{"t": "Fecha", "en": "fecha"}, {"t": "Mapa", "en": "mapa"}, {"t": "Protagonistas", "en": "protagonistas"},
                   {"t": "Precio", "en": "precio"}, {"t": "Verdad", "en": "verdad", "k": "ok"}, {"t": "Rumor", "en": "rumor", "k": "r"}]},
    ]},
    {"id": "c1", "titulo": "FECHA, PLATAFORMAS Y PC", "escenas": [
        {"id": "c1a", "tipo": "portada", "num": 1,
         "texto": "Capítulo uno. La fecha, las plataformas, y por qué no sale en PC.",
         "fuente": ""},
        {"id": "c1b", "tipo": "tarjetas", "dib": "calendario",
         "texto": "GTA seis sale el jueves diecinueve de noviembre de dos mil veintiséis. Take-Two lo volvió a confirmar el nueve de noviembre, en su último informe de resultados antes del lanzamiento. Y Take-Two insiste en que no habrá más retrasos.",
         "fuente": "Take-Two, informe del 9-11-2026 (StockTitan) · Vandal",
         "items": [{"t": "JUEVES 19 NOV 2026", "en": "diecinueve", "k": "g"},
                   {"t": "Reconfirmado por Take-Two el 9 de noviembre", "en": "nueve"},
                   {"t": "«No habrá más retrasos»", "en": "retrasos"}]},
        {"id": "c1c", "tipo": "tarjetas", "dib": "consolas",
         "texto": "Sale en PlayStation cinco y en Xbox Series X y Series S. Solo en la generación actual: ni PlayStation cuatro, ni Xbox One.",
         "fuente": "Rockstar Games · Take-Two",
         "items": [{"t": "PLAYSTATION 5", "en": "PlayStation"}, {"t": "XBOX SERIES X|S", "en": "Xbox"},
                   {"t": "PS4 y XBOX ONE", "en": "ni", "k": "x"}]},
        {"id": "c1d", "tipo": "tarjetas", "dib": "pc",
         "texto": "¿Y en PC? De momento, nada. No hay ninguna versión de PC anunciada. Así que si ves una reserva o una clave para PC, desconfía.",
         "fuente": "Infobae, 22-6-2026 · Take-Two",
         "items": [{"t": "PC: SIN ANUNCIAR", "en": "nada", "k": "x"}, {"t": "¿Claves de PC? Desconfía", "en": "desconfía"}]},
        {"id": "c1e", "tipo": "barras",
         "texto": "¿Por qué? Strauss Zelnick, el jefe de Take-Two, lo ha explicado: Rockstar va primero a consolas, porque ahí está su público principal. Ya lo hizo antes. GTA cinco llegó a PC un año y medio después. Y Red Dead Redemption dos tardó algo más de un año.",
         "fuente": "Infobae, 22-6-2026 · fechas de lanzamiento de GTA V (2013/2015) y RDR2 (2018/2019)",
         "titulo": "MESES DE ESPERA HASTA LLEGAR A PC",
         "items": [{"t": "GTA V", "n": 19, "suf": " meses", "en": "medio"}, {"t": "RED DEAD 2", "n": 13, "suf": " meses", "en": "tardó"}],
         "nota": {"t": "«Primero, consolas: ahí está su público»", "en": "consolas"}},
        {"id": "c1f", "tipo": "cita",
         "texto": "Y un antiguo desarrollador de Rockstar lo resumía así: es más fácil crear un juego dentro de los límites de una consola y luego ampliarlo para PC, que hacerlo al revés.",
         "fuente": "Vandal",
         "cita": "Es más fácil hacerlo dentro de los límites de una consola y luego ampliarlo para PC que al revés.",
         "autor": "John Ricchio, exdesarrollador de Rockstar", "en": "fácil"},
    ]},
    {"id": "c2", "titulo": "LOS RETRASOS", "escenas": [
        {"id": "c2a", "tipo": "portada", "num": 2,
         "texto": "Capítulo dos. Los retrasos, y la larga historia del desarrollo.",
         "fuente": ""},
        {"id": "c2b", "tipo": "cifra",
         "texto": "GTA cinco salió en septiembre de dos mil trece. Desde entonces han pasado más de trece años: el mayor salto entre dos entregas principales de la saga.",
         "fuente": "GTA V: 17-9-2013 · GTA VI: 19-11-2026",
         "items": [{"n": 13, "suf": " AÑOS", "pie": "de GTA V (sep. 2013) a GTA VI (nov. 2026)", "en": "trece#2"}]},
        {"id": "c2c", "tipo": "linea",
         "texto": "En febrero de dos mil veintidós, Rockstar confirmó por fin que el desarrollo estaba muy avanzado. Y en septiembre de ese mismo año sufrió una filtración enorme: un joven hacker publicó decenas de vídeos del juego en pleno desarrollo. La compañía calculó que aquello le costó unos cinco millones de dólares.",
         "fuente": "Rockstar Games, 4-2-2022 · Take-Two · prensa",
         "items": [{"f": "FEB 2022", "t": "Desarrollo «muy avanzado»", "en": "febrero"},
                   {"f": "SEP 2022", "t": "Filtración de vídeos", "en": "septiembre"},
                   {"f": "COSTE", "t": "≈ 5 millones de $", "en": "cinco"}]},
        {"id": "c2d", "tipo": "linea",
         "texto": "El primer tráiler, en diciembre de dos mil veintitrés, prometía el juego para dos mil veinticinco. Pero el dos de mayo de dos mil veinticinco llegó el primer retraso: al veintiséis de mayo de dos mil veintiséis. Y el seis de noviembre de ese año, el segundo: al diecinueve de noviembre.",
         "fuente": "Rockstar Games (X), 2-5-2025 y 6-11-2025 · 3DJuegos · Ámbito",
         "items": [{"f": "DIC 2023", "t": "Ventana: 2025", "en": "prometía", "k": "x"},
                   {"f": "2 MAY 2025", "t": "→ 26 de mayo de 2026", "en": "primer#2", "k": "x"},
                   {"f": "6 NOV 2025", "t": "→ 19 de noviembre de 2026", "en": "segundo", "k": "ok"}]},
        {"id": "c2e", "tipo": "cita",
         "texto": "Rockstar pidió disculpas, y explicó que necesitaba más tiempo para terminar el juego con el nivel de pulido que los fans esperan y merecen.",
         "fuente": "Rockstar Games, 6-11-2025 (3DJuegos, Geeknetic)",
         "cita": "Necesitamos más tiempo para terminarlo con el nivel de pulido que esperáis y merecéis.",
         "autor": "Rockstar Games, al anunciar el segundo retraso", "en": "pulido"},
        {"id": "c2f", "tipo": "tarjetas", "dib": "despidos",
         "texto": "Y no ha sido un camino tranquilo. En octubre de dos mil veinticinco, Rockstar despidió a más de treinta empleados, por difundir información confidencial, según la empresa. El sindicato británico IWGB la acusó de castigar a trabajadores que intentaban organizarse.",
         "fuente": "Prensa, oct. 2025 · IWGB",
         "items": [{"t": "+30 DESPIDOS", "en": "treinta", "k": "g"},
                   {"t": "Rockstar: «información confidencial»", "en": "confidencial"},
                   {"t": "Sindicato IWGB: «castigo por organizarse»", "en": "sindicato"}]},
    ]},
    {"id": "c3", "titulo": "LEONIDA Y VICE CITY", "escenas": [
        {"id": "c3a", "tipo": "portada", "num": 3,
         "texto": "Capítulo tres. Leonida y Vice City.",
         "fuente": ""},
        {"id": "c3b", "tipo": "mapa", "fase": 1,
         "texto": "GTA seis transcurre en Leonida, un estado ficticio inspirado en Florida. Y su gran ciudad es Vice City, la versión satírica de Miami, que vuelve a la saga más de veinte años después de GTA Vice City.",
         "fuente": "Rockstar Games",
         "items": [{"t": "LEONIDA", "en": "Leonida"}, {"t": "VICE CITY", "en": "Vice"}]},
        {"id": "c3c", "tipo": "mapa", "fase": 2,
         "texto": "Pero hay mucho más que la ciudad. Rockstar ha enseñado los Cayos de Leonida, inspirados en los Cayos de Florida. Grassrivers, unos pantanos que recuerdan a los Everglades. Port Gellhorn. Ambrosia. Y el parque nacional del monte Kalaga.",
         "fuente": "Rockstar Games (web oficial de GTA VI)",
         "items": [{"t": "CAYOS DE LEONIDA", "en": "Cayos"}, {"t": "GRASSRIVERS", "en": "Grassrivers"},
                   {"t": "PORT GELLHORN", "en": "Gellhorn"}, {"t": "AMBROSIA", "en": "Ambrosia"}, {"t": "MONTE KALAGA", "en": "Kalaga"}]},
        {"id": "c3d", "tipo": "tarjetas", "dib": "regla",
         "texto": "¿Y cuánto mide el mapa? Rockstar no ha dado ninguna cifra oficial. Las comparaciones que circulan, por ejemplo que es varias veces más grande que el de Red Dead Redemption dos, salen de filtraciones y de análisis de los tráileres. Tómalas con pinzas.",
         "fuente": "Sin cifra oficial de Rockstar · estimaciones de fans y filtraciones",
         "items": [{"t": "TAMAÑO OFICIAL: ?", "en": "oficial", "k": "g"},
                   {"t": "«Varias veces Red Dead 2»", "en": "varias", "k": "r"}]},
        {"id": "c3e", "tipo": "tarjetas", "dib": "movil",
         "texto": "Lo que sí está claro es el tono: una sátira de la América de hoy, con redes sociales, influencers, y mucho Florida Man.",
         "fuente": "Rockstar Games · tráileres oficiales",
         "items": [{"t": "REDES SOCIALES", "en": "redes"}, {"t": "INFLUENCERS", "en": "influencers"}, {"t": "FLORIDA MAN", "en": "Florida", "k": "g"}]},
        {"id": "c3f", "tipo": "tarjetas", "dib": "cartel",
         "texto": "Y la promoción ha saltado a la vida real. En Miami, Rockstar colocó un cartel gigante de Welcome to Vice City en el tejado del Kaseya Center, el pabellón de los Miami Heat. Según la prensa, el acuerdo con el condado ronda los novecientos setenta y cinco mil dólares.",
         "fuente": "Notebookcheck · Beebom · GamesRadar (sep. 2026)",
         "items": [{"t": "KASEYA CENTER · MIAMI", "en": "Kaseya"}, {"t": "≈ 975.000 $", "en": "novecientos", "k": "g"}]},
    ]},
    {"id": "c4", "titulo": "LUCÍA Y JASON", "escenas": [
        {"id": "c4a", "tipo": "portada", "num": 4,
         "texto": "Capítulo cuatro. Lucía y Jason.",
         "fuente": ""},
        {"id": "c4b", "tipo": "tarjetas", "dib": "pareja",
         "texto": "Por primera vez, la saga principal tiene una pareja protagonista: Lucía Caminos y Jason Duval.",
         "fuente": "Rockstar Games",
         "items": [{"t": "LUCÍA CAMINOS", "en": "Lucía"}, {"t": "JASON DUVAL", "en": "Jason"}]},
        {"id": "c4c", "tipo": "tarjetas", "dib": "lucia",
         "texto": "Lucía es la primera protagonista femenina de la saga principal. Su padre le enseñó a pelear en cuanto aprendió a andar. Luchar por su familia la llevó a la penitenciaría de Leonida. Y ahora, dice, solo hará movimientos inteligentes.",
         "fuente": "Rockstar Games (descripción oficial del personaje)",
         "items": [{"t": "1.ª PROTAGONISTA FEMENINA", "en": "femenina", "k": "g"},
                   {"t": "Penitenciaría de Leonida", "en": "penitenciaría"},
                   {"t": "«Solo movimientos inteligentes»", "en": "inteligentes"}]},
        {"id": "c4d", "tipo": "tarjetas", "dib": "jason",
         "texto": "Jason creció rodeado de timadores y delincuentes. Intentó dejar atrás esa vida en el ejército, pero acabó en los Cayos, haciendo lo que mejor sabe: trabajar para traficantes de la zona.",
         "fuente": "Rockstar Games (descripción oficial del personaje)",
         "items": [{"t": "Creció entre timadores", "en": "timadores"}, {"t": "Exmilitar", "en": "ejército"},
                   {"t": "Los Cayos", "en": "Cayos"}]},
        {"id": "c4e", "tipo": "tarjetas", "dib": "pareja",
         "texto": "Cuando un golpe fácil sale mal, los dos acaban en el lado más oscuro del lugar más soleado de Estados Unidos, en medio de una conspiración criminal que recorre todo Leonida. Y tendrán que apoyarse el uno en el otro. Muchos lo comparan con Bonnie y Clyde.",
         "fuente": "Rockstar Games · prensa",
         "items": [{"t": "UN GOLPE QUE SALE MAL", "en": "golpe", "k": "g"}, {"t": "Conspiración por todo Leonida", "en": "conspiración"},
                   {"t": "¿Bonnie y Clyde?", "en": "Bonnie"}]},
        {"id": "c4f", "tipo": "indice",
         "texto": "Rockstar también ha presentado a personajes secundarios como Cal Hampton, Boobie Ike, Dre'Quan Priest, Raul Bautista o Brian Heder.",
         "fuente": "Rockstar Games",
         "items": [{"t": "Cal Hampton", "en": "Cal"}, {"t": "Boobie Ike", "en": "Boobie"}, {"t": "Dre'Quan Priest", "en": "Priest"},
                   {"t": "Raul Bautista", "en": "Raul"}, {"t": "Brian Heder", "en": "Brian"}]},
    ]},
    {"id": "c5", "titulo": "TRÁILERES Y RÉCORDS", "escenas": [
        {"id": "c5a", "tipo": "portada", "num": 5,
         "texto": "Capítulo cinco. Los tráileres, y sus récords.",
         "fuente": ""},
        {"id": "c5b", "tipo": "cifra",
         "texto": "El primer tráiler salió el cuatro de diciembre de dos mil veintitrés, un día antes de lo previsto, porque se había filtrado. En veinticuatro horas sumó más de noventa millones de visualizaciones en YouTube. Récord Guinness.",
         "fuente": "Guinness World Records · Infobae · Variety (dic. 2023)",
         "items": [{"n": 90421491, "pie": "visualizaciones en 24 h en YouTube · 1.er tráiler · récord Guinness", "en": "noventa"}]},
        {"id": "c5c", "tipo": "cifra",
         "texto": "El segundo, en mayo de dos mil veinticinco, fue todavía más lejos: cuatrocientos setenta y cinco millones de visualizaciones en veinticuatro horas, sumando todas las plataformas, según Rockstar.",
         "fuente": "Rockstar Games (Claro Sports, mayo 2025)",
         "items": [{"n": 475000000, "pie": "visualizaciones en 24 h · 2.º tráiler · todas las plataformas, según Rockstar", "en": "cuatrocientos"}]},
        {"id": "c5d", "tipo": "barras",
         "texto": "Ese récord duró menos de un año. En marzo de dos mil veintiséis, el tráiler de Spider-Man Brand New Day lo superó, con más de setecientos dieciocho millones, según IGN.",
         "fuente": "HD Tecnología citando a IGN (20-3-2026) · cifras de cada estudio, no siempre comparables",
         "titulo": "VISUALIZACIONES EN 24 HORAS (MILLONES)",
         "items": [{"t": "GTA VI · 1.er tráiler (solo YouTube)", "n": 90, "en": "récord"}, {"t": "GTA VI · 2.º tráiler", "n": 475, "en": "récord"},
                   {"t": "Spider-Man: Brand New Day", "n": 718.6, "en": "setecientos", "k": "x"}]},
        {"id": "c5e", "tipo": "tarjetas", "dib": "tele",
         "texto": "En agosto llegó algo nunca visto en la saga: un avance de veintiséis minutos que se estrenó primero en Netflix. Según Take-Two, lo vieron treinta y un millones de espectadores en sus primeros cuatro días.",
         "fuente": "Netflix Tudum (27-8-2026) · Take-Two, 9-11-2026 (StockTitan)",
         "items": [{"t": "26 MINUTOS · PRIMERO EN NETFLIX", "en": "Netflix"}, {"t": "31 MILLONES en 4 días", "en": "treinta", "k": "g"}]},
        {"id": "c5f", "tipo": "tarjetas", "dib": "musica",
         "texto": "Y el quince de octubre, el tráiler de lanzamiento, con música de Justice, el dúo francés que firma la banda sonora original. En solo tres días superó todas las visualizaciones que el tráiler de lanzamiento de GTA cinco había sumado en trece años.",
         "fuente": "Gematsu (15-10-2026) · ixbt.games (20-10-2026)",
         "items": [{"t": "15 OCT · TRÁILER DE LANZAMIENTO", "en": "quince"}, {"t": "Música de JUSTICE", "en": "Justice"},
                   {"t": "3 DÍAS > 13 AÑOS de GTA V", "en": "tres", "k": "g"}]},
    ]},
    {"id": "c6", "titulo": "PRECIO Y EDICIONES", "escenas": [
        {"id": "c6a", "tipo": "portada", "num": 6,
         "texto": "Capítulo seis. Precio y ediciones.",
         "fuente": ""},
        {"id": "c6b", "tipo": "precios",
         "texto": "Las reservas abrieron el veinticinco de junio. La edición estándar cuesta setenta y nueve euros con noventa y nueve. Y la Ultimate, noventa y nueve con noventa y nueve.",
         "fuente": "Vandal · Xataka (25-6-2026) · precio oficial en España",
         "items": [{"t": "ESTÁNDAR", "p": "79,99 €", "en": "estándar"}, {"t": "ULTIMATE", "p": "99,99 €", "en": "Ultimate"}]},
        {"id": "c6c", "tipo": "tarjetas", "dib": "coche",
         "texto": "¿Qué trae la Ultimate? Vehículos, armas, ropa y otros extras repartidos a lo largo de la historia de Jason y Lucía, como un deportivo Grotti Cheetah de mil novecientos noventa y cinco, o un yate.",
         "fuente": "Rockstar Games (Vandal, 25-6-2026)",
         "items": [{"t": "Vehículos · armas · ropa", "en": "Vehículos"}, {"t": "Grotti Cheetah de 1995", "en": "Cheetah"},
                   {"t": "Un yate", "en": "yate", "k": "g"}]},
        {"id": "c6d", "tipo": "tarjetas", "dib": "regalo",
         "texto": "Y si reservas o compras antes del veinte de noviembre, te llevas el pack Vintage Vice City: un Vapid Stanier clásico de dos tonos, un garaje junto a Ocean Beach, y ropa y peinados para los dos. Además, las reservas digitales incluyen un mes de GTA plus.",
         "fuente": "Rockstar Games (Vandal) · Take-Two (StockTitan)",
         "items": [{"t": "ANTES DEL 20 NOV", "en": "veinte", "k": "g"}, {"t": "Pack Vintage Vice City", "en": "Vintage"},
                   {"t": "Digital: 1 mes de GTA+", "en": "plus"}]},
        {"id": "c6e", "tipo": "tarjetas", "dib": "caja",
         "texto": "Ojo con la edición física: no lleva disco. En la caja hay un código de descarga.",
         "fuente": "Rockstar Games (Vandal · VidaExtra)",
         "items": [{"t": "SIN DISCO", "en": "disco", "k": "x"}, {"t": "Código de descarga en la caja", "en": "código"}]},
        {"id": "c6f", "tipo": "tarjetas", "dib": "grafica",
         "texto": "¿Y cómo van las ventas? Take-Two no da cifras, pero dice que las reservas van muy por encima de sus expectativas iniciales, a niveles sin precedentes. Las cifras de millones de reservas que verás por internet son estimaciones de analistas, no datos oficiales.",
         "fuente": "Take-Two, 9-11-2026 (StockTitan) · estimaciones: Sensor Tower y otros",
         "items": [{"t": "«Muy por encima de nuestras expectativas»", "en": "expectativas"},
                   {"t": "«Niveles sin precedentes»", "en": "precedentes"},
                   {"t": "Cifras de reservas = ESTIMACIONES", "en": "estimaciones", "k": "r"}]},
    ]},
    {"id": "c7", "titulo": "DETALLES Y RUMORES", "escenas": [
        {"id": "c7a", "tipo": "portada", "num": 7,
         "texto": "Capítulo siete. Los detalles y las teorías que más se comentan. Y aquí, atención, porque voy a separar lo confirmado de lo que es solo rumor.",
         "fuente": ""},
        {"id": "c7b", "tipo": "tarjetas", "dib": "check",
         "texto": "Primero, lo confirmado. Rockstar lo describe como una experiencia para un jugador. Y la historia se divide en capítulos, como en Red Dead Redemption dos.",
         "fuente": "Rockstar Games (Vandal · StockTitan)",
         "items": [{"t": "CONFIRMADO", "en": "confirmado", "k": "ok"}, {"t": "Experiencia para un jugador", "en": "jugador"},
                   {"t": "Historia por capítulos", "en": "capítulos"}]},
        {"id": "c7c", "tipo": "tarjetas", "dib": "online",
         "texto": "Rumor número uno: el modo online. Ya en dos mil veinte, el periodista Jason Schreier informó de que Rockstar preparaba un gran componente online. Pero, a día de hoy, Rockstar no ha anunciado ningún modo multijugador.",
         "fuente": "Jason Schreier (2020) · Rockstar no ha anunciado online",
         "items": [{"t": "RUMOR 1 · MODO ONLINE", "en": "online", "k": "r"}, {"t": "Schreier, 2020: «gran componente online»", "en": "Schreier"},
                   {"t": "Rockstar: sin anunciar", "en": "multijugador", "k": "x"}]},
        {"id": "c7d", "tipo": "tarjetas", "dib": "fps",
         "texto": "Rumor dos: los treinta fotogramas por segundo. Un youtuber invitado a Rockstar North contó que, en desarrollo, el juego funciona a treinta fotogramas en consola. No hay ficha técnica oficial, y no se sabe si habrá un modo a sesenta.",
         "fuente": "VGC · GamesRadar (ago. 2026) · sin ficha técnica oficial",
         "items": [{"t": "RUMOR 2 · 30 FPS", "en": "fotogramas", "k": "r"}, {"t": "Dicho a un youtuber en Rockstar North", "en": "youtuber"},
                   {"t": "¿Modo a 60? Sin confirmar", "en": "sesenta"}]},
        {"id": "c7e", "tipo": "tarjetas", "dib": "pc",
         "texto": "Rumor tres: la fecha de PC. Fuentes del sector hablan de dos mil veintisiete, pero Rockstar no ha dicho nada.",
         "fuente": "Fuentes del sector (Infobae · Vandal) · sin confirmar",
         "items": [{"t": "RUMOR 3 · PC EN 2027", "en": "PC", "k": "r"}, {"t": "Rockstar: sin fecha", "en": "nada", "k": "x"}]},
        {"id": "c7f", "tipo": "tarjetas", "dib": "lupa",
         "texto": "Y cuidado con las filtraciones. En agosto, una cuenta llamada CyberLeek difundió supuestas imágenes del mapa y del juego, y Take-Two pidió a la justicia que Discord y Microsoft revelaran quién está detrás. Si ves un vídeo filtrado, desconfía: puede ser real, antiguo, o directamente falso.",
         "fuente": "VGC · Push Square (ago. 2026)",
         "items": [{"t": "CYBERLEEK", "en": "CyberLeek", "k": "r"}, {"t": "Take-Two: citaciones a Discord y Microsoft", "en": "Discord"},
                   {"t": "¿Real, antiguo o falso?", "en": "falso", "k": "g"}]},
    ]},
    {"id": "c8", "titulo": "EL DÍA DEL LANZAMIENTO", "escenas": [
        {"id": "c8a", "tipo": "portada", "num": 8,
         "texto": "Capítulo ocho. Qué esperar el día del lanzamiento.",
         "fuente": ""},
        {"id": "c8b", "tipo": "tarjetas", "dib": "descarga",
         "texto": "La precarga está abierta desde el diez de noviembre en PlayStation cinco y en Xbox. Y la versión física llega a las tiendas el doce: metes el código, y a descargar.",
         "fuente": "Rockstar Games (VidaExtra, 10-11-2026)",
         "items": [{"t": "PRECARGA DESDE EL 10 NOV", "en": "diez", "k": "g"}, {"t": "Física en tiendas: 12 NOV", "en": "doce"}]},
        {"id": "c8c", "tipo": "cifra",
         "texto": "Ve haciendo hueco: la descarga ronda los doscientos doce gigas. Si tu consola va justa, borra algo antes del diecinueve.",
         "fuente": "VidaExtra · El Diario de Madrid (10-11-2026)",
         "items": [{"n": 212, "suf": " GB", "pie": "tamaño de la descarga", "en": "doscientos"}]},
        {"id": "c8d", "tipo": "tarjetas", "dib": "reloj",
         "texto": "En España se podrá jugar desde la medianoche del diecinueve de noviembre, cuando se desbloquee en las tiendas de PlayStation y de Microsoft.",
         "fuente": "HardZone · SomosXbox",
         "items": [{"t": "00:00 · 19 NOV", "en": "medianoche", "k": "g"}, {"t": "Hora local", "en": "desbloquee"}]},
        {"id": "c8e", "tipo": "tarjetas", "dib": "poster",
         "texto": "Ese mismo día, Rockstar regalará un póster y un mapa de Leonida en descarga digital. Y mi consejo: precarga ya, para no depender de la descarga el mismo día.",
         "fuente": "Rockstar Games (VidaExtra, 10-11-2026)",
         "items": [{"t": "Póster + mapa de Leonida gratis", "en": "póster"}, {"t": "CONSEJO: PRECARGA YA", "en": "consejo", "k": "ok"}]},
    ]},
    {"id": "cierre", "titulo": "¿Y TÚ?", "escenas": [
        {"id": "f1", "tipo": "tarjetas", "dib": "pareja",
         "texto": "Trece años después, Vice City vuelve. Y ahora te toca a ti: ¿con quién vas a empezar, con Lucía o con Jason? ¿Y crees que estará a la altura del hype? Te leo en comentarios.",
         "fuente": "",
         "items": [{"t": "¿LUCÍA O JASON?", "en": "Jason", "k": "g"}, {"t": "¿Estará a la altura del hype?", "en": "hype"},
                   {"t": "TE LEO EN COMENTARIOS", "en": "comentarios", "k": "ok"}]},
        {"id": "f2", "tipo": "suscribir",
         "texto": "Si el vídeo te ha servido, dale a me gusta y suscríbete, que aquí vamos a seguir hablando de GTA seis. Nos vemos en Vice City.",
         "fuente": "",
         "items": [{"t": "ME GUSTA", "en": "gusta"}, {"t": "SUSCRÍBETE", "en": "suscríbete"}]},
    ]},
]

SEGMENTOS = [dict(e, escena=e["id"], cap=c["id"]) for c in CAPITULOS for e in c["escenas"]]
