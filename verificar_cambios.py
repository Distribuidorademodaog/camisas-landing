# -*- coding: utf-8 -*-
"""Validacion de los cambios SEO de 2026-08-14 antes de desplegar."""
import re, json, glob, os, subprocess

# --name-only tambien lista los BORRADOS; si no se filtran, el open() revienta.
tocados = [f for f in subprocess.run(["git", "diff", "--name-only"],
           capture_output=True, text=True).stdout.split()
           if f.endswith(".html") and os.path.exists(f)]
err = 0
print("Validando %d archivos HTML modificados\n" % len(tocados))

# 1) JSON-LD parseable
malos = 0
for f in tocados:
    s = open(f, encoding="utf-8").read()
    for i, m in enumerate(re.finditer(
            r'<script type="application/ld\+json">(.*?)</script>', s, re.S)):
        try:
            json.loads(m.group(1))
        except Exception as e:
            print("  JSON-LD ROTO %s bloque %d: %s" % (f, i, e)); malos += 1
print("1. JSON-LD: %d bloques rotos" % malos); err += malos

# 2) el balance de <div> no puede EMPEORAR respecto a HEAD
cambios = 0
for f in tocados:
    antes = subprocess.run(["git", "show", "HEAD:" + f],
                           capture_output=True).stdout.decode("utf-8", "replace")
    ahora = open(f, encoding="utf-8").read()
    da = len(re.findall(r"<div\b", antes)) - len(re.findall(r"</div>", antes))
    dn = len(re.findall(r"<div\b", ahora)) - len(re.findall(r"</div>", ahora))
    if da != dn:
        print("  CAMBIO EL BALANCE en %s: %+d -> %+d" % (f, da, dn)); cambios += 1
print("2. balance de div: %d archivos donde cambio (preexistentes se ignoran)" % cambios)
err += cambios

# 3) cero marcas ajenas usadas para POSICIONAR el producto.
#    Excepciones deliberadas, no son posicionamiento de marca:
#      - "Rene Lacoste" / "Lewis Lacey": los inventores del polo en 1926. Es un
#        hecho historico dentro del articulo de origen de la prenda.
#      - nombres de archivo de imagen en el CDN (order-bumps/lacoste-*.webp):
#        se reportan aparte porque hay que renombrarlos en el CDN, no aqui.
MARCAS = ["ralph lauren", "ralph", "lauren", "lacoste", "tommy hilfiger"]
EXCEPCIONES = ["rené lacoste", "rene lacoste", "lewis lacey"]
hits = 0
cdn = []
bumps = set()
for f in tocados:
    txt = open(f, encoding="utf-8").read().lower()
    for e in EXCEPCIONES:
        txt = txt.replace(e, "")
    # los nombres de archivo del CDN se anotan pero no cuentan como fallo
    for m in re.findall(r"order-bumps/[a-z0-9-]*(?:lacoste|ralph|lauren)[a-z0-9-]*\.webp", txt):
        cdn.append((f, m))
    txt = re.sub(r"order-bumps/[a-z0-9-]+\.webp", "", txt)
    # Los order bumps del checkout estaban rotulados con marcas ajenas.
    # DECISION DEL NEGOCIO 2026-08-25 (cambia la del 2026-08-18): se limpian,
    # porque Google Ads aplica su politica de falsificaciones a la pagina de
    # destino y sanciona la cuenta entera. Nombres aprobados por el negocio:
    #   Polo Psycho Bunny            -> Polo Bun
    #   Polo Lacoste                 -> Polo Coco
    #   Polo Purificacion Garcia     -> Polo Purificacion
    #   Camiseta Psycho Bunny        -> bump eliminado
    #   Camiseta Seleccion Colombia  -> bump eliminado
    # Se sigue vigilando el nombre COMPLETO de marca, no el abreviado.
    for m in re.findall(r"name:\s*'([^']*)'", txt):
        if any(b in m.lower() for b in ("lacoste", "psycho bunny",
                                        "purificacion garcia", "purificación garcía",
                                        "seleccion colombia", "selección colombia")):
            bumps.add(m.strip())
    txt = re.sub(r"name:\s*'[^']*'", "", txt)
    h = [m for m in MARCAS if m in txt]
    if h:
        print("  MARCA AJENA en %s: %s" % (f, sorted(set(h)))); hits += 1
if cdn:
    print("  (aviso) %d imagenes del CDN con marca en el nombre, p.ej. %s"
          % (len(cdn), cdn[0][1]))
if bumps:
    print("  (nota) %d order bumps con marca ajena en el nombre: decision "
          "tomada el 2026-08-18, se quedan asi." % len(bumps))
print("3. marcas ajenas de posicionamiento: %d archivos" % hits); err += hits

# 4) enlaces internos (separador normalizado: en Windows glob devuelve '\')
todos = set()
for p in glob.glob("*.html") + glob.glob("blog/*.html") + glob.glob("guias/*.html"):
    todos.add(p.replace(os.sep, "/"))


# Vercel resuelve estos antes de buscar el archivo: un enlace hacia el origen
# de un redirect NO esta roto (aunque conviene apuntar al destino final).
import json as _json
_vc = _json.load(open("vercel.json", encoding="utf-8"))
REDIRECTS = {r["source"].strip("/"): r.get("destination", "")
             for r in _vc.get("redirects", []) if ":" not in r.get("source", "")}


def existe(h):
    h = h.strip("/")
    if h == "":
        return True
    # cleanUrls=true en Vercel: /camisas-polo-cali sirve camisas-polo-cali.html
    if (h + ".html") in todos or (h + "/index.html") in todos:
        return True
    if h in REDIRECTS:
        return True
    return os.path.exists(h)  # assets estaticos: favicon, sitemap.xml, imagenes


rotos = []
for f in tocados:
    s = open(f, encoding="utf-8").read()
    for h in sorted(set(re.findall(r'href="(/[^"#?]*)"', s))):
        if not existe(h):
            rotos.append((f, h))
print("4. enlaces internos rotos: %d" % len(rotos))
for f, h in rotos[:20]:
    print("     %s -> %s" % (f, h))
err += len(rotos)

# 5) el bloque de color existe y todos sus destinos resuelven
BLOGS_COLOR = ["blog/colores-camisa-polo-segun-tono-de-piel.html",
               "blog/como-combinar-camisa-polo.html",
               "blog/tendencias-2026-camisas-polo-colombia.html",
               "blog/cuidados-camisa-polo.html",
               "blog/estilos-camisa-polo.html"]
nuevos = 0
for f in BLOGS_COLOR:
    s = open(f, encoding="utf-8").read()
    b = re.search(r'<div class="related-block" data-block="color-cluster">.*?</div></div>',
                  s, re.S)
    if not b:
        print("  FALTA el bloque de color en %s" % f); err += 1; continue
    for h in re.findall(r'href="(/[^"]*)"', b.group(0)):
        nuevos += 1
        if not existe(h):
            print("  ROTO en bloque de color: %s -> %s" % (f, h)); err += 1
print("5. enlaces de color nuevos que resuelven: %d" % nuevos)

# 6) checkout intacto en las landings tocadas (el JS no tiene null-guard)
CRITICOS = ["catalogGrid", "perShirtGrid", "pack-container", "carruselTrack"]
faltan = 0
for f in tocados:
    if f.startswith("blog/"):
        continue
    s = open(f, encoding="utf-8").read()
    m = [c for c in CRITICOS if c not in s]
    if m:
        print("  FALTA ELEMENTO DE CHECKOUT en %s: %s" % (f, m)); faltan += 1
print("6. elementos de checkout ausentes: %d" % faltan); err += faltan

# 7) titles y descriptions unicos en todo el sitio
ts, ds = {}, {}
for f in sorted(todos):
    s = open(f, encoding="utf-8").read()
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    d = re.search(r'<meta name="description" content="(.*?)">', s, re.S)
    if t:
        ts.setdefault(t.group(1).strip(), []).append(f)
    if d:
        ds.setdefault(d.group(1).strip(), []).append(f)
dupt = {k: v for k, v in ts.items() if len(v) > 1}
dupd = {k: v for k, v in ds.items() if len(v) > 1}
for k, v in list(dupt.items()) + list(dupd.items()):
    print("  DUPLICADO %r en %s" % (k[:55], v)); err += 1
print("7. %d paginas: %d titles duplicados, %d descriptions duplicadas"
      % (len(todos), len(dupt), len(dupd)))

# 8) coherencia noindex <-> sitemap: una pagina con noindex no debe estar en el
#    sitemap (señales contradictorias), y una indexable si debe estarlo.
sm = open("sitemap.xml", encoding="utf-8").read()
incoh = 0
for f in sorted(todos):
    if f in ("404.html", "gracias.html"):
        continue
    s = open(f, encoding="utf-8").read()
    m = re.search(r'<meta name="robots" content="([^"]*)"', s)
    noindex = bool(m) and "noindex" in m.group(1)
    slug = "/" if f == "index.html" else "/" + f[:-5].replace("/index", "")
    en_sm = ("<loc>https://www.camisascolombia.com%s</loc>" % slug) in sm
    if noindex and en_sm:
        print("  INCOHERENTE: %s tiene noindex pero sigue en el sitemap" % f)
        incoh += 1
    elif not noindex and not en_sm:
        print("  INCOHERENTE: %s es indexable pero no esta en el sitemap" % f)
        incoh += 1
print("8. coherencia noindex/sitemap: %d incoherencias" % incoh)
err += incoh

print("\n%s" % ("=== SIN ERRORES ===" if err == 0 else ">>> %d ERRORES <<<" % err))
raise SystemExit(1 if err else 0)
