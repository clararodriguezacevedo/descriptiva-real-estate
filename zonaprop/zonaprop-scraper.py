import re
import time
import sys
import os
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright


# ─── Helpers ────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def clean_text(text):
    if not text:
        return "N/A"
    text = text.replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_address(address_raw):
    calle = altura = piso = "N/A"
    if not address_raw or address_raw == "N/A":
        return calle, altura, piso
    try:
        address_raw = re.sub(r'[Pp]iso\s*', '', address_raw)
        match = re.search(r'^(.*?)\s+(\d+)(?:,\s*(.*))?$', address_raw.strip())
        if match:
            calle  = match.group(1).strip()
            altura = match.group(2).strip()
            piso   = match.group(3).strip() if match.group(3) else "0"
        else:
            calle = address_raw.strip()
    except Exception:
        pass
    return calle, altura, piso


def parse_price(price_text):
    if not price_text:
        return "Consultar", "N/A"
    price_text = clean_text(price_text)
    p_match = re.search(r'(USD|ARS|\$)\s*[\d.,]+', price_text, re.IGNORECASE)
    precio = p_match.group(0) if p_match else "Consultar"
    e_match = re.search(r'\+\s*[\$ARS\s]*([\d.,]+)', price_text, re.IGNORECASE)
    expensas = e_match.group(0).strip() if e_match else "N/A"
    return precio, expensas


def extract_smart_features(row):
    texto = " ".join([
        str(row.get('Descripción',    '')),
        str(row.get('Detalles',       '')),
        str(row.get('Caracteristicas', '')),
    ]).lower()

    return pd.Series({
        "Amenities":         1 if any(x in texto for x in [
            "amenities", "piscina", "pileta", "sum", "parrilla",
            "gym", "gimnasio", "sauna", "laundry", "quincho"]) else 0,
        "Losa_Central":      1 if any(x in texto for x in [
            "losa radiante", "calefacción central", "caldera central", "piso radiante"]) else 0,
        "Aire_Acond":        1 if any(x in texto for x in [
            "aire acondicionado", "split", " a/c", "frío-calor"]) else 0,
        "Apto_Credito":      1 if any(x in texto for x in [
            "apto crédito", "apto credito", "apto cr"]) else 0,
        "Cochera":           1 if any(x in texto for x in [
            "cochera", "coch.", "coch ", "espacio guarda coche", "estacionamiento"]) else 0,
        "Seguridad":         1 if any(x in texto for x in [
            "vigilancia", "seguridad 24", "tótem", "totem", "encargado"]) else 0,
        "Luminoso":          1 if any(x in texto for x in [
            "luminoso", "todo luz", "vista abierta", "vista panorámica"]) else 0,
        "Balcon_Aterrazado": 1 if any(x in texto for x in [
            "aterrazado", "balcón terraza", "terraza", "balcón"]) else 0,
    })


# ─── Detail page scraper (requests + BeautifulSoup) ─────────────────────────

def _extract_aviso_info(soup):
    """
    ZonaProp embeds all listing data as a JS object: const avisoInfo = { ... }
    Parse it to get generalFeatures and other structured data.
    """
    for script in soup.find_all("script"):
        src = script.string or ""
        if "avisoInfo" not in src or "generalFeatures" not in src:
            continue
        # Pull out the generalFeatures value (it's a JS object, close enough to JSON)
        m = re.search(r"'generalFeatures':\s*(\{.*?\})\s*,\s*\n", src, re.DOTALL)
        if m:
            try:
                gf = json.loads(m.group(1))
                labels = []
                for _category, items in gf.items():
                    for _item_id, item in items.items():
                        label = item.get("label", "")
                        value = item.get("value")
                        labels.append(f"{label}: {value}" if value else label)
                return " | ".join(labels)
            except Exception:
                pass
        # Fallback: grab all feature labels from the rendered HTML section
        break
    return "N/A"


def scrape_detail(url):
    """
    Fetch a ZonaProp listing page with requests and extract:
      - description  (SSR in #longDescription)
      - caracteristicas (from avisoInfo.generalFeatures JS object)
      - published_days_ago, views (from #user-views)
    Returns a dict.
    """
    clean_url = url.split("?")[0]   # strip tracking params
    result = {
        "Descripción":     "Sin descripción",
        "Caracteristicas": "N/A",
        "Publicado":       "N/A",
        "Visualizaciones": None,
    }
    try:
        r = requests.get(clean_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.content, "lxml")

        # ── Description ───────────────────────────────────────────────────
        long_desc = soup.find("div", id="longDescription")
        if long_desc:
            txt = clean_text(long_desc.get_text(" ", strip=True))
            # Strip the "Leer descripción completa" button text if present
            txt = re.sub(r"Leer descripci[oó]n completa.*", "", txt, flags=re.IGNORECASE).strip()
            if len(txt) > 20:
                result["Descripción"] = txt

        # ── Structured features (from JS avisoInfo object) ────────────────
        result["Caracteristicas"] = _extract_aviso_info(soup)

        # ── Published / views (from #user-views section) ──────────────────
        user_views = soup.find("div", id="user-views")
        if user_views:
            for p in user_views.find_all("p"):
                text = p.get_text(strip=True)
                if "Publicado hace" in text:
                    result["Publicado"] = text
                elif "visualizaciones" in text:
                    m = re.search(r"\d+", text)
                    result["Visualizaciones"] = int(m.group()) if m else None

        # ── Icon features (m², amb., dorm., etc.) from #section-icon-features-property ──
        feature_list = soup.find("ul", id="section-icon-features-property")
        if feature_list:
            for li in feature_list.find_all("li", class_="icon-feature"):
                icon = li.find("i")
                value = re.search(r"[\d]+", li.get_text(strip=True))
                if icon and value:
                    result[icon["class"][0]] = value.group()

    except Exception as e:
        print(f"    [detail error] {e}")

    return result


# ─── Main scraper ────────────────────────────────────────────────────────────

class ZonapropScraper:

    def _generate_urls(self, base_url, count):
        base_clean = re.sub(r"\.html$", "", base_url)
        base_clean = re.sub(r"-pagina-\d+", "", base_clean)
        return [
            f"{base_clean}.html" if i == 1 else f"{base_clean}-pagina-{i}.html"
            for i in range(1, count + 1)
        ]

    def scrape(self, base_url: str, max_pages: int = 5):
        all_results = []
        seen_ids = set()
        target_urls = self._generate_urls(base_url, max_pages)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context(user_agent=HEADERS["User-Agent"])
            list_page = context.new_page()
            list_page.route("**/*.{png,jpg,jpeg,webp,woff,woff2}", lambda r: r.abort())

            for url in target_urls:
                print(f"\n--- Scrapeando listado: {url} ---")
                try:
                    list_page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    for _ in range(3):
                        list_page.mouse.wheel(0, 2000)
                        list_page.wait_for_timeout(800)
                    list_page.wait_for_selector("div[data-qa='posting PROPERTY']", timeout=15000)
                    cards = list_page.query_selector_all("div[data-qa='posting PROPERTY']")
                    nuevos = 0

                    for card in cards:
                        try:
                            link_el = card.query_selector("h2[data-qa='POSTING_CARD_DESCRIPTION'] a")
                            if not link_el:
                                continue
                            href = link_el.get_attribute("href") or ""
                            id_match = re.search(r"-(\d+)\.html", href)
                            listing_id = id_match.group(1) if id_match else href
                            if listing_id in seen_ids:
                                continue

                            full_url = (
                                f"https://www.zonaprop.com.ar{href}"
                                if not href.startswith("http") else href
                            )

                            # ── Card-level data ────────────────────────────
                            price_el = card.query_selector("[data-qa='POSTING_CARD_PRICE']")
                            exp_el   = card.query_selector("[data-qa='expensas']")
                            precio, _ = parse_price(price_el.inner_text() if price_el else "")
                            expensas  = clean_text(exp_el.inner_text()) if exp_el else "N/A"

                            addr_el = (
                                card.query_selector("h4.postingLocations-module__location-address") or
                                card.query_selector("[data-qa='POSTING_CARD_LOCATION']")
                            )
                            calle, altura, piso = parse_address(
                                clean_text(addr_el.inner_text()) if addr_el else "N/A"
                            )

                            loc_el    = card.query_selector("[data-qa='POSTING_CARD_LOCATION']")
                            ubicacion = clean_text(loc_el.inner_text()) if loc_el else "N/A"

                            feat_el  = card.query_selector("[data-qa='POSTING_CARD_FEATURES']")
                            detalles = clean_text(
                                " | ".join(s.inner_text() for s in feat_el.query_selector_all("span"))
                            ) if feat_el else "N/A"

                            # ── Detail page (requests, much faster) ────────
                            print(f"  -> {calle} {altura} … obteniendo ficha")
                            detail = scrape_detail(full_url)

                            seen_ids.add(listing_id)
                            nuevos += 1
                            all_results.append({
                                "Precio":          precio,
                                "Expensas":        expensas,
                                "Calle":           calle,
                                "Altura":          altura,
                                "Piso":            piso,
                                "Ubicacion":       ubicacion,
                                "Detalles":        detalles,
                                "Caracteristicas": detail["Caracteristicas"],
                                "Descripción":     detail["Descripción"],
                                "Publicado":       detail["Publicado"],
                                "Visualizaciones": detail["Visualizaciones"],
                                "Link":            full_url,
                            })

                        except Exception as e:
                            print(f"    [card error] {e}")
                            continue

                    print(f"Nuevos: {nuevos} | Total: {len(all_results)}")
                    if nuevos == 0 and len(seen_ids) > 0:
                        print("No hay más resultados.")
                        break
                    context.clear_cookies()

                except Exception as e:
                    print(f"Error en {url}: {e}")
                    continue

            browser.close()

        return all_results


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python zonaprop_scraper.py \"<URL>\" [max_paginas]")
        sys.exit(1)

    url       = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    scraper = ZonapropScraper()
    results = scraper.scrape(url, max_pages)

    if not results:
        print("⚠️ No se obtuvieron datos.")
        sys.exit(0)

    df = pd.DataFrame(results)
    features_df = df.apply(extract_smart_features, axis=1)
    df = pd.concat([df, features_df], axis=1)

    os.makedirs("output", exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename  = f"output/zonaprop_{timestamp}.tsv"
    df.to_csv(filename, sep='\t', index=False, encoding='utf-8-sig')

    print(f"\n✅ Archivo guardado en: {filename}")
    print(df[["Precio", "Calle", "Caracteristicas", "Amenities", "Aire_Acond", "Seguridad"]].head(10).to_string())