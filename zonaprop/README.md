# Zonaprop Scraper

A Python-based web scraper built with Playwright to extract structured real estate listings from Zonaprop and export them as JSON files.

---

## Overview

This project scrapes property listings from Zonaprop search result pages and stores structured data in a JSON file.

It is designed to handle dynamic content rendered via JavaScript, making it suitable for modern Single Page Applications (SPA).

---

## Why Playwright?

Zonaprop is a **Single Page Application (SPA)**.

This means:

- The initial HTML response does not contain listing data.
- Property cards are rendered dynamically using JavaScript.
- Traditional scrapers (e.g., `requests + BeautifulSoup`) cannot access the content directly.

Playwright solves this by:

- Launching a real Chromium browser.
- Executing all JavaScript.
- Waiting for the DOM to render.
- Extracting fully loaded listing elements.

---

## Extracted Data

For each property listing, the scraper collects:

- Listing ID
- URL
- Price (numeric)
- Expenses (numeric)
- Address
- Location
- Total square meters
- Number of rooms
- Bedrooms
- Bathrooms
- Parking spaces
- Scraping timestamp

Duplicate listings across paginated pages are automatically filtered.

---

## Requirements

- Python 3.10+
- Playwright

---

## Installation

Clone the repository or download the script.

(Optional) Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install
```

---

## Usage

Basic usage:

```bash
python zonaprop_scraper.py "<URL>"
```

Example:

```bash
python zonaprop_scraper.py "https://www.zonaprop.com.ar/departamentos-alquiler-caballito.html"
```

Specify maximum number of pages:

```bash
python zonaprop_scraper.py "<URL>" 10
```

Arguments:

- First argument: Base search URL
- Second argument (optional): Maximum number of pages to scrape (default = 5)

---

## Output

The script:

- Automatically creates a `data/` folder if it does not exist.
- Saves results as a timestamped JSON file:

```
data/zonaprop_YYYYMMDD_HHMMSS.json
```

Example:

```
data/zonaprop_20260212_014523.json
```

---

## Project Structure

```
zonaprop-scraper/
│
├── data/
├── zonaprop_scraper.py
├── requirements.txt
└── README.md
```

---

## Disclaimer

This project is intended for educational and analytical purposes only.

Before running large-scale scraping:

- Review the website’s Terms of Service
- Respect responsible scraping practices
- Avoid excessive traffic

---

## To fix:

- If there are no properties matching the selected filters in the specified area(s), Zonaprop provides suggestions in other locations, and the scraper also extracts those suggested listings.
