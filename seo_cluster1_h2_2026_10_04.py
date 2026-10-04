"""
Añade una sección "También buscado en {ciudad}" en todas las páginas de ciudad
con H2s ricos en keywords del Clúster 1 del Plan SEO (ciudad + característica).

Se inserta justo ANTES de la sección FAQ (<!-- ═══════ FAQ ═══════ -->).
Idempotente: no re-inserta si ya existe el marcador.
"""
import re
from pathlib import Path

ROOT = Path("/home/user/camisas-landing")
MARKER = "<!-- SEO-CLUSTER1-H2 -->"
FAQ_MARKER = "<!-- ═══════ FAQ ═══════ -->"

# Mapeo slug -> nombre bonito (coincide con los <title>/<h1> existentes)
CITY_PRETTY = {}
# Extraer nombres bonitos de los títulos existentes
TITLE_RE = re.compile(r"<title>Camisas Polo Hombre ([^|<]+?)\s*[|·]", re.IGNORECASE)

def pretty_name(slug: str, html: str) -> str:
    m = TITLE_RE.search(html)
    if m:
        return m.group(1).strip()
    # Fallback: capitalize slug
    return slug.replace("-", " ").title()


def build_section(city_name: str) -> str:
    """Sección HTML con H2s ricos en keywords de Clúster 1."""
    return f"""
  {MARKER}
  <!-- ═══════ TAMBIÉN BUSCADO EN {city_name.upper()} ═══════ -->
  <div class="sec sec-light" style="padding:36px 0 28px;">
    <div class="sec-head" style="padding-bottom:0;">
      <div class="sec-kicker kicker-gold">También buscado en {city_name}</div>
      <h2 class="sec-title sec-title-light" style="font-size:24px;">Lo que más piden<br><em>los hombres de {city_name}</em></h2>
    </div>
    <div style="padding:16px 24px 0; display:grid; grid-template-columns:1fr; gap:14px;">
      <div style="padding:14px 16px; border:1px solid rgba(0,0,0,0.08); border-radius:10px; background:#fff;">
        <h3 style="font-family:'Outfit',sans-serif; font-size:14px; font-weight:600; color:var(--navy); margin-bottom:4px;">Camisas polo manga larga en {city_name}</h3>
        <p style="font-family:'Outfit',sans-serif; font-size:12.5px; color:#4a5568; line-height:1.5;">Para los días más frescos y oficinas con aire acondicionado — mismo tallaje S a 5XL, pago contraentrega al llegar a tu dirección.</p>
      </div>
      <div style="padding:14px 16px; border:1px solid rgba(0,0,0,0.08); border-radius:10px; background:#fff;">
        <h3 style="font-family:'Outfit',sans-serif; font-size:14px; font-weight:600; color:var(--navy); margin-bottom:4px;">Camisas polo tallas grandes en {city_name}</h3>
        <p style="font-family:'Outfit',sans-serif; font-size:12.5px; color:#4a5568; line-height:1.5;">Tallas XXL, 3XL, 4XL y 5XL siempre en stock. Tallaje colombiano real para hombres de contextura grande en {city_name}.</p>
      </div>
      <div style="padding:14px 16px; border:1px solid rgba(0,0,0,0.08); border-radius:10px; background:#fff;">
        <h3 style="font-family:'Outfit',sans-serif; font-size:14px; font-weight:600; color:var(--navy); margin-bottom:4px;">Camisas polo contraentrega en {city_name}</h3>
        <p style="font-family:'Outfit',sans-serif; font-size:12.5px; color:#4a5568; line-height:1.5;">Pagas solo cuando el domiciliario toca tu puerta y revisas la camisa. Cero anticipos, cero riesgo. Entrega 1-3 días en {city_name}.</p>
      </div>
      <div style="padding:14px 16px; border:1px solid rgba(0,0,0,0.08); border-radius:10px; background:#fff;">
        <h3 style="font-family:'Outfit',sans-serif; font-size:14px; font-weight:600; color:var(--navy); margin-bottom:4px;">Camisas polo hombre {city_name} precio</h3>
        <p style="font-family:'Outfit',sans-serif; font-size:12.5px; color:#4a5568; line-height:1.5;">Desde $86.000 por camisa en pack. Envío gratis a todo {city_name}. Más de 20 colores y 4 estilos disponibles ahora.</p>
      </div>
      <div style="padding:14px 16px; border:1px solid rgba(0,0,0,0.08); border-radius:10px; background:#fff;">
        <h3 style="font-family:'Outfit',sans-serif; font-size:14px; font-weight:600; color:var(--navy); margin-bottom:4px;">Dónde comprar camisas polo en {city_name}</h3>
        <p style="font-family:'Outfit',sans-serif; font-size:12.5px; color:#4a5568; line-height:1.5;">Compra online con despacho directo a tu dirección. Soporte por WhatsApp durante todo el proceso de pedido en {city_name}.</p>
      </div>
    </div>
  </div>

"""


def process_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return False  # ya procesado
    if FAQ_MARKER not in html:
        return False  # no se puede ubicar FAQ

    city_name = pretty_name(path.stem.replace("camisas-polo-", ""), html)
    section = build_section(city_name)
    new_html = html.replace(FAQ_MARKER, section + "  " + FAQ_MARKER, 1)
    path.write_text(new_html, encoding="utf-8")
    return True


def main():
    files = sorted(ROOT.glob("camisas-polo-*.html"))
    # Filtra: solo páginas de ciudad (no color/estilo/categoría)
    EXCLUDE_SUFFIXES = {
        "colores-hombre", "para-senores-hombre", "100-algodon-hombre",
        "manga-larga-contraentrega", "manga-corta-hombre",
        "oxford-hombre-colombia", "oxford-100-algodon",
        "azules-hombre", "azul-marino-hombre", "beige-hombre",
        "blancas-hombre", "celestes-hombre", "grises-hombre",
        "negras-hombre", "rojas-hombre", "verdes-hombre",
        "vinotinto-hombre", "cuadros-hombre", "baratas-colombia",
        "juveniles-hombre", "por-mayor-colombia", "premium-colombia",
    }
    done = 0
    skipped = 0
    for p in files:
        slug = p.stem.replace("camisas-polo-", "")
        if slug in EXCLUDE_SUFFIXES:
            continue
        if process_file(p):
            done += 1
            print(f"  OK: {p.name}")
        else:
            skipped += 1
    print(f"\n[OK] {done} city pages updated with Cluster 1 keyword H3s. {skipped} skipped.")


if __name__ == "__main__":
    main()
