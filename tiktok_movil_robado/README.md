# TikTok: «Imagínate que te roban el móvil: los primeros 10 minutos»

Vídeo vertical 1080×1920 hecho con el motor común `../motor_plano/` (estilo de «Si te siguen de noche»: personajes
planos, gancho desde el fotograma 0, subtítulos palabra a palabra, «dale like» a mitad y cierre guárdalo / mándaselo /
sígueme). Información general, no sustituye a profesionales.

**Gancho: tirón en la calle de noche, el ladrón huye con el móvil y sello «LOS PRIMEROS 10 MIN».**

Contenido:
- Qué hay en juego: correo, banco y SMS con códigos
- 1. Desde otro dispositivo: Buscar (iPhone) / Encontrar mi dispositivo (Android): marcar como perdido y bloquear
- 2. Llama a tu compañía: bloqueo de la SIM (nadie recibe tus SMS del banco)
- 3. Cambia la contraseña del correo y avisa al banco
- 4. Denuncia con el IMEI: la operadora puede bloquear el móvil
- Truco: marca *#06# y apunta tu IMEI hoy

```bash
pip install edge-tts certifi numpy pillow
python3 voz.py && python3 video.py          # -> movil_robado_tiktok.mp4
python3 video.py --preview 0 5 12           # fotogramas sueltos en build/
```

**Texto para publicar:** Marca *#06# ahora y guárdalo 📱 Mándaselo a quien siempre pierde el móvil 👇
`#movil #robo #consejos #seguridad #trucos`
