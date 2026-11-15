"""Load one month of NYC TLC taxi trips from the TLC website into Snowflake RAW."""

import os 
from datetime import datetime, timedelta

from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.sdk import Param, dag, task

from include.ingestion.tlc import ingest_month


SERVICES = ["yellow", "green"]
TABLES = {"yellow": "RAW.YELLOW_TRIPS","green": "RAW.GREEN_TRIPS"}
SNOWFLAKE_CONN_ID = "snowflake_default"


def file_name(service: str, year: int, month: int) -> str:
    return f"{service}_tripdata_{year}-{month:02d}.parquet"


@dag(
    dag_id = "nyc_taxi_monthly",
    schedule = None,
    start_date = datetime(2025, 9 , 1),
    catchup = False,
    default_args = {"retries": 1, "retry_delay": timedelta(minutes = 2)},
    params = {
        "year": Param(2026, type = "integer", minimum = 2009),
        "month": Param(8, type = "integer", minimum = 1, maximum = 12),
    },
    tags = ["nyc_taxi"]
)
def nyc_taxi_monthly():

    @task
    def ingest(service: str, **context) -> dict:
        """Download, validate and upload one month to S3"""
        params = context["params"]
        return ingest_month(service,params["year"],params["month"], bucket = os.environ["S3_BUCKET"])

    @task
    def load(summary: dict) -> dict:
        """Replace this months rows in the RAW table with a fresh COPY INTO"""
        service, year, month = summary["service"], summary["year"], summary["month"]
        table = TABLES[service]
        name  = file_name(service, year, month)
        hook = SnowflakeHook(snowflake_conn_id = SNOWFLAKE_CONN_ID)
        hook.run([
            f"DELETE FROM {table} WHERE _source_file LIKE '%{name}'",
            f"""
            COPY INTO {table} FROM 
            @RAW.S3_RAW_STAGE/{service}/{year}/{month:02d}
            FILE_FORMAT = (FORMAT_NAME = 'RAW.PARQUET_FMT')
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            INCLUDE_METADATA = (
            _source_file = METADATA$FILENAME
            _loaded_at = METADATA$START_SCAN_TIME
            )
            FORCE = TRUE
            """
        ])
        return summary

    @task
    def check_row_count(summary: dict) -> None:
        """Fails if the snowflake table does not have the expected number of rows as the amazon S3 bucket."""
        service, year, month = summary["service"], summary["year"], summary["month"]
        hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
        name = file_name(service, year, month)
        
        loaded = hook.get_first (
            f"SELECT COUNT(*) FROM {TABLES[service]} WHERE _source_file LIKE '%{name}'"
        )[0]

        expected = summary["row_count"]
        if loaded != expected:
            raise ValueError(f"{name}: file has {expected:,} rows but Snowflake has {loaded:,}")
        print(f"{name}: {loaded:,} rows loaded and reconciled ✅")

    for service in SERVICES:
        summary = ingest.override(task_id=f"ingest_{service}")(service)
        loaded = load.override(task_id=f"load_{service}")(summary)
        check_row_count.override(task_id=f"check_{service}")(loaded)


nyc_taxi_monthly()