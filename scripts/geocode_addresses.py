"""Geocodifica las direcciones de dataframe_limpio.tsv con USIG (GCBA) y Georef
(Estado nacional).

Salidas (data/geocoding/):
  cache/<api>.json          respuesta cruda por API, reanudable
  geocoded_sample.tsv       lat/lon por API + consenso + distancia entre fuentes
  dataframe_con_coords.tsv  dataframe_limpio + lat/lon de consenso
  report.md                 reporte de resultados, uso y rate limits

Uso:
  python scripts/geocode_addresses.py              # geocoding completo
  python scripts/geocode_addresses.py --refresh    # ignora cache
  python scripts/geocode_addresses.py --report-only # solo regenera reporte
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import threading
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Optional

import pandas as pd
import requests
from geopy.distance import geodesic

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "dataframe_limpio.tsv"
OUTDIR = ROOT / "data" / "geocoding"
CACHEDIR = OUTDIR / "cache"

USER_AGENT = "itba-ad-tp-geocoder/1.0 (academico; grupo1 ITBA Analitica Descriptiva)"

CABA_BBOX = (-58.55, -34.71, -58.33, -34.52)  # (lon_min, lat_min, lon_max, lat_max)


# --------------------------------------------------------------------------- #
# Normalizacion y clave de direccion
# --------------------------------------------------------------------------- #
def norm(s: object) -> str:
    """Normaliza para usar como clave: quita acentos, puntuacion, unifica
    Av/Avda/Avenida, colapsa espacios y baja a minusculas."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"[\.,'\"]", "", s)
    s = re.sub(r"\b(av|avda|avenida)\b\.?", "av", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def make_key(calle: object, altura: object, barrio: object) -> Optional[str]:
    """Clave canonica calle|altura|barrio. None si falta calle o altura."""
    if calle is None or altura is None:
        return None
    if isinstance(calle, float) and math.isnan(calle):
        return None
    try:
        alt = int(float(altura))
    except (TypeError, ValueError):
        return None
    c = norm(calle)
    if not c or c == "nan":
        return None
    return f"{c}|{alt}|{norm(barrio)}"


@dataclass(frozen=True)
class Address:
    key: str
    calle: str
    altura: int
    barrio: str

    @property
    def short(self) -> str:
        return f"{self.calle} {self.altura}"


# --------------------------------------------------------------------------- #
# Cache JSON reanudable
# --------------------------------------------------------------------------- #
class Cache:
    """key -> dict. Persiste atomicamente cada FLUSH_EVERY inserciones."""

    FLUSH_EVERY = 10

    def __init__(self, path: Path):
        self.path = path
        self.data: dict[str, dict] = {}
        if path.exists():
            try:
                self.data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                print(f"  [warn] cache corrupto en {path.name}, se reinicia")
        self._dirty = 0

    def get(self, key: str) -> Optional[dict]:
        return self.data.get(key)

    def put(self, key: str, result: dict) -> None:
        self.data[key] = result
        self._dirty += 1
        if self._dirty >= self.FLUSH_EVERY:
            self.flush()

    def flush(self) -> None:
        if self._dirty == 0 and self.path.exists():
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.path)
        self._dirty = 0


# --------------------------------------------------------------------------- #
# Geocoders
# --------------------------------------------------------------------------- #
class Geocoder:
    """Base: rate limit, reintentos, tope wall-clock duro y armado del resultado."""

    name = "base"
    min_delay = 1.0
    max_retries = 3
    backoff = 2.0
    hard_timeout = 30.0   # cap wall-clock por intento (sockets pueden ignorar el timeout HTTP)
    rate_limit_doc = ""
    endpoint = ""

    def __init__(self):
        self._last = 0.0

    def _throttle(self) -> None:
        wait = self.min_delay - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def _lookup(self, addr: Address):
        """Devuelve (lat, lon, label, raw). lat None => not_found (no reintenta).
        Excepcion => error (reintenta)."""
        raise NotImplementedError

    def _lookup_bounded(self, addr: Address):
        """_lookup con tope wall-clock duro via daemon thread."""
        result: list = [None]
        error: list = [None]

        def runner() -> None:
            try:
                result[0] = self._lookup(addr)
            except BaseException as e:  # noqa: BLE001
                error[0] = e

        t = threading.Thread(target=runner, daemon=True)
        t.start()
        t.join(self.hard_timeout)
        if t.is_alive():
            raise TimeoutError(f"hard timeout ({self.hard_timeout}s) en {self.name}")
        if error[0] is not None:
            raise error[0]
        return result[0]

    def geocode(self, addr: Address) -> dict:
        last_err = None
        elapsed = None
        for attempt in range(self.max_retries + 1):
            self._throttle()
            t0 = time.monotonic()
            try:
                lat, lon, label, raw = self._lookup_bounded(addr)
                elapsed = time.monotonic() - t0
                status = "ok" if lat is not None else "not_found"
                return self._result(addr, status, lat, lon, label, None, elapsed, raw)
            except Exception as e:  # noqa: BLE001
                last_err = e
                elapsed = time.monotonic() - t0
                if attempt < self.max_retries:
                    time.sleep(self.backoff * (attempt + 1))
        return self._result(addr, "error", None, None, None, repr(last_err), elapsed, None)

    def _result(self, addr, status, lat, lon, label, error, elapsed, raw) -> dict:
        in_bbox = None
        if lat is not None and lon is not None:
            lon_min, lat_min, lon_max, lat_max = CABA_BBOX
            in_bbox = (lon_min <= lon <= lon_max) and (lat_min <= lat <= lat_max)
        return {
            "api": self.name,
            "key": addr.key,
            "calle": addr.calle,
            "altura": addr.altura,
            "barrio": addr.barrio,
            "query": addr.short,
            "status": status,
            "lat": lat,
            "lon": lon,
            "label": label,
            "in_caba_bbox": in_bbox,
            "error": error,
            "elapsed_s": round(elapsed, 3) if elapsed is not None else None,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "raw": raw,
        }


class UsigGeocoder(Geocoder):
    name = "usig"
    min_delay = 0.34
    endpoint = "https://servicios.usig.buenosaires.gob.ar/normalizar/"
    rate_limit_doc = (
        "Servicio publico del GCBA, sin key. Sin limite estricto publicado; "
        "pensado para direcciones de CABA. Devuelve varias coincidencias "
        "(incluso de partidos del AMBA): se filtra cod_partido=='caba'."
    )

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def _lookup(self, addr: Address):
        params = {"direccion": addr.short, "geocodificar": "true"}
        r = self.session.get(self.endpoint, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        arr = data.get("direccionesNormalizadas") or []
        caba = [
            d for d in arr
            if str(d.get("cod_partido", "")).lower() == "caba" and d.get("coordenadas")
        ]
        if not caba:
            return None, None, None, data
        d = caba[0]
        c = d["coordenadas"]
        srid = c.get("srid")
        if srid not in (4326, "4326", None):
            raise ValueError(f"USIG devolvio srid no soportado: {srid}")
        return float(c["y"]), float(c["x"]), d.get("direccion"), d


class GeorefGeocoder(Geocoder):
    name = "georef"
    min_delay = 0.2
    endpoint = "https://apis.datos.gob.ar/georef/api/direcciones"
    rate_limit_doc = (
        "API abierta del Estado nacional, sin key. Sin limite estricto publicado; "
        "recomienda el endpoint batch (POST, hasta ~1000 consultas) para volumen alto."
    )

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def _lookup(self, addr: Address):
        params = {"direccion": addr.short, "provincia": "02", "max": 1}
        r = self.session.get(self.endpoint, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        arr = data.get("direcciones") or []
        if not arr:
            return None, None, None, data
        d = arr[0]
        ub = d.get("ubicacion") or {}
        lat, lon = ub.get("lat"), ub.get("lon")
        if lat is None or lon is None:
            return None, None, None, d
        return float(lat), float(lon), d.get("nomenclatura"), d


API_REGISTRY = {"usig": UsigGeocoder, "georef": GeorefGeocoder}
APIS = ["usig", "georef"]


# --------------------------------------------------------------------------- #
# Carga, ejecucion y consolidacion
# --------------------------------------------------------------------------- #
def load_unique_addresses(df: pd.DataFrame) -> list[Address]:
    """Direcciones unicas (calle+altura+barrio) con calle y altura presentes."""
    seen: dict[str, Address] = {}
    for calle, altura, barrio in zip(df["calle"], df["altura"], df["barrio_oficial"]):
        key = make_key(calle, altura, barrio)
        if key is None or key in seen:
            continue
        seen[key] = Address(
            key=key,
            calle=re.sub(r"\s+", " ", str(calle).strip()),
            altura=int(float(altura)),
            barrio=("" if pd.isna(barrio) else str(barrio).strip()),
        )
    return list(seen.values())


def run_api(api_name: str, addresses: list[Address], refresh: bool) -> Cache:
    geo = API_REGISTRY[api_name]()
    cache = Cache(CACHEDIR / f"{api_name}.json")

    def _stale(entry):
        # los "error" se reintentan en cada corrida (DNS, 5xx, timeouts transitorios)
        return entry is None or entry.get("status") == "error"

    pending = [a for a in addresses if refresh or _stale(cache.get(a.key))]
    print(
        f"\n=== {api_name.upper()} ===  {len(pending)} a consultar, "
        f"{len(addresses) - len(pending)} ya en cache  (delay {geo.min_delay}s)"
    )
    try:
        for i, addr in enumerate(pending, 1):
            res = geo.geocode(addr)
            cache.put(addr.key, res)
            if res["status"] == "ok":
                msg = f"{res['lat']:.5f},{res['lon']:.5f}"
                if res["in_caba_bbox"] is False:
                    msg += "  [!] fuera de bbox CABA"
            else:
                msg = res["status"] + (f" ({res['error']})" if res["error"] else "")
            print(f"  [{api_name}] {i}/{len(pending)}  {addr.short:<28} -> {msg}")
    except KeyboardInterrupt:
        print("\n[interrumpido] guardando cache...")
    finally:
        cache.flush()
    return cache


def max_pairwise_m(points: list[tuple[float, float]]) -> Optional[float]:
    if len(points) < 2:
        return None
    d = 0.0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = max(d, geodesic(points[i], points[j]).meters)
    return d


def consolidate(addresses: list[Address], caches: dict[str, Cache]) -> pd.DataFrame:
    rows = []
    for a in addresses:
        row = {"key": a.key, "calle": a.calle, "altura": a.altura, "barrio": a.barrio}
        pts = []
        for api in APIS:
            res = caches[api].get(a.key)
            if res and res.get("status") == "ok":
                row[f"{api}_lat"] = res["lat"]
                row[f"{api}_lon"] = res["lon"]
                pts.append((res["lat"], res["lon"]))
            else:
                row[f"{api}_lat"] = None
                row[f"{api}_lon"] = None
        row["n_ok"] = len(pts)
        md = max_pairwise_m(pts)
        row["max_pairwise_m"] = round(md, 1) if md is not None else None
        if pts:
            row["consensus_lat"] = round(median(sorted(p[0] for p in pts)), 7)
            row["consensus_lon"] = round(median(sorted(p[1] for p in pts)), 7)
        else:
            row["consensus_lat"] = None
            row["consensus_lon"] = None
        rows.append(row)
    return pd.DataFrame(rows)


def percentile(values: list[float], q: float) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    k = (len(s) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return s[int(k)]
    return s[lo] * (hi - k) + s[hi] * (k - lo)


def merge_back(df: pd.DataFrame, table: pd.DataFrame) -> pd.DataFrame:
    coords = table.set_index("key")[["consensus_lat", "consensus_lon"]]
    keys = [make_key(c, a, b) for c, a, b in zip(df["calle"], df["altura"], df["barrio_oficial"])]
    out = df.copy()
    out["lat"] = [coords["consensus_lat"].get(k) if k else None for k in keys]
    out["lon"] = [coords["consensus_lon"].get(k) if k else None for k in keys]
    out["geo_source"] = ["consenso_usig_georef" if (k and k in coords.index) else None for k in keys]
    return out


# --------------------------------------------------------------------------- #
# Reporte
# --------------------------------------------------------------------------- #
def build_report(addresses, caches, table, meta) -> str:
    L: list[str] = []
    L.append("# Reporte de geocodificacion de direcciones de CABA\n")
    L.append(f"_Generado: {meta['ts']}_\n")
    L.append(
        f"- Dataset: `{DATA.relative_to(ROOT)}` ({meta['total_rows']:,} filas, "
        f"{meta['rows_with_addr']:,} con calle+altura)\n"
        f"- Direcciones unicas (calle+altura+barrio): **{meta['n_unique']:,}**\n"
        f"- Coordenadas: **WGS84 / EPSG:4326** (lat, lon)\n"
    )

    L.append("\n## 1. APIs usadas\n")
    L.append("| API | Endpoint | Key | Delay | Reintentos |")
    L.append("|---|---|---|---|---|")
    for api in APIS:
        g = API_REGISTRY[api]
        L.append(f"| `{api}` | {g.endpoint} | no | {g.min_delay}s | {g.max_retries} |")
    L.append("\n**Rate limits:**\n")
    for api in APIS:
        L.append(f"- **{api}** — {API_REGISTRY[api].rate_limit_doc}")

    L.append("\n## 2. Resultados\n")
    L.append("| API | Consultadas | OK | No encontradas | Errores | % exito | Resp. media |")
    L.append("|---|---|---|---|---|---|---|")
    stats = {}
    for api in APIS:
        res = [caches[api].get(a.key) for a in addresses]
        res = [r for r in res if r is not None]
        ok = [r for r in res if r["status"] == "ok"]
        nf = [r for r in res if r["status"] == "not_found"]
        err = [r for r in res if r["status"] == "error"]
        times = [r["elapsed_s"] for r in ok if r.get("elapsed_s") is not None]
        att = len(res)
        rate = f"{100*len(ok)/att:.1f}%" if att else "-"
        avg = f"{sum(times)/len(times):.2f}s" if times else "-"
        stats[api] = {"rate": len(ok) / att if att else 0}
        L.append(f"| `{api}` | {att} | {len(ok)} | {len(nf)} | {len(err)} | {rate} | {avg} |")

    L.append("\n## 3. Cross-validacion USIG vs Georef\n")
    multi = table[table["n_ok"] >= 2]
    dists = [float(x) for x in multi["max_pairwise_m"].dropna().tolist()]
    if dists:
        within = lambda t: sum(1 for d in dists if d <= t)  # noqa: E731
        L.append(f"{len(multi):,} direcciones resueltas por ambas APIs. Distancia entre fuentes:\n")
        L.append("| metrica | valor |")
        L.append("|---|---|")
        L.append(f"| mediana | {median(dists):.1f} m |")
        L.append(f"| p90 | {percentile(dists, 0.9):.1f} m |")
        L.append(f"| maxima | {max(dists):.1f} m |")
        L.append(f"| <= 25 m (mismo portal) | {within(25):,}/{len(dists):,} |")
        L.append(f"| <= 100 m (misma cuadra) | {within(100):,}/{len(dists):,} |")
        L.append(f"| > 500 m (discrepan) | {sum(1 for d in dists if d > 500):,}/{len(dists):,} |")

    L.append("\n## 4. Ejemplos\n")
    ex = table.sort_values("n_ok", ascending=False).head(8)
    L.append("| Direccion | Barrio | usig | georef | consenso | acuerdo |")
    L.append("|---|---|---|---|---|---|")
    for _, r in ex.iterrows():
        cells = [f"{r['calle']} {r['altura']}", str(r["barrio"])]
        for api in APIS:
            lat, lon = r[f"{api}_lat"], r[f"{api}_lon"]
            cells.append(f"{lat:.5f}, {lon:.5f}" if pd.notna(lat) else "—")
        if pd.notna(r["consensus_lat"]):
            cells.append(f"{r['consensus_lat']:.5f}, {r['consensus_lon']:.5f}")
        else:
            cells.append("—")
        cells.append(f"{r['max_pairwise_m']:.0f} m" if pd.notna(r["max_pairwise_m"]) else "—")
        L.append("| " + " | ".join(cells) + " |")

    L.append("\n## 5. Archivos generados\n")
    L.append("- `data/geocoding/cache/<api>.json` — respuesta cruda por API (reanudable).")
    L.append("- `data/geocoding/geocoded_sample.tsv` — lat/lon por API + consenso + acuerdo.")
    L.append("- `data/geocoding/dataframe_con_coords.tsv` — dataframe_limpio + lat/lon de consenso.")
    L.append("- `data/geocoding/report.md` — este reporte.\n")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true", help="ignorar cache y volver a consultar")
    ap.add_argument("--report-only", action="store_true", help="no consultar, solo regenerar reporte")
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    CACHEDIR.mkdir(parents=True, exist_ok=True)

    print(f"Cargando {DATA.relative_to(ROOT)} ...")
    df = pd.read_csv(DATA, sep="\t")
    rows_with_addr = int((df["calle"].notna() & df["altura"].notna()).sum())
    addresses = load_unique_addresses(df)
    print(f"  {len(df):,} filas, {len(addresses):,} direcciones unicas")

    caches: dict[str, Cache] = {}
    if args.report_only:
        for api in APIS:
            caches[api] = Cache(CACHEDIR / f"{api}.json")
    else:
        for api in APIS:
            caches[api] = run_api(api, addresses, args.refresh)

    print("\nConsolidando ...")
    table = consolidate(addresses, caches)
    table.to_csv(OUTDIR / "geocoded_sample.tsv", sep="\t", index=False, encoding="utf-8")

    merged = merge_back(df, table)
    merged.to_csv(OUTDIR / "dataframe_con_coords.tsv", sep="\t", index=False, encoding="utf-8")
    n_filled = int(merged["lat"].notna().sum())
    print(f"  dataframe_con_coords.tsv: {n_filled:,}/{len(merged):,} filas con coordenadas")

    meta = {
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_rows": len(df),
        "rows_with_addr": rows_with_addr,
        "n_unique": len(addresses),
    }
    (OUTDIR / "report.md").write_text(build_report(addresses, caches, table, meta), encoding="utf-8")
    print(f"\nListo. Reporte en {(OUTDIR / 'report.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
