# TikTok: «Imagínate que te quedas encerrado en un ascensor»

Vídeo vertical 1080×1920 hecho con el motor común `../motor_plano/` (estilo de «Si te siguen de noche»: personajes
planos, gancho desde el fotograma 0, subtítulos palabra a palabra, «dale like» a mitad y cierre guárdalo / mándaselo /
sígueme). Información general, no sustituye a profesionales.

**Gancho: luz que parpadea, pulso rojo y sello «¿SE VA A CAER?» desde el fotograma 0.**

Contenido:
- No se cae: varios cables de acero (cada uno podría sostenerlo solo) y freno de emergencia que lo clava a las guías
- Hay aire: los ascensores no son herméticos
- Pulsa el botón de alarma (campana) unos segundos: te conecta con alguien que vendrá
- No salgas solo ni fuerces las puertas: entre dos plantas podrías caer al hueco
- Si nadie responde, llama al 112 y di la dirección del edificio

```bash
pip install edge-tts certifi numpy pillow
python3 voz.py && python3 video.py          # -> ascensor_tiktok.mp4
python3 video.py --preview 0 5 12           # fotogramas sueltos en build/
```

**Texto para publicar:** ¿Te ha pasado alguna vez? 😰 Guárdalo por si acaso 👇
`#ascensor #consejos #seguridad #sabiasque #curiosidades`
