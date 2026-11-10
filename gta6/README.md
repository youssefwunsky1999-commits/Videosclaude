# «GTA VI sale en menos de 10 días» + sorteo (TikTok)

Vídeo vertical 1080x1920 (~51 s) de hype con datos reales y anuncio de sorteo. Estética original de neón retro
(atardecer, palmeras, carretera de rejilla); **no** usa el logo, la tipografía ni imágenes de Rockstar Games.

Datos y fuentes: en `guion.py`. Sorteo: si el vídeo llega a 10.000 likes, 1 copia de GTA VI (PS5 o Xbox a elegir)
entre quienes den like y comenten «GTA6»; ganador el 19-11-2026. Es un sorteo del autor de la cuenta, no de Rockstar.

```bash
python3 voz.py && python3 audio.py && python3 construir.py
cd hf && npx hyperframes@0.9.26 render -o ../gta6.mp4 -q delivery
```
