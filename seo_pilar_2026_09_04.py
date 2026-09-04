# -*- coding: utf-8 -*-
"""
Rompe la canibalizacion de "camisas polo" — 2026-09-04.

Diagnostico (GSC, 6 ago - 2 sep 2026, cruce consulta x pagina):
  El termino cabeza lo captura la pagina EQUIVOCADA. Google elige el hub de
  colores, no la pilar:

      "camisas polo"             /camisas-polo-colores-hombre   pos 64,3
      "camisa polo"              /camisas-polo-colores-hombre   pos 56,0
      "camisas polo para hombre" /camisas-polo-colores-hombre   pos 60,4
      "camisa polo masculina"    /camisas-polo-colores-hombre   pos 55,0

  Mientras la pilar /camisas-polo-premium-colombia tiene 58 impresiones en
  posicion 13,5. Toda la familia cabeza (polos para hombre, camisas polo
  hombre, polo para hombre...) suma 565 impresiones en posicion 44-60 y CERO
  clics. El intento del 27-ago (seo_pilar_2026_08_27.py) enlazo 9 landings,
  pero no toco el blog, que es donde estan las 12.124 impresiones del mes.

Tres palancas, de mas a menos fuerte:
  1. La pilar no dice el termino cabeza. Su title era "Camisas Polo Estilo
     Premium en Colombia | Alternativa Premium": "Premium" tres veces y ni
     "para hombre" ni "polos". Se reescribe hacia la consulta real.
  2. El hub de colores SI lo dice, en el H1 oculto ("Guia de camisas polo de
     colores para hombre..."). Se desoptimiza hacia su propio termino, que ya
     rankea en posicion 6,4: "colores de camisa polo".
  3. Enlace contextual desde la prosa del blog hacia la pilar, con ancla
     exacta. El blog tiene 12.124 impresiones/mes de equity sin repartir.

OJO build_landings.py: usa la pilar como PLANTILLA y busca su title exacto.
Al cambiarlo hay que mover tambien las constantes RL_*. Se hace aqui.
(Ese build ya estaba roto por otro motivo: el JSON-LD de la pilar se reformateo
 con espacios y RL_WEBPAGE_NAME/RL_BC1 ya no casaban. No se arregla aqui.)

Uso:  python seo_pilar_2026_09_04.py [--dry-run]
"""
import glob
import io
import json
import re
import sys

PILAR_HTML = "camisas-polo-premium-colombia.html"
PILAR_URL = "/camisas-polo-premium-colombia"
HUB_HTML = "camisas-polo-colores-hombre.html"
HUB_META = "_landings/camisas-polo-colores-hombre.meta.json"
BUILD = "build_landings.py"

# ---- 1. pilar: del posicionamiento "premium" a la consulta real ----
T_VIEJO = "Camisas Polo Estilo Premium en Colombia | Alternativa Premium"
T_NUEVO = "Camisas Polo para Hombre en Colombia | Polos Estilo Premium"
TW_VIEJO = "Camisas Polo Hombre Estilo Premium en Colombia"
TW_NUEVO = "Camisas Polo para Hombre en Colombia | Polos Premium"
BC_VIEJO = "Camisas Polo Estilo Premium en Colombia"
BC_NUEVO = "Camisas Polo para Hombre en Colombia"

DESC_NUEVA = ("Camisas polo para hombre en Colombia: algodón piqué, corte "
              "clásico y +20 colores. Tallas S a 5XL desde $82.500 en pack, "
              "pago contraentrega y envío gratis.")
OGDESC_NUEVA = ("Camisas polo para hombre en Colombia: corte clásico, algodón "
                "piqué y +20 colores. Tallas S a 5XL, pago contraentrega y "
                "envío gratis a todo el país.")
TWDESC_NUEVA = ("Camisas polo para hombre: +20 colores, tallas S a 5XL. "
                "Paga al recibir. Envío gratis.")
WPDESC_NUEVA = ("Tienda online colombiana de camisas polo para hombre: algodón "
                "piqué, tallas S a 5XL, +20 colores, pago contraentrega y "
                "envío gratis.")
# El <span> oculto del H1 (el visible es "Vistete bien / Paga al llegar").
H1SR_NUEVO = ("Camisas polo para hombre en Colombia: corte clásico, algodón "
              "piqué, tallas S a 5XL y más de 20 colores, pago contraentrega "
              "y envío gratis.")

# ---- 2. hub de colores: soltar el termino cabeza ----
HUB_H1SR_NUEVO = ("Colores de camisa polo para hombre en Colombia: cómo elegir "
                  "el color según tu tono de piel, ocasión y estilo, con más de "
                  "20 tonos en algodón piqué premium desde 82.500 pesos en pack, "
                  "pago contraentrega y envío gratis.")

# ---- 3. enlazado desde el blog ----
MARCA = 'data-link="pilar-2026-09"'
# El intento de agosto excluia el singular ("el termino que canibaliza es
# plural"). Ya no: en la ventana 6-ago/2-sep tambien estan canibalizados
# "camisa polo" (42 impr, pos 45,7) y "camisa polo masculina" (30, pos 24,9).
# Sin el singular solo 9 de 21 blogs tienen mencion en prosa; con el, 20.
PATRONES = [re.compile(r"camisas polo para hombre", re.I),
            re.compile(r"camisas polo", re.I),
            re.compile(r"camisa polo", re.I)]


def sub1(pat, repl, s, label, flags=0):
    nuevo, n = re.subn(pat, lambda m: repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit("!! [%s] patron no encontrado" % label)
    return nuevo


def exacto(viejo, nuevo, s, label, veces=1):
    if s.count(viejo) != veces:
        raise SystemExit("!! [%s] esperaba %d ocurrencias, hay %d"
                         % (label, veces, s.count(viejo)))
    return s.replace(viejo, nuevo)


def h1_sr(html, texto, label):
    """Reescribe SOLO el <span> oculto del H1, deja el visible intacto."""
    m = re.search(r'(<h1 class="hero-title"><span style="[^"]*">)(.*?)(</span>)',
                  html, re.S)
    if not m:
        raise SystemExit("!! [%s] no se encontro el span oculto del H1" % label)
    return html[:m.start(2)] + texto + html[m.end(2):]


def pilar(dry):
    h = io.open(PILAR_HTML, encoding="utf-8").read()
    if T_NUEVO in h:
        print("pilar: ya aplicado")
        return
    # title + og:title + WebPage name comparten la misma cadena (3 veces)
    h = exacto(T_VIEJO, T_NUEVO, h, "title/og/webpage", veces=3)
    h = exacto(TW_VIEJO, TW_NUEVO, h, "twitter:title")
    h = exacto(BC_VIEJO, BC_NUEVO, h, "breadcrumb")
    h = sub1(r'<meta name="description" content="[^"]*">',
             '<meta name="description" content="%s">' % DESC_NUEVA, h, "desc")
    h = sub1(r'<meta property="og:description" content="[^"]*">',
             '<meta property="og:description" content="%s">' % OGDESC_NUEVA,
             h, "og:desc")
    h = sub1(r'<meta name="twitter:description" content="[^"]*">',
             '<meta name="twitter:description" content="%s">' % TWDESC_NUEVA,
             h, "tw:desc")
    h = sub1(r'"description": "Tienda online colombiana[^"]*"',
             '"description": "%s"' % WPDESC_NUEVA, h, "webpage:desc")
    h = h1_sr(h, H1SR_NUEVO, "pilar h1")
    if not dry:
        io.open(PILAR_HTML, "w", encoding="utf-8", newline="").write(h)
    print("pilar: title -> %s" % T_NUEVO)


def constantes_build(dry):
    """build_landings.py compara contra el title exacto de la pilar."""
    s = io.open(BUILD, encoding="utf-8").read()
    if T_NUEVO in s:
        print("build_landings: ya sincronizado")
        return
    s = exacto(T_VIEJO, T_NUEVO, s, "RL_TITLE/RL_OG_TITLE/RL_WEBPAGE_NAME", veces=3)
    s = exacto(TW_VIEJO, TW_NUEVO, s, "RL_TW_TITLE")
    s = exacto('"name": "Camisas Polo Estilo Premium en Colombia",',
               '"name": "%s",' % BC_NUEVO, s, "RL_BC2")
    s = exacto('"name":"Camisas Polo Estilo Premium","item"',
               '"name":"Camisas Polo para Hombre","item"', s, "RL_BC1")
    s = exacto('"description":"Tienda online colombiana de camisas polo premium '
               'para hombre estilo premium. Pago contraentrega, envío gratis '
               'y +20 colores."',
               '"description":"%s"' % WPDESC_NUEVA, s, "RL_WEBPAGE_DESC")
    if not dry:
        io.open(BUILD, "w", encoding="utf-8", newline="").write(s)
    print("build_landings: constantes RL_* sincronizadas")


def hub(dry):
    h = io.open(HUB_HTML, encoding="utf-8").read()
    if HUB_H1SR_NUEVO in h:
        print("hub colores: ya aplicado")
        return
    h = h1_sr(h, HUB_H1SR_NUEVO, "hub h1")
    if not dry:
        io.open(HUB_HTML, "w", encoding="utf-8", newline="").write(h)
    # la fuente (gitignored) tiene que quedar igual que lo desplegado
    m = json.load(io.open(HUB_META, encoding="utf-8"))
    m["hero_h1_sr"] = HUB_H1SR_NUEVO
    m["title"] = re.search(r"<title>(.*?)</title>", h, re.S).group(1)
    m["meta_description"] = re.search(
        r'<meta name="description" content="(.*?)">', h, re.S).group(1)
    if not dry:
        io.open(HUB_META, "w", encoding="utf-8", newline="").write(
            json.dumps(m, ensure_ascii=False, indent=2) + "\n")
    print("hub colores: H1 oculto -> 'Colores de camisa polo...' (+ meta.json)")


def dentro_de_enlace(cuerpo, pos):
    """True si pos cae dentro de un <a ...>...</a> del parrafo."""
    for a in re.finditer(r"<a\b.*?</a>", cuerpo, re.S):
        if a.start() <= pos < a.end():
            return True
    return False


def enlazar(html):
    if MARCA in html or ('href="%s"' % PILAR_URL) in html:
        return html, None
    for pat in PATRONES:
        for pm in re.finditer(r"<p[^>]*>(.*?)</p>", html, re.S):
            cuerpo = pm.group(1)
            if "${" in cuerpo:
                continue  # plantilla JS
            for m in pat.finditer(cuerpo):
                if dentro_de_enlace(cuerpo, m.start()):
                    continue
                nuevo = (cuerpo[:m.start()]
                         + '<a href="%s" %s>%s</a>' % (PILAR_URL, MARCA, m.group(0))
                         + cuerpo[m.end():])
                ini, fin = pm.span(1)
                return html[:ini] + nuevo + html[fin:], m.group(0)
    return html, None


def blog(dry):
    ok = 0
    for path in sorted(glob.glob("blog/*.html")):
        h = io.open(path, encoding="utf-8").read()
        nuevo, ancla = enlazar(h)
        if ancla is None:
            print("  %-56s sin mencion apta o ya enlaza" % path)
            continue
        assert nuevo.count("<p") == h.count("<p"), "parrafos alterados"
        assert nuevo.count("<a") == h.count("<a") + 1, "enlaces inesperados"
        assert nuevo.count("</a>") == h.count("</a>") + 1, "cierres inesperados"
        if not dry:
            io.open(path, "w", encoding="utf-8", newline="").write(nuevo)
        print('  %-56s ancla: "%s"' % (path, ancla))
        ok += 1
    print("%d enlaces nuevos a la pilar desde el blog" % ok)


def main():
    dry = "--dry-run" in sys.argv
    pilar(dry)
    constantes_build(dry)
    hub(dry)
    print("\nenlazado del blog:")
    blog(dry)
    print("\n%s" % ("(DRY-RUN, no se escribio nada)" if dry else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
