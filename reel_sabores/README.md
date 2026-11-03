# Reel: «Cómo distinguimos los sabores» (serie «Mitos y verdades del cuerpo»)

Vídeo vertical 1080×1920, 68,8 s, con el formato analizado en `../formato_mitos_cuerpo/README.md` (reel de
@sovera.ia): ilustración pintada (degradados, grano, desenfoque de fondo, viñeta), transiciones encadenadas sin
cortes (la escena anterior se acerca y se funde) y subtítulos pequeños arriba a la izquierda (palabras dichas en
blanco, futuras tenues, palabras clave recuadradas).

| # | Escena | Qué cuenta |
|---|---|---|
| 0 | gancho | Nariz tapada y ojos cerrados: manzana vs. cebolla cruda, «te va a costar muchísimo saber cuál es cuál» |
| 1 | cinco | La lengua sola distingue 5 sabores |
| 2 | lista | Dulce, salado, ácido, amargo y umami (iconos que aparecen sobre la lengua) |
| 3 | botones | Miles de botones gustativos en los bultitos de la lengua; se renuevan sin parar |
| 4 | mito | Mapa de la lengua → «MITO» · 1901 · toda la lengua nota los cinco |
| 5 | nariz | Corte de la cabeza: los aromas suben por detrás de la boca a la nariz (vía retronasal) |
| 6 | cerebro | Lengua + olfato + textura + temperatura + color → «SABOR» |
| 7 | resfriado | Nariz bloqueada: los aromas no llegan, la comida no sabe a nada |
| 8 | picante | La guindilla activa el receptor del calor (TRPV1): «DOLOR, NO SABOR» |
| 9 | cierre | «Dale las gracias a tu nariz» |
| 10 | cta | «Envíaselo a alguien que todavía no lo sabía»; el último segundo vuelve al gancho (bucle) |

Datos: mito del mapa de la lengua (Hänig 1901, mal interpretado por Boring en 1942; Collings 1974 mostró que toda
la lengua nota todos los sabores, con pequeñas diferencias de sensibilidad), olfato retronasal, prueba de la manzana
y la cebolla (cuesta mucho distinguirlas sin olfato ni vista; no siempre es imposible), picante = TRPV1.

```bash
pip install edge-tts certifi numpy pillow
python3 voz.py && python3 video.py          # -> sabores_reel.mp4  (~5 min con 4 núcleos; grano suave y tasa máx. 8 Mb/s para que pese ~70 MB)
```

**Texto para publicar** (con cebo de comentarios, como el reel de referencia):
«Te enseñaron que la punta de la lengua nota lo dulce y el fondo lo amargo… 👅 Mitos y verdades del cuerpo, un vídeo
al día. ¿Qué quieres que revise mañana?»
`#curiosidades #ciencia #cuerpohumano #sabiasque #mitos`
