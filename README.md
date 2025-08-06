# NYC 311 Dagster + DBT Project

This is a [Dagster](https://dagster.io/) project integrated with [DBT (Data Build Tool)](https://www.getdbt.com/) for processing NYC 311 service request data. The project fetches daily NYC 311 data from the NYC Open Data API, loads it into a DuckDB database, and uses DBT for data transformation and modeling.

## Project Overview

This project consists of two main components:

1. **Dagster Assets** - Handle data ingestion and orchestration
2. **DBT Models** - Handle data transformation and modeling

### Dagster Assets:
- **`nyc311_raw_data`** - Downloads daily NYC 311 data from the NYC Open Data API and loads it directly into DuckDB
- **`dbt_analytics`** - Orchestrates DBT models (non-incremental)
- **`incremental_dbt_models`** - Orchestrates incremental DBT models with partitioning

### DBT Models:
- **`stg_nyc311`** - Staging model that transforms and cleans the raw NYC 311 data (incremental)

The project uses daily partitioning starting from June 1, 2025 (configurable default), but can fetch data from 2010 onward. You can modify the start date in `nyc311_dagster_project/assets/constants.py` to process historical data.

## Data Flow

```
NYC Open Data API → DuckDB (raw table) → DBT Transformation → DuckDB (staged table)
```

**Detailed Flow:**
1. **Dagster** downloads data from NYC Open Data API
2. **Dagster** loads raw data into `nyc311_csv` table in DuckDB
3. **DBT** transforms the raw data using `stg_nyc311` model
4. **DBT** loads transformed data into `stg_nyc311` table in DuckDB

## Getting Started

### Prerequisites

- Python 3.9-3.12
- Access to NYC Open Data API (public, no authentication required)

### Installation

First, install your Dagster code location as a Python package. By using the --editable flag, pip will install your Python package in ["editable mode"](https://pip.pypa.io/en/latest/topics/local-project-installs/#editable-installs) so that as you develop, local code changes will automatically apply.

```bash
pip install -e ".[dev]"
```

### Environment Setup

Set the DuckDB database path as an environment variable. You can either:

**Option 1: Set environment variable directly**
```bash
# Windows PowerShell
$env:DUCKDB_DATABASE="data/staging/data.duckdb"

# Linux/Mac
export DUCKDB_DATABASE="data/staging/data.duckdb"
```

**Option 2: Use a .env file**
Create a `.env` file in the project root and add:
```
DUCKDB_DATABASE=data/staging/data.duckdb
DAGSTER_ENVIRONMENT=dev
```

### Running the Project

Start the Dagster UI web server:

```bash
dagster dev
```

Open http://localhost:3000 with your browser to see the project.

## Project Structure

```
data/
├── raw/                  # Raw CSV files from API (legacy)
└── staging/              # DuckDB database

nyc311_dagster_project/
├── assets/
│   ├── nyc311.py         # Data ingestion assets
│   ├── dbt_assets.py     # DBT orchestration assets
│   └── constants.py      # Configuration constants
├── partitions.py         # Daily partitioning configuration
├── resources.py          # DuckDB and DBT resource configuration
├── jobs.py               # Job definitions
├── dbt_project.py        # DBT project configuration
└── definitions.py        # Dagster definitions

src/
└── datawarehouse/        # DBT project
    ├── dbt_project.yml   # DBT project configuration
    ├── profiles.yml      # DBT database connection
    ├── models/
    │   ├── sources.yml   # DBT source definitions
    │   └── staging/
    │       └── stg_nyc311.sql  # Staging model
    └── target/           # DBT compilation artifacts
```

## Assets

### nyc311_raw_data
- **Purpose**: Downloads daily NYC 311 data from the NYC Open Data API and loads it directly into DuckDB
- **Partitioning**: Daily partitions starting from 2025-06-01
- **Output**: Data loaded into `nyc311_csv` table in DuckDB
- **Group**: `raw_data`

### dbt_analytics
- **Purpose**: Orchestrates non-incremental DBT models
- **Dependencies**: Automatically detected from DBT manifest
- **Partitioning**: None (for non-incremental models)

### incremental_dbt_models
- **Purpose**: Orchestrates incremental DBT models with partitioning
- **Dependencies**: Automatically detected from DBT manifest
- **Partitioning**: Daily partitions (inherited from Dagster)
- **DBT Variables**: Passes `partition_date`, `min_date`, `max_date` to DBT

## DBT Integration

### DBT Project: `datawarehouse`
The DBT project is located in `src/datawarehouse/` and is automatically discovered by Dagster.

### DBT Models

#### stg_nyc311
- **Purpose**: Staging model that transforms and cleans raw NYC 311 data
- **Materialization**: Incremental
- **Source**: `nyc311_csv` table in DuckDB
- **Partitioning**: Uses `partition_date` variable from Dagster
- **Output**: `stg_nyc311` table in DuckDB

### DBT Sources
The project defines DBT sources in `src/datawarehouse/models/sources.yml`:
- **`raw.nyc311_csv`** - Points to the raw data table created by Dagster

### DBT Dependencies
Dagster automatically detects dependencies between:
- **`nyc311_raw_data`** (Dagster asset) → **`stg_nyc311`** (DBT model)
- This is achieved through the `CustomizedDagsterDbtTranslator` that maps DBT sources to Dagster assets

## Database Schema

### Raw Data (`nyc311_csv` table)
Contains all columns from the NYC 311 API response.

### Staged Data (`stg_nyc311` table)
Transformed and cleaned data with the following key columns:
- `agency_name` - NYC agency handling the request
- `complaint_type` - Type of complaint/service request
- `descriptor` - Detailed description of the issue
- `location_type` - Type of location where the issue occurred
- `partition_date` - Date partition for the data

## Jobs

### nyc311_job
A partitioned job that processes NYC 311 data for specific dates. You can run this job for individual dates or backfill historical data.

## Development

### Adding new Python dependencies

You can specify new Python dependencies in `pyproject.toml`.

### Adding new DBT models

1. Create new SQL files in `src/datawarehouse/models/`
2. Dagster will automatically detect and orchestrate them
3. For incremental models, they will be included in the `incremental_dbt_models` asset
4. For non-incremental models, they will be included in the `dbt_analytics` asset

### Unit testing

Tests are in the `nyc311_dagster_project_tests` directory and you can run tests using `pytest`:

```bash
pytest nyc311_dagster_project_tests
```

### DBT Development

To work with DBT models directly:

```bash
cd src/datawarehouse
dbt run --select stg_nyc311
dbt test
dbt docs generate
```

### Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/guides/automate/schedules/) or [Sensors](https://docs.dagster.io/guides/automate/sensors/) for your jobs, the [Dagster Daemon](https://docs.dagster.io/guides/deploy/execution/dagster-daemon) process must be running. This is done automatically when you run `dagster dev`.

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.

## Data Sources

This project uses the NYC 311 Service Requests dataset from NYC Open Data:
- **API Endpoint**: https://data.cityofnewyork.us/resource/erm2-nwe9.csv
- **Data Source**: NYC 311 Service Requests
- **Update Frequency**: Real-time

## Key Features

- **Automatic DBT Discovery**: Dagster automatically discovers and orchestrates DBT models
- **Partitioning**: Both Dagster assets and DBT models support daily partitioning
- **Dependency Management**: Automatic dependency detection between Dagster assets and DBT models
- **Incremental Processing**: DBT models support incremental materialization for efficient processing
- **Unified Orchestration**: Single Dagster UI for monitoring both data ingestion and transformation

## Deploy on Dagster+

The easiest way to deploy your Dagster project is to use Dagster+.

Check out the [Dagster+ documentation](https://docs.dagster.io/dagster-plus/) to learn more.
