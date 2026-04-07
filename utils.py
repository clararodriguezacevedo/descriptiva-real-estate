import pandas as pd
import re
import os
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

SCHEMA_COLS = [
    "Fuente", "Precio", "Expensas", "Calle", "Altura", "Piso",
    "Ubicacion", "Detalles", "Caracteristicas", "Descripción",
    "Publicado", "Visualizaciones", "Link"
]
FEATURE_COLS = [
    "Amenities", "Losa_Central", "Aire_Acond", "Apto_Credito",
    "Cochera", "Seguridad", "Luminoso", "Balcon_Aterrazado"
]

def clean_text(text):
    """
    Limpia y normaliza el texto.
    """
    if not text:
        return "N/A"
    text = text.replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_address(address_raw):
    """
    Extrae calle, altura y piso de una cadena de dirección.
    """
    calle = altura = piso = "N/A"
    if not address_raw or address_raw == "N/A":
        return calle, altura, piso
    try:
        # Limpieza básica
        address_raw = re.sub(r'[Pp]iso\s*\d*', '', address_raw).strip()
        # Regex simple para Calle Numero, Piso
        match = re.search(r'^(.*?)\s+(\d+)(?:,\s*(.*))?$', address_raw)
        if match:
            calle  = match.group(1).strip()
            altura = match.group(2).strip()
            piso   = match.group(3).strip() if match.group(3) else "0"
        else:
            calle = address_raw.strip()
    except Exception:
        pass
    return calle, altura, piso

def parse_price(price_text):
    """
    Extrae el precio y las expensas de un texto.
    Soporta USD, ARS y símbolos de moneda.
    """
    if not price_text:
        return "Consultar", "N/A"
    
    price_text = clean_text(price_text)
    # Buscar precio principal
    p_match = re.search(r'(USD|ARS|\$)\s*([\d.,]+)', price_text, re.IGNORECASE)
    precio  = p_match.group(0) if p_match else 'Consultar'
    
    # Buscar expensas (usualmente precedidas por +)
    e_match = re.search(r'\+\s*(?:[\$ARS\s]*)([\d.,]+)', price_text, re.IGNORECASE)
    expensas = e_match.group(0).strip() if e_match else 'N/A'
    
    return precio, expensas

def extract_smart_features(row):
    """
    Detecta características clave mediante palabras clave en el contenido.
    """
    texto = " ".join([
        str(row.get("Descripción",     "")),
        str(row.get("Detalles",        "")),
        str(row.get("Caracteristicas", "")),
    ]).lower()
    
    return pd.Series({
        "Amenities":         1 if any(x in texto for x in ["amenities","piscina","pileta","sum","parrilla","gym","gimnasio","sauna","laundry","quincho"]) else 0,
        "Losa_Central":      1 if any(x in texto for x in ["losa radiante","calefacción central","caldera central","piso radiante"]) else 0,
        "Aire_Acond":        1 if any(x in texto for x in ["aire acondicionado","split"," a/c","frío-calor"]) else 0,
        "Apto_Credito":      1 if any(x in texto for x in ["apto crédito","apto credito","apto cr"]) else 0,
        "Cochera":           1 if any(x in texto for x in ["cochera","coch.","coch ","espacio guarda coche","estacionamiento"]) else 0,
        "Seguridad":         1 if any(x in texto for x in ["portero", "vigilancia","seguridad 24","tótem","totem","encargado"]) else 0,
        "Luminoso":          1 if any(x in texto for x in ["luminoso","todo luz","vista abierta","vista panorámica","sol"]) else 0,
        "Balcon_Aterrazado": 1 if any(x in texto for x in ["aterrazado","balcón terraza","terraza","balcón"]) else 0,
    })

def build_output_df(records):
    """
    Construye el DataFrame final aplicando el schema y las características.
    """
    if not records:
        return None
    
    df = pd.DataFrame(records)
    # Asegurar que todas las columnas del schema existan
    for col in SCHEMA_COLS:
        if col not in df.columns:
            df[col] = "N/A"
            
    df = df[SCHEMA_COLS].copy()
    # Agregar features inteligentes
    features_df = df.apply(extract_smart_features, axis=1)
    return pd.concat([df, features_df], axis=1)

def save_df(df, prefix, mode):
    """
    Guarda el DataFrame en formato TSV.
    """
    os.makedirs("output", exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')
    path = f'output/{prefix}_{mode}_{ts}.tsv'
    df.to_csv(path, sep='\t', index=False, encoding='utf-8-sig')
    print(f'✅ Archivo guardado: {path}')
    return path
