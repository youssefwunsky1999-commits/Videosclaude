# TikTok de misterio: los Andes, 1972 (La sociedad de la nieve)

Vídeo vertical 1080x1920 (~90 s) sobre el vuelo 571 de la Fuerza Aérea Uruguaya: radar que pierde la
señal, choque contra la cumbre y deslizamiento del fuselaje, frío a 3.600 m y −30 °C, la radio que anuncia
el fin de la búsqueda, la decisión más difícil, la avalancha, la travesía de Parrado y Canessa, la nota al
arriero y el rescate de los 16 supervivientes.

Novedades respecto a los vídeos anteriores:
- Voz generada frase a frase con pausas dramáticas (`voz.py`) y procesada en la mezcla (EQ con graves,
  compresión y reverberación sutil).
- Diseño sonoro: viento de montaña con silbido, motor turbohélice, metal e impacto, estática de radio,
  latidos, avalancha, pasos en la nieve, río, helicópteros e impactos graves de tráiler; música de cuerdas en
  menor que pasa a mayor con el rescate.
- Franjas de cine, tono frío, nieve con viento y temblor de cámara.

```bash
python3 voz.py && python3 video.py          # -> andes_tiktok.mp4
python3 video.py --preview 17 52 70         # fotogramas sueltos en build/
```
