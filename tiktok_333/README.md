# TikTok de terror: «El mensaje de las 3:33» (ficción original)

Vídeo vertical 1080x1920 (~90 s). Lucía vive sola; a las 3:33 recibe un mensaje de su propio número
(«No abras la puerta. No soy yo»), llaman tres veces, una voz idéntica a la suya susurra tras la puerta, el
móvil vibra con una foto en visión nocturna de ella durmiendo… con algo de pie a su lado, y el último mensaje:
«Ahora… mira detrás de ti». Susto final con glitch, «Comenta 333» y gancho a la parte 2.

- Dos voces: narrador grave y susurro femenino procesado (filtro, eco y trémolo), en `voz.py` por segmento.
- Diseño sonoro: dron disonante, caja de música desafinada, reloj, notificaciones, golpes de puerta, vibración,
  latidos que se aceleran, estática, silencio total antes del susto y acorde disonante con impacto.
- Efectos visuales: zoom lento hacia la puerta, sombras de pies bajo la puerta, visión nocturna, grano y glitch RGB.

```bash
python3 voz.py && python3 video.py          # -> 333_tiktok.mp4
python3 video.py --preview 0 30 66 78       # fotogramas sueltos en build/
```
