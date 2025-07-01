import dagster as dg
from nyc311_dagster_project.assets import constants

daily_partition = dg.DailyPartitionsDefinition(start_date=constants.START_DATE)