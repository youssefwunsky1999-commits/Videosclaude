import { continueRender, delayRender, staticFile } from "remotion";
import { theme } from "./theme";

const fuentes: [string, string][] = [
  [theme.fonts.display, "fonts/InterDisplay-Black.otf"],
  [theme.fonts.displayBold, "fonts/InterDisplay-Bold.otf"],
  [theme.fonts.body, "fonts/Inter-SemiBold.otf"],
  [theme.fonts.mono, "fonts/JetBrainsMono-Bold.ttf"],
];

let cargado = false;
export const cargarFuentes = () => {
  if (cargado || typeof document === "undefined") return;
  cargado = true;
  const h = delayRender("fuentes");
  Promise.all(
    fuentes.map(([nombre, ruta]) =>
      new FontFace(nombre, `url(${staticFile(ruta)})`).load().then((f) => document.fonts.add(f)),
    ),
  )
    .then(() => continueRender(h))
    .catch((e) => {
      console.error(e);
      continueRender(h);
    });
};
