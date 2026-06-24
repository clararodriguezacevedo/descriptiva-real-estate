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

El desarrollo completo de esta reflexión está en la sección 7.4 de `08_modelos_y_recomendaciones.ipynb`.
 
---

## Reproducibilidad

Todos los modelos y el clustering usan `SEED = 42` como semilla global, fijada tanto en `numpy.random` como en `random` y en el parámetro `random_state` de cada modelo de scikit-learn. El tipo de cambio se cachea localmente en `data/processed/tipo_cambio_cache.json` para que las conversiones a dólares sean consistentes entre corridas.