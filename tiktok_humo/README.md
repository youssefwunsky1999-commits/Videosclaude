# TikTok: «¿Sabías que en un incendio mata más el humo que el fuego?»

Vídeo vertical 1080×1920 hecho con el motor común `../motor_plano/` (estilo de «Si te siguen de noche»: personajes
planos, gancho desde el fotograma 0, subtítulos palabra a palabra, «dale like» a mitad y cierre guárdalo / mándaselo /
sígueme). Información general, no sustituye a profesionales.

**Gancho: salón con fuego, humo que baja del techo, persona tosiendo y sello «MATA MÁS EL HUMO».**

Contenido:
- La mayoría de víctimas mueren por inhalar humo: caliente, tóxico y sube
- Agáchate o ve a gatas: cerca del suelo el aire es más limpio
- Toca puerta y pomo con el dorso de la mano: si quema, no abras
- Cierra puertas detrás de ti y no uses el ascensor
- Si no puedes salir: enciérrate, toallas mojadas en las rendijas, ventana y 112
- Detector de humo: cuesta pocos euros

```bash
pip install edge-tts certifi numpy pillow
python3 voz.py && python3 video.py          # -> humo_tiktok.mp4
python3 video.py --preview 0 5 12           # fotogramas sueltos en build/
```

**Texto para publicar:** ¿Tienes detector de humo en casa? 🔥 Mándaselo a tu familia 👇
`#incendio #seguridad #sabiasque #consejos #bomberos`
