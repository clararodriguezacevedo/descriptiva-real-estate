# Análisis del Mercado Inmobiliario de CABA

**Analítica Descriptiva — Grupo 1**

| Integrante | Legajo |
| ----- | :---: |
| Clara Rodriguez Acevedo | 66527 |
| Valentina Contrera | 66577 |
| Valentina Ludmila Darchuk | 66009 |

Trabajo práctico de análisis de datos sobre el mercado inmobiliario de la Ciudad Autónoma de Buenos Aires con el objetivo de realizar una recomendación informada para un inversor amateur interesado en comprar un departamento en CABA. El proyecto cubre el ciclo completo: scraping de datos, limpieza, análisis exploratorio, geocoding, validación de hipótesis, reducción de dimensionalidad, clustering, modelos predictivos, exportación a un dashboard en Power BI y una herramienta de tasación contra mercado.

---

## Tabla de contenidos

1. [Resumen ejecutivo](#resumen-ejecutivo)
2. [Recomendación final](#recomendación-final)
3. [Contexto y perfil del cliente](#contexto)
4. [Dataset final y origen](#dataset-final-y-origen)
5. [Decisiones de preprocesamiento](#decisiones-de-preprocesamiento)
6. [Principales insights del análisis exploratorio](#principales-insights-del-análisis-exploratorio)
7. [Hipótesis y resultados estadísticos](#hipótesis-y-resultados-estadísticos)
8. [Estructura del repositorio](#estructura-del-repositorio)
9. [Dependencias y reproducibilidad](#dependencias-y-reproducibilidad)
10. [Scraping](#scraping)
11. [Pipeline de notebooks](#pipeline-de-notebooks)
12. [Dashboard de Power BI](#dashboard-de-power-bi)
13. [Scripts auxiliares](#scripts-auxiliares)
14. [Conclusiones y recomendaciones de negocio](#conclusiones-y-recomendaciones-de-negocio)
15. [Limitaciones y líneas futuras](#limitaciones-y-líneas-futuras)
16. [De prototipo a producción](#de-prototipo-a-producción)

---

## Resumen ejecutivo

Scrapeamos y unificamos ~52.000 avisos de venta, alquiler y alquiler temporario de ArgenProp y ZonaProp en CABA, los limpiamos y enriquecimos con geocoding y variables espaciales (distancia a subte, tren y espacios verdes), y construimos un set de KPIs de rentabilidad por barrio. Sobre esa base validamos cuatro hipótesis, redujimos la dimensionalidad de las variables de la propiedad en tres índices interpretables (Lujo, Confort, Antigüedad), segmentamos el mercado en cuatro micro-mercados con K-Means y entrenamos modelos explicativos de precio por m² y de modalidad de alquiler óptima.

Los hallazgos centrales: **los barrios más caros no son los más rentables** (correlación negativa entre precio/m² y rentabilidad neta), **los amenities premium suben el precio tanto en venta como en alquiler** (el caso más fuerte es el gimnasio, que suma ~52% en venta y ~60% en alquiler), y **la antigüedad y el nivel socioeconómico del barrio son las variables que más explican el precio por m²**. La recomendación final para el inversor principiante es una tabla por barrio con la modalidad de alquiler sugerida, la rentabilidad esperada y el cluster dominante, priorizando barrios de gama media sobre los más caros.

---

## Recomendación final

### Top 5 de barrios por rentabilidad neta

| Ranking | Largo plazo | Temporario |
| :---: | :--- | :--- |
| 1 | Villa Lugano (9%) | Nueva Pompeya (9%) |
| 2 | Constitución (7%) | Villa Luro (9%) |
| 3 | La Boca (7%) | Parque Avellaneda (7%) |
| 4 | Monserrat (7%) | La Boca (6%) |
| 5 | Nueva Pompeya (7%) | Constitución (5%) |

Los 7 barrios distintos que aparecen entre ambos rankings están al **sur de la Avenida Rivadavia**: una zona históricamente subvalorada por el mercado de inversión, con precios de entrada accesibles y demanda de alquiler sostenida. Ninguno suele aparecer en una conversación de café sobre inversión inmobiliaria, y ese es justamente el valor que aporta este análisis frente a la intuición de mercado.

### Modalidad recomendada: largo plazo

Como regla general se recomienda **alquiler tradicional de largo plazo**: los porcentajes promedio son mayores que en temporario una vez consideradas todas las modalidades, los años de recupero son menores y los rendimientos son más estables porque dependen de contratos fijos y no de un factor de ocupación variable.

El temporario alcanza picos comparables (9% en Nueva Pompeya y Villa Luro), pero el cálculo asume un **factor de ocupación del 75%** como estándar de mercado. Si la ocupación efectiva es mayor, el temporario puede superar ampliamente al largo plazo; si es menor, lo opuesto. Esta sensibilidad es la razón por la que el largo plazo se prefiere como modalidad de base.

### Horizonte de recupero

Con un presupuesto típico de USD 120.000 y la configuración recomendada (dos ambientes, edificio de menos de 15 años, con amenities), el horizonte de recupero en los barrios del podio se ubica entre **11 y 15 años** (10.9 en Villa Lugano, hasta 14.7 en La Boca). La misma operación en Belgrano, siguiendo la intuición de mercado, alarga el horizonte a **23.6 años**. Esa diferencia de más de una década es exactamente el valor que aporta decidir con datos en vez de con opinión.

### Herramienta de tasación (modelo de precio/m²)

Como complemento al ranking, entrenamos un modelo de regresión sobre las ~25.000 propiedades en venta para predecir el precio del m² esperado. Se aplica a cualquier propiedad nueva pasándole cuatro datos visibles en la publicación (superficie, antigüedad, amenities, dirección) y devuelve el precio que el mercado debería estar pidiendo para una propiedad con ese perfil.

La aplicación es directa: si una propiedad se publica a USD 3.500/m² y el modelo estima USD 2.700, el inversor sabe que está negociando contra un sobreprecio cercano al 30%. Para justificarlo, el departamento tiene que ser extraordinario en algún atributo que el modelo no captura (muy buena vista, terraza enorme, grifería de oro). Si no aparece ese atributo extraordinario, hay margen real de negociación.

---

## Contexto

El mercado inmobiliario porteño es confuso: la información de precios de venta, alquileres tradicionales y alquileres temporarios está dispersa en distintos portales, en distintas monedas y con criterios de publicación inconsistentes. El comprador minorista argentino no tiene visibilidad real sobre cuál barrio, qué tipología y qué modalidad de alquiler maximiza su rentabilidad para un departamento, y además opera bajo restricciones muy particulares: muchas veces compra al contado, en dólares, en un contexto donde la regulación de alquileres cambia cada dos años y donde el precio del metro cuadrado puede multiplicarse por cuatro entre dos barrios separados por seis kilómetros. Estas condiciones tienen una consecuencia directa: la primera compra es prácticamente irreversible. No hay refinanciación posible, y los costos de transacción de revender son altos. Por eso la decisión inicial define el rendimiento de la próxima década del patrimonio del inversor.

Asimismo, en los portales de venta no se ven los precios de cierre, y las inmobiliarias claramente no comparten esa información. Cada propiedad se evalúa básicamente comparándola con dos o tres vecinas que el comprador encuentra en un portal, lo que deja al inversor en desventaja informativa contra el vendedor. El modelo de tasación se entrenó precisamente para cubrir esa brecha.

### Perfil del cliente

**Inversor independiente principiante.** Persona física que busca su primera inversión en un departamento en CABA. Su duda central no es solo dónde comprar, sino también cómo alquilar: bajo la modalidad tradicional (contrato fijo con un inquilino) o bajo la modalidad temporal. Necesita evidencia cuantitativa para tomar una decisión estratégica antes de comprometer capital. Este perfil no incluye especialistas, personas con amplia experiencia previa o expertos en Real Estate.

---

## Dataset final y origen

Los datos provienen de dos portales inmobiliarios argentinos, **ArgenProp** y **ZonaProp**, con una extracción única de avisos de venta, alquiler y alquiler temporario en CABA. El dataset maestro original combina ambos scrapers en un dataframe con una fila por aviso.

Después del proceso de limpieza (deduplicación, corrección de errores de moneda, tratamiento de outliers y de valores faltantes), el **dataset final queda en 51.996 registros**, distribuidos en los tres tipos de operación (venta, alquiler y alquiler temporario) y en ambas monedas (ARS y USD). Alquiler temporario es la operación con menor volumen pero igual reúne más de 8.000 filas, suficientes para sacar conclusiones sólidas. Palermo, Belgrano, Recoleta y Caballito son los barrios con mayor representación en el dataset.

Sobre ese dataset limpio se calculan los 9 KPIs por barrio (rentabilidad bruta y neta, recupero de inversión, precio/m² relativo, índices de modalidad óptima), se resuelven coordenadas geográficas (con aproximadamente 1 de cada 7 avisos sin coordenadas, generalmente por falta de calle/altura), y se agregan variables espaciales y socioeconómicas para el resto del análisis.

---

## Decisiones de preprocesamiento

La limpieza fue uno de los componentes más pesados del proyecto, dado lo heterogéneo de los datos scrapeados. Las decisiones más relevantes:

- **Moneda y valores ficticios**: los precios marcados como "USD" se tomaron en dólares, el resto en pesos, y los marcados "Consultar" como NaN. Se detectaron valores simbólicos típicos de portales inmobiliarios (precios de "1 peso" o "111.111.111" para indicar "a consultar") y se trataron como faltantes en vez de precios reales.
- **Corrección de errores de clasificación de moneda**: se identificaron y reclasificaron registros donde el precio estaba en una moneda distinta a la indicada (ej. un alquiler de menos de $300.000 ARS es imposible en CABA en 2026 y casi seguro está en dólares). En total se reclasificaron 104 registros de ARS a USD y 153 de USD a ARS.
- **Outliers en precio**: se usó `precio_por_m2` como métrica central (en vez de precio absoluto) para no confundir tamaño con sobreprecio. Se aplicó winsorización por percentiles 1-99, adaptativa por segmento (operación + moneda + barrio, con fallback a operación + moneda cuando el barrio tenía menos de 30 registros), para no tratar como atípicas propiedades normales en barrios con rangos de precio muy distintos (ej. Puerto Madero vs. Villa Lugano).
- **Transformación logarítmica**: se aplicó `log1p` sobre los precios para estabilizar la varianza, dado que los precios inmobiliarios siguen una distribución log-normal.
- **Expensas**: se determinó un umbral de $2.000-3.000 ARS por debajo del cual un valor se considera "sin expensas reales" (ingresado como placeholder), usando un análisis de codo sobre la distribución ordenada de valores.
- **Valores faltantes**: se confirmó con un test chi-cuadrado que la ausencia de ciertos campos (ambientes, baños, antigüedad) depende del sitio de origen: por ejemplo, "ambientes" está prácticamente completo en ZonaProp (0,8% de faltantes) y casi vacío en ArgenProp (96,8%), y a la inversa para "antigüedad_años". Esto encuadra el patrón como faltante condicionado al sitio (MAR) y justificó una imputación diferenciada por sitio, cruzando datos entre ambos portales según m² cuando fue posible.
- **Deduplicación**: se usó `posting_id` + `sitio` como clave (no barrio/precio/m², que pueden coincidir en propiedades distintas), eliminando 3.243 filas duplicadas.

---

## Principales insights del análisis exploratorio

- El inmueble mediano tiene ~52 m², 2 ambientes, 1 dormitorio, 1 baño y 25 años de antigüedad; la media de superficie (~70 m²) es notablemente mayor a la mediana, señal de un segmento de propiedades grandes que empuja el promedio hacia arriba.
- Existe una relación aproximadamente lineal entre precio y superficie en propiedades de hasta 100 m²; por encima de ese umbral el precio responde más a lujo y ubicación que a los metros cuadrados en sí.
- El precio/m² se mantiene relativamente estable entre 1 y 3 ambientes, pero los departamentos de 4-5 ambientes alcanzan valores de precio/m² considerablemente más altos.
- Los departamentos con amenities (especialmente pileta y gimnasio) muestran precios sistemáticamente más altos que los que no tienen.
- A nivel geográfico, Puerto Madero se destaca como un mercado de lujo aparte, con precios muy por encima del resto; le siguen Recoleta, Palermo, Belgrano y Núñez (este último con una popularidad creciente, asociada a nuevos desarrollos en la zona). El mercado muestra una fuerte heterogeneidad territorial tanto en precio absoluto como en precio por m², lo que respalda analizar el negocio por micro-zonas y no solo por barrio.

---

## Hipótesis y resultados estadísticos

Se trabajó con un nivel de significancia del 5%.

| # | Hipótesis | Test | Resultado |
|---|---|---|---|
| 1 | En barrios turísticos (Palermo, San Telmo, Recoleta, La Boca), el alquiler temporario rinde más que el largo plazo | Mann-Whitney | **No rechazada.** No hay evidencia suficiente: la mediana de rentabilidad neta a largo plazo en esos barrios (6%) fue incluso mayor que la temporaria (4%). La muestra de solo 4 barrios turísticos limita la potencia del test. |
| 2 | Los barrios con mayor precio/m² no son los de mayor rentabilidad neta | Spearman + Mann-Whitney (top 10 más caros vs. resto) | **Confirmada.** Correlación de Spearman de -0,806 (p < 0,0001) entre precio/m² y rentabilidad neta; los 10 barrios más caros rinden significativamente menos que el resto. |
| 3 | Los amenities suben el precio de venta pero no el de alquiler | Mann-Whitney por amenity y tipo de operación | **Rechazada en su forma original.** Los amenities (pileta, gimnasio, parrilla, SUM, balcón, baulera) resultaron estadísticamente significativos en las tres modalidades, no solo en venta. El caso más marcado es el gimnasio: +52% en precio de venta y +60% en alquiler. |
| 4 | La cercanía al subte aumenta el precio por m² | Spearman (n=24.974 propiedades con coordenadas) | **Rechazada en el sentido esperado.** Hay correlación significativa (Spearman = 0,137, p < 0,0001) pero de signo positivo: a mayor distancia al subte, mayor precio por m², lo opuesto a la intuición. Esto puede reflejar que las zonas premium de CABA (Puerto Madero, Recoleta) no son necesariamente las de mejor cobertura de subte, por lo que el efecto socioeconómico/de ubicación domina sobre el efecto puro de accesibilidad. |

---

## Estructura del repositorio

```
descriptiva-real-estate/
├── data/
│   ├── raw/                                        # TSV crudos del scraping
│   ├── geocoding/                                  # Coordenadas y cache de las APIs
│   └── processed/                                  # Dataframes limpios, KPIs, exports para Power BI
├── notebooks/
│   ├── argenprop/argenprop_scraper.ipynb           # Scraper de ArgenProp
│   ├── zonaprop/zonaprop_scraper.ipynb             # Scraper de ZonaProp
│   ├── 01_dataframe_maestro.ipynb
│   ├── 02_data_cleaning_and_normalization.ipynb
│   ├── 03_eda_and_insights.ipynb
│   ├── 04_kpi_pipeline.ipynb
│   ├── 05_geocoding.ipynb
│   ├── 06_reduccion_y_clustering.ipynb
│   ├── 07_hipotesis.ipynb
│   ├── 08_modelos_y_recomendacion.ipynb
│   └── 09_powerbi_export.ipynb
├── scripts/
│   └── geocode_addresses.py                        # Geocoder reanudable (USIG + Georeferencia Nación)
└── dashboard/
    └── Tablero_Interactivo_Para_Inversor.pbix      # Dashboard de Power BI (ver sección Dashboard)
```

---

## Dependencias y reproducibilidad

```
pandas, numpy, matplotlib, seaborn, geopandas, scikit-learn, prince, scipy, requests, geopy, curl_cffi, beautifulsoup4
```

Instalación rápida:

```bash
pip install pandas numpy matplotlib seaborn geopandas scikit-learn prince scipy requests geopy curl_cffi beautifulsoup4
```

**Reproducibilidad.** Todos los modelos y el clustering usan `SEED = 42` como semilla global, fijada tanto en `numpy.random` como en `random` y en el parámetro `random_state` de cada modelo de scikit-learn. El tipo de cambio se cachea localmente en `data/processed/tipo_cambio_cache.json` para que las conversiones a dólares sean consistentes entre corridas. Los notebooks se ejecutan en orden numérico; los geocoded data y el dataframe limpio quedan en `data/` para no tener que re-scrapear ni re-geocodificar en cada corrida.

---

## Scraping

Los datos provienen de dos portales inmobiliarios argentinos: **ArgenProp** y **ZonaProp**. Cada portal tiene su propio scraper (en `notebooks/argenprop/` y `notebooks/zonaprop/` respectivamente), con la misma interfaz de salida pero ajustes técnicos distintos según las protecciones anti-bot de cada sitio.

### URLs scrapeadas

| Portal | Venta | Alquiler | Alquiler temporario |
| :--- | :--- | :--- | :--- |
| ArgenProp | [link](https://www.argenprop.com/departamentos/venta/capital-federal) | [link](https://www.argenprop.com/departamentos/alquiler/capital-federal) | [link](https://www.argenprop.com/departamentos/alquiler-temporal/capital-federal) |
| ZonaProp | [link](https://www.zonaprop.com.ar/departamentos-venta-capital-federal.html) | [link](https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal.html) | [link](https://www.zonaprop.com.ar/departamentos-alquiler-temporal-capital-federal.html) |

### Columnas del DataFrame de salida (idénticas en ambos scrapers)

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `Fecha_Scraping` | date | Fecha de ejecución (YYYY-MM-DD) |
| `Posting_ID` | str | ID único del aviso |
| `Sitio` | str | `argenprop` o `zonaprop` |
| `Operación` | str | `venta`, `alquiler` o `temporal` |
| `Precio` | str | Precio publicado (ej: `USD 85.000`) |
| `Expensas` | str | Expensas mensuales si figuran |
| `Calle` | str | Nombre de la calle (title case) |
| `Altura` | str | Número de puerta |
| `Piso` | str | Piso del departamento cuando figura |
| `Barrio` | str | Barrio de CABA |
| `Detalles` | str | m², ambientes, baños (texto libre) |
| `Descripción` | str | Descripción del aviso (texto libre) |
| `Link` | str | URL completa del aviso |
| `Amenities` | int | Conteo de amenities mencionados |
| `Losa_Central`, `Aire_Acond`, `Apto_Credito`, `Cochera`, `Seguridad`, `Luminoso`, `Balcon_Aterrazado` | int 0/1 | Variables binarias de detección léxica sobre la descripción |

### Uso

ArgenProp:

```python
df = run_scrapper_argenprop(
    enlace     = "https://www.argenprop.com/departamentos/venta/capital-federal",
    operacion  = "venta",
    max_pages  = 50,       # ~20 propiedades por página
    start_page = 1,        # útil para reanudar tras CAPTCHA
)
```

ZonaProp:

```python
df = run_scrapper_zonaprop(
    enlace    = "https://www.zonaprop.com.ar/departamentos-venta-capital-federal",  # sin .html final
    operacion = "venta",
    max_pages = 10,
)
```

### Diferencias técnicas entre los dos scrapers

| Aspecto | ArgenProp | ZonaProp |
| :--- | :--- | :--- |
| Librería HTTP | `requests` | `curl_cffi` con `impersonate="chrome120"` |
| Protección anti-bot | User-Agent de Chrome alcanza | Requiere fingerprint TLS completo (replica el handshake de Chrome 120) |
| Selector de cards | `div.listing__item` (clases CSS) | `div[data-qa="posting PROPERTY"]` (atributos `data-qa`) |
| Posting ID | atributo `id` | atributo `data-id` |
| Paginación | `?pagina-2` (query string) | `-pagina-2.html` (path) |
| Delay entre páginas | 1.5 s | 2 s |
| CAPTCHA | Aparece cada ~100 páginas, requiere intervención manual | No observamos CAPTCHA, pero hay 403 si no se usa `curl_cffi` |
| Encoding del TSV | `utf-8-sig` (compatible con Excel) | idem |

ZonaProp analiza la "firma TLS" de cada conexión entrante. La librería `requests` estándar tiene una firma distinta a la de un navegador real, lo que ZonaProp detecta y bloquea con HTTP 403. `curl_cffi` con `impersonate="chrome120"` replica exactamente el handshake TLS de Chrome 120, haciendo la conexión indistinguible de la de un usuario real, sin necesidad de Playwright ni navegador headless.

### Manejo de CAPTCHA en ArgenProp

ArgenProp presenta un CAPTCHA aproximadamente cada 100 páginas (no es rate-limit, sino estrictamente por número de página). Cuando ocurre, el scraper guarda el progreso parcial en un TSV antes de detenerse, muestra instrucciones para resolver el CAPTCHA en el navegador, solicita las cookies del navegador para recuperar la sesión y reintenta automáticamente con las cookies provistas. Si no se puede recuperar la sesión, el scraper indica desde qué página reanudar:

```python
df1 = pd.read_csv("output/argenprop_venta_PARCIAL_XXXXXXXXXX.tsv", sep='\t')
df2 = run_scrapper_argenprop(
    enlace="https://www.argenprop.com/departamentos/venta/capital-federal",
    operacion="venta",
    start_page=102,
    max_pages=200,
)
df_completo = pd.concat([df1, df2], ignore_index=True)
```

### Parseo de direcciones

Ambos scrapers usan una función `parse_address()` adaptada a las particularidades de cada portal. Casos cubiertos:
- `"Bolivia al 4400"` — limpieza del `"al"` previo al número (ZonaProp).
- `"SAN JOSE 445. Entre Belgrano y Venezuela"` — el punto rompía el regex.
- `"11 de Septiembre de 1888 2231"` — el año histórico se confundía con la altura.
- `"Torres del Yacht - Juana Manso al 600 - 2 Ambientes"` — extracción correcta con guiones múltiples.
- `"Alvear Tower - Azucena Villaflor"` — devolver `None` cuando no hay número de altura válido.
- `"El Faro - 3 Ambientes"` — descartar números menores a 100 (probable descripción, no dirección).
- `"Junín 1615 piso 13"` y `"Junín 1615 PB"` — capturar el piso correctamente.
- `"2º piso"` — limpieza del símbolo de ordinal.

---

## Pipeline de notebooks

### `01_dataframe_maestro`
Une los TSVs producidos por ambos scrapers y construye el dataframe maestro unificado. Cada fila corresponde a un aviso único, con la estructura descripta en la sección Scraping.

### `02_data_cleaning_and_normalization`
Limpieza integral de datos: eliminación de duplicados, tratamiento de outliers y gestión de valores faltantes a partir de las monedas utilizadas (ARS y USD) y las operaciones (venta, alquiler temporario, alquiler largo plazo). El dataset final queda en 51.996 registros (ver detalle en "Decisiones de preprocesamiento" más arriba).

### `03_eda_and_insights`
Análisis exploratorio: análisis geográfico de precios, distribución por barrio, tipo de operación y características de las propiedades (ver "Principales insights del análisis exploratorio" más arriba).

### `04_kpi_pipeline`
Cálculo de los siguientes KPIs por barrio, con precios normalizados a USD, y exportación a un dataframe consolidado:

| # | KPI | Fórmula | Propósito |
| :---- | :---- | :---- | :---- |
| 1 | Rentabilidad Bruta Largo Plazo | (Alquiler Mensual Mediano × 12) / Precio Venta Mediano × 100 | Rendimiento bruto anual sobre el capital invertido vía alquiler tradicional |
| 2 | Recupero de Inversión | Precio Venta / (Alquiler Mensual × 12) | Años necesarios para recuperar la inversión |
| 3 | Precio por m² | Precio Publicado / m² - mediana por barrio y tipo de operación | Normaliza el valor para comparar entre barrios |
| 4 | Rentabilidad Neta Largo Plazo | (Alquiler Anual − Expensas Anuales del Propietario) / Precio Venta × 100 | Rentabilidad real descontando expensas |
| 5 | Precio/m² Relativo por Barrio | Precio/m² propiedad / Mediana Precio/m² barrio | Identifica propiedades por debajo de la mediana del barrio |
| 6 | Rentabilidad Bruta Temporario | (Alquiler Mensual Mediano Temporario × 12) / Precio Venta Mediano × 100 | Rendimiento bruto temporario con una tasa de ocupación del 73% |
| 7 | Índice Bruto Modalidad Óptima | Rent. Bruta Temp / Rent. Bruta LP | > 1 indica que temporario supera al largo plazo (bruto) |
| 8 | Rentabilidad Neta Temporario | (Ingreso Anual Temporario − Expensas) / Precio × 100 | Rentabilidad temporaria neta |
| 9 | Índice Neto Modalidad Óptima | Rent. Neta Temp / Rent. Neta LP | > 1 indica que temporario supera al largo plazo (neto) |

### `05_geocoding`
Resolución de coordenadas geográficas (latitud y longitud) a partir de calles y alturas de cada propiedad, usando dos APIs oficiales argentinas (USIG-GCBA y Georeferencia Nación). El consenso entre ambas fuentes se guarda en `data/geocoding/`. El script reanudable que realiza el llamado masivo a las APIs vive en `scripts/geocode_addresses.py`; el notebook documenta el resultado y audita la cobertura.

### `06_reduccion_y_clustering`
Carga el dataset enriquecido con coordenadas y construye los índices sintéticos del proyecto, más el clustering de micro-mercados.

**Enriquecimiento espacial.** Para cada propiedad con coordenadas resueltas se calculan tres distancias geográficas mediante aproximación euclidiana corregida por latitud: distancia al subte más cercano (proxy de accesibilidad), al espacio verde más cercano (proxy ambiental) y a la estación de tren más cercana (accesibilidad en zonas con menor cobertura de subte). Se asigna a cada propiedad el nivel socioeconómico de su barrio (escala ordinal del 1 al 5) basado en clasificaciones del GCBA y datos del censo. Se documenta la cobertura del geocoding por barrio (Puerto Madero es el de menor cobertura con un 68%).

**Reducción de dimensionalidad e índices sintéticos.** Para reducir multicolinealidad y facilitar la interpretación de los modelos se construyen tres índices:
- **PCA sobre variables continuas** (precio/m², superficie, antigüedad): se retienen dos componentes que explican ~80% de la varianza. PC1 es el *Índice de precio y superficie*; PC2 es el *Score de Antigüedad*, normalizado a [0, 1].
- **MCA sobre amenities binarios**: el primer componente explica un 13,43% de la varianza por sí solo y se interpreta como **Índice de Lujo** (captura amenities premium: pileta, gimnasio, SUM, etc.).
- **Índice de Confort**: construido como la proporción de seis amenities de comodidad cotidiana presentes en la propiedad (aire acondicionado, ascensor, agua caliente central, lavadero, portero, losa central).

**Clustering para descubrir micro-mercados.** K-Means sobre características de la propiedad (precio/m², superficie, antigüedad) y entorno espacial (distancias al subte, espacios verdes y tren, nivel socioeconómico). La cantidad de clusters se selecciona con tres métricas (método del codo, silueta, Calinski-Harabasz). Se elige **k=4** como punto de quiebre más claro del codo. A cada cluster se le asigna un nombre comercial descriptivo generado a partir de sus medianas. Se incluye un DBSCAN como sanity check.

Cierra con mapas y heatmaps de perfil por cluster, y guarda un checkpoint (`checkpoint_post_clustering.pkl`) con el dataframe enriquecido y los objetos auxiliares (KPIs, capas geográficas, perfiles) para que los notebooks `07_hipotesis` y `08_modelos_y_recomendacion` puedan ejecutarse de forma independiente.

### `07_hipotesis`
Valida las cuatro hipótesis del proyecto (ver tabla completa en "Hipótesis y resultados estadísticos" más arriba). Carga el checkpoint `checkpoint_post_clustering.pkl` y puede ejecutarse de forma independiente una vez corrido `06_reduccion_y_clustering`.

### `08_modelos_y_recomendacion`
Carga el mismo checkpoint para construir dos modelos explicativos sobre el dataset enriquecido.

- *Precio por metro cuadrado (continuo)*: se comparan OLS, Ridge (L2) y Lasso (L1), evaluados por R² y MAE en test y con CV de 5 folds. Los tres modelos resultan prácticamente equivalentes. Variables con mayor impacto (coeficientes estandarizados): antigüedad en años (relación negativa fuerte), nivel socioeconómico del barrio, m² totales, Índice de Lujo y cantidad de baños. Confirmado por árbol de decisión de profundidad 4, permutation importance y curvas de sensibilidad. Importante: se usa la antigüedad cruda en años, **no** el `score_antiguedad` derivado del PCA, porque ese score se calcula sobre una matriz que incluye precio/m² como input y meterlo en el modelo sería leak del target.
- *Modalidad de alquiler (binario)*: target = si el temporario rinde más que el LP en el barrio. Se comparan regresión logística y árbol. AUC ~0.99 y ~0.97 respectivamente, **a interpretarse con cautela**: el target fue construido a nivel barrio, así que el modelo captura mayormente patrones del barrio, no de propiedades individuales. La variable más relevante es la distancia al subte.

La sección cierra con una **tabla de recomendación por barrio** con la modalidad sugerida, la rentabilidad esperada y el cluster dominante, y guarda el checkpoint final (`checkpoint_post_modelos.pkl`) para el siguiente notebook.

### `09_powerbi_export`
Genera todos los archivos necesarios para el dashboard de Power BI. Requiere `08_modelos_y_recomendacion` ejecutado hasta el final, ya que carga su checkpoint y produce:

- `fact_propiedades.csv` — una fila por propiedad
- `dim_barrios.csv` — una fila por barrio
- `dim_clusters.csv` — perfil de cada cluster con nombre y color
- `dim_puntos_referencia.csv` — estaciones de subte, tren y espacios verdes para overlay
- `dim_coeficientes_modelo.csv` — coeficientes Ridge e importancia por permutación
- `barrios.geojson` — polígonos de barrios para Shape Map

---

## Dashboard de Power BI

El archivo `.pbix` vive en `dashboard/Tablero_Interactivo_Para_Inversor.pbix`. También está publicado en Power BI Service: [Tablero Interactivo](https://app.powerbi.com/view?r=eyJrIjoiNWExMTc5NDMtOTBhMS00NGY3LWIzMTktNWY0MDQ0NDM3MWM5IiwidCI6ImExZjUwYTk3LTIxYzAtNDlhNy1hOWQ0LWYyNDRlYmI0MmRhNyIsImMiOjR9).

### Estructura general

El dashboard tiene 5 páginas, navegables desde la página de inicio ("Real Estate") o con las flechas de navegación arriba a la derecha:

1. Visión General del Mercado
2. Mapa Espacial
3. Segmentación por Clusters
4. Variables y Relaciones
5. KPIs de negocio y prescriptiva

Todas las páginas comparten los mismos slicers en el panel izquierdo: **Barrio**, **Precio USD** (rango), **Operación** (Alquiler Temporal / Alquiler / Venta), y **Cluster**. Estos filtros están sincronizados, así que cambiarlos en una página afecta a las demás.

La página 5 tiene un slicer adicional: **Modalidad** (Largo Plazo / Temporario), que solo afecta las medidas de rentabilidad y recupero, no filtra las propiedades.

### Página 1: Visión General del Mercado

Foto rápida del tamaño y composición del mercado antes del detalle: 3 tarjetas KPI (precio mediano por m² en USD, cantidad total de propiedades, m² promedio), gráfico de torta de **Operaciones**, **Treemap "Cantidad de Propiedades por Barrio (Top 15)"** coloreado por cluster dominante (Palermo, Recoleta y Belgrano son los de mayor volumen), e **histograma de precio USD/m²** con la cola larga de Puerto Madero y similares.

### Página 2: Mapa Espacial

Dimensión geográfica del mercado:
- **Shape Map (coroplético)** de precio USD/m² mediano por barrio (Puerto Madero diferenciado en azul). El tooltip muestra la rentabilidad a largo plazo.
- **Mapa de Puntos de Interés**: subte, tren y espacios verdes con botones para alternar capas.
- **Mapa de burbujas de Propiedades**: cada punto es una propiedad, tamaño proporcional al promedio de m² y color según precio USD/m².

El precio se concentra en el corredor norte (Núñez, Belgrano, Palermo, Recoleta, Puerto Madero) y cae hacia el sur y el oeste; la rentabilidad se comporta casi de manera opuesta.

### Página 3: Segmentación por Clusters

Evidencia que el mercado no es homogéneo sino 4 micro-mercados con perfiles distintos:

| Color | Cluster | Perfil |
| :--- | :--- | :--- |
| Negro | — | Selección "todo" (no es un cluster real) |
| Azul | Cluster 0 | Departamentos antiguos |
| Naranja | Cluster 1 | Departamentos lejos del subte |
| Verde | Cluster 2 | Departamentos en barrios de alto nivel socioeconómico |
| Rojo | Cluster 3 | Departamentos amplios y antiguos, en barrios de alto nivel socioeconómico |

Visuales: shape map por cluster dominante por barrio (verde domina el corredor norte, azul el centro, naranja el sur y el oeste); gráfico de índices por cluster; scatter m² total vs precio USD/m² coloreado por cluster.

### Página 4: Variables y Relaciones

Lado técnico: qué variables explican el precio por m² y cómo se separan los clusters en el espacio reducido.
- **Bar chart "Importancia Permutación por variable y signo"**: ordena las variables del modelo Ridge según cuánto cae el R² al aleatorizarlas. Encabezan antigüedad (negativo), nivel socioeconómico, índice de lujo y los dummies de cluster.
- **"Mediana precio m² según ambientes"**: bar chart con barras de error mostrando cómo sube el precio por m² con la cantidad de ambientes.
- **Scatter PCA**: proyecta las propiedades en dos componentes principales coloreado por cluster.

### Página 5: KPIs de negocio y prescriptiva — la página ejecutiva

Responde "¿dónde conviene invertir?":
- **Gauge de Rentabilidad neta (%)**: promedio de las propiedades visibles según filtros activos.
- **Tarjeta "% Prop. oportunidad"**: porcentaje de propiedades en venta cuyo precio por m² está al menos 15% por debajo de la mediana de su barrio (`es_oportunidad = 1` si `precio_m2_relativo_barrio < 0.85`).
- **Tarjeta "Modalidad Óptima"**: indica si conviene más LP o Temporario para el conjunto filtrado.
- **Tarjeta "Años para recupero"**.
- **Bar chart "Rentabilidad neta LP (%) por Barrio"**: ranking, reacciona al slicer de Modalidad.
- **Tabla "Propiedades Oportunidad en Venta"**: lista las propiedades en venta marcadas como oportunidad, ordenadas por menor precio relativo (más subvaluadas primero).

**El slicer de Modalidad: qué filtra y qué no.** A diferencia del resto, *Modalidad* no filtra las propiedades de la tabla ni del bar chart de barrios por cantidad. Es una tabla desconectada del modelo que solo controla qué columna de rentabilidad usan las medidas (LP vs Temporario). Esto es intencional: la modalidad es una decisión sobre cómo operar la propiedad después de comprarla, no un atributo de la propiedad en sí.

### Demo guiada para el inversor (flujo de la página 5)

Secuencia pensada para mostrar el dashboard en vivo, simulando la consulta del inversor:

1. **Presupuesto.** Mover el slicer de Precio USD para fijar el techo. El dashboard recalcula el gauge, las tarjetas y el ranking de barrios, descartando los barrios donde el presupuesto no alcanza.
2. **Ranking personalizado.** Con el presupuesto aplicado, el bar chart de barrios por rentabilidad neta muestra el top dentro de ese rango. Aparecen barrios que normalmente no están en mente como buenas opciones — ese es el aporte del análisis.
3. **Modalidad Temporario.** Cambiar el slicer a "Temporario". El gauge, la tarjeta de modalidad óptima, los años de recupero y el ranking se recalculan usando rentabilidad temporaria.
4. **Modalidad Largo Plazo.** Volver el slicer a LP. El ranking se reordena: distintos barrios pasan a liderar.
5. **Foco en un barrio.** Seleccionar un barrio puntual (ej. Nueva Pompeya). Todos los visuales se filtran a ese barrio: el gauge muestra su rentabilidad específica, la tabla de oportunidades solo sus propiedades en venta subvaluadas. El ID de Argenprop permite ir a la publicación original.

Con esto, la decisión deja de depender de una opinión externa y pasa a sostenerse sobre datos cuantificables, explorables en tiempo real.

---

## Scripts auxiliares

Junto a los notebooks, el repositorio incluye un único proceso pesado en `scripts/`:

- **`geocode_addresses.py`**: cliente reanudable que consulta dos APIs (USIG-GCBA y Georeferencia Nación), cachea localmente y consolida un consenso geodésico. Es la fuente de verdad de las coordenadas que después se usan en el notebook 05. Vive como `.py` y no como notebook porque la corrida completa toma varias horas, conviene reanudarla por línea de comandos y el resultado se guarda directamente en `data/geocoding/` para que los notebooks no necesiten re-geocodificar.

---

## Conclusiones y recomendaciones de negocio

Para el inversor principiante, la evidencia recolectada sugiere:

1. **No comprar en los barrios más caros buscando rentabilidad.** El precio por m² más alto (Puerto Madero, Recoleta, Palermo, Belgrano) no se traduce en mejor retorno; de hecho la correlación con la rentabilidad neta es negativa. Conviene mirar barrios de gama media o del corredor sur (Villa Lugano, Constitución, La Boca, Monserrat, Nueva Pompeya). Se deben tener en cuenta los barrios de gama alta solo si el inversor prioriza el status del barrio y/o la liquidez de venta de la propiedad sobre la rentabilidad.
2. **Los amenities premium (pileta, gimnasio) son una inversión defendible**, ya que su efecto sobre el precio se traslada también al alquiler; no es solo un costo de venta que no se recupera.
3. **La modalidad de alquiler óptima depende del barrio y del perfil de la propiedad**, no hay una respuesta universal. Aunque recomendamos al alquiler a largo plazo como base, depende fuertemente del porcentaje de ocupación particular. 
4. La hipótesis de que los barrios turísticos rinden mejor en alquiler temporario **no se pudo confirmar con la evidencia disponible**; en la muestra analizada, el largo plazo rindió incluso mejor en esos barrios.
5. El **modelo de tasación** sirve como contrapeso a la asimetría informativa entre comprador y vendedor: para cualquier propiedad publicada, devuelve el precio/m² esperado dado su perfil y permite cuantificar cuánto sobreprecio está pidiendo el vendedor.
6. El **dashboard de Power BI** permite explorar estas conclusiones de forma interactiva, filtrando por presupuesto, barrio, cluster y modalidad.

---

## Limitaciones y líneas futuras

- **Sin componente temporal**: toda la base proviene de un único período de scraping, por lo que no es posible validar tendencias ni evaluar la estabilidad de los segmentos a lo largo del tiempo. Una línea futura natural es repetir el scraping periódicamente para construir una serie temporal.
- **Tipo de cambio cacheado**: la conversión ARS→USD depende del día en que se ejecutó el notebook. Las conclusiones relativas (qué barrio rinde más que otro) son estables, pero las cifras absolutas en dólares pueden variar entre corridas.
- **Muestra chica para la Hipótesis 1**: solo cuatro barrios se clasificaron como turísticos, lo que reduce la potencia del test de Mann-Whitney; es posible que exista una diferencia real que el test no pudo detectar con tan pocos casos.
- **Nivel socioeconómico aproximado**: se asignó por barrio a partir de clasificaciones publicadas y conocimiento general de la ciudad, no a partir de un dato fino por radio censal. Se podría refinar con datos oficiales del INDEC/GCBA a nivel comuna.
- **Cobertura de geocoding desigual**: aproximadamente 1 de cada 7 avisos no tiene coordenadas resueltas, y la cobertura varía por barrio (Puerto Madero es el caso más bajo, con 68%), lo que introduce un sesgo potencial en los análisis espaciales para esos barrios.
- **Clustering hecho sobre ventas en dólares**: los micro-mercados descubiertos no son directamente extrapolables al mercado de alquileres, que podría tener su propia segmentación.
- **Modelo de modalidad de alquiler con target a nivel barrio**: el AUC alto debe leerse con cautela ya que el target se construyó a nivel barrio y la clase "temporario" es minoritaria.
- **Factor de ocupación temporario asumido**: el ingreso temporario se calcula asumiendo 73% de ocupación anual. La rentabilidad efectiva escala con este factor.
- **Sin precios de cierre**: los precios usados son de oferta. El precio real al que se cierran las operaciones suele ser menor por margen de negociación, pero el portal no lo publica. De todas formas, utilizar el precio de publicación es realista ya que son los precios disponibles para cualquier inversor.  

---

## De prototipo a producción

Hoy el proyecto es una secuencia de notebooks que se corren a mano sobre un scraping puntual. Es importante notar que este caso es de **inferencia Batch (offline)**, no una API en tiempo real: no hay un usuario esperando una predicción puntual, sino un proceso programado (ej. semanal) que recalcula KPIs, clusters y modelos sobre todo el universo de propiedades. Esto simplifica el despliegue frente a, por ejemplo, un caso de scoring de fraude con latencia crítica.

Llevarlo a producción implicaría:

- **Empaquetado**: serializar los modelos (Ridge/Lasso, regresión logística, K-Means) con `joblib` (más adecuado que Pickle u ONNX para este tipo de modelos de scikit-learn) y unificar la limpieza, el enriquecimiento espacial y los índices sintéticos en un único objeto `Pipeline`, para que cada corrida nueva de scraping pase por exactamente los mismos pasos que los datos de entrenamiento.
- **Validación de inputs**: hoy gran parte de la limpieza consiste en detectar a posteriori errores ya cargados en los datos (precios "a consultar" como "1 peso", monedas mal clasificadas). En producción convendría validar cada aviso contra un esquema (ej. Pydantic) en el momento del scraping, antes de que entre al pipeline.
- **Monitoreo de Data Drift**: test de Kolmogorov-Smirnov para variables numéricas (precio/m², superficie) y test Chi-cuadrado para categóricas (mix de barrios, proporción ARS/USD), comparando cada corrida nueva contra la anterior, más alertas simples ante categorías nunca vistas.
- **Concept Drift**: la relación entre variables y precio también puede cambiar con el tiempo (ej. la relación entre distancia al subte y precio/m², que en este análisis salió positiva y contraria a la intuición, podría invertirse si cambia la regulación de alquileres o el contexto cambiario), lo que justifica re-validar las hipótesis periódicamente.
- **Reentrenamiento y dashboard**: reentrenar modelos y clustering en una cadencia más espaciada que el scraping (ej. mensual), versionando los artefactos para poder hacer rollback, y publicar el `.pbix` en Power BI Service con un dataflow conectado a un storage compartido y actualización programada, en vez de exportar y subir el archivo a mano.

El desarrollo completo de esta reflexión está en el notebook `08_modelos_y_recomendacion.ipynb`.
