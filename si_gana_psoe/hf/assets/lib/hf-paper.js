/* hf-paper.js — monta un shader de Paper Shaders y lo deja parado (velocidad 0) para que HyperFrames lo dibuje
   fotograma a fotograma desde la línea de tiempo de cada escena: misma t => mismo píxel, en vista previa y en render.

   const fondo = hfPaper("clave", el, PaperShaders.meshGradientFragmentShader, uniforms, { speed: 0.6, offset: 3 });
   tl.eventCallback("onUpdate", () => fondo.draw(tl.time()));

   Las texturas se pasan como hfImg("assets/x.png"); el shader se crea cuando todas han cargado y esa espera queda
   registrada en window.__hf.buildReady, así que el render no empieza antes.                                      */
(function () {
  const P = window.PaperShaders;
  window.hfPaperColor = P.getShaderColorFromString;
  window.hfPaperSizing = function (fit, extra) {
    return Object.assign({
      u_fit: P.ShaderFitOptions[fit || "cover"], u_scale: 1, u_rotation: 0, u_originX: 0.5, u_originY: 0.5,
      u_offsetX: 0, u_offsetY: 0, u_worldWidth: 0, u_worldHeight: 0,
    }, extra || {});
  };
  window.hfImg = function (src) { const im = new Image(); im.src = src; return im; };
  window.hfNoise = function () { return P.getShaderNoiseTexture(); };

  const carga = (im) => (im.complete && im.naturalWidth ? Promise.resolve() : new Promise((ok, mal) => {
    im.addEventListener("load", () => ok(), { once: true });
    im.addEventListener("error", () => mal(new Error("hf-paper: no carga " + im.src.slice(0, 80))), { once: true });
  }));

  window.hfPaper = function (clave, el, frag, uniforms, opts) {
    opts = opts || {};
    let m = null, ultimo = null, pendiente = 0;
    const pintar = (t) => {
      const f = ((opts.offset || 0) + t * (opts.speed == null ? 1 : opts.speed)) * 1000;
      if (f === ultimo || !m || !m.program) return;
      ultimo = f;
      m.currentFrame = f;
      m.lastRenderTime = performance.now();
      m.render(m.lastRenderTime);
    };
    const imgs = Object.values(uniforms).filter((v) => v instanceof HTMLImageElement);
    const listo = Promise.all(imgs.map(carga)).then(() => {
      m = new P.ShaderMount(el, frag, uniforms, { preserveDrawingBuffer: true, antialias: false }, 0, 0,
        opts.pixelRatio || 1, opts.maxPixels || 1080 * 1920 * 0.6, opts.mipmaps);
      pintar(pendiente);
    });
    window.__hf = window.__hf || {};
    window.__hf.buildReady = window.__hf.buildReady || {};
    window.__hf.buildReady["paper-" + clave] = listo;
    return {
      draw(t) { pendiente = t; pintar(t); },
      set(u) { if (m) { m.setUniforms(u); ultimo = null; } },
      listo,
    };
  };
})();
