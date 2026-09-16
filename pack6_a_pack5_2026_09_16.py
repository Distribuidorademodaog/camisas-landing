# -*- coding: utf-8 -*-
"""
El pack de 6 camisas pasa a pack de 5 por $430.000 — 2026-09-16.

Decision del negocio. Numeros derivados (aritmetica, no opinion):

                     pack de 6 (antes)   pack de 5 (ahora)
    precio               $495.000           $430.000
    por camisa            $82.500            $86.000     (430.000 / 5)
    referencia x115.000  $690.000           $575.000     (5 x 115.000)
    ahorro               $195.000           $145.000     (575.000 - 430.000)

El "$82.500" es ademas el "Desde ..." de titles, hero, descriptions, schema
AggregateOffer (lowPrice) y FAQs de todo el sitio, asi que el cambio es
transversal: medido antes de tocar, ~1.550 ocurrencias en 68 paginas.

Que se toca (solo en contexto de pack; los "3 a 6 dias" de entrega NO):
  - importes: 495.000/495000, 82.500/82500, 195.000/195000, 690.000/690000
  - cantidad: "Pack Pro - 6 Camisas", "CC-PACK-6", ">6 Camisas<", "pack de 6",
    "6 camisas", "seis camisas", data-pack-qty="6", pickPack(this,6,...),
    openCheckoutWithPack(6, ...), S.pack = '6 camisas', txt.includes('495')

Fuera de este script (se cambian aparte): la app movil (src/data/content.ts)
y pedidos-analyzer (ventas.py, reportes.py, guias.py).

Uso:  python pack6_a_pack5_2026_09_16.py [--dry-run]
"""
import glob
import io
import os
import re
import sys

# Orden: primero los importes (con \b para no pisar telefonos ni otros
# numeros), despues las cantidades en contexto de pack.
REGLAS = [
    (r"\b495\.000\b", "430.000"), (r"\b495000\b", "430000"),
    (r"\b82\.500\b",  "86.000"),  (r"\b82500\b",  "86000"),
    (r"\b195\.000\b", "145.000"), (r"\b195000\b", "145000"),
    (r"\b690\.000\b", "575.000"), (r"\b690000\b", "575000"),

    (r"Pack Pro - 6 Camisas", "Pack Pro - 5 Camisas"),
    (r"CC-PACK-6", "CC-PACK-5"),
    (r">6 Camisas<", ">5 Camisas<"),
    (r'data-pack-qty="6"', 'data-pack-qty="5"'),
    (r"pickPack\(this,\s*6,", "pickPack(this,5,"),
    (r"openCheckoutWithPack\(6,", "openCheckoutWithPack(5,"),
    (r"txt\.includes\('495'\)", "txt.includes('430')"),
    (r"S\.pack = '6 camisas'", "S.pack = '5 camisas'"),
    (r"S\.packQty = 6\b", "S.packQty = 5"),

    (r"\b[Pp]ack de 6 camisas\b", lambda m: m.group(0)[0] + "ack de 5 camisas"),
    (r"\b[Pp]ack de seis camisas\b", lambda m: m.group(0)[0] + "ack de cinco camisas"),
    (r"\b[Pp]ack de 6\b(?! d[ií]as)", lambda m: m.group(0)[0] + "ack de 5"),
    (r"\b[Pp]ack de seis\b", lambda m: m.group(0)[0] + "ack de cinco"),
    (r"\b[Pp]acks de 6\b", lambda m: m.group(0)[0] + "acks de 5"),
    (r"\b6 camisas\b", "5 camisas"),
    (r"\b[Ss]eis camisas\b", lambda m: m.group(0)[0].replace("S", "C").replace("s", "c") + "inco camisas"),
    (r"\bseis polos\b", "cinco polos"),
    (r"\b6 polos\b", "5 polos"),
]

# Vigilancia: nada de esto debe cambiar
CENTINELAS = [r"\b[1-3] a 6 d[ií]as", r"\b6 d[ií]as", r"\bde 1 a 6\b", r"\b3 y 6\b"]


def main():
    dry = "--dry-run" in sys.argv
    pgs = sorted(set(p.replace(os.sep, "/") for p in
                 glob.glob("*.html") + glob.glob("blog/*.html") + glob.glob("guias/*.html")))
    cuenta = {}
    tocados = 0
    cent_antes = cent_despues = 0
    for f in pgs:
        h = io.open(f, encoding="utf-8").read()
        orig = h
        cent_antes += sum(len(re.findall(c, h)) for c in CENTINELAS)
        for pat, rep in REGLAS:
            h, n = re.subn(pat, rep, h)
            if n:
                cuenta[pat] = cuenta.get(pat, 0) + n
        cent_despues += sum(len(re.findall(c, h)) for c in CENTINELAS)
        if h != orig:
            tocados += 1
            if not dry:
                io.open(f, "w", encoding="utf-8", newline="").write(h)
    print("%-42s %5s" % ("patron", "n"))
    for pat, n in sorted(cuenta.items(), key=lambda x: -x[1]):
        print("%-42s %5d" % (pat[:41], n))
    print("\narchivos tocados: %d   reemplazos: %d" % (tocados, sum(cuenta.values())))
    print("plazos de entrega con '6' antes/despues: %d / %d %s"
          % (cent_antes, cent_despues, "OK" if cent_antes == cent_despues else "!! CAMBIARON"))
    if cent_antes != cent_despues:
        raise SystemExit(1)
    # nada del pack de 6 puede sobrevivir
    if not dry:
        resto = 0
        for f in pgs:
            h = io.open(f, encoding="utf-8").read()
            resto += len(re.findall(r"\b495\.?000\b|\b82\.?500\b|CC-PACK-6|Pack Pro - 6|pack de 6 camisas", h))
        print("restos del pack de 6:", resto)
    print("\n%s" % ("(DRY-RUN, no se escribio)" if dry else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
