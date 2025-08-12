import requests
import dagster as dg
from dagster_duckdb import DuckDBResource
from nyc_opendata_dagster_project.assets import constants
from nyc_opendata_dagster_project.partitions import daily_partition


@dg.asset(
    partitions_def=daily_partition,
    group_name="raw_data",
    description="Downloads NYC 311 data and stores in DuckDB",
)
def nyc311_raw_data(context: dg.AssetExecutionContext, database: DuckDBResource) -> dg.MaterializeResult:
    """
    Downloads daily NYC 311 data from the NYC Open Data API and stores it in DuckDB.
    This asset handles the 'Extract' part of the ETL pipeline.
    """
    partition_date_str = context.partition_key[0:10]
    raw_nyc311_url = (
        f"https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
        f"?$where=created_date between '{partition_date_str}T00:00:00' and '{partition_date_str}T23:59:59'"
    )
    context.log.info(f"Fetching NYC311 data from URL: {raw_nyc311_url}")
    raw_nyc311 = requests.get(raw_nyc311_url)
    context.log.info(f"Status code: {raw_nyc311.status_code}")

    # Store data in DuckDB
    with database.get_connection() as conn:
        # Read CSV data
        import pandas as pd
        import io
        df = pd.read_csv(io.StringIO(raw_nyc311.text))
        df['partition_date'] = partition_date_str
        
        # Drop existing table and recreate with correct schema
        conn.execute("DROP TABLE IF EXISTS nyc311_csv")
        
        # Create table with the actual columns from the CSV
        conn.execute("CREATE TABLE nyc311_csv AS SELECT * FROM df LIMIT 0")
        
        # Insert all data
        conn.execute("INSERT INTO nyc311_csv SELECT * FROM df")
    
    context.log.info(f"Successfully stored NYC311 data in DuckDB for partition {partition_date_str}")
    
    return dg.MaterializeResult(
        metadata={
            "partition_date": dg.MetadataValue.text(partition_date_str),
            "records_processed": dg.MetadataValue.int(len(df))
        }
    )