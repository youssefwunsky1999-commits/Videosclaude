# MENTE404 — «¿Cómo funciona realmente el dinero?»

Vídeo vertical 1080×1920 a 30 fps (~85 s), hecho con **Remotion** (React), voz en off
`es-ES-AlvaroNeural` (edge-tts), subtítulos sincronizados por palabra y música y efectos
sintetizados (sin descargas).

Escenas (una por frase del guion, sincronizadas con las palabras clave):

1. Gancho: moneda de euro girando → «¿SABES CÓMO FUNCIONA?»
2. «Abre los ojos»: un ojo dorado que se abre
3. Una pila de lingotes que se vacía → sello «SIN ORO DETRÁS»
4. 1971: el contador de años avanza y la cadena dólar ⇄ oro se rompe justo al decir «1971»
5. Los pilares (confianza, instituciones, economía) sostienen el «sistema monetario»
6. «Pero aquí viene lo interesante…» (glitch + subida)
7. Banco → préstamo → depósito nuevo (+10.000 €)
8. Barras: dinero ↑, producción ≈, precios ↑
9. ¿Quién lo nota primero? Un foco que no se para en el que más tiene
10. Ahorros: mismos 1.000 €, la cesta de la compra se encoge
11. Activos: empresas, inmuebles, acciones
12. Expediente «confidencial»: la otra realidad
13. «No necesitas ser millonario… pero sí necesitas entenderlo»
14. Unos trabajan por dinero / otros estudian el dinero
15. ¿Cuánto ganas? → ¿Cuánto **entiendes**?
16. Cierre: MENTE404 · Despierta. Cuestiona. Comprende.

## Cómo regenerarlo

```bash
npm install
pip install edge-tts certifi
python3 scripts/voz.py          # voz -> public/voz/*.wav + src/voz.json (tiempos por palabra)
node scripts/gen-audio.mjs      # música + efectos -> public/sfx/
npx remotion render src/index.ts Mente404Dinero out/video.mp4 --codec h264 --crf 17
node scripts/stills.mjs 30 470 900   # fotogramas sueltos en out/ para revisar
```

- El texto de la voz está en `scripts/guion.py`. Si lo cambias, vuelve a ejecutar `voz.py`: la
  duración de cada escena y la sincronización con las palabras se recalculan solas (`src/timeline.ts`).
- Colores, tipografías y curvas de animación: `src/theme.ts`.
- `npx remotion studio` abre el editor visual para previsualizar.
