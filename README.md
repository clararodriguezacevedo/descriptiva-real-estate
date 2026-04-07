# 🏠 Descriptiva Real Estate Scrapers

## 📁 Project Structure

descriptiva-real-estate/
│
├── zonaprop/
│ └── zonaprop_scraper.ipynb
│
├── argenprop/
│ └── argenprop_scraper.ipynb
│
├── utils.py
└── README.md

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd descriptiva-real-estate


### 2. Create a virtual environment
macOS / Linux
python3 -m venv venv
source venv/bin/activate
Windows
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies

pip install --upgrade pip
pip install requests beautifulsoup4 pandas lxml playwright jupyter notebook


###  4. Install Playwright browser (required for Zonaprop)

Run this once:

playwright install chromium

## 🚀 Running the Project
Start Jupyter
jupyter notebook
or
jupyter lab3

## Running Scrapers
Argenprop Scraper

Open:
argenprop/argenprop_scraper.ipynb
Run all cells


Zonaprop Scraper

Open:
zonaprop/zonaprop_scraper.ipynb
Run all cells


## Dependencies (Reference)

These are all required packages:

requests
beautifulsoup4
pandas
lxml
playwright
jupyter
notebook

## 📤 Output

The scrapers generate structured datasets using:

build_output_df
save_df

Output format:

CSV files (typically)