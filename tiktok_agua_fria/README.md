# TikTok: «Si caes al agua fría, NO nades»

Vídeo vertical 1080×1920 hecho con el motor común `../motor_plano/` (estilo de «Si te siguen de noche»: personajes
planos, gancho desde el fotograma 0, subtítulos palabra a palabra, «dale like» a mitad y cierre guárdalo / mándaselo /
sígueme). Información general, no sustituye a profesionales.

**Gancho: caída al agua con salpicadura, pulso rojo y sello «NO NADES» desde el fotograma 0.**

Contenido:
- El choque por frío: jadeo sin control, corazón disparado, pánico
- Pasa en más o menos un minuto: aguanta ese minuto
- Flota boca arriba, cabeza atrás, brazos y piernas abiertos como una estrella; respira despacio
- Después: pide ayuda o nada hacia algo a lo que agarrarte
- Si ves a alguien caer: no te tires, llama al 112 y lánzale algo que flote
- No hace falta que sea invierno: por debajo de 15 °C el agua ya puede provocar el choque

```bash
pip install edge-tts certifi numpy pillow
python3 voz.py && python3 video.py          # -> agua_fria_tiktok.mp4
python3 video.py --preview 0 5 12           # fotogramas sueltos en build/
```

**Texto para publicar:** Aunque sepas nadar 🌊 Mándaselo a quien va a la playa o al río 👇
`#agua #seguridad #flotar #sabiasque #consejos`
