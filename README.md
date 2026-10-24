# Gas Prices ETL Pipeline

[![CI Pipeline](https://github.com/ojpierre/gas-prices-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/ojpierre/gas-prices-etl/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-ready Python ETL pipeline that extracts state- and city-level retail gas pricing data from CollectAPI, performs schema cleaning, type casting, and fuel analytics, and loads the normalized dataset into a PostgreSQL or SQLite relational database using SQLAlchemy.

---

## Architecture Overview

```
                      +-----------------------------+
                      |   CollectAPI Gas Service    |
                      |   (or Offline Mock Data)    |
                      +--------------+--------------+
                                     |
                                     | Extract (HTTP / requests)
                                     v
                      +-----------------------------+
                      |       src/extract.py        |
                      |  - Multi-state query engine |
                      |  - Rate-limit/error handler |
                      +--------------+--------------+
                                     |
                                     | Raw Payload
                                     v
                      +-----------------------------+
                      |      src/transform.py       |
                      |  - Column standardization   |
                      |  - Float type casting       |
                      |  - Fuel spread calculation  |
                      |  - Deduplication & UTC ts   |
                      +--------------+--------------+
                                     |
                                     | Cleaned DataFrame
                                     v
                      +-----------------------------+
                      |        src/load.py          |
                      |  - SQLAlchemy 2.0 Engine    |
                      |  - Declarative Schema       |
                      |  - Append / Replace modes   |
                      +--------------+--------------+
                                     |
                       +-------------+-------------+
                       |                           |
                       v                           v
             +-------------------+       +-------------------+
             |    PostgreSQL     |       |   Local SQLite    |
             |   (Production)    |       |   (Development)   |
             +-------------------+       +-------------------+
```

---

## Features

- **Multi-State & Batch Extraction**: Query single states (e.g. `WA`) or batch queries across multiple states (e.g. `WA,CA,TX`).
- **Data Enrichment & Fuel Analytics**:
  - `price_spread`: Calculates the price difference between premium and regular fuel (`premium - regular`).
  - `diesel_vs_regular`: Tracks the spread between diesel and regular gasoline.
  - `cheapest_fuel`: Evaluates the most economical fuel grade per municipality.
  - `extracted_at`: Ingests an ISO UTC timestamp for historical time-series analytics.
- **Dual Database Engine Support**:
  - Connects to **PostgreSQL** via `psycopg2` when database credentials are provided.
  - Automatically falls back to **SQLite** (`sqlite:///gas_prices.db`) for immediate, zero-dependency local runs and verification.
- **Offline / Sandbox Mode**: Includes a built-in mock dataset matching the CollectAPI schema (`--mock`), allowing users to test and grade the pipeline without requiring a paid API key.
- **Structured Logging**: Uses Python's standard `logging` module with timestamped, level-formatted logs and execution summaries.
- **Automated Testing & CI**: Comprehensive `pytest` test suite with automated GitHub Actions CI covering unit and end-to-end integration flows.

---

## Project Structure

```
gas-prices-etl/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions continuous integration workflow
├── src/
│   ├── __init__.py            # Package initializer
│   ├── config.py              # Centralized environment and database configuration
│   ├── extract.py             # Data extraction module (CollectAPI & mock client)
│   ├── load.py                # Database loading module with SQLAlchemy schema
│   ├── main.py                # Pipeline orchestrator and CLI entrypoint
│   ├── mock_data.py           # Sample CollectAPI dataset for testing/demos
│   └── transform.py           # Data normalization, typing, and analytics module
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test fixtures and in-memory SQLite database
│   ├── test_extract.py        # Extraction and error handling tests
│   ├── test_load.py           # Database schema and loading tests
│   ├── test_pipeline.py       # End-to-end pipeline integration test
│   └── test_transform.py      # Transformation, typing, and metrics tests
├── .env.example               # Example configuration file
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
├── pytest.ini                 # Pytest configuration
├── README.md                  # Project documentation
└── requirements.txt           # Python project dependencies
```

---

## Prerequisites

- Python 3.11 or later
- (Optional) PostgreSQL instance running locally or via Docker
- (Optional) CollectAPI key (required only for live production fetches)

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ojpierre/gas-prices-etl.git
   cd gas-prices-etl
   ```

2. **Create and activate a virtual environment**:
   - **Linux / macOS**:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Configure your credentials:
   ```ini
   # CollectAPI credentials
   COLLECTAPI_KEY=your_collectapi_key_here

   # PostgreSQL connection string (defaults to SQLite if unset)
   DATABASE_URL=postgresql://user:password@localhost:5432/gas_prices
   ```

---

## Usage

### 1. Run with Mock Data (Zero Setup Demo)
To run the full pipeline end-to-end without needing an external database or API key:
```bash
python src/main.py --mock --state WA,CA,TX
```

### 2. Live API Extraction
Fetch live gas prices for Washington State:
```bash
python src/main.py --state WA
```

Fetch live data for multiple states in batch:
```bash
python src/main.py --state WA,CA,TX,NY
```

### 3. Specify Target Database
Point the pipeline to a custom PostgreSQL or SQLite database URL:
```bash
python src/main.py --state WA --db-url "postgresql://postgres:secret@localhost:5432/analytics"
```

### 4. Database Load Modes
- `append` (default): Preserves existing records and appends the new extraction batch:
  ```bash
  python src/main.py --mode append
  ```
- `replace`: Drops and recreates the target table before writing:
  ```bash
  python src/main.py --mode replace
  ```

---

## CLI Reference

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--state` | `-s` | Target US state abbreviation or comma-separated list | `WA` |
| `--db-url` | | Database connection string override | Config / SQLite |
| `--mode` | | Load mode: `append` or `replace` | `append` |
| `--mock` | | Run using built-in synthetic dataset | `False` |
| `--log-level` | | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |

---

## Database Schema (`gas_prices`)

| Column Name | SQL Type | Description |
|-------------|----------|-------------|
| `id` | `INTEGER` | Primary Key, Auto-increment |
| `state` | `VARCHAR(10)` | Two-letter state postal abbreviation (indexed) |
| `city_name` | `VARCHAR(100)` | Municipality name (indexed) |
| `regular` | `FLOAT` | Regular unleaded gasoline price ($ / gallon) |
| `mid_grade` | `FLOAT` | Mid-grade gasoline price ($ / gallon) |
| `premium` | `FLOAT` | Premium gasoline price ($ / gallon) |
| `diesel` | `FLOAT` | Diesel fuel price ($ / gallon) |
| `price_spread` | `FLOAT` | Price difference between premium and regular |
| `diesel_vs_regular`| `FLOAT` | Price difference between diesel and regular |
| `cheapest_fuel` | `VARCHAR(20)` | Fuel grade with lowest price in city |
| `extracted_at` | `TIMESTAMP WITH TIME ZONE` | UTC extraction timestamp |

---

## Running Tests

Execute the complete test suite with coverage:
```bash
pytest -v
```

Run specific test modules:
```bash
pytest tests/test_extract.py -v
pytest tests/test_transform.py -v
pytest tests/test_load.py -v
pytest tests/test_pipeline.py -v
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
