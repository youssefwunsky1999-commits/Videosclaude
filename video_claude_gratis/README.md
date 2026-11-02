# Vídeo: «Soy Claude, y puedes usarme gratis»

Vídeo de ~77 s (1080p, 30 fps, audio estéreo) generado al 100 % con código: guion, voz neuronal, animaciones y música.

Estilo visual claro inspirado en la estética de Claude: fondo crema, color arcilla, tipografía serif (Source Serif 4, licencia OFL, en `fuentes/`), sombras suaves y transiciones con paneles de color.

- `guion.py` – texto de la narración y escena de cada frase.
- `voz.py` – sintetiza la voz (edge-tts, `es-ES-AlvaroNeural`) y guarda el tiempo de cada palabra.
- `video.py` – dibuja cada fotograma con Pillow (brillos, confeti, red neuronal, tokens, terminal…),
  sincroniza las animaciones y los subtítulos con las palabras, sintetiza la música con NumPy
  (pad Am–F–C–G, arpegio, bombo, efectos de *whoosh* e impacto) y monta todo con ffmpeg.

```bash
pip install edge-tts pillow numpy
python3 voz.py && python3 video.py      # -> claude_gratis.mp4
python3 video.py --preview 10 33 64     # fotogramas sueltos en build/
```
