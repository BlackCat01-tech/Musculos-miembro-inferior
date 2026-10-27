#!/usr/bin/env python3
"""
Descarga las animaciones (GIF) de los músculos del miembro inferior desde
Wikimedia Commons y las guarda en ./img/<slug>.gif, que es la ruta que usa index.html.

Uso:
    python descargar_imagenes.py              # descarga todo lo que falte
    python descargar_imagenes.py --forzar     # vuelve a descargar todo
    python descargar_imagenes.py --solo sartorio gracil_o_recto_interno
    python descargar_imagenes.py --lista      # solo muestra qué encontraría, sin descargar

Solo usa la biblioteca estándar (no necesitas pip install).
Genera también creditos.json con autor, licencia y página de origen de cada archivo.
"""
import argparse, html, json, re, sys, time
import urllib.error, urllib.parse, urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
# Wikimedia exige un User-Agent identificable. Cambia el correo por el tuyo.
UA = "AtlasMiembroInferior/1.0 (proyecto academico de anatomia; contacto: juanrodriguez70083@gmail.com)"
PAUSA = 1.5  # segundos entre peticiones, para no saturar el servidor

MUSCULOS = [
 {
  "slug": "sartorio",
  "es": "Sartorio",
  "queries": [
   "Sartorius"
  ],
  "must": [
   "sartorius"
  ]
 },
 {
  "slug": "pectineo",
  "es": "Pectíneo",
  "queries": [
   "Pectineus"
  ],
  "must": [
   "pectineus"
  ]
 },
 {
  "slug": "recto_femoral",
  "es": "Recto femoral (cuádriceps)",
  "queries": [
   "Rectus femoris"
  ],
  "must": [
   "rectus femoris"
  ]
 },
 {
  "slug": "vasto_intermedio_o_crural",
  "es": "Vasto intermedio o crural (cuádriceps)",
  "queries": [
   "Vastus intermedius"
  ],
  "must": [
   "vastus intermedius"
  ]
 },
 {
  "slug": "vasto_lateral_o_externo",
  "es": "Vasto lateral o externo (cuádriceps)",
  "queries": [
   "Vastus lateralis"
  ],
  "must": [
   "vastus lateralis"
  ]
 },
 {
  "slug": "vasto_medial_o_interno",
  "es": "Vasto medial o interno (cuádriceps)",
  "queries": [
   "Vastus medialis"
  ],
  "must": [
   "vastus medialis"
  ]
 },
 {
  "slug": "articular_de_la_rodilla",
  "es": "Articular de la rodilla (subcrural)",
  "queries": [
   "Articularis genus"
  ],
  "must": [
   "articularis genus"
  ]
 },
 {
  "slug": "aductor_menor",
  "es": "Aductor menor (adductor brevis)",
  "queries": [
   "Adductor brevis"
  ],
  "must": [
   "adductor brevis"
  ]
 },
 {
  "slug": "aductor_mediano_o_largo",
  "es": "Aductor mediano o largo (adductor longus)",
  "queries": [
   "Adductor longus"
  ],
  "must": [
   "adductor longus"
  ]
 },
 {
  "slug": "aductor_mayor",
  "es": "Aductor mayor (adductor magnus)",
  "queries": [
   "Adductor magnus"
  ],
  "must": [
   "adductor magnus"
  ]
 },
 {
  "slug": "gracil_o_recto_interno",
  "es": "Grácil o recto interno (gracilis)",
  "queries": [
   "Gracilis"
  ],
  "must": [
   "gracilis"
  ]
 },
 {
  "slug": "biceps_femoral",
  "es": "Bíceps femoral",
  "queries": [
   "Biceps femoris"
  ],
  "must": [
   "biceps femoris"
  ]
 },
 {
  "slug": "semimembranoso",
  "es": "Semimembranoso",
  "queries": [
   "Semimembranosus"
  ],
  "must": [
   "semimembranosus"
  ]
 },
 {
  "slug": "semitendinoso",
  "es": "Semitendinoso",
  "queries": [
   "Semitendinosus"
  ],
  "must": [
   "semitendinosus"
  ]
 },
 {
  "slug": "tibial_anterior",
  "es": "Tibial anterior",
  "queries": [
   "Tibialis anterior"
  ],
  "must": [
   "tibialis anterior"
  ]
 },
 {
  "slug": "extensor_largo_de_los_dedos",
  "es": "Extensor largo de los dedos",
  "queries": [
   "Extensor digitorum longus"
  ],
  "must": [
   "extensor digitorum longus"
  ]
 },
 {
  "slug": "extensor_largo_del_dedo_gordo",
  "es": "Extensor largo del dedo gordo (hallux)",
  "queries": [
   "Extensor hallucis longus"
  ],
  "must": [
   "extensor hallucis longus"
  ]
 },
 {
  "slug": "peroneo_anterior_o_fibular_tercero",
  "es": "Peroneo anterior o fibular tercero",
  "queries": [
   "Fibularis tertius",
   "Peroneus tertius"
  ],
  "must": [
   "fibularis tertius",
   "peroneus tertius"
  ]
 },
 {
  "slug": "peroneo_lateral_corto",
  "es": "Peroneo lateral corto (fibular corto)",
  "queries": [
   "Fibularis brevis",
   "Peroneus brevis"
  ],
  "must": [
   "fibularis brevis",
   "peroneus brevis"
  ]
 },
 {
  "slug": "peroneo_lateral_largo",
  "es": "Peroneo lateral largo (fibular largo)",
  "queries": [
   "Fibularis longus",
   "Peroneus longus"
  ],
  "must": [
   "fibularis longus",
   "peroneus longus"
  ]
 },
 {
  "slug": "tibial_posterior",
  "es": "Tibial posterior",
  "queries": [
   "Tibialis posterior"
  ],
  "must": [
   "tibialis posterior"
  ]
 },
 {
  "slug": "flexor_largo_de_los_dedos",
  "es": "Flexor largo de los dedos",
  "queries": [
   "Flexor digitorum longus"
  ],
  "must": [
   "flexor digitorum longus"
  ]
 },
 {
  "slug": "flexor_largo_del_dedo_gordo",
  "es": "Flexor largo del dedo gordo (hallux)",
  "queries": [
   "Flexor hallucis longus"
  ],
  "must": [
   "flexor hallucis longus"
  ]
 },
 {
  "slug": "soleo",
  "es": "Sóleo",
  "queries": [
   "Soleus"
  ],
  "must": [
   "soleus"
  ]
 },
 {
  "slug": "gastrocnemio_o_gemelos",
  "es": "Gastrocnemio o gemelos",
  "queries": [
   "Gastrocnemius"
  ],
  "must": [
   "gastrocnemius"
  ]
 },
 {
  "slug": "plantar_delgado",
  "es": "Plantar delgado",
  "queries": [
   "Plantaris"
  ],
  "must": [
   "plantaris"
  ]
 },
 {
  "slug": "popliteo",
  "es": "Poplíteo",
  "queries": [
   "Popliteus"
  ],
  "must": [
   "popliteus"
  ]
 },
 {
  "slug": "extensor_corto_de_los_dedos",
  "es": "Extensor corto de los dedos (pedio)",
  "queries": [
   "Extensor digitorum brevis"
  ],
  "must": [
   "extensor digitorum brevis"
  ]
 },
 {
  "slug": "extensor_corto_del_hallux",
  "es": "Extensor corto del hallux",
  "queries": [
   "Extensor hallucis brevis"
  ],
  "must": [
   "extensor hallucis brevis"
  ]
 },
 {
  "slug": "abductor_del_hallux",
  "es": "Abductor del hallux",
  "queries": [
   "Abductor hallucis"
  ],
  "must": [
   "abductor hallucis"
  ]
 },
 {
  "slug": "flexor_corto_del_hallux",
  "es": "Flexor corto del hallux",
  "queries": [
   "Flexor hallucis brevis"
  ],
  "must": [
   "flexor hallucis brevis"
  ]
 },
 {
  "slug": "aductor_del_hallux",
  "es": "Aductor del hallux",
  "queries": [
   "Adductor hallucis"
  ],
  "must": [
   "adductor hallucis"
  ]
 },
 {
  "slug": "flexor_corto_de_los_dedos",
  "es": "Flexor corto de los dedos",
  "queries": [
   "Flexor digitorum brevis"
  ],
  "must": [
   "flexor digitorum brevis"
  ]
 },
 {
  "slug": "cuadrado_plantar",
  "es": "Cuadrado plantar (flexor accesorio)",
  "queries": [
   "Quadratus plantae"
  ],
  "must": [
   "quadratus plantae"
  ]
 },
 {
  "slug": "lumbricales",
  "es": "Lumbricales (4)",
  "queries": [
   "Lumbricals of the foot",
   "Lumbrical muscles foot"
  ],
  "must": [
   "lumbrical"
  ]
 },
 {
  "slug": "abductor_del_dedo_pequeno",
  "es": "Abductor del dedo pequeño (5º dedo)",
  "queries": [
   "Abductor digiti minimi foot"
  ],
  "must": [
   "abductor digiti minimi"
  ]
 },
 {
  "slug": "flexor_corto_del_dedo_pequeno",
  "es": "Flexor corto del dedo pequeño (5º dedo)",
  "queries": [
   "Flexor digiti minimi brevis foot"
  ],
  "must": [
   "flexor digiti minimi brevis"
  ]
 },
 {
  "slug": "interoseos_dorsales",
  "es": "Interóseos dorsales (4)",
  "queries": [
   "Dorsal interossei of the foot"
  ],
  "must": [
   "dorsal interossei"
  ]
 },
 {
  "slug": "interoseos_plantares",
  "es": "Interóseos plantares (3)",
  "queries": [
   "Plantar interossei of the foot"
  ],
  "must": [
   "plantar interossei"
  ]
 }
]


def pedir(url, binario=False, intentos=4):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                datos = r.read()
            return datos if binario else json.loads(datos.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < intentos - 1:
                espera = int(e.headers.get("Retry-After", 5 * (i + 1)))
                print(f"   servidor ocupado ({e.code}), espero {espera}s…")
                time.sleep(espera)
                continue
            raise
        except urllib.error.URLError:
            if i < intentos - 1:
                time.sleep(3)
                continue
            raise


def api(**params):
    params.update(format="json", formatversion="2")
    return pedir(API + "?" + urllib.parse.urlencode(params))


def buscar_gif(m):
    """Devuelve (titulo, url, meta) del mejor GIF para el músculo, o None."""
    mejor = None
    for q in m["queries"]:
        res = api(action="query", list="search", srnamespace=6, srlimit=30,
                  srsearch=f"{q} muscle animation gif")
        time.sleep(PAUSA)
        for h in res.get("query", {}).get("search", []):
            t = h["title"]                       # "File:Sartorius muscle - animation.gif"
            tl = t.lower()
            if not tl.endswith(".gif"):
                continue
            if not any(k in tl for k in m["must"]):
                continue
            puntos = 0
            if "animation" in tl: puntos += 3
            if "muscle" in tl: puntos += 1
            if "left" in tl: puntos += 1          # evita duplicados izquierdo/derecho
            if "foot" in tl or "pedis" in tl: puntos += 4
            if any(w in tl for w in ("hand", "manus")): puntos -= 10
            if mejor is None or puntos > mejor[0]:
                mejor = (puntos, t)
        if mejor and mejor[0] > 0:
            break
    if not mejor or mejor[0] <= 0:
        return None
    t = mejor[1]
    info = api(action="query", titles=t, prop="imageinfo", iiprop="url|extmetadata")
    ii = info["query"]["pages"][0]["imageinfo"][0]
    meta = ii.get("extmetadata", {})
    limpio = lambda k: html.unescape(re.sub(r"<[^>]+>", "", meta.get(k, {}).get("value", ""))).strip()
    return t, ii["url"], {
        "autor": limpio("Artist"),
        "licencia": limpio("LicenseShortName"),
        "pagina": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(t.replace(" ", "_")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forzar", action="store_true", help="vuelve a descargar aunque exista")
    ap.add_argument("--solo", nargs="+", help="solo estos slugs")
    ap.add_argument("--lista", action="store_true", help="no descarga, solo busca")
    ap.add_argument("--carpeta", default="img")
    a = ap.parse_args()

    out = Path(a.carpeta); out.mkdir(exist_ok=True)
    cred_path = Path("creditos.json")
    creditos = json.loads(cred_path.read_text("utf-8")) if cred_path.exists() else {}
    faltan = []
    lote = [m for m in MUSCULOS if not a.solo or m["slug"] in a.solo]

    for n, m in enumerate(lote, 1):
        destino = out / f"{m['slug']}.gif"
        print(f"[{n}/{len(lote)}] {m['es']}")
        if destino.exists() and not a.forzar and not a.lista:
            print("   ya existe, lo salto"); continue
        try:
            r = buscar_gif(m)
            if not r:
                print("   ✗ sin GIF en Commons"); faltan.append(m["es"]); continue
            titulo, url, meta = r
            print(f"   → {titulo}")
            if a.lista: continue
            destino.write_bytes(pedir(url, binario=True))
            time.sleep(PAUSA)
            creditos[m["slug"]] = {"archivo": titulo, "url": url, **meta}
            cred_path.write_text(json.dumps(creditos, ensure_ascii=False, indent=1), "utf-8")
            print(f"   ✓ guardado ({destino.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"   ✗ error: {e}"); faltan.append(m["es"])

    print("\nListo.")
    if faltan:
        print("Sin imagen (la web mostrará el texto igual):")
        for f in faltan: print("  -", f)
        print("Puedes poner tu propio GIF/PNG como img/<slug>.gif y la web lo usará.")


if __name__ == "__main__":
    sys.exit(main())
