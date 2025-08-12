import json
import dagster as dg
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets
from nyc_opendata_dagster_project.dbt_project import dbt_project
from nyc_opendata_dagster_project.partitions import daily_partition


# Define selectors for different types of models
STAGING_SELECTOR = "fqn:staging"
INCREMENTAL_SELECTOR = "config.materialized:incremental"
STG_NYC311_SELECTOR = "fqn:staging.stg_nyc311"


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
        return dbt_resource_props["fqn"][1]


@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
    exclude=INCREMENTAL_SELECTOR,
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
    # Pass partition date to DBT
    partition_date = context.partition_key
    print(f"Processing partition: {partition_date}")
    dbt_vars = {
        "partition_date": partition_date
    }
    
    yield from dbt.cli(
        ["build", "--vars", json.dumps(dbt_vars)], 
        context=context
    ).stream() 