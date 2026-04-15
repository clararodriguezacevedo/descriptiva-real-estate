
**15/04/2026**

**Analítica Descriptiva**

**Trabajo Práctico N°1 : Primera pre-entrega**

| Grupo N°1 |  |
| ----- | :---: |
| Clara Rodriguez Acevedo | 66527 |
| Valentina Contrera | 66577 |
| Valentina Ludmila Darchuk | 66009 |

# 

# **1\. Contexto y Situación de Negocio**

Hoy en día, una de las formas más comunes de invertir es hacerlo en Real Estate. La compra, venta y alquiler de propiedades son operaciones que se realizan constantemente. Para un inversionista nuevo en el mercado del Real Estate, comenzar puede ser intimidante sin suficiente conocimiento o experiencia previa. Por eso mismo, decidimos realizar un análisis que responda la siguiente pregunta: ¿Qué departamento conviene comprar para obtener el retorno de inversión más rápido según un barrio determinado? Asimismo, también queremos responder: ¿Qué tipo de alquiler es más conveniente? ¿Un alquiler temporario o un alquiler a largo plazo? 

## **1.1 Contexto**

El mercado inmobiliario porteño es confuso: la información de precios de venta, alquileres tradicionales y alquileres temporarios está dispersa en distintos portales, en distintas monedas y con criterios de publicación inconsistentes. El inversor no tiene visibilidad real sobre cuál barrio, qué tipología y qué modalidad de alquiler maximiza su rentabilidad para un departamento.

## **1.2 Perfil del Cliente (Interlocutor)**

**Inversor Independiente Principiante**  
Nuestro cliente objetivo es una persona física que busca su primera inversión en un departamento en la Ciudad de Buenos Aires. Su duda central no es solo dónde comprar, sino también cómo alquilar: bajo la modalidad tradicional (contrato fijo con un inquilino) o bajo la modalidad temporal. Necesita evidencia cuantitativa para tomar una decisión estratégica antes de comprometer capital. Este perfil no incluye a personas especialistas en el mercado, personas con amplia experiencia previa o expertos en Real Estate. 

# **2\. Preguntas Clave por Nivel de Análisis**

## **2.1 Nivel Descriptivo \- ¿Qué está pasando?**

* ¿Cuál es el precio del metro cuadrado en venta de departamentos por barrio?  
* ¿Cuál es el precio mensual de alquiler a largo plazo por barrio?  
* ¿Cuáles son las diferencias entre las propiedades que se suelen alquilar a largo y a corto plazo?

## **2.2 Nivel Diagnóstico \- ¿Por qué está pasando?**

* ¿Qué suele hacer que varíen los precios del metro cuadrado en venta dentro del mismo barrio?  
* Misma pregunta, pero con precios de alquiler.  
* ¿Hay barrios en los cuales hay una diferencia importante de oferta entre alquileres temporarios y alquileres a largo plazo? ¿Cuáles son las diferencias de características entre ambos?

## **2.3 Nivel Predictivo \- ¿Qué va a pasar?**

* Dado el perfil de cierta propiedad, ¿cuántos meses tardaría en recuperarse la inversión inicial? ¿Con alquiler a largo plazo? ¿Y con alquiler temporal?   
* ¿Podemos estimar la rentabilidad esperada de una propiedad no listada en Argenprop o Zonaprop, basándonos en sus vecinos comparables?

## **2.4 Nivel Prescriptivo \- ¿Qué deberíamos hacer?**

* ¿Qué barrio y tipología específica maximiza la rentabilidad bruta para el inversor según su presupuesto?  
* ¿En qué zonas conviene optar por alquiler temporal sobre tradicional, y en cuáles no vale la pena la complejidad operativa?

# **3\. Definición de KPIs**

Los siguientes indicadores serán calculados para cada barrio:

| KPI | Fórmula | Propósito |
| :---- | :---- | :---- |
| Rentabilidad Bruta Largo plazo | (Alquiler Mensual × 12\) / Precio Venta | Mide el rendimiento anual sobre el capital invertido |
| Rentabilidad Bruta Temporario | (Tarifa Diaria de zona \* Ocupación Estimada)/ Precio de Venta | Mide el rendimiento sobre el capital invertido si se decide alquilar por de forma temporaria..  |
| Recupero de Inversión Largo Plazo | Precio Venta / (Alquiler Mensual × 12\)  | Años necesarios para recuperar la inversión |
| Precio/m² | Precio Publicado / Superficie (m²) | Normaliza el valor para comparar entre propiedades |
| Ocupación Estimada | 365 \- Ocupación anual promedio por barrio  | Forma de aproximar la ocupación esperada |
| Índice bruto modalidad óptima | Rentabilidad Bruta temp/ Rentabilidad bruta LP | Comparación de ambas modalidades |
| Rentabilidad Neta Largo plazo | Rentabilidad Bruta Largo plazo \- costos operativos | Descuenta los costos inmobiliarios, reparaciones  |
| Rentabilidad Neta Temporario | Rentabilidad Bruta Temporario \- costos operativos | Descuenta los costos inmobiliarios, reparaciones, costos de limpieza  |
| Índice neto modalidad óptima | Rentabilidad Neto temp/ Rentabilidad neto LP | Comparación de ambas modalidades |

# **4\. Hipótesis Iniciales a Validar**

1. En los barrios más turísticos, la rentabilidad neta temporaria va a ser más que la rentabilidad neta a largo plazo, con una diferencia estadísticamente significativa.  
2. Los barrios con mayor precio de venta por m² no van a ser los que ofrezcan la mayor rentabilidad neta. Si no, se espera que barrios de precio intermedio (como Caballito, Villa Crespo o Almagro) tengan una rentabilidad neta mayor estadísticamente significativa.  
3. La presencia de amenities y extras incrementa el precio de venta con respecto a propiedades equivalentes sin ellos, pero estos aumentos no se reflejan en el precio de alquiler (aumentan las expensas pero no el alquiler). Se puede hacer un análisis de ANOVA.  
4. La cercanía a estaciones de subte genera un aumento estadísticamente significativo en el valor del m².

# **5\. Fuentes de Datos**

## **5.1 Fuentes Primarias (Web Scraping)**

Los siguientes son dos portales inmobiliarios que muestran la oferta de distintos departamentos en venta, alquiler y alquiler temporal en Argentina. 

**Argenprop**  
URLs: [Venta](https://www.argenprop.com/departamentos/venta/capital-federal) \- [Alquiler](https://www.argenprop.com/departamentos/alquiler/capital-federal) \- [Alquiler Temporal](https://www.argenprop.com/departamentos/alquiler-temporal/capital-federal)  
Datos: precio, expensas, dirección, altura,  m², ambientes, piso, amenities, descripción.  
Frecuencia: extracción única \+ actualización semanal.  
Tipo de datos: numéricos, textuales, dicotómicos.

**ZonaProp**  
URLs: [Venta](https://www.zonaprop.com.ar/departamentos-venta-capital-federal.html) \- [Alquiler](https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal.html) \- [Alquiler Temporal](https://www.zonaprop.com.ar/departamentos-alquiler-temporal-capital-federal.html)  
Datos: idem Argenprop. Permite cross-validación de precios.  
Frecuencia: extracción única \+ actualización semanal.  
Tipo de datos: numéricos, textuales, dicotómicos.

## **5.2 Fuentes Secundarias (APIs y Datasets Públicos)**

APIs y datasets que tenemos planificado utilizar para realizar un análisis más profundo. 

| Nombre | URL | Datos |
| :---- | :---- | :---- |
| GCBA \- Comunas y Barrios | data.buenosaires.gob.ar | Polígonos GeoJSON de barrios y comunas para análisis espacial |
| BCRA \- Tipo de Cambio | estadisticasbcra.com.ar / API BCRA | Serie temporal USD/ARS para normalizar precios en pesos |
| GCBA: Estaciones de subte | https://cdn.buenosaires.gob.ar/datosabiertos/datasets/sbase/subte-estaciones/estaciones-de-subte.csv | Listado de las latitudes y longitudes de las estaciones de cada línea.  |

## 

## **5.3 Estructura del Repositorio**

**Arquitectura GitHub**: **descriptiva-real-estate**

* data/raw           
  * los 6 tsv extraídos (venta, alquiler, alquiler temporal; de argenprop y zonaprop)  
  * dataframe\_maestro.tsv (utiliza Git Large File Storage)  
* notebooks  
  * argenprop → argenprop\_scraper.ipynb \+ README  
  * zonaprop → zonaprop\_scaper.ipynb \+ README  
  * dataframe\_maestro.ipynb → donde concatenamos los 6 tsv

# **6\. Ejecución del Web Scraping**

Esta sección documenta el proceso de extracción de datos, las decisiones de diseño tomadas, los cambios realizados al scraper original provisto por la cátedra, y la arquitectura final del pipeline de datos.

## **6.1 Fuentes de Datos Scrapeadas**

| Portal | URL base | Librería HTTP |
| :---- | :---- | :---- |
| Argenprop | argenprop.com/departamentos/{op}/capital-federal | requests |
| ZonaProp | zonaprop.com.ar/departamentos-{op}-capital-federal | curl\_cffi (impersonate) |

Ambos portales exponen sus listings como HTML lo que permite scraping directo sin navegador. Sin embargo, ZonaProp detecta y bloquea librerías HTTP convencionales, por lo cual la solución fue reemplazar requests por curl\_cffi con impersonate='chrome120', que evita el bloqueo realizado por la página sin necesidad de Playwright (que consume más memoria y es más lento).

## **6.2 Cambios al Scraper Original (Argenprop)**

El scraper provisto por la cátedra fue el punto de partida. A continuación se detallan todas las modificaciones realizadas: 

| Área | Versión mejorada | Impacto |
| :---- | :---- | :---- |
| Datos de extracción | Agrega Fecha\_Scraping, Posting\_ID, Sitio, Operación en cada fila | Información extra que permite comparar entre sitios y fechas |
| Modificación función parse\_address() | Extrae piso del sufijo, ‘Piso N’, filtra guiones, descarta años históricos (1800–1950) (por ejemplo, para calles como ‘11 de Septiembre de 1888’), itera todos los números buscando altura \>= 100\. | Mejor obtención de datos sobre la Calle y arreglo de altura incorrecta en las direcciones.  |
| Extracción de barrio | Logramos identificar el barrio de la propiedad.  | Permite filtrar y agrupar por barrio |
| Amenities (conteo) | Suma cuántos amenities distintos aparecen. | Permite un contador de amenities por propiedad, no solo presencia. |
| Seguridad (vocabulario) | Suma portero, guardia, cámara, monitoreo | Permite detectar la seguridad utilizando otro vocabulario.  |
| Luminoso (vocabulario) | Suma muy soleado, soleado | Captura más variantes del lenguaje refiriéndose a la luminosidad.  |
| Limpieza de N/A | df.replace('N/A', None)  | Evita que 'N/A' sea tratado como texto en análisis numéricos. |
| Parámetros de entrada | run\_scraper\_argenprop(enlace, operacion, max\_pages, start\_page), todos parametrizables | Reutilizable para venta, alquiler y temporario sin modificar el código. |
| Manejo de CAPTCHA | Ante la aparición de un CAPTCHA, se guarda el proceso en un TSV, se muestran instrucciones para resolver el CAPTCHA, se solicitan las cookies y se retoma el scraping. | Argenprop presenta CAPTCHAs cada 100 páginas aproximadamente que frenan el scraping. |

**6.3 Cambios para adaptar al scraper a Zonaprop:**  
La siguiente tabla detalla cada modificación realizada al scraper de Argenprop para construir el de ZonaProp.

| Área | ZonaProp | Motivo del cambio |
| :---- | :---- | :---- |
| Librería HTTP | curl\_cffi con impersonate='chrome120' | Evita el bloqueo adicional que realiza Zonaprop.  |
| Etiquetas | Cambios en la forma de extraer información como el precio, expensas, dirección, barrio, descripción.  | Argenprop utiliza clases CSS para etiquetar los elementos HTML de su web, mientras que Zonaprop utiliza atributos data-qa. Esto requiere ciertas modificaciones en el código para extraer la información.  |
| Modificación función parse\_address() | Agrega manejo de 'al' previo al número, guiones complejos con nombre de edificio, y piso inline sin coma | Zonaprop utiliza otro formato de escritura al mencionar las direcciones de las propiedades.  |
| Formato de paginación | Ajustes al formato de paginación.  | Cada portal usa una convención distinta para construir las URLs de páginas sucesivas |
| Delay entre páginas | Aumento del delay entre páginas. ‘time.sleep(2)’ | ZonaProp es más agresivo en la detección de patrones de scraping. Por eso, un delay mayor reduce el riesgo de bloqueo por frecuencia. |

## 

## **6.4 Estructura del DataFrame Resultante**

Cada fila del DataFrame maestro corresponde a un aviso único. Las columnas son:

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

## **Concatenamos las tablas obtenidas en un DataFrame Maestro:** (https://colab.research.google.com/drive/10u6_cv9xnMFIaxbJU3bVoCrjNJqRqo57#scrollTo=I1ndjH19nvi9)

## **6.5 Desafíos Técnicos y Soluciones**

	

En primer lugar, al intentar correr el scraper inicial nos encontramos con limitaciones al correrlo desde Google Colab. Por ejemplo, desde esta plataforma corría como máximo una página del sitio web. Por eso mismo, decidimos migrar el proyecto a Visual Studio Code. Luego de realizar las modificaciones detalladas previamente para recibir un output más completo, pudimos comprobar que el scraper funcionaba de igual manera para extraer datos de ventas, alquileres y alquileres temporales lo cual necesitábamos para cumplir con el objetivo del proyecto. 

	

El primer cambio importante que implementamos fue reemplazar la función ‘get\_description(url, headers)’. Esta función, hacía un request adicional a cada propiedad, para poder obtener los datos. Sin embargo, esto demoraba entre 1-2 minutos, para scrapear 60 propiedades, por lo que extraer los datos de decenas de miles de propiedades iba a demorar demasiado. Entonces, decidimos crear la función parse\_card, que toma los datos directamente de la tarjeta de la propiedad, que se ve en el menú general, sin tener que ingresar a cada publicación. Esto realmente agiliza el proceso, y en definitiva, obtenemos la misma información.

Igualmente, para no limitarnos con la información brindada por Argenprop, quisimos incluir a Zonaprop a nuestra base de datos. Encontramos un scraper público en GitHub que funcionaba para los departamentos de CABA en venta del sitio web y entregaba resultados similares al del scraper anterior. De todas formas, al probarlo en los departamentos en alquiler o alquiler temporal, el scraper era incapaz de obtener adecuadamente los features como amenities, seguridad, etc. Probamos repetidamente sobrepasar los métodos adicionales de seguridad que tiene Zonaprop para obtener la información de estas variables críticas para nuestro análisis, pero no obtuvimos ningún resultado. 


Por eso mismo, decidimos abandonar el scraper que habíamos encontrado y optamos por intentar adaptar el scraper de Argenprop que habíamos optimizado. Primero, tuvimos que inspeccionar el HTML de Zonaprop, para descubrir su estructura, ya que no funcionaba como la de Argenprop. Entonces, vimos que ZonaProp usa atributos data-qa en lugar de clases CSS tradicionales, y definimos los selectores correctos, como POSTING\_CARD\_PRICE, POSTING\_CARD\_FEATURES, POSTING\_CARD\_LOCATION, etc. Luego de realizar los cambios correspondientes, nos encontramos con la misma complicación de antes, con los métodos de seguridad. Sin embargo, continuamos intentando solucionar este problema y finalmente lo logramos. Nuestra respuesta fue reemplazar la librería ‘requests’ por ‘curl\_cffi’ con ‘impersonate='chrome120’ que logra convencer a Zonaprop que somos un usuario más accediendo al sitio web.  


De esta forma, pudimos scrapear las primeras páginas de Zonaprop, y notamos problemas con cómo se cargaban las direcciones, alturas y pisos: en dirección quedaba algo como ‘Belgrano, Capital Federal’, y altura y piso quedaban vacíos. Descubrimos entonces, que la direccion no se guardaba en POSTING\_CARD\_LOCATION, sino que estaba en location-address. De esa forma, pudimos extraer la información necesaria, y decidimos sumar los barrios que estaban en POSTING\_CARD\_LOCATION. Igualmente, nos encontramos con casos particulares, que generaban complicaciones, y modificamos parse\_adress para poder manejarlos: 

* "Bolivia al 4400" → debíamos limpiar el "al".  
* "SAN JOSE 445\. Entre Belgrano y Venezuela" → el punto después del número rompía el regex.  
* "11 de Septiembre de 1888 2231" → el año 1888 era confundido con la altura y el 11 se borraba.  
* "Torres del Yacht \- Juana Manso al 600 \- 2 Ambientes" → extraer el fragmento correcto cuando hay guiones.  
* "Alvear Tower \- Azucena Villaflor" → devolver None cuando no hay número válido de altura.  
* "El Faro \- 3 Ambientes" → descartar números menores a 100, ya que probablemente no sean una dirección, sino una descripción del departamento, puesta en el lugar equivocado.  
* "Junín 1615 piso 13" y "Junín 1615 PB" → capturar el piso correctamente.  
* "2º piso" → limpiar el símbolo de ordinal.

	

Finalmente, al momento de scrapear Argenprop, nos encontramos con una dificultad significativa. Como medida de seguridad, el sitio de Argenprop muestra un CAPTCHA a partir de la página 100 del sitio. Navegando manualmente, comprobamos que no es un rate-limit, sino estrictamente por el número de página. Para sortearlo, resolvimos el captcha manualmente, copiamos las cookies nuevas, y las insertamos en el scraper. Y de esta forma, conseguimos todos los datos que necesitábamos.

## **7\. Tareas futuras**

En la siguiente fase del proyecto, vamos a tener que realizar una limpieza de los datos del DataFrame maestro. Se estandarizarán los precios, extrayendo el valor numérico y la moneda (USD vs. ARS) en columnas separadas para permitir comparaciones. Se parseará el campo Detalles para extraer m² totales, cantidad de ambientes y baños como variables numéricas independientes. Se imputarán o descartarán registros con campos críticos nulos (precio, barrio, m²) según criterios a definir, y se eliminarán duplicados. Asimismo, agregaremos información adicional de las fuentes secundarias mencionadas en la sección 5.2: distancia a la estación de subte más cercana (calculada con la fórmula de Haversine sobre el dataset de SBASE), e histórico del tipo de cambio USD/ARS del BCRA para normalizar precios en pesos. Una vez que el dataframe esté completo, realizaremos un análisis exhaustivo y verificaremos nuestras teorías mediante pruebas estadísticas.  
