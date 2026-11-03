# TikTok: «Imagínate que te atragantas y estás solo en casa»

Vídeo vertical 1080×1920 hecho con el motor común `../motor_plano/` (estilo de «Si te siguen de noche»: personajes
planos, gancho desde el fotograma 0, subtítulos palabra a palabra, «dale like» a mitad y cierre guárdalo / mándaselo /
sígueme). Información general, no sustituye a profesionales.

**Gancho: manos al cuello, latidos, pulso rojo y sello «NO PUEDES RESPIRAR» desde el fotograma 0.**

Contenido:
- Si puedes toser, tose con fuerza
- Si no puedes toser ni hablar: llama al 112 y deja la llamada abierta
- Compresiones a ti mismo: puño encima del ombligo, otra mano encima, hacia dentro y arriba
- Sin fuerza: déjate caer sobre el respaldo de una silla o el borde de la encimera
- Si hay alguien: manos al cuello (señal universal de atragantamiento)
- Aunque lo expulses, ve al médico

```bash
pip install edge-tts certifi numpy pillow
python3 voz.py && python3 video.py          # -> atragantarse_tiktok.mp4
python3 video.py --preview 0 5 12           # fotogramas sueltos en build/
```

**Texto para publicar:** Esto le puede salvar la vida a alguien que vive solo 🙏 Mándaselo 👇
`#primerosauxilios #atragantamiento #salud #consejos #sabiasque`
