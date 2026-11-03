# TikTok: «¿Por qué te pierdes en IKEA?» (Trucos de las tiendas · 1)

Vídeo vertical 1080×1920, ~56 s. Formato «historia con giro» (ver `../formato_giro_final/README.md`): la tienda es
el «culpable» que tiene un plan, y cada truco se cuenta como un paso del plan.

**Gancho desde el fotograma 0:** plano cenital del laberinto con el protagonista perdido (signos «?»), titular
«¿POR QUÉ TE PIERDES EN IKEA?» y, antes del segundo 4, el sello «ESTÁ HECHO A PROPÓSITO».

| # | Escena | Truco |
|---|---|---|
| 0 | gancho | El laberinto: no es culpa tuya |
| 1 | bolsa | Bolsa amarilla enorme para venir a por una lámpara |
| 2 | camino | Un único camino con flechas que pasa por todo; atajos casi invisibles |
| 3 | salones | Salones montados: te imaginas viviendo ahí |
| 4 | restaurante | Comes, recuperas energía (barra 15 % → 100 %) y sigues |
| 5 | mercado | Cosas pequeñas y baratas que caen en la bolsa; el ticket sube |
| 6 | dato | ~60 % de lo que se compra no estaba en la lista (Prof. Alan Penn, UCL) |
| 7 | montaje | Lo montas tú y lo valoras más: «efecto IKEA» (Norton, Mochon y Ariely, 2011) |
| 8 | final | Sale con media tienda y contento → «+ SEGUIR» + avance «Los trucos del súper»; el último segundo vuelve al laberinto (bucle) |

Ilustración propia y genérica: no se usa el logotipo ni la tipografía de la marca, solo se la nombra.

```bash
pip install edge-tts certifi numpy pillow
python3 voz.py && python3 video.py          # -> ikea_tiktok.mp4
python3 video.py --preview 1 12 30          # fotogramas sueltos en build/
```

**Descripción sugerida para publicar:**
«Entraste a por una lámpara… 🛋️ ¿Cuánto te gastaste tú la última vez? 👇 #ikea #curiosidades #psicologia #trucos»
