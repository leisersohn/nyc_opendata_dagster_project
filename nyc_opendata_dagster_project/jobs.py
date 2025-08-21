import dagster as dg
from nyc_opendata_dagster_project.partitions import daily_partition

nyc311_job = dg.define_asset_job(
    name= "nyc311_job",
    partitions_def=daily_partition,
    selection=dg.AssetSelection.assets(["nyc311_raw_data"]),
)

nypd_arrest_job = dg.define_asset_job(
    name= "nypd_arrest_job",
    partitions_def=daily_partition,
    selection=dg.AssetSelection.assets(["nypd_arrest_raw_data"])
)

nypd_per_partition_job = dg.define_asset_job(
    name="nypd_per_partition_job",
    partitions_def=daily_partition,
    selection=dg.AssetSelection.keys("dwh_nypd_arrest").upstream(),
    tags={"flow": "nypd_arrest"},
)