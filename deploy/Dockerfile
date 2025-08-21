FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git wget unzip \
 && rm -rf /var/lib/apt/lists/*

# Install DuckDB CLI
RUN wget https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip \
 && unzip duckdb_cli-linux-amd64.zip \
 && mv duckdb /usr/local/bin/ \
 && chmod +x /usr/local/bin/duckdb \
 && rm duckdb_cli-linux-amd64.zip

ENV PYTHONUNBUFFERED=1 \
    DAGSTER_HOME=/opt/dagster \
    DBT_PROJECT_DIR=/app/src/datawarehouse

WORKDIR /app

# Copy metadata first (cache-friendly)
COPY pyproject.toml ./
# If you have a lockfile (poetry.lock / pdm.lock / hatch.toml), COPY it too

# Copy your FLAT-LAYOUT package and dbt project so the build sees them
COPY nyc_opendata_dagster_project/ ./nyc_opendata_dagster_project/
COPY src/datawarehouse/ ./src/datawarehouse/

# Install strictly from pyproject (no ad-hoc deps)
RUN pip3 install --no-cache-dir -U pip setuptools wheel build \
 && pip3 install --no-cache-dir .

# Bring in the rest (README, configs, data dir, etc.) without breaking cache above
COPY . .

RUN mkdir -p $DAGSTER_HOME
CMD ["bash","-lc","sleep infinity"]