# Valdemora · Ep. 01 «Las 3:17» — vídeo

Producción del episodio descrito en `../ep01_las_317.md` (ficción original), en vertical 1080x1920 (~90 s).

- **Voces:** narrador (Álvaro, grave), abuela Remedios (Elvira), y el doble con la misma voz que Leo, lenta y
  susurrada con eco. Cada frase se genera por separado para tener pausas dramáticas (`voz.py`).
- **Imagen:** personajes de bloques 3D según las fichas (sudadera mostaza, zapatillas de suela roja, moño y gafas
  de la abuela…), cámara por escena (grúa, travelling, cámara en mano, zoom), niebla volumétrica animada,
  desenfoque de fondo en primeros planos, ojo de pez en la mirilla, foto sepia de 1979 con grano, gradación de
  color por escena, grano de película y franjas de cine. Subtítulos con color por personaje.
- **Sonido:** campanas a las 3:17, luces que se apagan, péndulo, murmullo del aula que se corta, reloj digital,
  golpes, latidos, zumbido de farola, papel, golpes sordos dentro del armario tras 1,2 s de silencio absoluto,
  bisagra y el tema de caja de música de Valdemora.

```bash
python3 voz.py && python3 video.py          # -> valdemora_ep01_317.mp4
python3 video.py --preview 0.2 46 60 87     # fotogramas sueltos en build/
```
