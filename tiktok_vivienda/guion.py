"""Guion del TikTok: el problema de la vivienda en España, el suelo, los impuestos y el 29N.

Fuentes de los datos (consultadas en noviembre de 2026):
- Déficit de ~750.000 viviendas; 240.000 hogares creados y ~92.000 viviendas terminadas en 2025:
  Banco de España, Informe Anual 2025 (junio de 2026).
- Alquiler medio de 1.176 € = 98,7 % del salario medio joven (1.191 €): Observatorio de Emancipación (CJE), 2025.
- Subida del alquiler en 2025 ≈ 8,5 %: idealista.
- ~15 años de media para pasar de suelo urbanizable a construir: Colliers y APCEspaña, «Necesidad de suelo 2024».
- Reforma de la Ley del Suelo: retirada en mayo de 2024 y rechazada en el Congreso en febrero de 2025.
- ITP entre el 6 % y el 10 % según la comunidad; IVA del 10 % en vivienda nueva.
- Recaudación por ITP y AJD +14,19 % (REAF, Panorama de la fiscalidad autonómica 2025).
- Elecciones generales: 29 de noviembre de 2026.
"""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+26%"
TONO = "-5Hz"
PAUSA = 0.2

SEGMENTOS = [
    {"escena": "gancho",
     "texto": "Un joven en España necesita el 98% de su sueldo para alquilar solo. ¿Por qué? ¿Y quién gana con que no se arregle?"},
    {"escena": "deficit",
     "texto": "Según el Banco de España, faltan 750.000 viviendas. En 2025 se crearon 240.000 hogares, y solo 92.000 casas."},
    {"escena": "precios",
     "texto": "Mucha gente, pocas casas: el alquiler sube un 8% en un año. Tu sueldo, no."},
    {"escena": "suelo",
     "texto": "¿Por qué no se construye? Falta suelo. Hacer un terreno edificable tarda unos 15 años, y un juez puede tumbar el plan entero por un defecto de forma."},
    {"escena": "ley",
     "texto": "La reforma para evitarlo ha fracasado dos veces en el Congreso."},
    {"escena": "like",
     "texto": "Si te parece una locura, dale like. Ahora viene lo que nadie cuenta."},
    {"escena": "impuestos",
     "texto": "Cuanto más cara la casa, más se recauda: hasta un 10% al comprar, el IBI cada año y el IRPF de cada alquiler."},
    {"escena": "recaudacion",
     "texto": "En 2025, los impuestos por comprar casas subieron más de un 14%. No decimos que sea a propósito, pero el incentivo para bajar precios… no está."},
    {"escena": "solucion",
     "texto": "La solución, según los expertos: más oferta. Liberar suelo, agilizar licencias y construir."},
    {"escena": "votar",
     "texto": "El 29 de noviembre hay elecciones. Mira qué propone cada partido sobre vivienda. Tu casa también se decide en las urnas."},
    {"escena": "final",
     "texto": "¿Cuánto pagas tú de alquiler? Te leo. Y sígueme para más."},
]
