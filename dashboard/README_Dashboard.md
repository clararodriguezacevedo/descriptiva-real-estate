# README: Dashboard "Real Estate" (Inversión en CABA)

Este documento explica qué muestra cada página del dashboard, cómo navegarlo, y cómo un inversor puede usarlo.

---

## Estructura general

El dashboard tiene 5 páginas, navegables desde la página de inicio ("Real Estate") o con las flechas de navegación arriba a la derecha:

1. Visión General del Mercado
2. Mapa Espacial
3. Segmentación por Clusters
4. Variables y Relaciones
5. KPIs de negocio y prescriptiva

Todas las páginas comparten los mismos slicers en el panel izquierdo: **Barrio**, **Precio USD** (rango), **Operación** (Alquiler Temporal / Alquiler / Venta), y **Cluster**. Estos filtros están sincronizados, así que cambiarlos en una página afecta a las demás.

La página 5 tiene un slicer adicional: **Modalidad** (Largo Plazo / Temporario), que solo afecta las medidas de rentabilidad y recupero, no filtra las propiedades.

---

## Página 1: Visión General del Mercado

**Objetivo:** dar una foto rápida del tamaño y composición del mercado antes de explorar el detalle.

**Qué muestra:**
- 3 tarjetas KPI: precio mediano por m² (USD), cantidad total de propiedades, y m² promedio.
- Gráfico de torta de **Operaciones**: distribución entre Venta, Alquiler y Alquiler Temporal.
- **Treemap "Cantidad de Propiedades por Barrio (Top 15)"**, coloreado por cluster dominante. Palermo, Recoleta y Belgrano son los barrios con mayor volumen de publicaciones.
- **Histograma de precio USD/m²**, que muestra cómo se concentra la mayoría de las propiedades en el rango bajo, con una cola larga de propiedades caras (Puerto Madero y similares).

**Para qué le sirve al inversor:** establece el contexto inicial, "así es el mercado hoy", antes de pasar a las páginas más analíticas.

---

## Página 2: Mapa Espacial

**Objetivo:** mostrar la dimensión geográfica del mercado: dónde están las propiedades y cómo varía el precio por zona.

**Qué muestra:**
- **Shape Map (coroplético)** de precio USD/m² mediano por barrio. Los tonos más oscuros (verde intenso, Puerto Madero diferenciado en azul, ya que presenta precios mucho mayores al resto) marcan los barrios más caros. En el tooltip se puede ver la rentabilidad a largo plazo de los barrios.
- **Mapa de Puntos de Interés**: subte, tren y espacios verdes, con botones para alternar entre capas.
- **Mapa de burbujas de Propiedades**: cada punto es una propiedad, con tamaño proporcional al promedio de m² y color según precio USD/m².

**Para qué le sirve al inversor:** es el bloque de exploración visual pura. Sirve para ver cómo el precio se concentra en el corredor norte (Núñez, Belgrano, Palermo, Recoleta, Puerto Madero) y cae hacia el sur y el oeste; y además notar el comportamiento casi opuesto que tiene la rentabilidad.

---

## Página 3: Segmentación por Clusters

**Objetivo:** explicar que el mercado no es homogéneo, sino que existen 4 micro-mercados con perfiles distintos, identificados mediante K-Means.

**Los 4 clusters:**

| Color | Cluster | Perfil |
|---|---|---|
| Negro | - | Selección "todo" (no es un cluster real) |
| Azul | Cluster 0 | Departamentos antiguos |
| Naranja | Cluster 1 | Departamentos lejos del subte |
| Verde | Cluster 2 | Departamentos en barrios de alto nivel socioeconómico |
| Rojo | Cluster 3 | Departamentos amplios y antiguos, en barrios de alto nivel socioeconómico |

**Qué muestra:**
- **Shape Map** coloreado por cluster dominante por barrio. Se ve claramente la separación geográfica: el cluster verde domina el corredor norte, el azul el centro, y el naranja el sur y el oeste.
- **Gráfico "Índices por Clusters"**: compara índice de lujo, distancia al subte y score de antigüedad entre los 4 clusters, para ver como se compone cada uno. Por ejemplo, el Cluster 1 (lejos del subte) se distingue por su alta distancia al subte; el resto tiene perfiles más parecidos en esa variable.
- **Scatter "m² total y Precio USD/m2"**, coloreado por cluster. Permite ver cómo los clusters 2 y 3 (alto nivel socioeconómico) concentran los precios más altos, mientras que 0 y 1 quedan en el rango bajo.

**Para qué le sirve al inversor:** es el punto donde se introduce la idea de que "el mercado no es uno, son cuatro", permitiendo razonar en términos de segmentos y no de barrios sueltos.

---

## Página 4: Variables y Relaciones

**Objetivo:** mostrar, desde el lado más técnico, qué variables explican el precio por m² y cómo se separan los clusters en el espacio reducido.

**Qué muestra:**
- **Bar chart "Importancia Permutación por variable y signo"**: ordena las variables del modelo Ridge según cuánto cae el R² al aleatorizarlas. `score_antiguedad` aparece como la más relevante (signo negativo), seguida de `antiguedad_años` (signo positivo), `nivel_socioeconomico`, `índice_lujo`, y los dummies de cluster.
- **Gráfico "Mediana precio m² según ambientes"**: bar chart con barras de error (sustituto del boxplot) mostrando cómo sube el precio por m² a medida que aumentan los ambientes, con su dispersión.
- **Scatter PCA**: proyecta las propiedades en dos componentes principales (`pca_precio_sup` y `pca_antiguedad`), coloreado por cluster. Sirve como validación visual de que el clustering capturó una separación real: el Cluster 3 (rojo) se distingue claramente del resto en el eje de antigüedad.

**Para qué le sirve al inversor:** cierra la parte analítica/cuantitativa antes de pasar a la página de decisión.

---

## Página 5: KPIs de negocio y prescriptiva

**Esta es la página ejecutiva: la que responde "¿dónde conviene invertir?"**

### Qué muestra

- **Gauge de Rentabilidad neta (%)**: muestra el promedio de rentabilidad neta de las propiedades visibles según los filtros activos. Reacciona a precio, barrio, cluster y modalidad.
- **Tarjeta "% Prop. oportunidad"**: porcentaje de propiedades en venta (dentro del conjunto filtrado) cuyo precio por m² está al menos 15% por debajo de la mediana de su barrio (`es_oportunidad = 1` si `precio_m2_relativo_barrio < 0.85`).
- **Tarjeta "Modalidad Óptima"**: indica si, en promedio, conviene más el alquiler a Largo Plazo o Temporario para el conjunto de barrios filtrado, según cuál tiene mayor rentabilidad neta.
- **Tarjeta "Años para recupero"**: cuánto tarda en recuperarse el capital invertido, en promedio, sobre las propiedades filtradas.
- **Bar chart "Rentabilidad neta LP (%) por Barrio"**: ranking de barrios ordenado por rentabilidad. Reacciona al slicer de Modalidad (Largo Plazo / Temporario) y muestra la rentabilidad correspondiente a la modalidad seleccionada.
- **Tabla "Propiedades Oportunidad en Venta que cumplen los requisitos ingresados"**: lista las propiedades en venta marcadas como oportunidad, con `propiedad_id`, barrio, precio y precio USD/m². Ordenada de forma que las más subvaluadas (menor precio relativo al barrio) aparecen primero.

### El slicer de Modalidad: qué filtra y qué no

A diferencia de los demás slicers, **Modalidad no filtra las propiedades de la tabla ni del bar chart de barrios por cantidad**. Es una tabla desconectada del modelo que solo controla qué columna de rentabilidad usan las medidas (Largo Plazo vs Temporario). Esto es intencional: la modalidad es una decisión sobre cómo operar la propiedad después de comprarla, no un atributo de la propiedad en sí. Por eso la tabla de oportunidades siempre muestra propiedades en venta, sin importar qué modalidad esté seleccionada.

---

## Demo guiada para el inversor (flujo de la página 5)

Esta es la secuencia pensada para mostrar el dashboard en vivo, simulando la consulta que haría un inversor real:

**Acción 1: Presupuesto.** Mover el slicer de Precio USD para fijar el techo en el presupuesto máximo del inversor. El dashboard recalcula automáticamente el gauge, las tarjetas y el ranking de barrios, descartando los barrios donde ese presupuesto no alcanza para una propiedad estándar.

**Acción 2: Ranking personalizado.** Con el presupuesto aplicado, el bar chart de barrios por rentabilidad neta muestra el top de oportunidades dentro de ese rango. Estos son barrios que normalmente no tenemos en mente como buenas opciones de inversión inmobiliaria. Esta es justamente la idea del análisis.

**Acción 3: Modalidad Temporario.** Cambiar el slicer de Modalidad a "Temporario". El gauge, la tarjeta de modalidad óptima, los años de recupero y el ranking de barrios se recalculan usando la rentabilidad temporaria en lugar de la de largo plazo.

**Acción 4: Modalidad Largo Plazo.** Volver el slicer a "Largo Plazo". El ranking se reordena: distintos barrios pasan a liderar, mostrando que la decisión de modalidad cambia la recomendación.

**Acción 5: Foco en un barrio.** Seleccionar un barrio puntual desde el slicer de Barrio (por ejemplo, Nueva Pompeya). Todos los visuales de la página se filtran a ese barrio: el gauge muestra su rentabilidad específica, la tarjeta de años de recupero su valor puntual, y la tabla de oportunidades solo sus propiedades en venta subvaluadas. Aca es donde mejor resulta la página, porque el gauge y las tarjetas se calculan por barrio. Además, se puede tomar el ID de las propiedades de Argenprop, para ir a verlas en el sitio oficial, analizarlas con mayor profundidad y cuando el inversor se decida, poder comprarla.

Entonces, la decisión del inversor deja de depender de una opinión de mercado y pasa a sostenerse sobre datos cuantificables, explorables en tiempo real.

---

## Link al Tablero:
[Tablero Interactivo - Power BI Service](https://app.powerbi.com/view?r=eyJrIjoiNWExMTc5NDMtOTBhMS00NGY3LWIzMTktNWY0MDQ0NDM3MWM5IiwidCI6ImExZjUwYTk3LTIxYzAtNDlhNy1hOWQ0LWYyNDRlYmI0MmRhNyIsImMiOjR9)