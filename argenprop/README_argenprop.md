# 🏠 Scrapper Argenprop — Departamentos CABA

Extrae listings de departamentos de [argenprop.com](https://www.argenprop.com) y los guarda como archivo TSV listo para análisis en pandas o Excel.

---

## Requisitos

```bash
pip install requests beautifulsoup4 pandas
```

---

## Uso

```python
df = run_scrapper_argenprop(
    enlace    = "https://www.argenprop.com/departamentos/venta/capital-federal",
    operacion = "venta",
    max_pages = 50,       # cuántas páginas scrapear (~20 propiedades por página)
    start_page = 1,       # desde qué página arrancar (útil para reanudar)
)
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `enlace` | str | — | URL base del listado de Argenprop |
| `operacion` | str | — | Etiqueta para el archivo de salida: `"venta"`, `"alquiler"`, `"temporal"` |
| `max_pages` | int | 3 | Número máximo de páginas a scrapear |
| `start_page` | int | 1 | Página desde la que arrancar (para reanudar una corrida cortada) |
| `initial_data` | list | None | Lista de registros de una corrida anterior (para concatenar) |
| `initial_seen` | set | None | Set de links ya vistos en una corrida anterior (evita duplicados) |

### URLs de ejemplo

```python
# Departamentos en venta
enlace = "https://www.argenprop.com/departamentos/venta/capital-federal"

# Departamentos en alquiler
enlace = "https://www.argenprop.com/departamentos/alquiler/capital-federal"

# Alquiler temporario
enlace = "https://www.argenprop.com/departamentos/alquiler-temporal/capital-federal"
```

---

## Output

Se genera un archivo `.tsv` en la carpeta `output/` con el nombre:

```
output/argenprop_{operacion}_{timestamp}.tsv
```

### Columnas del DataFrame

| Campo | Descripción |
|---|---|
| `Fecha_Scraping` | Fecha de ejecución (YYYY-MM-DD) |
| `Posting_ID` | ID único del aviso en Argenprop |
| `Sito` | Siempre `'argenprop'` |
| `Operación` | Valor del parámetro `operacion` |
| `Precio` | Precio publicado (ej: `USD 85.000`) |
| `Expensas` | Expensas mensuales si figuran en el aviso |
| `Calle` | Nombre de la calle (title case) |
| `Altura` | Número de puerta |
| `Piso` | Piso del departamento cuando figura |
| `Barrio` | Barrio de CABA |
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

## Manejo de CAPTCHA

Argenprop puede presentar un CAPTCHA aproximadamente cada 100 páginas. Cuando esto ocurre, el scrapper:

1. **Guarda el progreso parcial** en un TSV antes de detenerse
2. **Muestra instrucciones** para resolver el CAPTCHA en el navegador
3. **Solicita las cookies** del navegador para recuperar la sesión
4. **Reintenta automáticamente** con las cookies provistas

Si no se puede recuperar la sesión, el scrapper indica exactamente desde qué página reanudar:

```python
# Reanudar desde página 102 con el TSV anterior ya guardado
df1 = pd.read_csv("output/argenprop_venta_PARCIAL_XXXXXXXXXX.tsv", sep='\t')

df2 = run_scrapper_argenprop(
    enlace     = "https://www.argenprop.com/departamentos/venta/capital-federal",
    operacion  = "venta",
    start_page = 102,
    max_pages  = 200,
)

df_completo = pd.concat([df1, df2], ignore_index=True)
```

---

## Notas técnicas

- **Anti-bot**: usa `User-Agent` de Chrome 122. Argenprop no requiere impersonación TLS completa.
- **Paginación**: `?pagina-2`, `?pagina-3`, etc. (query string).
- **Deduplicación**: por URL del link. Un mismo aviso no se guarda dos veces aunque aparezca en múltiples páginas.
- **Delay**: 1.5 segundos entre páginas.
- **Encoding**: UTF-8 con BOM (`utf-8-sig`) para compatibilidad con Excel y Google Sheets.
- **parse_address()**: maneja casos complejos como `"ARAOZ 1200, Piso 8"`, guiones, años históricos en nombres de calle y pisos inline.
