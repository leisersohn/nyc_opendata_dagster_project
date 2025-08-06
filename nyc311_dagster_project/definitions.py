import dagster as dg

from nyc311_dagster_project.resources import database_resource, dbt_resource
from nyc311_dagster_project.jobs import nyc311_job
# from nyc311_dagster_project.schedules import nyc311_schedule
# from nyc311_dagster_project.sensors import nyc311_sensor
from nyc311_dagster_project.assets import nyc311, dbt_assets

nyc311_assets = dg.load_assets_from_modules([nyc311])
all_jobs = [nyc311_job]

defs = dg.Definitions(
    assets=[*nyc311_assets, dbt_assets.dbt_analytics, dbt_assets.incremental_dbt_models],
    resources={
        "database": database_resource,
        "dbt": dbt_resource,
    },
    jobs=all_jobs,
)
