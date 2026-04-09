# ZonaProp Scraper

Scrapes property listings from ZonaProp and exports them as a TSV file.

## How it works

- **Listing pages** are scraped with Playwright (cards are JavaScript-rendered)
- **Detail pages** are fetched with requests + BeautifulSoup (description is server-side rendered, structured features are parsed from an embedded JSON object)

This hybrid approach keeps things fast — detail pages take ~1s each instead of ~10s with a headless browser.

## Setup

```bash
pip install curl_cffi beautifulsoup4 pandas
```

## Usage

```bash
python zonaprop_scraper.py "<URL>" [max_pages]
```

**Arguments:**
- `enlace` — ZonaProp search results page (required)
- `operacion` — type of transaction (venta, alquiler or alquiler temporal)
- `max_pages` — number of pages to scrape (optional, default: 5)

**Example:**
```bash
python zonaprop_scraper.py "https://www.zonaprop.com.ar/departamentos-venta-capital-federal.html" 3
```

## Output

A TSV file saved to `output/zonaprop_operacion_YYYYMMDD_HHMMSS.tsv` with the following columns:

| Column | Description |
|---|---|
| Precio | Listing price |
| Expensas | Monthly expenses |
| Calle | Street name |
| Altura | Street number |
| Piso | Floor |
| Barrio | Neighbourhood |
| Detalles | Features from card (m², rooms, etc.) |
| Descripción | Full listing description |
| Link | URL of the listing |
| Amenities | Binary: pool, gym, SUM, parrilla, etc. |
| Losa_Central | Binary: central heating |
| Aire_Acond | Binary: air conditioning |
| Apto_Credito | Binary: mortgage eligible |
| Cochera | Binary: parking |
| Seguridad | Binary: security/doorman |
| Luminoso | Binary: bright/open views |
| Balcon_Aterrazado | Binary: terrace or balcony |