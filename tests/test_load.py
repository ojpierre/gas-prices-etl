import pandas as pd
from sqlalchemy import text
from src.load import ensure_table_exists, load


def test_ensure_table_exists(memory_db_engine):
    table = ensure_table_exists(memory_db_engine, table_name="test_gas_prices")
    assert table.name == "test_gas_prices"

    with memory_db_engine.connect() as conn:
        result = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='test_gas_prices'")
        ).fetchone()
        assert result is not None


def test_load_dataframe_append(memory_db_engine, sample_wa_raw_payload):
    from src.transform import transform

    df = transform(sample_wa_raw_payload)
    rows_written = load(df, engine=memory_db_engine, table_name="test_load", if_exists="append")

    assert rows_written == 2

    with memory_db_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM test_load")).scalar()
        assert count == 2

    # Test second append
    load(df, engine=memory_db_engine, table_name="test_load", if_exists="append")
    with memory_db_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM test_load")).scalar()
        assert count == 4


def test_load_empty_dataframe(memory_db_engine):
    empty_df = pd.DataFrame()
    rows_written = load(empty_df, engine=memory_db_engine, table_name="test_empty")
    assert rows_written == 0
