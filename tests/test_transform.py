import json
import pandas as pd
import pytest
from src.transform import transform


def test_transform_normalizes_columns(sample_wa_raw_payload):
    df = transform(sample_wa_raw_payload)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "city_name" in df.columns
    assert "regular" in df.columns
    assert "mid_grade" in df.columns
    assert "premium" in df.columns
    assert "diesel" in df.columns
    assert "state" in df.columns
    assert "price_spread" in df.columns
    assert "extracted_at" in df.columns


def test_transform_computes_numeric_prices(sample_raw_json_str):
    df = transform(sample_raw_json_str)

    assert df["regular"].dtype == float
    assert df["mid_grade"].dtype == float
    assert df["premium"].dtype == float
    assert df["diesel"].dtype == float

    seattle = df[df["city_name"] == "Seattle"].iloc[0]
    assert seattle["regular"] == 4.899
    assert seattle["price_spread"] == round(5.329 - 4.899, 3)
    assert seattle["diesel_vs_regular"] == round(4.749 - 4.899, 3)


def test_transform_drops_duplicates():
    payload = {
        "success": True,
        "result": {
            "state": "WA",
            "cities": [
                {"name": "Seattle", "gasoline": "4.899", "midGrade": "5.099", "premium": "5.329", "diesel": "4.749"},
                {"name": "Seattle", "gasoline": "4.999", "midGrade": "5.199", "premium": "5.429", "diesel": "4.849"},
            ],
        },
    }
    df = transform(payload)
    assert len(df) == 1
    assert df.iloc[0]["regular"] == 4.999


def test_transform_handles_empty_payload():
    df = transform({"success": True, "result": {"state": "WA", "cities": []}})
    assert df.empty
    assert "city_name" in df.columns


def test_transform_filters_invalid_prices():
    payload = {
        "success": True,
        "result": {
            "state": "WA",
            "cities": [
                {"name": "InvalidCity", "gasoline": "N/A", "midGrade": "0", "premium": "0", "diesel": "0"},
                {"name": "ValidCity", "gasoline": "4.250", "midGrade": "4.450", "premium": "4.650", "diesel": "4.350"},
            ],
        },
    }
    df = transform(payload)
    assert len(df) == 1
    assert df.iloc[0]["city_name"] == "ValidCity"
