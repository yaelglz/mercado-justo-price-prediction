#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import re
from urllib.parse import urlencode

import pandas as pd
import requests
from bs4 import BeautifulSoup


CONSULTA_URL = (
    "https://www.economia-sniim.gob.mx/nuevo/Consultas/MercadosNacionales/"
    "PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx?SubOpcion=4"
)
RESULTADOS_URL = (
    "https://www.economia-sniim.gob.mx/nuevo/Consultas/MercadosNacionales/"
    "PreciosDeMercado/Agricolas/ResultadosConsultaFechaFrutasYHortalizas.aspx"
)
TARGET_PRODUCT_RE = re.compile(r"\b(?:aguacate|lim[oó]n)\b", re.IGNORECASE)
DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$")
PAGINATION_RE = re.compile(r"Página\s+(\d+)\s+de\s+(\d+)", re.IGNORECASE)
RESULT_COLUMNS = [
    "fecha",
    "presentacion",
    "origen",
    "destino",
    "precio_min",
    "precio_max",
    "precio_frec",
    "obs",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recolecta historico SNIIM para todos los tipos de aguacate y limon."
    )
    parser.add_argument("--start-date", default="01/01/2016", help="Formato dd/mm/yyyy.")
    parser.add_argument(
        "--end-date",
        default=datetime.now().strftime("%d/%m/%Y"),
        help="Formato dd/mm/yyyy.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/sniim_aguacate_limon_2016_hoy.csv"),
        help="CSV de salida.",
    )
    parser.add_argument(
        "--rows-per-page",
        type=int,
        default=100000,
        help="Registros por pagina solicitados al endpoint de resultados.",
    )
    parser.add_argument(
        "--max-products",
        type=int,
        default=None,
        help="Limita productos procesados (util para pruebas).",
    )
    return parser.parse_args()


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/146.0 Safari/537.36"
            )
        }
    )
    return session


def get_target_products(session: requests.Session) -> list[tuple[str, str]]:
    response = session.get(CONSULTA_URL, timeout=60)
    response.raise_for_status()
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "html.parser")
    select = soup.find("select", {"name": "ddlProducto"})
    if not select:
        raise RuntimeError("No se encontro la lista de productos (ddlProducto).")

    products: list[tuple[str, str]] = []
    for option in select.find_all("option"):
        value = (option.get("value") or "").strip()
        text = option.get_text(" ", strip=True)
        if not value or not text or text.lower() == "todos":
            continue
        if TARGET_PRODUCT_RE.search(text):
            products.append((value, text))
    return products


def parse_pagination_info(soup: BeautifulSoup) -> tuple[int, int]:
    span = soup.find(id="lblPaginacion")
    if not span:
        return 1, 1
    match = PAGINATION_RE.search(span.get_text(" ", strip=True))
    if not match:
        return 1, 1
    return int(match.group(1)), int(match.group(2))


def parse_result_rows(soup: BeautifulSoup, product_name: str) -> list[dict[str, str]]:
    table = soup.find(id="tblResultados")
    if not table:
        return []

    rows: list[dict[str, str]] = []
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) != 8:
            continue
        values = [" ".join(td.get_text(" ", strip=True).split()) for td in tds]
        if not DATE_RE.match(values[0]):
            continue
        row = {col: val for col, val in zip(RESULT_COLUMNS, values)}
        row["producto"] = product_name
        rows.append(row)
    return rows


def fetch_result_page(
    session: requests.Session,
    product_id: str,
    product_name: str,
    start_date: str,
    end_date: str,
    rows_per_page: int,
) -> tuple[list[dict[str, str]], int, int]:
    params = {
        "fechaInicio": start_date,
        "fechaFinal": end_date,
        "ProductoId": product_id,
        "OrigenId": -1,
        "Origen": "Todos",
        "DestinoId": -1,
        "Destino": "Todos",
        "PreciosPorId": 1,
        "RegistrosPorPagina": rows_per_page,
    }
    url = f"{RESULTADOS_URL}?{urlencode(params)}"
    response = session.get(url, timeout=180)
    response.raise_for_status()
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "html.parser")
    current_page, total_pages = parse_pagination_info(soup)
    rows = parse_result_rows(soup, product_name=product_name)
    return rows, current_page, total_pages


def fetch_product_rows_split(
    session: requests.Session,
    product_id: str,
    product_name: str,
    start_dt: datetime,
    end_dt: datetime,
    rows_per_page: int,
) -> list[dict[str, str]]:
    start_str = start_dt.strftime("%d/%m/%Y")
    end_str = end_dt.strftime("%d/%m/%Y")

    try:
        rows, current_page, total_pages = fetch_result_page(
            session=session,
            product_id=product_id,
            product_name=product_name,
            start_date=start_str,
            end_date=end_str,
            rows_per_page=rows_per_page,
        )
        print(
            f"[{product_name}] {start_str} a {end_str} -> "
            f"pagina {current_page}/{total_pages}: {len(rows)} filas."
        )
    except requests.HTTPError as exc:
        if start_dt >= end_dt:
            raise
        if exc.response is None or exc.response.status_code < 500:
            raise
        mid = start_dt + (end_dt - start_dt) / 2
        mid = datetime(mid.year, mid.month, mid.day)
        left = fetch_product_rows_split(
            session=session,
            product_id=product_id,
            product_name=product_name,
            start_dt=start_dt,
            end_dt=mid,
            rows_per_page=rows_per_page,
        )
        right = fetch_product_rows_split(
            session=session,
            product_id=product_id,
            product_name=product_name,
            start_dt=mid + timedelta(days=1),
            end_dt=end_dt,
            rows_per_page=rows_per_page,
        )
        return left + right

    if total_pages <= 1 or start_dt >= end_dt:
        return rows

    mid = start_dt + (end_dt - start_dt) / 2
    mid = datetime(mid.year, mid.month, mid.day)
    left = fetch_product_rows_split(
        session=session,
        product_id=product_id,
        product_name=product_name,
        start_dt=start_dt,
        end_dt=mid,
        rows_per_page=rows_per_page,
    )
    right = fetch_product_rows_split(
        session=session,
        product_id=product_id,
        product_name=product_name,
        start_dt=mid + timedelta(days=1),
        end_dt=end_dt,
        rows_per_page=rows_per_page,
    )
    return left + right


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    start_dt = datetime.strptime(args.start_date, "%d/%m/%Y")
    end_dt = datetime.strptime(args.end_date, "%d/%m/%Y")
    if start_dt > end_dt:
        raise ValueError("start-date no puede ser mayor que end-date.")

    session = build_session()
    products = get_target_products(session)
    if args.max_products is not None:
        products = products[: args.max_products]

    if not products:
        raise RuntimeError("No se encontraron productos de aguacate o limon.")

    print(f"[INFO] Productos a procesar: {len(products)}")
    all_rows: list[dict[str, str]] = []
    for index, (product_id, product_name) in enumerate(products, start=1):
        print(f"[INFO] ({index}/{len(products)}) Procesando: {product_name}")
        rows = fetch_product_rows_split(
            session=session,
            product_id=product_id,
            product_name=product_name,
            start_dt=start_dt,
            end_dt=end_dt,
            rows_per_page=args.rows_per_page,
        )
        if not rows:
            print(f"[INFO] {product_name}: sin registros en el rango.")
        all_rows.extend(rows)

    if not all_rows:
        raise RuntimeError("No se recolectaron filas para aguacate/limon en el rango indicado.")

    df = pd.DataFrame(all_rows)
    before = len(df)
    df = df.drop_duplicates()
    dropped = before - len(df)
    df["collected_at"] = datetime.now().isoformat(timespec="seconds")
    df.to_csv(args.output, index=False)
    if dropped:
        print(f"[INFO] Filas duplicadas eliminadas: {dropped}")
    print(f"[DONE] CSV guardado en {args.output} con {len(df)} filas.")


if __name__ == "__main__":
    main()
