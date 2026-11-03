# Motor común de los TikToks de estilo plano

`motor.py` es el motor de «Si te siguen de noche» generalizado: personajes planos, cámara con zoom en las palabras
clave, subtítulos palabra a palabra, insignia de paso, rótulos genéricos (titular, sello, chip ✓, regla ✓/✗, número,
fuente, like, final) y mezcla de voz + música + efectos.

Cada vídeo es una carpeta con:
- `guion.py`: texto por escenas y ajustes (`SALIDA`, `CABECERA`, `EXTRA`, `CLAVE`, `FUSIONES`, `MUSICA_LUZ`, `AMBIENTE`).
- `escenas.py`: funciones de cada escena (`FUNCS`) y `efectos(fx, E)` para el sonido.
- `voz.py` y `video.py`: copias de `motor_plano/voz.py` y `motor_plano/motor.py`.

```bash
python3 voz.py && python3 video.py
```

Vídeos hechos con él: `tiktok_ascensor`, `tiktok_atragantarse`, `tiktok_humo`, `tiktok_agua_fria`,
`tiktok_movil_robado`, `tiktok_112`.
