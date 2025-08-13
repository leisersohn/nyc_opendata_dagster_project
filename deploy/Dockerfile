FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git \
 && rm -rf /var/lib/apt/lists/*

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