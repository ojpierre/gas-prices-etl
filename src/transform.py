import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Union
import pandas as pd

logger = logging.getLogger(__name__)

PRICE_COLUMNS = ["regular", "mid_grade", "premium", "diesel"]


def _find_cheapest_fuel(row: pd.Series) -> str:
    valid_prices = {col: row[col] for col in PRICE_COLUMNS if pd.notna(row[col]) and row[col] > 0}
    if not valid_prices:
        return "unknown"
    return min(valid_prices, key=valid_prices.get)


def _normalize_single_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = payload.get("result", {})
    if isinstance(result, list):
        records = []
        for item in result:
            record = dict(item)
            record.setdefault("state", item.get("name", "USA"))
            records.append(record)
        return records

    state_code = result.get("state", "UNKNOWN")
    cities = result.get("cities", [])
    records = []
    for city in cities:
        item = dict(city)
        item["state"] = state_code
        records.append(item)
    return records


def transform(data: Union[str, bytes, Dict[str, Any], List[Dict[str, Any]]]) -> pd.DataFrame:
    if isinstance(data, (str, bytes)):
        data = json.loads(data)

    if isinstance(data, dict):
        raw_items = _normalize_single_payload(data)
    elif isinstance(data, list):
        raw_items = []
        for item in data:
            if isinstance(item, dict):
                raw_items.extend(_normalize_single_payload(item))
            elif isinstance(item, (str, bytes)):
                raw_items.extend(_normalize_single_payload(json.loads(item)))
    else:
        raise ValueError(f"Unsupported payload type for transformation: {type(data)}")

    if not raw_items:
        logger.warning("No records extracted to transform; returning empty DataFrame.")
        return pd.DataFrame(
            columns=[
                "state",
                "city_name",
                "regular",
                "mid_grade",
                "premium",
                "diesel",
                "price_spread",
                "diesel_vs_regular",
                "cheapest_fuel",
                "extracted_at",
            ]
        )

    df = pd.DataFrame(raw_items)

    rename_map = {
        "name": "city_name",
        "gasoline": "regular",
        "midGrade": "mid_grade",
    }
    df.rename(columns=rename_map, inplace=True)

    if "lowername" in df.columns:
        df.drop(columns=["lowername"], inplace=True)
    if "currency" in df.columns:
        df.drop(columns=["currency"], inplace=True)

    for col in PRICE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = pd.NA

    df.dropna(subset=["city_name", "regular"], inplace=True)
    df = df[df["regular"] > 0]

    df["price_spread"] = (df["premium"] - df["regular"]).round(3)
    df["diesel_vs_regular"] = (df["diesel"] - df["regular"]).round(3)
    df["cheapest_fuel"] = df.apply(_find_cheapest_fuel, axis=1)

    now_utc = datetime.now(timezone.utc)
    df["extracted_at"] = now_utc

    df.drop_duplicates(subset=["state", "city_name"], keep="last", inplace=True)
    df.reset_index(drop=True, inplace=True)

    ordered_cols = [
        "state",
        "city_name",
        "regular",
        "mid_grade",
        "premium",
        "diesel",
        "price_spread",
        "diesel_vs_regular",
        "cheapest_fuel",
        "extracted_at",
    ]
    df = df[[col for col in ordered_cols if col in df.columns]]

    logger.info("Transformed %d gas price records successfully.", len(df))
    return df