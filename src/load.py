import logging
from typing import Optional, Union
import pandas as pd
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    inspect,
)
from sqlalchemy.engine import Engine

try:
    from .config import settings
except ImportError:
    from config import settings

logger = logging.getLogger(__name__)

TABLE_NAME = "gas_prices"


def get_engine(database_url: Optional[str] = None) -> Engine:
    url = database_url or settings.get_database_url()
    return create_engine(url, pool_pre_ping=True)


def ensure_table_exists(engine: Engine, table_name: str = TABLE_NAME) -> Table:
    metadata = MetaData()
    table = Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("state", String(10), index=True, nullable=False),
        Column("city_name", String(100), index=True, nullable=False),
        Column("regular", Float, nullable=False),
        Column("mid_grade", Float, nullable=True),
        Column("premium", Float, nullable=True),
        Column("diesel", Float, nullable=True),
        Column("price_spread", Float, nullable=True),
        Column("diesel_vs_regular", Float, nullable=True),
        Column("cheapest_fuel", String(20), nullable=True),
        Column("extracted_at", DateTime(timezone=True), nullable=False),
    )
    metadata.create_all(engine)
    return table


def load(
    df: pd.DataFrame,
    engine: Optional[Union[Engine, str]] = None,
    table_name: str = TABLE_NAME,
    if_exists: str = "append",
) -> int:
    if df.empty:
        logger.warning("Empty DataFrame provided to load stage; skipping database write.")
        return 0

    if engine is None:
        db_engine = get_engine()
    elif isinstance(engine, str):
        db_engine = get_engine(engine)
    else:
        db_engine = engine

    ensure_table_exists(db_engine, table_name=table_name)

    logger.info(
        "Loading %d records into database table '%s' (mode: %s)...",
        len(df),
        table_name,
        if_exists,
    )

    with db_engine.begin() as connection:
        df.to_sql(
            name=table_name,
            con=connection,
            if_exists=if_exists,
            index=False,
            method="multi",
        )

    logger.info("Successfully loaded %d records into '%s'.", len(df), table_name)
    return len(df)