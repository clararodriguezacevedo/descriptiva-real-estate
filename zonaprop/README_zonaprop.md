# 🏠 Scrapper ZonaProp — Departamentos CABA

Extrae listings de departamentos de [zonaprop.com.ar](https://www.zonaprop.com.ar) y los guarda como archivo TSV listo para análisis en pandas o Excel.

---

## Requisitos

```bash
pip install curl_cffi beautifulsoup4 pandas
```

> **¿Por qué `curl_cffi` y no `requests`?**
> ZonaProp analiza la "firma TLS" de cada conexión entrante. La librería `requests` estándar tiene una firma distinta a la de un navegador real, lo que ZonaProp detecta y bloquea con HTTP 403. `curl_cffi` con `impersonate="chrome120"` replica exactamente el handshake TLS de Chrome 120, haciendo la conexión indistinguible de la de un usuario real.

---

## Uso

```python
df = run_scrapper_zonaprop(
    enlace    = "https://www.zonaprop.com.ar/departamentos-venta-capital-federal",
    operacion = "venta",
    max_pages = 10,
)
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `enlace` | str | — | URL base del listado **sin** `.html` al final |
| `operacion` | str | — | Etiqueta para el archivo de salida: `"venta"`, `"alquiler"`, `"temporal"` |
| `max_pages` | int | 3 | Número máximo de páginas a scrapear |

### URLs de ejemplo

```python
# Departamentos en venta
enlace = "https://www.zonaprop.com.ar/departamentos-venta-capital-federal"

# Departamentos en alquiler
enlace = "https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal"

# Alquiler temporario (inmuebles en general)
enlace = "https://www.zonaprop.com.ar/inmuebles-alquiler-temporal-capital-federal"

# Filtro por barrio
enlace = "https://www.zonaprop.com.ar/departamentos-venta-palermo"
```

> **Importante**: pasá la URL **sin** `.html`. El scrapper lo agrega automáticamente y construye las páginas siguientes como `{base}-pagina-2.html`, `{base}-pagina-3.html`, etc.

---

## Output

Se genera un archivo `.tsv` en la carpeta `output/` con el nombre:

```
output/zonaprop_{operacion}_{timestamp}.tsv
```

### Columnas del DataFrame

| Campo | Descripción |
|---|---|
| `Fecha_Scraping` | Fecha de ejecución (YYYY-MM-DD) |
| `Posting_ID` | ID único del aviso (atributo `data-id` del card) |
| `Sito` | Siempre `'zonaprop'` |
| `Operación` | Valor del parámetro `operacion` |
| `Precio` | Precio publicado (ej: `USD 120.000`) |
| `Expensas` | Expensas mensuales si figuran en el aviso |
| `Calle` | Nombre de la calle (title case) |
| `Altura` | Número de puerta |
| `Piso` | Piso del departamento cuando figura |
| `Barrio` | Barrio de CABA (primer fragmento del campo ubicación) |
| `Detalles` | m², ambientes, baños (texto libre) |
| `Descripción` | Descripción del aviso (texto libre) |
| `Link` | URL completa del aviso |
| `Amenities` | Conteo de amenities mencionados (0, 1, 2, ...) |
| `Losa_Central` | 1 si menciona losa/calefacción central |
| `Aire_Acond` | 1 si menciona aire acondicionado o split |
| `Apto_Credito` | 1 si es apto crédito |
| `Cochera` | 1 si incluye cochera o estacionamiento |
| `Seguridad` | 1 si menciona vigilancia, portero o cámaras |
| `Luminoso` | 1 si menciona luminosidad o vista abierta |
| `Balcon_Aterrazado` | 1 si tiene balcón o terraza |

---

## Notas técnicas

- **Anti-bot**: usa `curl_cffi` con `impersonate="chrome120"` para replicar el fingerprint TLS de Chrome. No requiere Playwright ni navegador headless.
- **Paginación**: `{base}.html` para página 1, `{base}-pagina-N.html` para páginas siguientes.
- **Deduplicación**: por URL del link. Un mismo aviso no se guarda dos veces aunque aparezca en múltiples páginas.
- **Delay**: 2 segundos entre páginas (más conservador que Argenprop por las protecciones del sitio).
- **Encoding**: UTF-8 con BOM (`utf-8-sig`) para compatibilidad con Excel y Google Sheets.
- **parse_address()**: maneja casos complejos de ZonaProp como `"Bolivia al 4400"`, nombres de edificio con guión (`"Alvear Tower - Azucena Villaflor"` → `None`), años históricos en nombres de calle (`"11 de Septiembre de 1888 2231"`) y pisos inline (`"Junín 1615 piso 13"`).

---

## Diferencias con el scrapper de Argenprop

| Aspecto | Argenprop | ZonaProp |
|---|---|---|
| Librería HTTP | `requests` | `curl_cffi` |
| Protección anti-bot | User-Agent alcanza | Requiere fingerprint TLS completo |
| Selector de cards | `div.listing__item` | `div[data-qa="posting PROPERTY"]` |
| Posting ID | atributo `id` | atributo `data-id` |
| Paginación | `?pagina-2` | `-pagina-2.html` |
| Delay entre páginas | 1.5 s | 2 s |
