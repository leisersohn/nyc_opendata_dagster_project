# NYC 311 Dagster Project

This is a [Dagster](https://dagster.io/) project for processing NYC 311 service request data. The project fetches daily NYC 311 data from the NYC Open Data API and loads it into a DuckDB database for analysis.

## Project Overview

This project consists of two main assets:

1. **`nyc311_file`** - Downloads daily NYC 311 data from the NYC Open Data API and saves it as CSV files
2. **`nyc311_data`** - Loads the raw CSV data into a DuckDB database table for analysis

The project uses daily partitioning starting from June 1, 2025 (configurable default), but can fetch data from 2010 onward. You can modify the start date in `nyc311_dagster_project/assets/constants.py` to process historical data.

## Data Flow

```
NYC Open Data API → CSV Files (data/raw/) → DuckDB Database (data/staging/)
```

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
```

### Running the Project

Start the Dagster UI web server:

```bash
dagster dev
```

Open http://localhost:3000 with your browser to see the project.

## Project Structure

```
nyc311_dagster_project/
├── assets/
│   ├── nyc311.py          # Main data processing assets
│   └── constants.py       # Configuration constants
├── data/
│   ├── raw/              # Raw CSV files from API
│   └── staging/          # DuckDB database
├── partitions.py         # Daily partitioning configuration
├── resources.py          # DuckDB resource configuration
├── jobs.py              # Job definitions
└── definitions.py       # Dagster definitions
```

## Assets

### nyc311_file
- **Purpose**: Downloads daily NYC 311 data from the NYC Open Data API
- **Partitioning**: Daily partitions starting from 2025-06-01
- **Output**: CSV files in `data/raw/nyc311_YYYY-MM-DD.csv`

### nyc311_data
- **Purpose**: Loads a subset of columns from raw CSV data into DuckDB database (for practice purposes)
- **Dependencies**: `nyc311_file`
- **Partitioning**: Daily partitions
- **Output**: Data loaded into `nyc311_data` table in DuckDB

## Database Schema

The `nyc311_data` table contains the following columns:
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

### Unit testing

Tests are in the `nyc311_dagster_project_tests` directory and you can run tests using `pytest`:

```bash
pytest nyc311_dagster_project_tests
```

### Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/guides/automate/schedules/) or [Sensors](https://docs.dagster.io/guides/automate/sensors/) for your jobs, the [Dagster Daemon](https://docs.dagster.io/guides/deploy/execution/dagster-daemon) process must be running. This is done automatically when you run `dagster dev`.

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.

## Data Sources

This project uses the NYC 311 Service Requests dataset from NYC Open Data:
- **API Endpoint**: https://data.cityofnewyork.us/resource/erm2-nwe9.csv
- **Data Source**: NYC 311 Service Requests
- **Update Frequency**: Real-time

## Deploy on Dagster+

The easiest way to deploy your Dagster project is to use Dagster+.

Check out the [Dagster+ documentation](https://docs.dagster.io/dagster-plus/) to learn more.
