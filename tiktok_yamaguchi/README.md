# TikTok: «Sobrevivió a dos bombas atómicas» (Tsutomu Yamaguchi, 1945)

Vídeo vertical 1080x1920 (~90 s) optimizado para retención y crecimiento:

- **Gancho en el fotograma 0**: sin fundido; texto grande «SOBREVIVIÓ A 2 BOMBAS ATÓMICAS», voz desde 0,05 s
  y golpe de taiko + impacto grave al instante. Sello «100% REAL» para credibilidad.
- **Cabecera fija** con el tema durante todo el vídeo (para quien entra a mitad).
- **«Zoom punch»** automático en cada palabra clave y un cambio visual/sonoro cada pocos segundos.
- **Like a mitad de vídeo con bucle abierto**: «Si no conocías esta historia, dale like. Porque lo que pasó
  después parece imposible».
- **Llamada a seguir con promesa de valor** al final: «cada día te cuento una historia real que parece inventada».

Estética de cartel japonés (papel, tinta y rojo), música de koto (Karplus-Strong) y taiko sintetizada, silencio
tenso + pitido + estallido en cada bomba, tren, «pop» del like; voz con pausas y procesado de estudio.

```bash
python3 voz.py && python3 video.py          # -> yamaguchi_tiktok.mp4
python3 video.py --preview 0 38 64          # fotogramas sueltos en build/
```
