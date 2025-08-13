# NYC OpenData Dagster + DBT Project

This is a [Dagster](https://dagster.io/) project integrated with [DBT (Data Build Tool)](https://www.getdbt.com/) for processing various NYC OpenData datasets. The project fetches data from multiple NYC Open Data APIs, loads it into a DuckDB database, and uses DBT for data transformation and modeling with a proper data warehouse architecture.

## Project Overview

This project consists of two main components:

1. **Dagster Assets** - Handle data ingestion and orchestration for multiple NYC OpenData datasets
2. **DBT Models** - Handle data transformation and modeling with a three-layer data warehouse architecture

### Dagster Assets:
- **`nyc311_raw_data`** - Downloads daily NYC 311 service request data from the NYC Open Data API and loads it directly into DuckDB
- **`nypd_arrest_raw_data`** - Downloads daily NYPD arrest data from the NYC Open Data API and loads it directly into DuckDB
- **`dbt_analytics`** - Orchestrates DBT models (non-incremental)
- **`incremental_dbt_models`** - Orchestrates incremental DBT models with partitioning
- **`dimension_models`** - Orchestrates dimension tables with SCD Type 1 implementation

### DBT Models:
- **Staging Layer**:
  - **`stg_nyc311`** - Staging model that transforms and cleans the raw NYC 311 data (incremental)
  - **`stg_nypd_arrest`** - Staging model that transforms and cleans the raw NYPD arrest data
  - **`stg_dim_pd`** - Staging dimension table for PD codes and descriptions
  - **`stg_dim_ky`** - Staging dimension table for KY codes and descriptions

- **Data Warehouse Layer**:
  - **`dwh_dim_pd`** - DWH dimension table for PD data with SCD Type 1 implementation
  - **`dwh_dim_ky`** - DWH dimension table for KY data with SCD Type 1 implementation
  - **`dwh_nypd_arrest`** - DWH fact table for NYPD arrest data with full historical records, partitioned by date

The project uses daily partitioning starting from June 1, 2025 (configurable default), but can fetch data from 2010 onward. You can modify the start date in `nyc_opendata_dagster_project/assets/constants.py` to process historical data.

## Data Flow

```
NYC Open Data APIs → DuckDB (raw tables) → DBT Staging → DBT DWH (dimensions + facts)
```

**Detailed Flow:**
1. **Dagster** downloads data from multiple NYC Open Data APIs
2. **Dagster** loads raw data into respective tables in DuckDB:
   - `nyc311_csv` table for NYC 311 service requests
   - `nypd_arrest_json` table for NYPD arrest data
3. **DBT Staging** transforms and validates the raw data
4. **DBT DWH** creates business-ready dimension and fact tables:
   - **Dimensions**: Current state using SCD Type 1 (overwrites previous data)
   - **Facts**: Historical data partitioned by date

## Data Warehouse Architecture

### Three-Layer Design

#### 1. **Staging Layer** (Fresh Data Each Run)
- **Purpose**: Data transformation, validation, and cleaning
- **Materialization**: Table with conditional truncate
- **Data Lifecycle**: Fresh data every run, no historical accumulation
- **Tables**: `stg_nypd_arrest`, `stg_dim_pd`, `stg_dim_ky`
- **Exceptions**: `stg_nyc311` which contains historical (partitioned) data (to be re-modelled)

#### 2. **Dimension Layer** (SCD Type 1)
- **Purpose**: Master data with current state
- **Materialization**: Table (full refresh each run)
- **SCD Type 1**: Always reflects current state, overwrites previous data
- **Handles**: Inserts, updates, and deletions from operational systems
- **Tables**: `dwh_dim_pd`, `dwh_dim_ky`

#### 3. **Fact Layer** (Historical Data)
- **Purpose**: Transactional data with full history
- **Materialization**: Incremental with partitioning
- **Partitioning**: By `partition_date` for efficient historical data management
- **Data Lifecycle**: Accumulates historical data across partitions
- **Tables**: `dwh_nypd_arrest`

## Getting Started

### Prerequisites

- Python 3.9-3.12
- Access to NYC Open Data APIs (public, no authentication required)

### Installation

First, install your Dagster code location as a Python package. By using the --editable flag, pip will install your Python package in ["editable mode"](https://pip.pypa.io/en/latest/topics/local-project-installs/#editable-installs) so that as you develop, local code changes will automatically apply.

```bash
pip install -e ".[dev]"
```

### Environment Setup

Set the DuckDB database path as an environment variable. You can either:

**Option 1: Set environment variable directly**
```bash
# Linux/Mac
export DUCKDB_DATABASE="$(pwd)/nyc_opendata_dagster_project/data/staging/data.duckdb"
```

**Option 2: Use a .env file**
Create a `.env` file in the project root and add:
```
DUCKDB_DATABASE=${PWD}/data/staging/data.duckdb
DAGSTER_ENVIRONMENT=dev
```

## Execution Options

### Option 1: Local Execution

The simplest way to run the project locally:

```bash
# Rename .env.example to .env (if it exists)
cp .env.example .env  # or manually create .env file

# Install the project
pip install -e .

# Start Dagster UI
dagster dev -h 0.0.0.0 -p 3000
```

### Option 2: Virtual Environment

For better dependency isolation:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the project
pip install -e .

# Start Dagster UI
dagster dev -h 0.0.0.0 -p 3000
```

### Option 3: Docker

For containerized execution:

```bash
# Navigate to deploy directory
cd deploy

# Rename .env.example to .env (if it exists)
cp .env.example .env  # or manually create .env file

# Install Docker (if not already installed)
# On Ubuntu/Debian:
sudo apt-get update && sudo apt-get install docker.io docker-compose

# On Amazon Linux/RHEL/CentOS:
sudo yum install -y docker docker-compose

# On macOS: Download Docker Desktop from https://www.docker.com/products/docker-desktop

# Build and start services
docker compose build
docker compose up -d
```

**Note**: After starting with any option, open http://localhost:3000 in your browser to access the Dagster UI.

### Running the Project

Start the Dagster UI web server using one of the execution options above:

```bash
dagster dev
```

Open http://localhost:3000 with your browser to see the project.

## Docker Deployment

This project includes a complete Docker setup for production deployment. The Docker configuration provides:

- **Webserver service**: Dagster UI accessible on port 3000
- **Daemon service**: Background job execution and scheduling
- **Persistent storage**: Data and Dagster state preserved across container restarts
- **Environment isolation**: Consistent runtime environment

### Prerequisites for Docker

- Docker and Docker Compose installed
- At least 4GB of available memory
- Port 3000 available on your host machine

### Quick Start with Docker

1. **Navigate to the deploy directory:**
   ```bash
   cd deploy
   ```

2. **Build and start the services:**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the Dagster UI:**
   Open http://localhost:3000 in your browser

4. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f webserver
   docker-compose logs -f daemon
   ```

5. **Stop the services:**
   ```bash
   docker-compose down
   ```

### Docker Configuration Details

#### Services

- **`webserver`**: Runs the Dagster UI on port 3000
- **`daemon`**: Runs the Dagster daemon for background job execution

#### Volumes

- **`./dagster_home:/opt/dagster`**: Persists Dagster's local state
- **`./workspace.yaml:/opt/dagster/workspace.yaml:ro`**: Workspace configuration
- **`../data:/app/data`**: Project data directory (DuckDB files)
- **`../nyc_opendata_dagster_project:/app/nyc_opendata_dagster_project`**: Project source code

#### Environment Variables

The Docker setup uses environment variables from `deploy/.env`:
- `DUCKDB_DATABASE`: Path to DuckDB database file (e.g., `${PWD}/data/staging/data.duckdb`)
- `DAGSTER_ENVIRONMENT`: Environment setting
- `DBT_PROJECT_DIR`: DBT project directory path
- `DBT_PROFILES_DIR`: DBT profiles directory path


## Project Structure

```
data/
├── raw/                  # Raw CSV files from API (legacy)
└── staging/              # DuckDB database

deploy/                   # Docker deployment configuration
├── Dockerfile            # Container image definition
├── docker-compose.yml    # Multi-service orchestration
├── workspace.yaml        # Dagster workspace configuration
├── .env                  # Environment variables for Docker
├── dagster_home/         # Persistent Dagster state (excluded from git)
└── secrets/              # Secret management (excluded from git)

nyc_opendata_dagster_project/
├── assets/
│   ├── nyc311.py         # NYC 311 data ingestion assets
│   ├── nypd_arrest.py    # NYPD arrest data ingestion assets
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
    │   ├── schema.yml    # DBT model documentation and tests
    │   ├── staging/      # Staging layer models
    │   │   ├── stg_nyc311.sql      # NYC 311 staging model
    │   │   ├── stg_nypd_arrest.sql # NYPD arrest staging model
    │   │   ├── stg_dim_pd.sql      # PD dimension staging
    │   │   └── stg_dim_ky.sql      # KY dimension staging
    │   └── dwh/          # Data warehouse layer models
    │       ├── dwh_dim_pd.sql      # PD dimension table
    │       ├── dwh_dim_ky.sql      # KY dimension table
    │       └── dwh_nypd_arrest.sql # NYPD arrest fact table
    └── target/           # DBT compilation artifacts
```

## Assets

### nyc311_raw_data
- **Purpose**: Downloads daily NYC 311 service request data from the NYC Open Data API and loads it directly into DuckDB
- **Partitioning**: Daily partitions starting from 2025-06-01
- **Output**: Data loaded into `nyc311_csv` table in DuckDB

### nypd_arrest_raw_data
- **Purpose**: Downloads daily NYPD arrest data from the NYC Open Data API and loads it directly into DuckDB
- **Partitioning**: Daily partitions starting from 2025-06-01
- **Output**: Data loaded into `nypd_arrest_json` table in DuckDB

### dbt_analytics
- **Purpose**: Orchestrates non-incremental DBT models
- **Dependencies**: Automatically detected from DBT manifest
- **Partitioning**: None (for non-incremental models)

### incremental_dbt_models
- **Purpose**: Orchestrates incremental DBT models with partitioning
- **Dependencies**: Automatically detected from DBT manifest
- **Partitioning**: Daily partitions (inherited from Dagster)
- **DBT Variables**: Passes `partition_date` to DBT
- **Models**: `stg_nyc311`, `dwh_nypd_arrest`

### dimension_models
- **Purpose**: Orchestrates dimension tables with SCD Type 1 implementation
- **Dependencies**: Automatically detected from DBT manifest
- **Partitioning**: None (dimensions maintain current state)
- **Models**: `dwh_dim_pd`, `dwh_dim_ky`

## DBT Integration

### DBT Project: `datawarehouse`
The DBT project is located in `src/datawarehouse/` and is automatically discovered by Dagster.

### DBT Models

#### Staging Layer

##### stg_nyc311
- **Purpose**: Staging model that transforms and cleans raw NYC 311 data
- **Materialization**: Incremental
- **Source**: `nyc311_csv` table in DuckDB
- **Partitioning**: Uses `partition_date` variable from Dagster
- **Output**: `stg_nyc311` table in DuckDB

##### stg_nypd_arrest
- **Purpose**: Staging model that transforms and cleans raw NYPD arrest data
- **Materialization**: Table with conditional truncate
- **Source**: `nypd_arrest_json` table in DuckDB
- **Output**: `stg_nypd_arrest` table in DuckDB

##### stg_dim_pd
- **Purpose**: Staging dimension table for PD codes and descriptions
- **Materialization**: Table with conditional truncate
- **Source**: `nypd_arrest_json` table in DuckDB
- **Output**: `stg_dim_pd` table in DuckDB

##### stg_dim_ky
- **Purpose**: Staging dimension table for KY codes and descriptions
- **Materialization**: Table with conditional truncate
- **Source**: `nypd_arrest_json` table in DuckDB
- **Output**: `stg_dim_ky` table in DuckDB

#### Data Warehouse Layer

##### dwh_dim_pd
- **Purpose**: DWH dimension table for PD data with SCD Type 1 implementation
- **Materialization**: Table (full refresh each run)
- **Source**: `stg_dim_pd` table
- **SCD Type 1**: Always reflects current state, handles inserts/updates/deletions
- **Natural Key**: `pd_id`
- **Output**: `dwh_dim_pd` table in DuckDB

##### dwh_dim_ky
- **Purpose**: DWH dimension table for KY data with SCD Type 1 implementation
- **Materialization**: Table (full refresh each run)
- **Source**: `stg_dim_ky` table
- **SCD Type 1**: Always reflects current state, handles inserts/updates/deletions
- **Natural Key**: `ky_id`
- **Output**: `dwh_dim_ky` table in DuckDB

##### dwh_nypd_arrest
- **Purpose**: DWH fact table for NYPD arrest data with full historical records
- **Materialization**: Incremental with partitioning
- **Source**: `stg_nypd_arrest` table + dimension tables
- **Partitioning**: By `partition_date` for historical data management
- **Pre-hook**: Truncates current partition before loading new data
- **Foreign Keys**: References `dwh_dim_pd.pd_id` and `dwh_dim_ky.ky_id`
- **Output**: `dwh_nypd_arrest` table in DuckDB

### DBT Sources
The project defines DBT sources in `src/datawarehouse/models/sources.yml`:
- **`raw.nyc311_csv`** - Points to the raw NYC 311 data table created by Dagster
- **`raw.nypd_arrest_json`** - Points to the raw NYPD arrest data table created by Dagster

### DBT Dependencies
Dagster automatically detects dependencies between:
- **`nyc311_raw_data`** (Dagster asset) → **`stg_nyc311`** (DBT model)
- **`nypd_arrest_raw_data`** (Dagster asset) → **`stg_nypd_arrest`** (DBT model)
- **`stg_nypd_arrest`** → **`dwh_nypd_arrest`** (fact table)
- **`stg_dim_pd`** → **`dwh_dim_pd`** (dimension table)
- **`stg_dim_ky`** → **`dwh_dim_ky`** (dimension table)

## Database Schema

### Raw Data Tables
- **`nyc311_csv`** - Contains all columns from the NYC 311 API response
- **`nypd_arrest_json`** - Contains all columns from the NYPD arrest API response

### Staging Tables
- **`stg_nyc311`** - Transformed and cleaned NYC 311 data
- **`stg_nypd_arrest`** - Transformed and cleaned NYPD arrest data
- **`stg_dim_pd`** - PD codes and descriptions from NYPD arrest data
- **`stg_dim_ky`** - KY codes and descriptions from NYPD arrest data

## Jobs

### nyc311_job
A partitioned job that processes NYC 311 data for specific dates. You can run this job for individual dates or backfill historical data.

### nypd_arrest_job
A partitioned job that processes NYPD arrest data for specific dates. You can run this job for individual dates or backfill historical data.

## Development

### Adding new Python dependencies

You can specify new Python dependencies in `pyproject.toml`.

### Adding new DBT models

1. Create new SQL files in `src/datawarehouse/models/`
2. Dagster will automatically detect and orchestrate them
3. For incremental models, they will be included in the `incremental_dbt_models` asset
4. For dimension tables, they will be included in the `dimension_models` asset
5. For other models, they will be included in the `dbt_analytics` asset

### Unit testing

Tests are in the `nyc_opendata_dagster_project_tests` directory and you can run tests using `pytest`:

```bash
pytest nyc_opendata_dagster_project_tests
```

### DBT Development

To work with DBT models directly:

```bash
cd src/datawarehouse
dbt run --select stg_nyc311
dbt run --select stg_nypd_arrest
dbt run --select dwh_dim_pd
dbt run --select dwh_dim_ky
dbt run --select dwh_nypd_arrest
dbt test
dbt docs generate
```

### Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/guides/automate/schedules/) or [Sensors](https://docs.dagster.io/guides/automate/sensors/) for your jobs, the [Dagster Daemon](https://docs.dagster.io/guides/deploy/execution/dagster-daemon) process must be running. This is done automatically when you run `dagster dev`.

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.

## Data Sources

This project uses multiple datasets from NYC Open Data:

### NYC 311 Service Requests
- **API Endpoint**: https://data.cityofnewyork.us/resource/erm2-nwe9.csv
- **Data Source**: NYC 311 Service Requests
- **Update Frequency**: Real-time

### NYPD Arrest Data
- **API Endpoint**: 
  - Current year: https://data.cityofnewyork.us/resource/uip8-fykc.json
  - Historical data: https://data.cityofnewyork.us/resource/8h9b-rp9u.json
- **Data Source**: NYPD Arrest Data
- **Update Frequency**: Daily
- **Coverage**: 2006 to present

## Deploy on Dagster+

The easiest way to deploy your Dagster project is to use Dagster+.

Check out the [Dagster+ documentation](https://docs.dagster.io/dagster-plus/) to learn more.
