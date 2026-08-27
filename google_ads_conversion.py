# -*- coding: utf-8 -*-
"""Conversiones de Google Ads para camisascolombia.com

El sitio tiene DOS rutas de compra y solo una pasaba por /gracias:

  contraentrega -> submitForm() dispara fbq Purchase EN LA MISMA PAGINA
                   con el precio real (S.packPrice). NO va a /gracias.  (67 paginas)
  Wompi         -> payWithWompi() redirige a Wompi y Wompi vuelve a
                   /gracias?ref=<referencia>.                            (11 paginas)

Por eso la conversion de Google Ads NO puede vivir solo en /gracias: se
perderia todo el contraentrega, que es el grueso del negocio.

  --fix-valor   Parte 1, no necesita nada de Google Ads. Arregla dos bugs de
                la ruta Wompi: /gracias recibe ?ref= pero lee ?valor= y
                ?pedido=, asi que TODA compra prepagada se reporta con el
                valor por defecto de $82.500 y con transaction_id 'cc-<ts>'
                (que rompe la deduplicacion).

  --aw AW-123456789/AbC-D_efGh   Parte 2. Instala la etiqueta de Google Ads:
                config en las 91 paginas, evento de conversion en submitForm()
                junto al Purchase de Meta (mismo guard de 24 h, precio real y
                telefono para conversiones mejoradas) y en /gracias para Wompi.

Idempotente: no duplica nada si ya esta puesto. Preserva CRLF.
Uso:  python google_ads_conversion.py --fix-valor [--dry]
      python google_ads_conversion.py --aw AW-XXXXXXXXX/etiqueta [--dry]
"""
import argparse, glob, io, os, re, sys

EXCLUIR = ("output", "_landings", "_cities", "_blog", "node_modules")


def paginas():
    raiz = os.path.dirname(os.path.abspath(__file__))
    for ruta in sorted(glob.glob(os.path.join(raiz, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(ruta, raiz).replace("\\", "/")
        if rel.split("/")[0] in EXCLUIR:
            continue
        yield rel, ruta


def leer(ruta):
    with io.open(ruta, encoding="utf-8", newline="") as f:
        return f.read()


def escribir(ruta, s):
    with io.open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(s)


# --------------------------------------------------------------- parte 1
REDIR_VIEJO = ("'redirect-url': 'https://www.camisascolombia.com/gracias?ref=' "
               "+ orderData.reference,")
REDIR_NUEVO = ("'redirect-url': 'https://www.camisascolombia.com/gracias?ref=' "
               "+ orderData.reference + '&valor=' + total,")
ORDERID_VIEJO = "var orderId = qs.get('pedido') || qs.get('order') || qs.get('id') || '';"
ORDERID_NUEVO = ("var orderId = qs.get('pedido') || qs.get('order') || qs.get('id') "
                 "|| qs.get('ref') || '';")


def fix_valor(dry):
    n_redir = n_order = 0
    for rel, ruta in paginas():
        s = orig = leer(ruta)
        if REDIR_VIEJO in s:
            s = s.replace(REDIR_VIEJO, REDIR_NUEVO); n_redir += 1
        if ORDERID_VIEJO in s:
            s = s.replace(ORDERID_VIEJO, ORDERID_NUEVO); n_order += 1
        if s != orig and not dry:
            escribir(ruta, s)
    print(f"{'[dry] ' if dry else ''}redirect-url con &valor: {n_redir} archivos")
    print(f"{'[dry] ' if dry else ''}orderId lee ?ref: {n_order} archivos")
    return n_redir, n_order


# --------------------------------------------------------------- parte 2
CFG_ANCLA = "gtag('config', 'G-QZ03N4NWTW');"
# el ancla del contraentrega tiene dos variantes: solo index.html usa el id
# determinista capiEventId, las otras 65 paginas siguen con pedidoId
COD_RE = re.compile(r"console\.log\('Evento Purchase enviado con ID:', "
                    r"(?:capiEventId|pedidoId)\);")
GRACIAS_ANCLA = "    if (window.gtag) {"
MARCA = "google_ads_conversion"


def nl(s):
    """El salto de linea propio del archivo (los HTML del repo son CRLF)."""
    return "\r\n" if "\r\n" in s else "\n"


def aw(send_to, dry):
    n_cfg = n_cod = n_gr = 0
    awid = send_to.split("/")[0]
    for rel, ruta in paginas():
        s = orig = leer(ruta)
        eol = nl(s)

        # a) config de la etiqueta, junto al de GA4, respetando la indentacion
        if CFG_ANCLA in s and awid not in s:
            i = s.index(CFG_ANCLA)
            sangria = s[s.rfind("\n", 0, i) + 1:i]
            s = s.replace(CFG_ANCLA, CFG_ANCLA + eol + sangria +
                          f"gtag('config', '{awid}');", 1)
            n_cfg += 1

        # b) contraentrega: dentro del mismo guard de 24 h que el Purchase de Meta.
        #    El transaction_id se calcula aqui a partir de datos estables (celular +
        #    fecha Bogota) para no depender de cual de las dos variantes tenga el
        #    archivo; pedidoId es nuevo en cada submit y no sirve para deduplicar.
        m = COD_RE.search(s)
        if m and MARCA not in s:
            bloque = [
                m.group(0),
                f"    // ── GOOGLE ADS conversion ({MARCA}) ──",
                "    // Va aqui y NO en /gracias: el contraentrega nunca pasa por",
                "    // /gracias. Comparte el guard de 24 h y el precio real.",
                "    if (typeof gtag !== 'undefined') {",
                "      var _gaTxn = 'cc_' + celSoloNum + '_' + new Date(Date.now() -"
                " 5 * 3600 * 1000).toISOString().slice(0, 10).replace(/-/g, '');",
                "      gtag('set', 'user_data', { phone_number: '+57' + celSoloNum });",
                "      gtag('event', 'conversion', {",
                f"        send_to: '{send_to}',",
                "        value: S.packPrice,",
                "        currency: 'COP',",
                "        transaction_id: _gaTxn",
                "      });",
                "    }",
            ]
            s = s[:m.start()] + eol.join(bloque) + s[m.end():]
            n_cod += 1

        # c) Wompi: en /gracias. value y orderId ya estan en alcance aqui.
        if rel == "gracias.html" and GRACIAS_ANCLA in s and MARCA not in s:
            bloque = [
                GRACIAS_ANCLA,
                f"      // ── GOOGLE ADS conversion ({MARCA}) — ruta Wompi ──",
                "      gtag('event', 'conversion', {",
                f"        send_to: '{send_to}',",
                "        value: value,",
                "        currency: 'COP',",
                "        transaction_id: orderId",
                "      });",
            ]
            s = s.replace(GRACIAS_ANCLA, eol.join(bloque), 1)
            n_gr += 1

        if s != orig and not dry:
            escribir(ruta, s)

    p = "[dry] " if dry else ""
    print(f"{p}config {awid}: {n_cfg} paginas")
    print(f"{p}conversion en submitForm (contraentrega): {n_cod} paginas")
    print(f"{p}conversion en /gracias (Wompi): {n_gr} pagina")
    return n_cfg, n_cod, n_gr


# --------------------------------------------------------------- parte 3
def cambiar_aw(nuevo, dry):
    """Reemplaza el send_to y el AW- ya instalados por los de otra cuenta.

    Sirve si hay que mudarse a una cuenta de Google Ads distinta: no reinserta
    bloques (eso lo hace --aw), solo cambia los identificadores en su sitio.
    """
    nuevo_id = nuevo.split("/")[0]
    viejos = set()
    for _, ruta in paginas():
        for m in re.finditer(r"AW-\d+/[A-Za-z0-9_-]+", leer(ruta)):
            viejos.add(m.group(0))
    viejos.discard(nuevo)
    if not viejos:
        print("No hay ninguna etiqueta AW- instalada que reemplazar.")
        return 0
    if len(viejos) > 1:
        print("Hay mas de un send_to instalado, revisar a mano:", sorted(viejos))
        return 0
    viejo = viejos.pop()
    viejo_id = viejo.split("/")[0]
    n = 0
    for _, ruta in paginas():
        s = orig = leer(ruta)
        s = s.replace(viejo, nuevo).replace(
            f"gtag('config', '{viejo_id}')", f"gtag('config', '{nuevo_id}')")
        if s != orig:
            n += 1
            if not dry:
                escribir(ruta, s)
    print(f"{'[dry] ' if dry else ''}{viejo} -> {nuevo}: {n} paginas")
    return n


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-valor", action="store_true")
    ap.add_argument("--aw", metavar="AW-XXXXXXXXX/etiqueta")
    ap.add_argument("--cambiar-aw", metavar="AW-XXXXXXXXX/etiqueta",
                    help="mudar la etiqueta ya instalada a otra cuenta")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    if not a.fix_valor and not a.aw and not a.cambiar_aw:
        ap.error("elige --fix-valor, --aw o --cambiar-aw")
    if a.fix_valor:
        fix_valor(a.dry)
    if a.cambiar_aw:
        if "/" not in a.cambiar_aw or not a.cambiar_aw.startswith("AW-"):
            sys.exit("El --cambiar-aw debe ser 'AW-XXXXXXXXX/etiqueta'")
        cambiar_aw(a.cambiar_aw, a.dry)
    if a.aw:
        if "/" not in a.aw or not a.aw.startswith("AW-"):
            sys.exit("El --aw debe ser 'AW-XXXXXXXXX/etiqueta' (send_to completo)")
        aw(a.aw, a.dry)
