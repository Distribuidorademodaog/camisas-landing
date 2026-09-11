# -*- coding: utf-8 -*-
"""
Unifica ORDER_BUMPS_CONFIG en las 65 paginas con checkout — 2026-09-11.

El problema: la configuracion de order bumps esta DUPLICADA en cada pagina con
checkout y se desincronizo. Habia cuatro versiones conviviendo:

    51 paginas  landings comerciales
    10 paginas  ciudades principales
     3 paginas  envigado, itagui, soacha
     1 pagina   index.html  <- la unica al dia

Consecuencias medidas antes de tocar nada:

1. Todo lo trabajado con el negocio los dias 10 y 11 de septiembre (las 10
   camisetas nuevas en webp, las 3 fotos nuevas de polo blanca/negra/azul
   oscura, las tallas corregidas de azul rey y azul medio) vivia SOLO en la
   home. Quien llegaba al checkout desde /camisas-3xl-hombre o desde una
   ciudad veia el catalogo viejo y podia pedir tallas que ya no hay.

2. En 54 de esas paginas habia DOS bumps llamados «Polo Premium» a la vez
   (bump5 y bump6) con inventarios que se contradecian: uno decia que beige
   solo quedaba en 3XL y el otro que habia en cinco tallas. No es un bump
   duplicado de verdad: es un resto del renombrado del 2026-08-25, cuando
   «Polo Lacoste» se cambio por «Polo Coco» en 11 paginas y por «Polo Premium»
   —el nombre que ya usaba bump5— en las otras 54.

3. beige quedo sin ninguna talla en bump5 y el negocio lo dio por agotado. La
   config canonica ya no referencia polo-beige.webp, asi que tras unificar esa
   foto se puede borrar del CDN. OJO: el beige de «Polo Coco»
   (lacoste-beige.webp) y el de «Polo Purificacion» (purificaciongarcia-beige)
   son OTRAS prendas con su propio stock y se quedan.

Que hace: copia el bloque ORDER_BUMPS_CONFIG de index.html —la version que el
negocio mantiene al dia— a las otras 64 paginas, tal cual. La estructura ya era
identica (bump2, bump5, bump6, bump7, bump8 con los mismos ids de variante), lo
que cambiaba era el contenido.

Uso:  python unificar_order_bumps_2026_09_11.py [--dry-run]
"""
import glob
import hashlib
import io
import os
import re
import subprocess
import sys

ANCLA = "const ORDER_BUMPS_CONFIG"
FIN = "\n];"


def bloque(html):
    """Devuelve (inicio, fin) del bloque de configuracion, o None."""
    i = html.find(ANCLA)
    if i < 0:
        return None
    j = html.find(FIN, i)
    if j < 0:
        return None
    return i, j + len(FIN)


def parsea(cfg, etiqueta):
    """El bloque tiene que ser JS valido y dejar todas las variantes con tallas."""
    tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "chk_bumps.js")
    io.open(tmp, "w", encoding="utf-8").write(cfg + """
const malas = [];
ORDER_BUMPS_CONFIG.forEach(b => {
  const ids = b.variants.map(v => v.id);
  if (new Set(ids).size !== ids.length) malas.push(b.id + ': ids repetidos');
  b.variants.forEach(v => {
    if (!v.tallas || !v.tallas.length) malas.push(b.id + '/' + v.id + ': sin tallas');
    if (!/^https:\\/\\//.test(v.img)) malas.push(b.id + '/' + v.id + ': img rara');
  });
});
console.log(malas.length ? 'FALLOS: ' + malas.join(' | ')
                         : 'OK ' + ORDER_BUMPS_CONFIG.length + ' bumps, '
                           + ORDER_BUMPS_CONFIG.reduce((a, b) => a + b.variants.length, 0) + ' variantes');
""")
    r = subprocess.run(["node", tmp], capture_output=True, text=True)
    salida = (r.stdout or r.stderr).strip()
    if not salida.startswith("OK"):
        raise SystemExit("!! [%s] %s" % (etiqueta, salida[:200]))
    return salida


def main():
    dry = "--dry-run" in sys.argv

    canon_html = io.open("index.html", encoding="utf-8").read()
    b = bloque(canon_html)
    if not b:
        raise SystemExit("!! index.html no tiene ORDER_BUMPS_CONFIG")
    canon = canon_html[b[0]:b[1]]
    print("canonica (index.html): %s" % parsea(canon, "index"))
    if "polo-beige.webp" in canon:
        raise SystemExit("!! la canonica todavia referencia polo-beige.webp")

    paginas = [p for p in sorted(glob.glob("*.html"))
               if p not in ("404.html", "gracias.html", "index.html")]
    firmas_antes = {}
    cambiadas = igual = 0
    for f in paginas:
        h = io.open(f, encoding="utf-8").read()
        pos = bloque(h)
        if not pos:
            print("  (sin checkout) %s" % f)
            continue
        actual = h[pos[0]:pos[1]]
        firmas_antes[hashlib.md5(actual.encode()).hexdigest()[:8]] = \
            firmas_antes.get(hashlib.md5(actual.encode()).hexdigest()[:8], 0) + 1
        if actual == canon:
            igual += 1
            continue
        nuevo = h[:pos[0]] + canon + h[pos[1]:]
        # el reemplazo no puede alterar nada fuera del bloque
        assert nuevo[:pos[0]] == h[:pos[0]] and nuevo[pos[0] + len(canon):] == h[pos[1]:]
        if not dry:
            io.open(f, "w", encoding="utf-8", newline="").write(nuevo)
        cambiadas += 1

    print("\nconfiguraciones distintas que habia: %d  %s"
          % (len(firmas_antes), dict(firmas_antes)))
    print("paginas unificadas: %d   (ya estaban al dia: %d)" % (cambiadas, igual))

    if not dry:
        # comprobacion real pagina por pagina, no de muestra
        malas = []
        for f in paginas:
            h = io.open(f, encoding="utf-8").read()
            pos = bloque(h)
            if not pos:
                continue
            if h[pos[0]:pos[1]] != canon:
                malas.append(f)
            if "polo-beige.webp" in h:
                malas.append(f + " (aun con polo-beige)")
        print("paginas que NO quedaron con la canonica: %s" % (malas or "ninguna"))
        parsea(canon, "resultado")

    print("\n%s" % ("(DRY-RUN, no se escribio)" if dry else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
