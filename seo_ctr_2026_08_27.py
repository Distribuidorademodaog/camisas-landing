# -*- coding: utf-8 -*-
"""
Reescritura de title/description por CTR — 2026-08-27.

Motivo (GSC 28 abr - 25 ago 2026, cruce consulta x pagina):
  504 impresiones en posicion 4-15 produjeron CERO clics. El caso extremo es
  /camibusos-hombre: 865 impresiones en 11 dias, 7 clics (0,8%), posicion 8,7.
  No es un problema de ranking: estas en pagina 1 y el snippet no da motivo
  para hacer clic.

Criterio, igual que en seo_titles_2026_08.py:
  1. <= 62 chars, ninguna frase cortada.
  2. El titulo responde la INTENCION REAL medida en GSC, no la que suponemos.
  3. Promesa que la AI Overview no da: precio, tallas, foto, contraentrega.

Intencion medida por pagina:
  * camibusos-hombre        -> mezcla definicional ("que es un camibuso",
                               "como se escribe camibuso") y comercial
                               ("camibusos para hombre"). El titulo debe
                               servir a las dos.
  * camisas-polo-colores    -> "paleta de colores para polos", "colores de
                               camisa polo": quieren una PALETA, no comprar.
                               El titulo actual promete precio; por eso 0 clics.
  * blog/estilos-camisa-polo-> "tipos de polo", "tipos de corte de polo",
                               "partes de una camisa polo": buscan taxonomia.
                               El titulo dice "4 estilos" y se queda corto.

Uso:  python seo_ctr_2026_08_27.py [--dry-run]
"""
import io
import json
import re
import sys

DRY = "--dry-run" in sys.argv

PAGES = {
    # 865 impresiones / 7 clics / pos 8,7 — la mayor oportunidad del sitio
    "camibusos-hombre.html": (
        "Camibusos para Hombre: Qué Son, Precio y Tallas S a 5XL",
        "Camibuso es como le decimos en Colombia a la camisa tipo polo. Los "
        "tenemos en +20 colores y tallas S a 5XL desde $82.500 en pack, con "
        "pago contraentrega.",
    ),
    # 467 impresiones acumuladas / 0 clics — la intencion es paleta, no compra
    "camisas-polo-colores-hombre.html": (
        "Colores de Camisa Polo: Paleta de +20 Tonos con Foto Real",
        "La paleta completa de colores de camisa polo para hombre, con foto "
        "real de cada tono: cuál favorece tu piel y con qué combinarlo. Tallas "
        "S a 5XL, envío gratis.",
    ),
    # 326 impresiones / 1 clic / pos 6,6 — buscan taxonomia, no 4 estilos
    "blog/estilos-camisa-polo.html": (
        "Tipos de Camisa Polo: Estilos, Cortes y Partes Explicados",
        "Los tipos de camisa polo que existen: Oxford, lino, cuadros y rayas, "
        "los cortes slim y regular, y las partes de la prenda explicadas una "
        "por una, con fotos.",
    ),
}

# FAQ que falta y que SI se busca: "como se escribe camibuso" (15 impresiones)
FAQ_NUEVA = {
    "@type": "Question",
    "name": "¿Cómo se escribe camibuso?",
    "acceptedAnswer": {
        "@type": "Answer",
        "text": "Se escribe camibuso, en una sola palabra y sin tilde: "
                "cami-buso. El plural es camibusos. Viene de unir «camisa» y "
                "«buso», que es como se le dice en varias regiones de Colombia "
                "a la prenda de punto con cuello. No se escribe «cami buso» "
                "separado ni «caminuso».",
    },
}


def set_meta(h, title, desc):
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, h,
               count=1, flags=re.S)
    h = re.sub(r'(<meta\s+name="description"\s+content=")[^"]*(")',
               lambda m: m.group(1) + desc + m.group(2), h, count=1)
    # OG y Twitter siguen al title/description para no dejar el social viejo
    h = re.sub(r'(<meta\s+property="og:title"\s+content=")[^"]*(")',
               lambda m: m.group(1) + title + m.group(2), h, count=1)
    h = re.sub(r'(<meta\s+property="og:description"\s+content=")[^"]*(")',
               lambda m: m.group(1) + desc + m.group(2), h, count=1)
    h = re.sub(r'(<meta\s+name="twitter:title"\s+content=")[^"]*(")',
               lambda m: m.group(1) + title + m.group(2), h, count=1)
    h = re.sub(r'(<meta\s+name="twitter:description"\s+content=")[^"]*(")',
               lambda m: m.group(1) + desc + m.group(2), h, count=1)
    return h


def add_faq(h, nueva):
    """Anade una pregunta al primer FAQPage si no existe ya."""
    def repl(m):
        try:
            d = json.loads(m.group(1))
        except Exception:
            return m.group(0)
        if d.get("@type") != "FAQPage":
            return m.group(0)
        nombres = {q.get("name", "").lower() for q in d.get("mainEntity", [])}
        if nueva["name"].lower() in nombres:
            return m.group(0)
        d["mainEntity"].append(nueva)
        return ('<script type="application/ld+json">'
                + json.dumps(d, ensure_ascii=False) + "</script>")

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>',
                  repl, h, flags=re.S)


def main():
    for path, (title, desc) in PAGES.items():
        h = open(path, encoding="utf-8").read()
        antes_t = re.search(r"<title>(.*?)</title>", h, re.S)
        antes_t = " ".join(antes_t.group(1).split()) if antes_t else ""
        nuevo = set_meta(h, title, desc)
        if path == "camibusos-hombre.html":
            nuevo = add_faq(nuevo, FAQ_NUEVA)
        if not DRY and nuevo != h:
            open(path, "w", encoding="utf-8", newline="").write(nuevo)
        print("%s" % path)
        print("   antes  (%2d): %s" % (len(antes_t), antes_t))
        print("   ahora  (%2d): %s" % (len(title), title))
        print("   desc   (%2d)" % len(desc))
        if len(title) > 62:
            print("   !! TITULO LARGO")
        if len(desc) > 160:
            print("   !! DESCRIPCION LARGA")
        print()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
