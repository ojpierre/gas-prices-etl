# Gas Prices ETL Pipeline

A Python ETL project that extracts state-level gas price data from the CollectAPI gas pricing API, transforms the raw response into a clean tabular format, and loads the results into a PostgreSQL database.

## Project Structure

- `src/` - source code for the ETL pipeline
- `src/extract.py` — extracts gas price data from the CollectAPI service.
- `src/transform.py` — applies simple transformations to normalize the extracted dataset.
- `src/load.py` — writes the transformed data into a PostgreSQL table using SQLAlchemy.
- `src/main.py` — orchestrates the extract-transform-load pipeline.
- `requirements.txt` — Python dependencies for the project.

## Features

- Extracts gas price data for a given U.S. state.
- Renames and cleans source fields for downstream storage.
- Loads transformed data into a PostgreSQL database table named `gas_prices`.

## Prerequisites

- Python 3.11 or later
- PostgreSQL database available and reachable
- CollectAPI account with an API key

## Setup

1. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Configure environment variables in a `.env` file at the repository root:
```
COLLECTAPI_KEY=your_collectapi_key_here
DATABASE_URL=postgresql://user:password@host:port/database
```

## Usage

Run the ETL pipeline from the repository root:

```
python src/main.py
```

The pipeline will:

1. call the CollectAPI endpoint to fetch gas prices for the default state (`WA`),
2. transform the returned city-level data,
3. load the result into the configured PostgreSQL database.

## Customization

- To change the state being extracted, update the `state` argument in `src/extract.py`.

## Notes

- The project currently relies on `python-dotenv` for environment variable loading.
- Ensure the `DATABASE_URL` contains valid PostgreSQL credentials and that the target database exists.
- If no API key is provided, the pipeline will raise an exception during extraction.
