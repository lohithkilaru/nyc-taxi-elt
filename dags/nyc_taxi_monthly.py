"""Load one month of NYC TLC taxi trips from the TLC website into Snowflake RAW.

Scheduled runs on the first day of each month to check if the previous month's data is available to load successfully.
Manual runs can be triggered to load a specific month's data from the Astronomer UI

"""

import os 
from datetime import datetime, timedelta

import requests
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.sdk import Param, dag, task
from airflow.timetables.trigger import CronTriggerTimetable

from include.ingestion.tlc import build_url,ingest_month
from include.alerts import notify_failure


SERVICES = ["yellow", "green"]
TABLES = {"yellow": "RAW.YELLOW_TRIPS","green": "RAW.GREEN_TRIPS"}
SNOWFLAKE_CONN_ID = "snowflake_default"
DBT_PROJECT_DIR = "/usr/local/airflow/dbt"
DBT_BIN = "/usr/local/airflow/dbt_venv/bin/dbt_BROKEN"


def file_name(service: str, year: int, month: int) -> str:
    return f"{service}_tripdata_{year}-{month:02d}.parquet"


@dag(
    dag_id = "nyc_taxi_monthly",
    schedule = CronTriggerTimetable("0 6 1 * *", timezone = "UTC"),
    start_date = datetime(2025, 9 , 1),
    catchup = False,
    max_active_runs=3,
    default_args = {"retries": 1, "retry_delay": timedelta(minutes = 2), "on_failure_callback": notify_failure},
    params = {
        "year": Param(None, type=["null", "integer"], minimum = 2009),
        "month": Param(None, type=["null", "integer"], minimum = 1, maximum = 12),
    },
    tags = ["nyc_taxi"]
)
def nyc_taxi_monthly():

    @task
    def target_month(**context) -> dict:
        """Pick the month to load the params if given, otherwise default to the previous month of the run date"""
        params = context["params"]
        if params.get("year") and params.get("month"):
            return {"year": params["year"], "month": params["month"]}

        run_date = context.get("logical_date") or context["dag_run"].run_after
        last_month = run_date.replace(day=1) - timedelta(days=1)
        return {"year": last_month.year, "month": last_month.month}

    @task.sensor(poke_interval=timedelta(hours = 12), timeout=timedelta(days = 75), mode="reschedule")
    def wait_for_file(service: str, target: dict) -> bool:
        """Succeed if TLC has published a new file"""
        url = build_url(service, target["year"], target["month"])
        return requests.head(url,timeout = 30).status_code == 200

    @task
    def ingest(service: str, target: dict) -> dict:
        """Download, validate and upload one month to S3"""
        return ingest_month(service,target["year"],target["month"], bucket = os.environ["S3_BUCKET"])

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
        print(f"{name}: {loaded:,} rows loaded and reconciled")

    @task.bash
    def dbt_build() -> str:
        """rebuild dbt project after the raw loads"""
        return f"cd {DBT_PROJECT_DIR} && {DBT_BIN} deps && {DBT_BIN} build"


    target = target_month()
    checks = []
    for service in SERVICES:
        waited = wait_for_file.override(task_id = f"wait_{service}")(service,target)
        summary = ingest.override(task_id=f"ingest_{service}")(service,target)
        waited >> summary
        loaded = load.override(task_id=f"load_{service}")(summary)
        checks.append(check_row_count.override(task_id=f"check_{service}")(loaded))
    
    checks >> dbt_build()

nyc_taxi_monthly()