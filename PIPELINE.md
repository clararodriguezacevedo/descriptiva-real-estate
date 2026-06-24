# Estructura del repositorio

```
descriptiva-real-estate/
├── data/
│   ├── raw/                                        # Datos crudos obtenidos por scraping
│   ├── geocoding/                                  # GeoJSONs y dataframe con coordenadas por propiedad
│   └── processed/                                  # Dataframes limpios, KPIs y archivos listos para análisis
├── notebooks/
│   ├── argenprop/                                  # Scraper de ArgenProp (ver README interno)
│   ├── zonaprop/                                   # Scraper de ZonaProp (ver README interno)
│   ├── 01_dataframe_maestro.ipynb
│   ├── 02_data_cleaning_and_normalization.ipynb
│   ├── 03_eda_and_insights.ipynb
│   ├── 04_kpi_pipeline.ipynb
│   ├── 05_geocoding.ipynb
│   ├── 06_hipotesis.ipynb
│   ├── 07_insights_y_modelos.ipynb
│   └── 08_powerbi_export.ipynb
└── dashboard/
    └── Tablero_Interactivo_Para_Inversor.pbix      # Ver README interno para entender el funcionamiento
```

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

## Scraping

Los datos provienen de dos portales inmobiliarios argentinos: **ArgenProp** y **ZonaProp**, dos portales inmobiliarios que muestran la oferta de distintos departamentos en venta, alquiler y alquiler temporal en Argentina. Cada uno tiene su propio scraper y README con instrucciones de uso en las carpetas `notebooks/argenprop/` y `notebooks/zonaprop/` respectivamente. Los archivos resultantes del scraping se guardan en `data/raw/`.

**Argenprop**
URLs: [Venta](https://www.argenprop.com/departamentos/venta/capital-federal) \- [Alquiler](https://www.argenprop.com/departamentos/alquiler/capital-federal) \- [Alquiler Temporal](https://www.argenprop.com/departamentos/alquiler-temporal/capital-federal)
Datos: precio, expensas, dirección, altura,  m², ambientes, piso, amenities, descripción.
Frecuencia: extracción única.
Tipo de datos: numéricos, textuales, dicotómicos.

**ZonaProp**
URLs: [Venta](https://www.zonaprop.com.ar/departamentos-venta-capital-federal.html) \- [Alquiler](https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal.html) \- [Alquiler Temporal](https://www.zonaprop.com.ar/departamentos-alquiler-temporal-capital-federal.html)
Datos: idem Argenprop. Permite cross-validación de precios.
Frecuencia: extracción única.
Tipo de datos: numéricos, textuales, dicotómicos.

## Pipeline de notebooks

### `01_dataframe_maestro`
Une los TSVs producidos por ambos scrapers y construye el dataframe maestro unificado. Cada fila del DataFrame maestro corresponde a un aviso único. Las columnas son:

| Campo | Tipo | Descripción |
| :---- | :---- | :---- |
| Fecha\_Scraping | date | Fecha de ejecución del scrapping (YYYY-MM-DD) |
| Posting\_ID | string | ID único del aviso  |
| Sitio | string | 'argenprop' o 'zonaprop' |
| Operación | string | 'venta', 'alquiler' o 'temporal' |
| Precio | string | Precio publicado (ej: 'USD 85.000', 'ARS 450.000') |
| Expensas | string | Expensas mensuales cuando figuran en el aviso |
| Calle | string | Nombre de la calle |
| Altura | string | Número de puerta |
| Piso | string | Piso del departamento, cuando figura |
| Barrio | string | Barrio de CABA  |
| Detalles | string | m², ambientes, baños, antigüedad (texto libre) |
| Descripción | string | Descripción del aviso (texto libre) |
| Link | string | URL completa del aviso |
| \+ 8 features | int 0/1 | Variables binarias/numéricas para identificar presencia/ausencia de amenities, losa\_central, aire\_acond, apto\_credito, cochera, seguridad, luminoso y balcon\_aterrazado.  |

### `02_data_cleaning_and_normalization`
Limpieza integral de datos: eliminación de duplicados, tratamiento de outliers y gestión de valores faltantes a partir de las monedas utilizadas (ARS y USD) y las operaciones (venta, alquiler temporario, alquiler largo plazo). El dataset final queda en 51.996 registros.

### `03_eda_and_insights`
Análisis exploratorio de los datos. Incluye análisis geográfico de precios, distribución por barrio, tipo de operación y características de las propiedades.

### `04_kpi_pipeline`
Cálculo de los siguientes KPIs y exportación a un dataframe consolidado. Los indicadores son calculados por barrio, con precios normalizados a USD:

| \# | KPI | Fórmula | Propósito |
| :---- | :---- | :---- | :---- |
| 1 | Rentabilidad Bruta Largo Plazo | (Alquiler Mensual Mediano × 12\) / Precio Venta Mediano × 100 | Rendimiento bruto anual sobre el capital invertido vía alquiler tradicional |
| 2 | Recupero de Inversión | Precio Venta / (Alquiler Mensual × 12\) | Años necesarios para recuperar la inversión; es el inverso del KPI 1 |
| 3 | Precio por m² | Precio Publicado / m² - mediana por barrio y tipo de operación | Normaliza el valor para comparar propiedades entre barrios |
| 4 | Rentabilidad Neta Largo Plazo | (Alquiler Anual − Expensas Anuales del Propietario\) / Precio Venta × 100 | Rentabilidad real descontando expensas en los casos donde las paga el propietario |
| 5 | Precio/m² Relativo por Barrio | Precio/m² de la propiedad / Mediana Precio/m² de su barrio | Identifica propiedades por debajo de la mediana del barrio (oportunidades de compra\) |
| 6 | Rentabilidad Bruta Temporario | (Alquiler Mensual Mediano Temporario × 12\) / Precio Venta Mediano × 100 | Rendimiento bruto anual si se alquila de forma temporaria |
| 7 | Índice Bruto Modalidad Óptima | Rentabilidad Bruta Temporario / Rentabilidad Bruta Largo Plazo | Índice > 1 indica que el temporario supera al largo plazo en términos brutos |
| 8 | Rentabilidad Neta Temporario | (Ingreso Anual Temporario − Expensas Anuales del Propietario\) / Precio Venta × 100 | Rentabilidad real temporaria; en Airbnb el propietario suele pagar las expensas, por lo que se descuentan en casi todos los casos |
| 9 | Índice Neto Modalidad Óptima | Rentabilidad Neta Temporario / Rentabilidad Neta Largo Plazo | Índice > 1 indica que el temporario supera al largo plazo en términos netos |

### `05_geocoding`
Resolución de coordenadas geográficas (latitud y longitud) a partir de calles y alturas de cada propiedad, usando dos APIs oficiales argentinas. El consenso entre ambas fuentes se guarda en `data/geocoding/`.

### `06_reduccion_y_clustering`
Carga el dataset enriquecido con coordenadas y construye los índices sintéticos del proyecto: PCA sobre variables continuas (precio/m², superficie, antigüedad) en dos componentes (*Índice de Precio y Superficie* y *Score de Antigüedad*), MCA sobre amenities binarios (*Índice de Lujo*) e *Índice de Confort* construido de forma explícita sobre seis amenities de uso cotidiano. Con esos índices y las variables espaciales, aplica K-Means (**k=4**, elegido por método del codo, silueta y Calinski-Harabasz) para segmentar el mercado en micro-mercados con nombre comercial propio, validado contra DBSCAN como sanity check. Cierra con mapas y heatmaps de perfil por cluster, y guarda un checkpoint (`checkpoint_post_clustering.pkl`) con el dataframe enriquecido y los objetos auxiliares (KPIs, capas geográficas, perfiles) para que `07_hipotesis` y `08_modelos_y_recomendaciones` puedan ejecutarse de forma independiente.
 
### `07_hipotesis`
Valida las cuatro hipótesis del proyecto:
1. En los barrios más turísticos, la rentabilidad neta temporaria va a ser más que la rentabilidad neta a largo plazo.
2. Los barrios con mayor precio de venta por m² no van a ser los que ofrezcan la mayor rentabilidad neta.
3. La presencia de amenities y extras incrementa el precio de venta con respecto a propiedades equivalentes sin ellos, pero estos aumentos no se reflejan en el precio de alquiler (aumentan las expensas pero no el alquiler).
4. La cercanía a estaciones de subte genera un aumento estadísticamente significativo en el valor del m².

Carga el checkpoint `checkpoint_post_clustering.pkl` y puede ejecutarse de forma independiente una vez corrido `06_reduccion_y_clustering`.
 
### `08_modelos_y_recomendaciones`
Carga el mismo checkpoint para construir dos modelos explicativos sobre el dataset enriquecido. El primero explica el **precio por metro cuadrado** (target continuo) comparando OLS, Ridge y Lasso, con árbol de decisión, permutation importance y curvas de sensibilidad como apoyo interpretativo; las variables con mayor peso son el score de antigüedad, el nivel socioeconómico del barrio, los m² totales, el Índice de Lujo y la cantidad de baños. El segundo predice la **modalidad de alquiler óptima** (target binario: temporario vs. largo plazo) comparando regresión logística y árbol de clasificación, con la distancia al subte como variable más relevante. Cierra con una **tabla de recomendación por barrio** (modalidad sugerida, rentabilidad esperada y cluster dominante) orientada al inversor principiante, y guarda el checkpoint final (`checkpoint_post_modelos.pkl`) para `09_powerbi_export`.

### `09_powerbi_export`
Genera todos los siguientes archivos, que son necesarios para el dashboard de Power BI: 
- `fact_propiedades.csv`: una fila por propiedad
- `dim_barrios.csv`: una fila por barrio
- `dim_clusters.csv`: perfil de cada cluster con nombre y color
- `dim_puntos_referencia.csv`: estaciones de subte, tren y espacios verdes para overlay del mapa
- `dim_coeficientes_modelo.csv`: coeficientes Ridge e importancia por permutación
- `barrios.geojson`: polígonos de barrios para Shape Map

El dashboard mismo se encuentra en `dashboard/` titulado `Tablero_Interactivo_Para_Inversor.pbix`