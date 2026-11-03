"""Guion del reel «Tu tarjeta no tiene batería» (formato «Cómo funciona por dentro»).

Base técnica (NFC / ISO 14443): el datáfono emite un campo magnético de 13,56 MHz; la antena en espiral de la
tarjeta lo convierte en corriente por inducción y alimenta el chip; el chip responde con «modulación de carga»
(varía cuánta energía absorbe) y el lector detecta esas variaciones; alcance de pocos centímetros; con dos tarjetas
juntas el lector detecta colisión; en pagos EMV cada operación genera un criptograma de un solo uso."""

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+6%"
TONO = "-6Hz"
PAUSA = 0.26

SEGMENTOS = [
    {"escena": "paradoja", "texto": "Tu tarjeta no tiene batería. Ni un cable. Ni un botón. Y aun así, en medio segundo, habla con el datáfono."},
    {"escena": "pregunta", "texto": "¿De dónde saca la energía? No la tiene. Se la presta el datáfono."},
    {"escena": "campo", "texto": "Antes de que acerques la tarjeta, el datáfono ya está creando un campo magnético invisible, que cambia de sentido trece millones de veces por segundo."},
    {"escena": "antena", "texto": "Dentro de la tarjeta, siguiendo el borde, hay un cable enrollado en varias vueltas. Es una antena."},
    {"escena": "corriente", "texto": "Cuando el campo la atraviesa, genera una corriente. Poquísima, pero suficiente para despertar al chip."},
    {"escena": "respuesta", "texto": "Y aquí viene lo curioso: el chip no tiene fuerza para enviar nada. Así que responde absorbiendo un poco más o un poco menos de energía, muy rápido. El datáfono nota esos parpadeos y los lee como unos y ceros."},
    {"escena": "cerca", "texto": "Por eso tienes que acercarla tanto: a unos centímetros, el campo ya es demasiado débil para despertarla."},
    {"escena": "dos", "texto": "Por eso falla si pasas la cartera con dos tarjetas: responden las dos a la vez, y el datáfono no sabe a cuál escuchar."},
    {"escena": "codigo", "texto": "Y por eso copiar lo que dice no basta: cada pago lleva un código que solo vale una vez."},
    {"escena": "final", "texto": "Así que tu tarjeta nunca ha hablado con el datáfono. Solo ha parpadeado dentro de su energía."},
    {"escena": "cta", "texto": "Sígueme, y envíaselo a ese amigo que pasa la tarjeta tres veces por encima del datáfono."},
]
