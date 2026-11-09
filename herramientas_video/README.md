# «4 herramientas gratis para hacer vídeos con código» — TikTok vertical

Vídeo 1080x1920 (~50 s) que presenta las cuatro herramientas de la imagen, **hecho con esas mismas herramientas**:

| # | Herramienta | Qué hace aquí |
|---|---|---|
| 1 | [HyperFrames](https://github.com/heygen-com/hyperframes) (HeyGen) | Todo el vídeo es HTML (`hf/`) y HyperFrames lo renderiza a MP4 fotograma a fotograma. |
| 2 | [Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar) | La escena 2 muestra sus 66 estilos con sus fotogramas reales (`hf/assets/lemo/`, CC BY 4.0, © LemoLab). |
| 3 | [Claude Animation Base](https://github.com/JohnHeibel/ClaudeAnimationBase) | Clawd pinta un arcoíris con p5.brush (`clawd/arcoiris.js`), renderizado con su motor. |
| 4 | [Paper Shaders](https://github.com/paper-design/shaders) | Todos los fondos: mesh gradient, grain gradient, paper texture, semitono (sobre un fotograma de Clawd) y metal líquido. |

Resultado: `herramientas_video.mp4`.

## Cómo se genera

```bash
pip install edge-tts numpy pillow
python3 voz.py          # 1. narración (edge-tts, es-ES-AlvaroNeural) + tiempo de cada palabra -> build/
python3 audio.py        # 2. coloca las frases, sintetiza música y efectos con NumPy -> build/mezcla.wav, build/tiempos.json
#                         3. Clawd (ver abajo) -> clawd/frames/
python3 construir.py    # 4. rellena las plantillas de escenas/ con los tiempos de la voz -> hf/
cd hf && npx hyperframes@0.9.26 render -o ../herramientas_video.mp4 -q delivery
```

- `escenas/*.html`: una escena por herramienta. Son plantillas: `{{w:palabra}}` es el segundo en que la voz dice esa palabra,
  así las animaciones caen justo con la narración aunque se cambie el guion.
- `hf/assets/lib/hf-paper.js`: puente entre Paper Shaders y HyperFrames. Monta cada shader parado y lo dibuja desde la
  línea de tiempo de la escena, de modo que el render es determinista. `paper-shaders.js` es el paquete
  `@paper-design/shaders@0.0.82` empaquetado con esbuild (Apache-2.0). El lint de HyperFrames avisa de que la librería
  usa `performance.now()`/`requestAnimationFrame`: con velocidad 0 no los usa para animar, el tiempo lo pone la escena.
- Subtítulos palabra a palabra generados desde `build/tiempos.json` (`hf/compositions/subtitulos.html`).

### Clawd (Claude Animation Base)

```bash
git clone https://github.com/JohnHeibel/ClaudeAnimationBase && cd ClaudeAnimationBase && npm install
cp ../clawd/arcoiris.js src/scenes/
# en studio.html: cambiar src/scenes/demo.js por src/scenes/arcoiris.js (y quitar la fuente de Google si no hay red)
# en src/config.js: duration: 7
NODE_PATH=$(npm root -g) node ../clawd/render_frames.cjs . ../clawd/frames 12 7     # 12 dibujos/s («a dos»), Playwright + SwiftShader
```

Sin GPU cada dibujo tarda ~15–40 s; con GPU, `node render.mjs --clip` del propio kit es mucho más rápido.
`construir.py` pasa los dibujos a 24 fps, recorta el cuadrado central y saca el fotograma del semitono.
