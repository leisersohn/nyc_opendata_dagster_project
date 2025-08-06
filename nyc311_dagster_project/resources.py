import dagster as dg
from dagster_duckdb import DuckDBResource
from dagster_dbt import DbtCliResource
from nyc311_dagster_project.dbt_project import dbt_project

database_resource = DuckDBResource(
    database=dg.EnvVar("DUCKDB_DATABASE")
)

dbt_resource = DbtCliResource(
    project_dir=dbt_project.project_dir,
)