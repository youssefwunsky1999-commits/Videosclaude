"""Tiempos provisionales (sin voz) para revisar el diseño: reparte las palabras a ~2,8 por segundo.
    python3 maqueta.py && python3 construir.py"""
import json, os, re
from guion import SEGMENTOS
t, esc = 0.3, []
for s in SEGMENTOS:
    ws = re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ'-]+", s["texto"])
    pal, tt = [], t
    for w in ws:
        d = 0.12 + 0.045 * len(w)
        pal.append({"t": round(tt, 3), "d": round(d, 3), "w": w}); tt += d + 0.04
    esc.append({"escena": s["escena"], "t0": t, "dur_voz": tt - t, "texto": s["texto"], "palabras": pal})
    t = tt + 0.5
total = round(t + 1.5, 2)
for i, e in enumerate(esc):
    e["ini"] = 0.0 if i == 0 else round(e["t0"] - 0.25, 3)
    fin = total if i == len(esc) - 1 else esc[i + 1]["t0"] - 0.25
    e["dur"] = round(fin - e["ini"], 3)
os.makedirs("build", exist_ok=True)
json.dump({"total": total, "escenas": esc}, open("build/tiempos.json", "w"), ensure_ascii=False, indent=1)
print("total provisional", total)
