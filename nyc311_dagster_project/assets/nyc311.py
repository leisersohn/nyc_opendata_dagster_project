import requests
import dagster as dg
from dagster_duckdb import DuckDBResource
from nyc311_dagster_project.assets import constants
from nyc311_dagster_project.partitions import daily_partition


@dg.asset(
        partitions_def=daily_partition
)
def nyc311_file(context: dg.AssetExecutionContext) -> None:
    partition_date_str = context.partition_key[0:10]
    raw_nyc311_url = (
        f"https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
        f"?$where=created_date between '{partition_date_str}T00:00:00' and '{partition_date_str}T23:59:59'"
    )
    context.log.info(f"Fetcing NYC311 data from URL: {raw_nyc311_url}")
    raw_nyc311 = requests.get(raw_nyc311_url)
    context.log.info(f"Status code: {raw_nyc311.status_code}")

    file_path = constants.DATA_PATH_TEMPLATE.format(partition_date_str)
    context.log.info(f"Saving NYC311 data to {file_path}")
    with open(file_path,"wb") as output_file:
       output_file.write(raw_nyc311.content)


@dg.asset(
    deps=["nyc311_file"],
    partitions_def=daily_partition
)
def nyc311_data(context: dg.AssetExecutionContext, database: DuckDBResource) -> None:
    """
      Load raw data into DuckDB database
    """
    partition_date_str = context.partition_key[0:10]
    
    query = f"""
        create table if not exists nyc311_data (
          agency_name varchar,
          complaint_type varchar,
          descriptor varchar,
          location_type varchar,
          partition_date varchar
        );

        delete from nyc311_data where partition_date = '{partition_date_str}';

        insert into nyc311_data
        select
            agency_name,
            complaint_type,
            descriptor,
            location_type,
            '{partition_date_str}' as partition_date
          from '{constants.DATA_PATH_TEMPLATE.format(partition_date_str)}';
    """

    with database.get_connection() as conn:
        conn.execute(query)