import requests
import dagster as dg
from dagster_duckdb import DuckDBResource
from nyc_opendata_dagster_project.assets import constants
from nyc_opendata_dagster_project.partitions import daily_partition
from datetime import datetime

@dg.asset(
    partitions_def=daily_partition,
    group_name="raw_data",
    description="Downloads NYPD Arrest data and stores in DuckDB",
)
def nypd_arrest_raw_data(context: dg.AssetExecutionContext, database: DuckDBResource) -> dg.MaterializeResult:
    """
    Downloads daily NYPD arrest data from the NYC Open Data API and stores it in DuckDB.
    This asset handles the 'Extract' part of the ETL pipeline.
    """
    partition_date_str = context.partition_key[0:10]

    partition_date = datetime.strptime(partition_date_str, '%Y-%m-%d')
    current_year = datetime.now().year
    partition_year = partition_date.year

    # Define API URL depdending on year
    if partition_year < current_year:
        # From 2006 until the previous calendar year
        url = 'https://data.cityofnewyork.us/resource/8h9b-rp9u.json'
    elif partition_year == current_year:
        # Current year
        url = 'https://data.cityofnewyork.us/resource/uip8-fykc.json'
    else:
        error_msg = f"Invalid partition date: {partition_date_str} (year: {partition_year})"
        context.log.error(error_msg)
        raise ValueError(error_msg)

    raw_nypd_arrest_url = (
        f"{url}"
        f"?$where=arrest_date between '{partition_date_str}T00:00:00' and '{partition_date_str}T23:59:59'"
    )
    context.log.info(f"Fetching NYPD arrest data from URL: {raw_nypd_arrest_url}")
    raw_nypd_arrest = requests.get(raw_nypd_arrest_url)
    context.log.info(f"Status code: {raw_nypd_arrest.status_code}")

    # Parse JSON response
    try:
        data = raw_nypd_arrest.json()
    except:
        error_msg = f"Failed to parse JSON response: {e}"
        context.log.error(error_msg)
        raise ValueError(error_msg)

    # Check if response is empty
    if not data or len(data) == 0:
        context.log.info(f"No data available for partition {partition_date_str} - skipping")
        return dg.MaterializeResult(
            metadata={
                "partition_date": dg.MetadataValue.text(partition_date_str),
                "records_processed": dg.MetadataValue.int(0),
                "status": dg.MetadataValue.text("skipped_no_data")
            }
        )

    context.log.info(f"Received {len(data)} records from API")

    # Store data in DuckDB
    with database.get_connection() as conn:
        # Read CSV data
        import pandas as pd
        import io
        df = pd.DataFrame(data)
        df['partition_date'] = partition_date_str
        
        # Drop existing table and recreate with correct schema
        conn.execute("DROP TABLE IF EXISTS nypd_arrest_json")
        
        # Create table with the actual columns from the JSON
        conn.execute("CREATE TABLE nypd_arrest_json AS SELECT * FROM df LIMIT 0")
        
        # Insert all data
        conn.execute("INSERT INTO nypd_arrest_json SELECT * FROM df")
    
    context.log.info(f"Successfully stored NYPD arrest data in DuckDB for partition {partition_date_str}")
    
    return dg.MaterializeResult(
        metadata={
            "partition_date": dg.MetadataValue.text(partition_date_str),
            "records_processed": dg.MetadataValue.int(len(df))
        }
    )