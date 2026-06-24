# Análisis del Mercado Inmobiliario de CABA

Trabajo práctico de análisis de datos sobre el mercado inmobiliario de la Ciudad Autónoma de Buenos Aires con el objetivo de realizar una recomendación informada hacia un inversor amateur interesado en comprar un departamento en CABA. El proyecto cubre el ciclo completo: scraping de datos, limpieza, análisis exploratorio, geocoding, validación de hipótesis, reducción de dimensionalidad, clustering, modelos predictivos y exportación a un dashboard en Power BI.

| Integrantes |  |
| ----- | :---: |
| Clara Rodriguez Acevedo | 66527 |
| Valentina Contrera | 66577 |
| Valentina Ludmila Darchuk | 66009 |

---

## Resumen ejecutivo

Scrapeamos y unificamos ~52.000 avisos de venta, alquiler y alquiler temporario de ArgenProp y ZonaProp en CABA, los limpiamos y enriquecimos con geocoding y variables espaciales (distancia a subte, tren y espacios verdes), y construimos un set de KPIs de rentabilidad por barrio. Sobre esa base validamos cuatro hipótesis, redujimos la dimensionalidad de las variables de la propiedad en tres índices interpretables (Lujo, Confort, Antigüedad), segmentamos el mercado en cuatro micro-mercados con K-Means y entrenamos modelos explicativos de precio por m² y de modalidad de alquiler óptima.

Los hallazgos centrales: **los barrios más caros no son los más rentables** (correlación negativa entre precio/m² y rentabilidad neta), **los amenities premium suben el precio tanto en venta como en alquiler** (el caso más fuerte es el gimnasio, que suma ~52% en venta y ~60% en alquiler), y **la antigüedad y el nivel socioeconómico del barrio son las variables que más explican el precio por m²**. La recomendación final para el inversor principiante es una tabla por barrio con la modalidad de alquiler sugerida, la rentabilidad esperada y el cluster dominante, priorizando barrios de gama media sobre los más caros.

---

## Contexto

Hoy en día, una de las formas más comunes de invertir es hacerlo en Real Estate. La compra, venta y alquiler de propiedades son operaciones que se realizan constantemente.

Sin embargo, el mercado inmobiliario porteño es confuso: la información de precios de venta, alquileres tradicionales y alquileres temporarios está dispersa en distintos portales, en distintas monedas y con criterios de publicación inconsistentes. El comprador minorista argentino no tiene visibilidad real sobre cuál barrio, qué tipología y qué modalidad de alquiler maximiza su rentabilidad para un departamento y además, opera bajo restricciones muy particulares: muchas veces compra al contado, en dólares, en un contexto donde la regulación de alquileres cambia cada dos años y donde el precio del metro cuadrado puede multiplicarse por cuatro entre dos barrios separados por seis kilómetros. Estas condiciones tienen una consecuencia directa: la primera compra es prácticamente irreversible. No hay refinanciación posible, y los costos de transacción de revender son altos. Por eso la decisión inicial define el rendimiento de la próxima década del patrimonio del inversor.

Entonces, para un inversionista nuevo en el mercado del Real Estate, comenzar puede ser intimidante sin suficiente conocimiento o experiencia previa. Por eso mismo, decidimos realizar un análisis que responda la siguiente pregunta: ¿Qué departamento conviene comprar para obtener el retorno de inversión más rápido según un barrio determinado? Asimismo, también queremos responder: ¿Qué tipo de alquiler es más conveniente? ¿Un alquiler temporario o un alquiler a largo plazo?

### Perfil del Cliente (Interlocutor)

**Inversor Independiente Principiante**
Nuestro cliente objetivo es una persona física que busca su primera inversión en un departamento en la Ciudad de Buenos Aires. Su duda central no es solo dónde comprar, sino también cómo alquilar: bajo la modalidad tradicional (contrato fijo con un inquilino) o bajo la modalidad temporal. Necesita evidencia cuantitativa para tomar una decisión estratégica antes de comprometer capital. Este perfil no incluye a personas especialistas en el mercado, personas con amplia experiencia previa o expertos en Real Estate.

---

## Dataset final y origen

Los datos provienen de dos portales inmobiliarios argentinos, **ArgenProp** y **ZonaProp**, con una extracción única de avisos de venta, alquiler y alquiler temporario en CABA. El dataset maestro original combina ambos scrapers en un dataframe con una fila por aviso (ver columnas en la sección de pipeline más abajo).

Después del proceso de limpieza (deduplicación, corrección de errores de moneda, tratamiento de outliers y de valores faltantes), el **dataset final queda en 51.996 registros**, distribuidos en los tres tipos de operación (venta, alquiler y alquiler temporario) y en ambas monedas (ARS y USD). Alquiler temporario es la operación con menor volumen pero igual reúne más de 8.000 filas, suficientes para sacar conclusiones sólidas en los tres tipos de operación. Palermo, Belgrano, Recoleta y Caballito son los barrios con mayor representación en el dataset, lo que coincide con su popularidad actual.

Sobre ese dataset limpio se calculan los 9 KPIs por barrio (rentabilidad bruta y neta, recupero de inversión, precio/m² relativo, índices de modalidad óptima (ver tabla completa en la sección de pipeline)), se resuelven coordenadas geográficas (con aproximadamente 1 de cada 7 avisos sin coordenadas resueltas, generalmente por falta de calle/altura), y se agregan variables espaciales y socioeconómicas para el resto del análisis.

---

## Decisiones de preprocesamiento

La limpieza fue uno de los componentes más pesados del proyecto, dado lo heterogéneo de los datos scrapeados. Las decisiones más relevantes:

- **Moneda y valores ficticios**: los precios marcados como "USD" se tomaron en dólares, el resto en pesos, y los marcados "Consultar" como NaN. Se detectaron valores simbólicos típicos de portales inmobiliarios (precios de "1 peso" o "111.111.111" para indicar "a consultar") y se trataron como faltantes en vez de precios reales.
- **Corrección de errores de clasificación de moneda**: se identificaron y reclasificaron registros donde el precio estaba en una moneda distinta a la indicada (ej. un alquiler de menos de $300.000 ARS es imposible en CABA en 2026 y casi seguro está en dólares). En total se reclasificaron 104 registros de ARS a USD y 153 de USD a ARS.
- **Outliers en precio**: se usó `precio_por_m2` como métrica central (en vez de precio absoluto) para no confundir tamaño con sobreprecio. Se aplicó winsorización por percentiles 1-99, adaptativa por segmento (operación + moneda + barrio, con fallback a operación + moneda cuando el barrio tenía menos de 30 registros), para no tratar como atípicas propiedades normales en barrios con rangos de precio muy distintos (ej. Puerto Madero vs. Villa Lugano).
- **Transformación logarítmica**: se aplicó `log1p` sobre los precios para estabilizar la varianza, dado que los precios inmobiliarios siguen una distribución log-normal.
- **Expensas**: se determinó un umbral de $2.000-3.000 ARS por debajo del cual un valor se considera "sin expensas reales" (ingresado como placeholder), usando un análisis de codo sobre la distribución ordenada de valores.
- **Valores faltantes**: se confirmó con un test chi-cuadrado que la ausencia de ciertos campos (ambientes, baños, antigüedad) depende del sitio de origen: por ejemplo, "ambientes" está prácticamente completo en ZonaProp (0,8% de faltantes) y casi vacío en ArgenProp (96,8%), y a la inversa para "antigüedad_años". Esto encuadra el patrón como faltante condicionado al sitio (MAR) y justificó una imputación diferenciada por sitio, cruzando datos entre ambos portales según m² cuando fue posible. Las columnas con cobertura insuficiente para ser confiables se descartaron.
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
| 3 | Los amenities suben el precio de venta pero no el de alquiler | Mann-Whitney por amenity y tipo de operación | **Rechazada en su forma original.** Los amenities (pileta, gimnasio, parrilla, SUM, balcón, baulera) resultaron estadísticamente significativos en las tres modalidades, no solo en venta. El caso más marcado es el gimnasio: +52% en precio de venta y +60% en alquiler (la modalidad de alquiler capturó incluso más premium que la venta). |
| 4 | La cercanía al subte aumenta el precio por m² | Spearman (n=24.974 propiedades con coordenadas) | **Rechazada en el sentido esperado.** Hay correlación significativa (Spearman = 0,137, p < 0,0001) pero de signo positivo: a mayor distancia al subte, mayor precio por m², lo opuesto a la intuición. Esto puede reflejar que las zonas premium de CABA (Puerto Madero, Recoleta) no son necesariamente las de mejor cobertura de subte, por lo que el efecto socioeconómico/de ubicación domina sobre el efecto puro de accesibilidad.

---

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

---

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
Limpieza integral de datos: eliminación de duplicados, tratamiento de outliers y gestión de valores faltantes a partir de las monedas utilizadas (ARS y USD) y las operaciones (venta, alquiler temporario, alquiler largo plazo). El dataset final queda en 51.996 registros (ver detalle de decisiones en la sección "Decisiones de preprocesamiento" más arriba).

### `03_eda_and_insights`
Análisis exploratorio de los datos. Incluye análisis geográfico de precios, distribución por barrio, tipo de operación y características de las propiedades (ver "Principales insights del análisis exploratorio" más arriba).

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

### `06_hipotesis`
Valida las cuatro hipótesis del proyecto (ver tabla de resultados completa en "Hipótesis y resultados estadísticos" más arriba):
1. En los barrios más turísticos, la rentabilidad neta temporaria va a ser más que la rentabilidad neta a largo plazo.
2. Los barrios con mayor precio de venta por m² no van a ser los que ofrezcan la mayor rentabilidad neta.
3. La presencia de amenities y extras incrementa el precio de venta con respecto a propiedades equivalentes sin ellos, pero estos aumentos no se reflejan en el precio de alquiler (aumentan las expensas pero no el alquiler).
4. La cercanía a estaciones de subte genera un aumento estadísticamente significativo en el valor del m².

Carga el checkpoint `checkpoint_post_enriquecimiento.pkl` y puede ejecutarse de forma independiente una vez corrida la sección 2 de `07_insights_y_modelos`.

### `07_insights_y_modelos`
Este notebook integra todos los análisis avanzados del proyecto.

#### 1. Setup e importación de datos
Carga del dataset enriquecido con coordenadas. Normalización de nombres de barrios para alinear con el GeoJSON oficial. Se descarta un subconjunto muy pequeño de ventas publicadas en pesos por inconsistencias de precio (en general, propiedades en mal estado que distorsionaban las conclusiones incluso convertidas a dólares). Se agrega una columna con todos los precios convertidos a dólares, usando un tipo de cambio cacheado localmente para garantizar reproducibilidad entre corridas.

#### 2. Enriquecimiento espacial
Para cada propiedad con coordenadas resueltas se calculan tres distancias geográficas mediante aproximación euclidiana corregida por latitud, válida para distancias cortas dentro de la ciudad:

- **Distancia al subte más cercano**: descargada desde datos abiertos del GCBA. Sirve como proxy de accesibilidad al transporte público.
- **Distancia al espacio verde más cercano**: proxy de calidad ambiental.
- **Distancia a la estación de tren más cercana**: captura accesibilidad en barrios con menor cobertura de subte.

Adicionalmente, se asigna a cada propiedad el **nivel socioeconómico de su barrio** (escala ordinal del 1 al 5) basado en clasificaciones del GCBA y datos del censo.

Se incluye una revisión de la cobertura del geocoding por barrio, dejando documentado el sesgo potencial en zonas con menos coordenadas resueltas (Puerto Madero es el de menor cobertura con un 68%).

Se generan mapas coropléticos con la distribución del precio por metro cuadrado y la distancia al subte por barrio. Al final de esta sección se guarda un checkpoint (`checkpoint_post_enriquecimiento.pkl`) que permite ejecutar los notebooks de hipótesis y exportación de forma independiente.

#### 3. Reducción de dimensionalidad e índices sintéticos
Para reducir multicolinealidad y facilitar la interpretación de los modelos, se construyen tres índices:

**PCA sobre variables continuas** (precio/m², superficie, antigüedad): se retienen dos componentes que explican aproximadamente el 80% de la varianza.
- *PC1: Índice de precio y superficie*: sube con propiedades grandes y caras por metro cuadrado. Perfil de gama media-alta.
- *PC2: Score de Antigüedad*: sube con propiedades viejas y relativamente baratas. Se normaliza al rango [0, 1] como feature explícita para los modelos.

**MCA sobre amenities binarios**: equivalente del PCA para variables categóricas, aplicado sobre los amenities binarios. El primer componente explica un 13,43% de la varianza por sí solo y se interpreta como **Índice de Lujo** (captura amenities premium: pileta, gimnasio, SUM, etc.).

**Índice de Confort**: construido de forma explícita como la proporción de seis amenities de comodidad cotidiana presentes en la propiedad (aire acondicionado, ascensor, agua caliente central, lavadero, portero, losa central). Complementa al Índice de Lujo capturando una dimensión distinta del valor.

Los tres índices se validan contra el precio por metro cuadrado en ventas: Lujo tiene una correlación positiva considerable, Confort una correlación positiva más leve, y el Score de Antigüedad una correlación negativa marcada, consistente con su construcción.

#### 4. Clustering para descubrir micro-mercados
Se aplica K-Means sobre un conjunto de variables que cubre tres dimensiones: características de la propiedad (precio/m², superficie, antigüedad) y entorno espacial (distancias al subte, espacios verdes y tren, nivel socioeconómico del barrio).

La cantidad de clusters se selecciona con tres métricas complementarias: método del codo, score de silueta e índice de Calinski-Harabasz. Se elige **k=4** como punto de quiebre más claro del codo (la inercia cae fuerte entre k=3 y k=4, ~37 mil unidades, y luego las caídas son marginales), con una diferencia menor respecto a k=5 en silueta (0,203 → 0,224) y Calinski-Harabasz (9.819 → 10.184) que no justifica la pérdida de interpretabilidad de un cluster adicional.

A cada cluster se le asigna un nombre comercial descriptivo generado dinámicamente a partir de sus medianas (por ejemplo: "departamentos compactos, antiguos, lejos del subte"). El primer cluster agrupa propiedades relativamente económicas y antiguas; en el otro extremo, el segundo cluster reúne las propiedades más grandes y con mayor precio por m² (aunque no necesariamente en edificios nuevos); los clusters restantes representan rangos medios. Estos nombres se usan luego como variable en los modelos y en el dashboard.

Se incluye también una corrida de **DBSCAN** como sanity check: no devolvió más de un cluster significativo (solo separó ruido), por lo que se confirma a K-Means como la opción adecuada para la segmentación principal de negocio.

Los resultados se visualizan con: heatmap de perfiles por cluster, scatter sobre el espacio del PCA, mapa coroplético del cluster dominante por barrio, mapa de rentabilidad neta a largo plazo, y scatter a nivel propiedad sobre el polígono de CABA.

#### 5. Modelos explicativos
Se construyen dos modelos con distinto target:

**Precio por metro cuadrado (target continuo)**: se comparan tres modelos lineales (OLS, Ridge (L2) y Lasso (L1)) evaluados por R² y MAE en test y con validación cruzada de 5 folds. Lasso muestra una mejora marginal en MAE, pero los tres modelos resultan prácticamente equivalentes: la regularización no aporta una mejora significativa frente a OLS para este conjunto de variables. Según los coeficientes estandarizados, las variables con mayor impacto sobre el precio por m² son **score de antigüedad** (relación fuertemente negativa), **nivel socioeconómico del barrio**, **m² totales**, **Índice de Lujo** y **cantidad de baños**. Estos resultados se confirman con un árbol de decisión de profundidad 4 (mismas variables dominantes en los primeros splits), con permutation importance y con curvas de sensibilidad por variable (variando cada feature entre sus percentiles 5 y 95, con el resto fijo en la mediana).

**Modalidad de alquiler (target binario)**: la variable objetivo es si el alquiler temporario rinde más que el largo plazo en el barrio de la propiedad. Se comparan regresión logística y árbol de clasificación. Ambos modelos logran un AUC muy alto (~0,99 y ~0,97 respectivamente), pero esto debe interpretarse con cautela: el target fue construido a nivel barrio y luego asignado a cada propiedad, por lo que el modelo puede estar capturando patrones espaciales/socioeconómicos del barrio más que diferencias individuales entre propiedades, y la clase "temporario" es minoritaria (f1-score de 0,34 para esa clase), lo que infla el AUC. Para alquiler temporario, la variable más relevante y menos visible en análisis previos es la **distancia al subte**, consistente con que los inquilinos temporarios suelen priorizar buena conectividad.

La sección cierra con una **tabla de recomendación por barrio** con la modalidad sugerida (temporario si su rentabilidad neta supera a la de largo plazo, largo plazo en caso contrario o de empate), la rentabilidad esperada y el cluster dominante, orientada al inversor principiante.

#### 6. Conclusiones
Principales hallazgos:
- La cercanía al subte tiene una relación estadísticamente significativa con el precio por metro cuadrado, aunque de signo contrario al esperado (ver Hipótesis 4): la correlación es positiva, probablemente porque las zonas premium de CABA no coinciden necesariamente con las de mejor cobertura de subte.
- Los barrios con mayor precio/m² no son los más rentables: hay correlación negativa entre precio y rentabilidad neta a largo plazo, lo que orienta al inversor hacia gama media.
- Los amenities tienen mayor peso en el precio de venta que en el de alquiler, pero también suben el precio de alquiler de forma significativa.
- Los tres índices sintéticos (Lujo, Confort, Antigüedad) capturan dimensiones distintas del valor de una propiedad y resultan relevantes en los modelos.
- El clustering identifica micro-mercados con perfiles de rentabilidad diferenciados.

### `08_powerbi_export`
Genera todos los archivos necesarios para el dashboard de Power BI. Requiere haber ejecutado `07_insights_y_modelos` hasta el final de la sección 6, ya que carga el checkpoint del final de esta sección y produce los siguientes archivos para el dashboard:

- `fact_propiedades.csv`: una fila por propiedad
- `dim_barrios.csv`: una fila por barrio
- `dim_clusters.csv`: perfil de cada cluster con nombre y color
- `dim_puntos_referencia.csv`: estaciones de subte, tren y espacios verdes para overlay del mapa
- `dim_coeficientes_modelo.csv`: coeficientes Ridge e importancia por permutación
- `barrios.geojson`: polígonos de barrios para Shape Map

El dashboard mismo se encuentra en `dashboard/` titulado `Tablero_Interactivo_Para_Inversor.pbix`

---

## Conclusiones y recomendaciones de negocio

Para el inversor principiante, la evidencia recolectada sugiere:

1. **No comprar en los barrios más caros buscando rentabilidad.** El precio por m² más alto (Puerto Madero, Recoleta, Palermo, Belgrano) no se traduce en mejor retorno; de hecho la correlación con la rentabilidad neta es negativa. Conviene mirar barrios de gama media.
2. **Los amenities premium (pileta, gimnasio) son una inversión defendible**, ya que su efecto sobre el precio se traslada también al alquiler; no es solo un costo de venta que no se recupera.
3. **La modalidad de alquiler óptima depende del barrio y del perfil de la propiedad**, no hay una respuesta universal. La distancia al subte es un factor relevante específicamente para decidir si conviene apuntar a alquiler temporario.
4. La hipótesis de que los barrios turísticos rinden mejor en alquiler temporario **no se pudo confirmar con la evidencia disponible**; en la muestra analizada, el largo plazo rindió incluso mejor en esos barrios.
5. El dashboard de Power BI permite explorar estas conclusiones de forma interactiva, filtrando por barrio, cluster y tipo de operación.

---

## Limitaciones del estudio y líneas futuras

- **Sin componente temporal**: toda la base proviene de un único período de scraping, por lo que no es posible validar tendencias ni evaluar la estabilidad de los segmentos a lo largo del tiempo. Una línea futura natural es repetir el scraping periódicamente para construir una serie temporal.
- **Tipo de cambio cacheado**: la conversión ARS→USD depende del día en que se ejecutó el notebook. Las conclusiones relativas (qué barrio rinde más que otro) son estables, pero las cifras absolutas en dólares pueden variar entre corridas.
- **Muestra chica para la Hipótesis 1**: solo cuatro barrios se clasificaron como turísticos, lo que reduce la potencia del test de Mann-Whitney; es posible que exista una diferencia real que el test no pudo detectar con tan pocos casos.
- **Nivel socioeconómico aproximado**: se asignó por barrio a partir de clasificaciones publicadas y conocimiento general de la ciudad, no a partir de un dato fino por radio censal. Se podría refinar con datos oficiales del INDEC/GCBA a nivel comuna.
- **Cobertura de geocoding desigual**: aproximadamente 1 de cada 7 avisos no tiene coordenadas resueltas, y la cobertura varía por barrio (Puerto Madero es el caso más bajo, con 68%), lo que introduce un sesgo potencial en los análisis espaciales para esos barrios.
- **Clustering hecho sobre ventas en dólares**: los micro-mercados descubiertos no son directamente extrapolables al mercado de alquileres, que podría tener su propia segmentación.
- **Modelo de modalidad de alquiler con target a nivel barrio**: el AUC alto del modelo de modalidad óptima debe leerse con cautela, ya que el target se construyó a nivel barrio y luego se asignó a cada propiedad individual, por lo que el modelo puede estar capturando principalmente el efecto del barrio y no diferencias entre propiedades específicas. Además, la clase "temporario" es minoritaria, lo que puede dar una imagen de desempeño más optimista de la real.

---
 
## De prototipo a producción
 
Hoy el proyecto es una secuencia de notebooks que se corren a mano sobre un scraping puntual. Es importante notar que este caso es de **inferencia Batch (offline)**, no una API en tiempo real: no hay un usuario esperando una predicción puntual, sino un proceso programado (ej. semanal) que recalcula KPIs, clusters y modelos sobre todo el universo de propiedades. Esto simplifica el despliegue frente a, por ejemplo, un caso de scoring de fraude con latencia crítica.
 
Entonces, llevarlo a producción implicaría:
 
- **Empaquetado**: serializar los modelos (Ridge/Lasso, regresión logística, K-Means) con `joblib` (más adecuado que Pickle u ONNX para este tipo de modelos de scikit-learn) y unificar la limpieza, el enriquecimiento espacial y los índices sintéticos en un único objeto `Pipeline`, para que cada corrida nueva de scraping pase por exactamente los mismos pasos que los datos de entrenamiento.
- **Validación de inputs**: hoy gran parte de la limpieza consiste en detectar a posteriori errores ya cargados en los datos (precios "a consultar" como "1 peso", monedas mal clasificadas). En producción convendría validar cada aviso contra un esquema (ej. Pydantic) en el momento del scraping, antes de que entre al pipeline.
- **Monitoreo de Data Drift**: test de Kolmogorov-Smirnov para variables numéricas (precio/m², superficie) y test Chi-cuadrado para categóricas (mix de barrios, proporción ARS/USD), comparando cada corrida nueva contra la anterior, más alertas simples ante categorías nunca vistas (barrios o segmentos nuevos).
- **Concept Drift**: la relación entre variables y precio también puede cambiar con el tiempo (ej. la relación entre distancia al subte y precio/m², que en este análisis salió positiva y contraria a la intuición, podría invertirse si cambia la regulación de alquileres o el contexto cambiario), lo que justifica re-validar las hipótesis periódicamente en vez de asumirlas permanentes.
- **Reentrenamiento y dashboard**: reentrenar modelos y clustering en una cadencia más espaciada que el scraping (ej. mensual), versionando los artefactos para poder hacer rollback, y publicar el `.pbix` en Power BI Service con un dataflow conectado a un storage compartido y actualización programada, en vez de exportar y subir el archivo a mano.

El desarrollo completo de esta reflexión está en la sección 7.4 de `07_insights_y_modelos.ipynb`.
 
---

## Reproducibilidad

Todos los modelos y el clustering usan `SEED = 42` como semilla global, fijada tanto en `numpy.random` como en `random` y en el parámetro `random_state` de cada modelo de scikit-learn. El tipo de cambio se cachea localmente en `data/processed/tipo_cambio_cache.json` para que las conversiones a dólares sean consistentes entre corridas.