import json
import dagster as dg
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets
from nyc_opendata_dagster_project.dbt_project import dbt_project
from nyc_opendata_dagster_project.partitions import daily_partition


# Define selectors for different types of models
STAGING_SELECTOR = "fqn:staging"
INCREMENTAL_SELECTOR = "fqn:staging.stg_nyc311 fqn:dwh.dwh_nypd_arrest"  # Only specific incremental models that need partitions
DIMENSION_SELECTOR = "fqn:dwh.dwh_dim_pd fqn:dwh.dwh_dim_ky"  # Only specific dimension tables
STG_NYC311_SELECTOR = "fqn:staging.stg_nyc311"
SNAPSHOT_SELECTOR = "resource_type:snapshot"

class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):

        # Meta override
        dagster_meta = (dbt_resource_props.get("meta") or {}).get("dagster",{})
        ak = dagster_meta.get("asset_key")
        if ak:
            return dg.AssetKey(ak)
        else:
            return super().get_asset_key(dbt_resource_props)
    
    def get_group_name(self, dbt_resource_props):
        if dbt_resource_props.get("resource_type") == "snapshot":
            return "snapshots"
        return dbt_resource_props["fqn"][1]

@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
    exclude=INCREMENTAL_SELECTOR + " " + DIMENSION_SELECTOR + " " + SNAPSHOT_SELECTOR,
)
def dbt_analytics(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
    select=INCREMENTAL_SELECTOR,
    partitions_def=daily_partition,
)
def incremental_dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    # Pass partition date to DBT for incremental models (stg_nyc311 and dwh_nypd_arrest)
    partition_date = context.partition_key
    print(f"Processing partition: {partition_date}")
    dbt_vars = {
        "partition_date": partition_date
    }
    
    yield from dbt.cli(
        ["build", "--vars", json.dumps(dbt_vars)], 
        context=context
    ).stream()

@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
    select=SNAPSHOT_SELECTOR,
)
def snapshot_assets(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["snapshot"], context=context).stream()

@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
    select=SNAPSHOT_SELECTOR + " " + DIMENSION_SELECTOR,
)
def dimension_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    # Dimension tables don't need partitions
    yield from dbt.cli(["build"], context=context).stream() 