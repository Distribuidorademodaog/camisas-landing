# -*- coding: utf-8 -*-
"""
IndexNow para camisascolombia.com — avisa a Bing, Yandex, Seznam y Naver.

Por que aqui y por que importa: Bing tiene el sitio MEJOR que Google. Medido el
2026-10-11 con la API de Bing Webmaster:

    Bing     104 paginas en el indice, rastrea 19-51 al dia
    Google    82 paginas, mediana de 21 dias desde el ultimo rastreo

Y las 439 consultas que dan impresiones en Bing no son busquedas, son prompts
(«mejor marca de camisas polo en colombia para absorber…», «¿que es mejor,
algodon o pique?»): es la capa de recuperacion de ChatGPT y Copilot, que se
apoyan en el indice de Bing. Ese es el canal donde este sitio ya va primero
(ChatGPT lo cita en 5 de 5 respuestas), asi que avisar a Bing al instante vale
mas aqui que en ningun otro sitio del catalogo.

**IndexNow no tiene cuota**, al contrario que la Indexing API de Google, que se
agota antes de mediodia peleada entre todos los proyectos y que el 7-oct dejo 41
URLs de este sitio en 429.

La clave vive en `<clave>.txt` en la raiz del repo, asi que **sobrevive a
cualquier redespliegue de Vercel** — el fallo tipico es subirla a mano y perderla
en el siguiente build.

🚨 El primer envio SIEMPRE da 403 `SiteVerificationNotCompleted`: Bing todavia no
ha ido a buscar el fichero de clave. Un envio simple por GET lo dispara y acto
seguido el POST del lote pasa. Este script lo hace solo.

⚠️ Un 200 confirma RECEPCION, no indexacion. El resultado se mira en Bing
Webmaster Tools (GetCrawlStats), y sus datos van ~6 dias por detras.

Uso:
    python indexnow.py                 # todas las URLs del sitemap
    python indexnow.py url1 url2 ...   # solo esas
    python indexnow.py --dry-run
"""
import glob
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HOST = "www.camisascolombia.com"
BASE = "https://" + HOST
SITEMAP = "sitemap.xml"
ENDPOINTS = ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]
UA = "Mozilla/5.0 (compatible; camisascolombia-indexnow/1.0)"


def clave():
    """La clave es el nombre del unico <hex>.txt de la raiz del repo."""
    cands = [f for f in glob.glob("*.txt")
             if re.fullmatch(r"[0-9a-f]{8,128}\.txt", os.path.basename(f))]
    if len(cands) != 1:
        raise SystemExit("!! esperaba UN fichero <clave>.txt en la raiz, hay %d: %s"
                         % (len(cands), cands))
    k = os.path.basename(cands[0])[:-4]
    contenido = io.open(cands[0], encoding="utf-8").read()
    if contenido != k:
        raise SystemExit("!! %s debe contener EXACTAMENTE la clave y nada mas "
                         "(tiene %d bytes, esperaba %d)" % (cands[0], len(contenido), len(k)))
    return k


def comprobar_fichero(k):
    """El fichero tiene que estar servido y devolver exactamente la clave."""
    url = "%s/%s.txt" % (BASE, k)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30)
        cuerpo = r.read().decode("utf-8", "replace").strip()
        tipo = r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        raise SystemExit("!! %s devuelve %s — despliega el fichero antes de enviar" % (url, e.code))
    if cuerpo != k:
        raise SystemExit("!! %s devuelve %r, esperaba la clave" % (url, cuerpo[:40]))
    print("  clave servida OK en %s  (%s)" % (url, tipo))
    return url


def urls_sitemap():
    s = io.open(SITEMAP, encoding="utf-8").read()
    us = re.findall(r"<loc>([^<]+)</loc>", s)
    return [u for u in us if not re.search(r"\.(webp|jpg|jpeg|png|gif|svg)$", u, re.I)]


def enviar(k, keyloc, urls, dry):
    cuerpo = {"host": HOST, "key": k, "keyLocation": keyloc, "urlList": urls}
    data = json.dumps(cuerpo).encode()
    for ep in ENDPOINTS:
        if dry:
            print("  (DRY-RUN) %s  %d URLs" % (ep, len(urls)))
            continue
        code, texto = _post(ep, data)
        # 403 en el primer envio = Bing aun no ha leido el fichero de clave.
        # Un GET simple lo dispara; despues el POST del lote pasa.
        if code == 403:
            print("  %s -> 403 (verificacion pendiente), disparando GET y reintentando" % ep)
            g = "%s?url=%s&key=%s&keyLocation=%s" % (ep, urls[0], k, keyloc)
            try:
                gr = urllib.request.urlopen(urllib.request.Request(g, headers={"User-Agent": UA}), timeout=30)
                print("     GET -> %s" % gr.getcode())
            except urllib.error.HTTPError as e:
                print("     GET -> %s" % e.code)
            time.sleep(4)
            code, texto = _post(ep, data)
        print("  %-42s -> %s %s" % (ep, code, (texto or "")[:90]))


def _post(ep, data):
    req = urllib.request.Request(ep, data=data, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8",
                                          "User-Agent": UA})
    try:
        r = urllib.request.urlopen(req, timeout=60)
        return r.getcode(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return "ERR", str(e)[:120]


def main():
    dry = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    k = clave()
    print("clave: %s" % k)
    keyloc = comprobar_fichero(k)

    urls = args or urls_sitemap()
    # IndexNow devuelve 422 si alguna URL no es del mismo host
    malas = [u for u in urls if not u.startswith(BASE + "/") and u != BASE + "/"]
    if malas:
        raise SystemExit("!! %d URLs no son de %s, p.ej. %s" % (len(malas), HOST, malas[0]))
    if len(urls) > 10000:
        raise SystemExit("!! %d URLs, el maximo por peticion es 10.000" % len(urls))
    print("  %d URLs%s" % (len(urls), "  (del sitemap)" if not args else ""))
    enviar(k, keyloc, urls, dry)
    print("\n%s" % ("(DRY-RUN)" if dry else
          "enviado. El resultado se mira en Bing Webmaster (GetCrawlStats), "
          "y sus datos van ~6 dias por detras."))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
