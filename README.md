
**11/06/2026**

**Analítica Descriptiva**

**Trabajo Práctico N°3 : Técnicas Analíticas Avanzadas, Segmentación y Construcción de Insights Estratégicos**

| Grupo N°1 |  |
| ----- | :---: |
| Clara Rodriguez Acevedo | 66527 |
| Valentina Contrera | 66577 |
| Valentina Ludmila Darchuk | 66009 |

# Análisis del Mercado Inmobiliario de CABA

Trabajo práctico de análisis de datos sobre el mercado inmobiliario de la Ciudad Autónoma de Buenos Aires con el objetivo de realizar una recomendación informada hacia un inversor amateur interesado en comprar un departamenteo en CABA. El proyecto cubre el ciclo completo: scraping de datos, limpieza, análisis exploratorio, geocoding, validación de hipótesis, reducción de dimensionalidad, clustering, modelos predictivos y exportación a un dashboard en Power BI.

---

## Estructura del repositorio

```
descriptiva-real-estate/
├── data/
│   ├── raw/                  # Datos crudos obtenidos por scraping
│   ├── geocoding/            # GeoJSONs y dataframe con coordenadas por propiedad
│   └── processed/            # Dataframes limpios, KPIs y archivos listos para análisis
├── notebooks/
│   ├── argenprop/            # Scraper de ArgenProp (ver README interno)
│   ├── zonaprop/             # Scraper de ZonaProp (ver README interno)
│   ├── 01_dataframe_maestro.ipynb
│   ├── 02_data_cleaning_and_normalization.ipynb
│   ├── 03_eda_and_insights.ipynb
│   ├── 04_kpi_pipeline.ipynb
│   ├── 05_geocoding.ipynb
│   ├── TP3_Grupo_1.ipynb
│   ├── TP3_hipotesis.ipynb
│   └── TP3_power_bi_export.ipynb
```

---

## Scraping

Los datos provienen de dos portales inmobiliarios argentinos: **ArgenProp** y **ZonaProp**. Cada uno tiene su propio scraper y README con instrucciones de uso en las carpetas `notebooks/argenprop/` y `notebooks/zonaprop/` respectivamente. Los archivos resultantes del scraping se guardan en `data/raw/`.

---

## Pipeline de notebooks

### `01_dataframe_maestro`
Une los TSVs producidos por ambos scrapers y construye el dataframe maestro unificado.

### `02_data_cleaning_and_normalization`
Limpieza integral de datos: eliminación de duplicados, tratamiento de outliers y gestión de valores faltantes a partir de las monedas utilizadas (ARS y USD) y las operaciones (venta, alquiler temporario, alquiler largo plazo). 

### `03_eda_and_insights`
Análisis exploratorio de los datos. Incluye análisis geográfico de precios, distribución por barrio, tipo de operación y características de las propiedades.

### `04_kpi_pipeline`
Cálculo de KPIs (detallados en README_TP1) y exportación a un dataframe consolidado.

### `05_geocoding`
Resolución de coordenadas geográficas (latitud y longitud) a partir de calles y alturas de cada propiedad, usando dos APIs oficiales argentinas. El consenso entre ambas fuentes se guarda en `data/geocoding/`.

---

## Entrega 3 — Notebook principal: `TP3_Grupo_1`

Este es el notebook central de la tercera entrega. Integra todos los análisis avanzados del proyecto.

### 1. Setup e importación de datos
Carga del dataset enriquecido con coordenadas. Normalización de nombres de barrios para alinear con el GeoJSON oficial. Se descarta un subconjunto muy pequeño de ventas publicadas en pesos por inconsistencias de precio. Se agrega una columna con todos los precios convertidos a dólares, usando un tipo de cambio cacheado localmente para garantizar reproducibilidad entre corridas.

### 2. Enriquecimiento espacial
Para cada propiedad con coordenadas resueltas se calculan tres distancias geográficas mediante aproximación euclidiana corregida por latitud, válida para distancias cortas dentro de la ciudad:

- **Distancia al subte más cercano**: descargada desde datos abiertos del GCBA. Sirve como proxy de accesibilidad al transporte público.
- **Distancia al espacio verde más cercano**: proxy de calidad ambiental.
- **Distancia a la estación de tren más cercana**: captura accesibilidad en barrios con menor cobertura de subte.

Adicionalmente, se asigna a cada propiedad el **nivel socioeconómico de su barrio** (escala ordinal del 1 al 5) basado en clasificaciones del GCBA y datos del censo.

Se incluye una revisión de la cobertura del geocoding por barrio, dejando documentado el sesgo potencial en zonas con menos coordenadas resueltas (Puerto Madero es el de menor cobertura con un 68%).

Se generan mapas coropléticos con la distribución del precio por metro cuadrado y la distancia al subte por barrio. Al final de esta sección se guarda un checkpoint (`checkpoint_post_enriquecimiento.pkl`) que permite ejecutar los notebooks de hipótesis y exportación de forma independiente.

### 3. Validación de hipótesis
Las cuatro hipótesis del trabajo se validan en el notebook `TP3_hipotesis.ipynb` (ver más abajo), que carga el checkpoint generado en la sección anterior.

### 4. Reducción de dimensionalidad e índices sintéticos
Para reducir multicolinealidad y facilitar la interpretación de los modelos, se construyen tres índices:

**PCA sobre variables continuas** (precio/m², superficie, antigüedad): se retienen dos componentes que explican aproximadamente el 80% de la varianza.
- *PC1 — Índice de precio y superficie*: sube con propiedades grandes y caras por metro cuadrado. Perfil de gama media-alta.
- *PC2 — Score de Antigüedad*: sube con propiedades viejas y relativamente baratas. Se normaliza al rango [0, 1] como feature explícita para los modelos.

**MCA sobre amenities binarios**: equivalente del PCA para variables categóricas, aplicado sobre 26 amenities binarios. El primer componente se interpreta como **Índice de Lujo** (captura amenities premium: pileta, gimnasio, SUM, etc.).

**Índice de Confort**: construido de forma explícita como la proporción de seis amenities de comodidad cotidiana presentes en la propiedad (aire acondicionado, ascensor, agua caliente central, lavadero, portero, losa central). Complementa al Índice de Lujo capturando una dimensión distinta del valor.

Los tres índices se validan contra el precio por metro cuadrado en ventas: Lujo y Confort muestran correlaciones positivas significativas; el Score de Antigüedad muestra correlación negativa, consistente con su construcción.

### 5. Clustering para descubrir micro-mercados
Se aplica K-Means sobre un conjunto de variables que cubre tres dimensiones: características de la propiedad (precio/m², superficie, antigüedad) y entorno espacial (distancias al subte, espacios verdes y tren, nivel socioeconómico del barrio).

La cantidad de clusters se selecciona con tres métricas complementarias: método del codo, score de silueta e índice de Calinski-Harabasz. Se elige **k=4** como punto de quiebre más claro del codo, con una diferencia marginal respecto a k=5 en las otras métricas que no justifica la pérdida de interpretabilidad.

A cada cluster se le asigna un nombre comercial descriptivo generado dinámicamente a partir de sus medianas (por ejemplo: "departamentos compactos, antiguos, lejos del subte"). Estos nombres se usan luego como variable en los modelos y en el dashboard.

Se incluye también una corrida de **DBSCAN** como sanity check: identifica outliers que K-Means asigna a algún cluster por diseño, y confirma que K-Means es la opción correcta para la segmentación principal de negocio. 

Los resultados se visualizan con: heatmap de perfiles por cluster, scatter sobre el espacio del PCA, mapa coroplético del cluster dominante por barrio, mapa de rentabilidad neta a largo plazo, y scatter a nivel propiedad sobre el polígono de CABA.

### 6. Modelos explicativos
Se construyen dos modelos con distinto target:

**Precio por metro cuadrado (target continuo)**: se comparan tres modelos lineales — OLS, Ridge (L2) y Lasso (L1) — evaluados por R² y MAE en test y con validación cruzada de 5 folds. Se complementan con un árbol de decisión de profundidad 4 para generar reglas interpretables. El análisis incluye comparación de coeficientes estandarizados entre los tres modelos, permutation importance (caída de R² al aleatorizar cada variable) y curvas de sensibilidad por variable (variando cada feature entre sus percentiles 5 y 95, con el resto fijo en la mediana).

**Modalidad de alquiler (target binario)**: la variable objetivo es si el alquiler temporario rinde más que el largo plazo en el barrio de la propiedad. Se comparan regresión logística y árbol de clasificación. Se reportan matriz de confusión, classification report, AUC-ROC y odds ratios estandarizados.

La sección cierra con una **tabla de recomendación por barrio** con la modalidad sugerida, la rentabilidad esperada y el cluster dominante, orientada al inversor principiante.

### 7. Conclusiones, limitaciones y próximos pasos

Principales hallazgos:
- La cercanía al subte incide positivamente en el precio por metro cuadrado.
- Los barrios con mayor precio/m² no son los más rentables: hay correlación negativa entre precio y rentabilidad neta a largo plazo, lo que orienta al inversor hacia gama media.
- Los amenities tienen mayor peso en el precio de venta que en el de alquiler.
- Los tres índices sintéticos (Lujo, Confort, Antigüedad) capturan dimensiones distintas del valor de una propiedad y resultan relevantes en los modelos.
- El clustering identifica micro-mercados con perfiles de rentabilidad diferenciados.

Limitaciones documentadas: base de un solo período de scraping (sin análisis temporal), muestra pequeña de barrios turísticos para algunas hipótesis, nivel socioeconómico asignado a nivel barrio y no por radio censal, y dependencia del tipo de cambio del día de ejecución para las comparaciones absolutas en dólares.

### 8. Exportación para Power BI
La exportación de archivos vive en `TP3_power_bi_export.ipynb`, que carga el checkpoint del final de la sección 6 y produce los siguientes archivos para el dashboard:

- `fact_propiedades.csv` — una fila por propiedad
- `dim_barrios.csv` — una fila por barrio
- `dim_clusters.csv` — perfil de cada cluster con nombre y color
- `dim_puntos_referencia.csv` — estaciones de subte, tren y espacios verdes para overlay del mapa
- `dim_coeficientes_modelo.csv` — coeficientes Ridge e importancia por permutación
- `barrios.geojson` — polígonos de barrios para Shape Map

---

## Entrega 3 — Notebooks complementarios

### `TP3_hipotesis`
Valida las cuatro hipótesis planteadas en la introducción del trabajo:
1. Rentabilidad temporaria vs. largo plazo en barrios turísticos.
2. Mayor precio por metro cuadrado no implica mayor rentabilidad.
3. Los amenities aumentan el precio de venta pero no el de alquiler.
4. La cercanía al subte impacta en el precio por metro cuadrado.

Carga el checkpoint `checkpoint_post_enriquecimiento.pkl` y puede ejecutarse de forma independiente una vez corrida la sección 2 de `TP3_Grupo_1`.

### `TP3_power_bi_export`
Genera todos los archivos necesarios para el dashboard de Power BI. Requiere haber ejecutado `TP3_Grupo_1` hasta el final de la sección 6.

---

## Dependencias

```
pandas, numpy, matplotlib, seaborn, geopandas, scikit-learn, prince, scipy, requests, geopy
```

Instalación rápida:

```bash
pip install scikit-learn prince geopandas scipy matplotlib seaborn geopy
```

---

## Reproducibilidad

Todos los modelos y el clustering usan `SEED = 42` como semilla global, fijada tanto en `numpy.random` como en `random` y en el parámetro `random_state` de cada modelo de scikit-learn. El tipo de cambio se cachea localmente en `data/processed/tipo_cambio_cache.json` para que las conversiones a dólares sean consistentes entre corridas.

