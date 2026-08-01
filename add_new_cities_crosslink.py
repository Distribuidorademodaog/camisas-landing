# Agrega las 8 ciudades nuevas al modulo "cities-footer-grid" en todas las paginas.
# Idempotente: si una ciudad ya esta enlazada en el nav, no la duplica.
import re
from pathlib import Path

ROOT = Path(__file__).parent

# Ciudades nuevas (slug -> etiqueta con tildes)
NEW = [
    ("armenia", "Armenia"),
    ("monteria", "Montería"),
    ("neiva", "Neiva"),
    ("pasto", "Pasto"),
    ("popayan", "Popayán"),
    ("santa-marta", "Santa Marta"),
    ("valledupar", "Valledupar"),
    ("villavicencio", "Villavicencio"),
]

NAV_RE = re.compile(r'(<nav class="cities-footer-grid"[^>]*>)(.*?)(</nav>)', re.DOTALL)

def process(path):
    html = path.read_text(encoding="utf-8")
    if 'cities-footer-grid' not in html:
        return None
    m = NAV_RE.search(html)
    if not m:
        return ("sin-nav", 0)
    open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
    added = []
    extra = ""
    for slug, label in NEW:
        if f'/camisas-polo-{slug}"' in inner or f'/camisas-polo-{slug}<' in inner:
            continue  # ya esta
        extra += f'      <a href="/camisas-polo-{slug}">{label}</a>\n'
        added.append(slug)
    if not added:
        # aun asi corregir el subtitulo si dice 10
        new_html = html.replace("10 ciudades principales", "18 ciudades principales")
        if new_html != html:
            path.write_text(new_html, encoding="utf-8")
            return ("solo-subtitulo", 0)
        return ("ya-ok", 0)
    # insertar antes del </nav>, respetando que inner suele terminar con indentacion
    new_inner = inner.rstrip("\n ") + "\n" + extra + "    "
    new_block = open_tag + new_inner + close_tag
    new_html = html[:m.start()] + new_block + html[m.end():]
    new_html = new_html.replace("10 ciudades principales", "18 ciudades principales")
    path.write_text(new_html, encoding="utf-8")
    return ("actualizado", len(added))

def main():
    files = sorted(ROOT.glob("*.html"))
    tot = 0
    for f in files:
        r = process(f)
        if r is None:
            continue
        status, n = r
        if status == "actualizado":
            tot += 1
            print(f"  [+{n}] {f.name}")
        elif status in ("solo-subtitulo",):
            print(f"  [txt] {f.name}")
        elif status == "sin-nav":
            print(f"  [!!] sin nav: {f.name}")
    print(f"\n[OK] {tot} paginas actualizadas con las 8 ciudades nuevas")

if __name__ == "__main__":
    main()
