# Reel: «Tu tarjeta no tiene batería» (formato «Cómo funciona por dentro»)

Vídeo vertical 1080×1920, 74,7 s, pensado para Instagram Reels (en TikTok también funciona).
Formato analizado en `../formato_como_funciona/README.md`.

**Estilo:** macro oscuro con proyección 3D real (tarjeta y datáfono como objetos 3D con cámara en movimiento),
brillo tipo *bloom* para la energía (dorado) y el campo magnético (cian), rótulos técnicos finos y subtítulos
pequeños arriba con la palabra activa recuadrada.

| # | Escena | Qué se ve |
|---|---|---|
| 0 | paradoja | Tarjeta flotando; rótulos «BATERÍA ✗ / CABLES ✗ / BOTONES ✗»; «BIP · PAGO ACEPTADO» |
| 1 | pregunta | Batería al 0 %; partículas doradas: «ENERGÍA DEL DATÁFONO» |
| 2 | campo | Datáfono 3D emitiendo anillos de campo que suben y cambian de sentido; contador hasta 13.560.000 |
| 3 | antena | Tarjeta en rayos X: la antena de 5 vueltas se dibuja en dorado hasta el chip |
| 4 | corriente | La tarjeta baja sobre el datáfono, la corriente recorre la antena (mA) y el chip se enciende |
| 5 | respuesta | «NO PUEDE EMITIR» → osciloscopio: la portadora baja cuando el chip absorbe → bits 1011001110 |
| 6 | cerca | La tarjeta se aleja con regla en cm; la energía cae y el chip se apaga |
| 7 | dos | Dos tarjetas: señal caótica y pantalla «UNA SOLA TARJETA» |
| 8 | codigo | PAGO 1 ✓ · COPIA ✗ (mismo código) · PAGO 2 ✓ (código nuevo) |
| 9 | final | «Nunca ha hablado: solo ha parpadeado dentro de su energía» |
| 10 | cta | «+ SEGUIR» y «ENVÍASELO ↗»; el último segundo vuelve al plano inicial (bucle) |

Base técnica: NFC/ISO 14443 (campo de 13,56 MHz, alimentación por inducción, modulación de carga, alcance de pocos
centímetros, detección de colisión con dos tarjetas) y EMV (criptograma de un solo uso por pago).

```bash
pip install edge-tts certifi numpy pillow
python3 voz.py && python3 video.py          # -> contactless_reel.mp4  (~4 min con 4 núcleos)
python3 video.py --preview 1 14 40          # fotogramas sueltos en build/
```

**Texto para el post:** «¿Tu tarjeta sin batería… hablando? 💳⚡ Envíaselo a quien la pasa tres veces por el datáfono»
`#curiosidades #ciencia #tecnologia #nfc #sabiasque`
