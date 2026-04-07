# Real Estate Scraper - Argentina

Este proyecto contiene herramientas para scrapear anuncios de departamentos en venta y alquiler en Capital Federal desde las plataformas **Zonaprop** y **Argenprop**.

## 🚀 Funcionalidades

- **Zonaprop Scraper**: Utiliza Playwright para manejar el renderizado de JavaScript en las páginas de listado y Requests para obtener detalles de forma eficiente.
- **Argenprop Scraper**: Basado enteramente en Requests y BeautifulSoup.
- **Procesamiento Inteligente**: Extracción automática de características (Amenities, Cochera, Seguridad, etc.) mediante análisis de texto.
- **Salida Estandarizada**: Genera archivos TSV compatibles entre ambas fuentes.

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

1. **Python 3.10+**
2. **Pip** (gestor de paquetes de Python)

## 📥 Instalación

1. Clona este repositorio o descarga los archivos.
2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Instala los navegadores necesarios para Playwright:
   ```bash
   playwright install chromium
   ```

## 🖥️ Uso

El proyecto está organizado en Notebooks de Jupyter para facilitar la ejecución interactiva:

- `zonaprop/zonaprop_scraper.ipynb`: Scraper para Zonaprop.
- `argenprop/argenprop_scraper.ipynb`: Scraper para Argenprop.

### Notas sobre Zonaprop
Zonaprop requiere el uso de **Playwright** debido a que gran parte de su contenido se carga dinámicamente mediante JavaScript. Aunque parte del HTML es estático (SSR), la estructura de las tarjetas y la paginación son más robustas de manejar con un navegador automatizado para evitar bloqueos y asegurar la captura de todos los datos.

## 📁 Estructura del Proyecto

```
.
├── utils.py                # Funciones compartidas de limpieza y procesamiento
├── requirements.txt        # Dependencias del proyecto
├── zonaprop/
│   ├── zonaprop_scraper.ipynb
│   └── output/             # Archivos generados
└── argenprop/
    ├── argenprop_scraper.ipynb
    └── output/             # Archivos generados
```
