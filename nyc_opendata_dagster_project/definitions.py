import dagster as dg

from nyc_opendata_dagster_project.resources import database_resource, dbt_resource
from nyc_opendata_dagster_project.jobs import nyc311_job, nypd_arrest_job
# from nyc_opendata_dagster_project.schedules import nyc311_schedule
# from nyc_opendata_dagster_project.sensors import nyc311_sensor
from nyc_opendata_dagster_project.assets import nyc311, dbt_assets, nypd_arrest

nyc311_assets = dg.load_assets_from_modules([nyc311])
nypd_arrest_assets = dg.load_assets_from_modules([nypd_arrest])

all_jobs = [nyc311_job, nypd_arrest_job]

defs = dg.Definitions(
    assets=[*nyc311_assets, *nypd_arrest_assets, dbt_assets.dbt_analytics, dbt_assets.incremental_dbt_models, dbt_assets.dimension_models],
    resources={
        "database": database_resource,
        "dbt": dbt_resource,
    },
    jobs=all_jobs,
)
