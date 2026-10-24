import argparse
import logging
import sys
from typing import List, Optional

try:
    from .config import settings
    from .extract import extract
    from .load import load
    from .transform import transform
except ImportError:
    from config import settings
    from extract import extract
    from load import load
    from transform import transform

logger = logging.getLogger("gas_prices_etl")


def setup_logging(log_level: str = "INFO") -> None:
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_pipeline(
    states: str = "WA",
    database_url: Optional[str] = None,
    mode: str = "append",
    use_mock: bool = False,
) -> int:
    logger.info("Starting Gas Prices ETL Pipeline")
    logger.info("Target states: %s | Mode: %s | Mock: %s", states, mode, use_mock)

    raw_data = extract(states=states, use_mock=use_mock)
    if not raw_data:
        logger.error("No data extracted. Aborting pipeline.")
        return 0

    df = transform(raw_data)
    if df.empty:
        logger.warning("No records produced after transformation.")
        return 0

    rows_loaded = load(df=df, engine=database_url, if_exists=mode)

    logger.info("Pipeline Summary:")
    logger.info(" - Total rows extracted and loaded: %d", rows_loaded)
    if "regular" in df.columns:
        logger.info(" - Average regular price: $%.3f", df["regular"].mean())
        cheapest_row = df.loc[df["regular"].idxmin()]
        expensive_row = df.loc[df["regular"].idxmax()]
        logger.info(
            " - Lowest price city: %s, %s ($%.3f)",
            cheapest_row["city_name"],
            cheapest_row["state"],
            cheapest_row["regular"],
        )
        logger.info(
            " - Highest price city: %s, %s ($%.3f)",
            expensive_row["city_name"],
            expensive_row["state"],
            expensive_row["regular"],
        )

    logger.info("ETL process is complete!")
    return rows_loaded


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gas Prices ETL Pipeline - Extract, transform, and load gas pricing data."
    )
    parser.add_argument(
        "--state",
        "-s",
        type=str,
        default=settings.default_state,
        help="Target state code or comma-separated list of state codes (e.g. WA or WA,CA,TX).",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Database connection URL override (PostgreSQL or SQLite).",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["append", "replace"],
        default="append",
        help="Database table load mode: append or replace (default: append).",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run pipeline using mock gas price dataset without external API calls.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity level (default: INFO).",
    )
    return parser


def main(args: Optional[List[str]] = None) -> int:
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    setup_logging(parsed_args.log_level)

    try:
        run_pipeline(
            states=parsed_args.state,
            database_url=parsed_args.db_url,
            mode=parsed_args.mode,
            use_mock=parsed_args.mock,
        )
        return 0
    except Exception as exc:
        logger.exception("Pipeline failed with unhandled error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())