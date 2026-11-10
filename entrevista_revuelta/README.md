# «Broncano vs Abascal en La Revuelta»: resumen en 5 momentos (TikTok)

Vídeo vertical 1080x1920 (~61 s) que resume la entrevista de David Broncano a Santiago Abascal en *La Revuelta*
(RTVE, 9-11-2026), a menos de tres semanas de las generales del 29N.

- **Gancho:** «BRONCANO VS ABASCAL» en el fotograma 0, y la frase con la que acabó todo («Me sale el punto cómico que tú has perdido»).
- **5 momentos:** el regalo de la bandera de Ceuta, vivienda, Israel y Gaza (el más tenso), tres frases rápidas (violencia de género, clima y franquismo) y la despedida.
- **Cierre:** «¿Quién ganó?», pidiendo opiniones en comentarios.

**Rigor:** todas las citas son textuales y salen de Infobae, Europa Press (en Diario de Pontevedra) y Última Hora,
del 9 y 10 de noviembre de 2026. Las fuentes aparecen en pantalla y están en `guion.py`. Es un resumen neutral: no
da ganador. No hay imágenes ni voces de las personas reales; la voz es sintética y lo narra en tercera persona.

```bash
pip install edge-tts numpy
python3 voz.py && python3 audio.py && python3 construir.py
cd hf && npx hyperframes@0.9.26 render -o ../broncano_abascal.mp4 -q delivery
```

Para cambiar el texto o las tarjetas, se edita `guion.py`: cada tarjeta lleva la palabra de la voz con la que aparece.
Usa los fondos de Paper Shaders y el puente `hf-paper.js` de `herramientas_video/`.
