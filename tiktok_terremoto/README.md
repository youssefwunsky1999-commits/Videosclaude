# TikTok: «Si te pilla un terremoto…»

Vídeo vertical 1080x1920 (~60 s): salón en corte que tiembla (lámpara que se balancea, cuadro y libros
que caen, grietas, polvo), sismógrafo en pantalla, fachada con cristales y cornisas cayendo, mesa, cama y
escaleras; voz neuronal, subtítulos palabra a palabra, música de tensión y retumbar sincronizado con el temblor.

Contenido basado en las recomendaciones de USGS, FEMA y Cruz Roja: el marco de la puerta es un mito en
casas modernas, no salir corriendo durante el temblor, y «Agáchate, Cúbrete, Agárrate» (Drop, Cover, Hold On).

```bash
python3 voz.py && python3 video.py          # -> terremoto_tiktok.mp4
python3 video.py --preview 4 27 33          # fotogramas sueltos en build/
```
