import dagster as dg
from nyc311_dagster_project.partitions import daily_partition

nyc311_job = dg.define_asset_job(
    name= "nyc311_job",
    partitions_def=daily_partition,
    selection=dg.AssetSelection.assets(["nyc311_raw_data"]),
)