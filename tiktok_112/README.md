# TikTok: «¿Sabías que el 112 sabe dónde estás?»

Vídeo vertical 1080×1920 hecho con el motor común `../motor_plano/` (estilo de «Si te siguen de noche»: personajes
planos, gancho desde el fotograma 0, subtítulos palabra a palabra, «dale like» a mitad y cierre guárdalo / mándaselo /
sígueme). Información general, no sustituye a profesionales.

**Gancho: mapa con chincheta que late, llamada al 112 en curso y sello «SABEN DÓNDE ESTÁS».**

Contenido:
- AML: al llamar, el móvil activa GPS y wifi y envía tu ubicación en un mensaje que no ves
- Antes: la antena (kilómetros); ahora, muchas veces, decenas de metros
- Funciona con la ubicación apagada, es gratis y no gasta datos
- Se puede llamar con el móvil bloqueado (botón de emergencia)
- Sin saldo y sin cobertura de tu compañía: usa otra red disponible
- Mismo número en toda la Unión Europea

```bash
pip install edge-tts certifi numpy pillow
python3 voz.py && python3 video.py          # -> 112_tiktok.mp4
python3 video.py --preview 0 5 12           # fotogramas sueltos en build/
```

**Texto para publicar:** No lo sabía casi nadie 📍 Mándaselo a tus padres 👇
`#112 #emergencias #sabiasque #curiosidades #movil`
