import { Config } from "@remotion/cli/config";
import { existsSync } from "node:fs";

// En la nube no hay descarga de Chrome: usar el headless shell preinstalado si existe.
const SHELL = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
if (existsSync(SHELL)) Config.setBrowserExecutable(SHELL);
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(92);
