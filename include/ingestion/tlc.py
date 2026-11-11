import time
from pathlib import Path

import requests
import pyarrow.parquet as pq
import boto3

'''
Helpers for downloading NYC TLC Trip record data
'''

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
VALID_SERVICES = {"yellow", "green"}

def build_url(service: str, year: int, month: int) -> str:
    """Return the download URL for one month of TLC trip data.

    Example: build_url("yellow", 2026, 8)
    -> https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-08.parquet
    """
    if not isinstance(service, str) or service not in VALID_SERVICES:
        raise ValueError(f"service must be one of {VALID_SERVICES}, got {service!r}")
    if not isinstance(year, int) or not 2009 <= year <= 2100:
        raise ValueError(f"year must be an integer from 2009 onward, got {year!r}")
    if not isinstance(month, int) or not 1 <= month <= 12:
        raise ValueError(f"month must be an integer from 1 to 12, got {month!r}")

    return f"{BASE_URL}/{service}_tripdata_{year}-{month:02d}.parquet"


def s3_key(service: str, year: int, month: int) -> str:
    """Return where this month's file lives in S3, under the raw/ prefix.

    Example: s3_key("yellow", 2026, 8)
    -> raw/yellow/2026/08/yellow_tripdata_2026-08.parquet
    """
    filename = f"{service}_tripdata_{year}-{month:02d}.parquet"
    return f"raw/{service}/{year}/{month:02d}/{filename}"

class MonthNotAvailable(Exception):
     """Raised when TLC hasn't published the requested month yet."""

def download_file(url: str, dest: str | Path, retries: int = 3, backoff_seconds: int = 5) -> Path:
    """Download url to dest, retrying on network errors. Returns the saved path."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")

    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=60) as resp:
                if resp.status_code in (403, 404):
                    raise MonthNotAvailable(f"File not published: {url}")
                resp.raise_for_status()

                with open(tmp, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=1024 * 1024):
                        f.write(chunk)

            tmp.rename(dest)
            return dest

        except MonthNotAvailable:
            raise
        except requests.RequestException as err:
            if attempt == retries:
                raise
            wait = backoff_seconds * 2 ** (attempt - 1)
            print(f"Attempt {attempt} failed ({err}); retrying in {wait}s")
            time.sleep(wait)

class SchemaMismatch(Exception):
    """Raised when a downloaded file is missing expected columns or has no rows."""

EXPECTED_COLUMNS = {
    "yellow": {
        "vendorid", "tpep_pickup_datetime", "tpep_dropoff_datetime",
        "passenger_count", "trip_distance", "ratecodeid", "store_and_fwd_flag",
        "pulocationid", "dolocationid", "payment_type", "fare_amount", "extra",
        "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge",
        "total_amount", "congestion_surcharge", "airport_fee", "cbd_congestion_fee",
    },
    "green": {
        "vendorid", "lpep_pickup_datetime", "lpep_dropoff_datetime",
        "store_and_fwd_flag", "ratecodeid", "pulocationid", "dolocationid",
        "passenger_count", "trip_distance", "fare_amount", "extra", "mta_tax",
        "tip_amount", "tolls_amount", "ehail_fee", "improvement_surcharge",
        "total_amount", "payment_type", "trip_type", "congestion_surcharge",
        "cbd_congestion_fee",
    },
}

def validate_parquet(path: str | Path, service: str) -> int:
    """Check a downloaded file has the expected columns and at least one row.

    Returns the row count. Raises SchemaMismatch if the file looks wrong.
    """
    parquet_file = pq.ParquetFile(path)

    actual = {name.lower() for name in parquet_file.schema_arrow.names}
    expected = EXPECTED_COLUMNS[service]

    missing = expected - actual
    if missing:
        raise SchemaMismatch(f"{path} is missing columns: {sorted(missing)}")

    extra = actual - expected
    if extra:
        print(f"Note: {path} has new columns not in our schema: {sorted(extra)}")

    row_count = parquet_file.metadata.num_rows
    if row_count == 0:
        raise SchemaMismatch(f"{path} has no rows")

    return row_count

def upload_to_s3(local_path: str | Path, bucket: str, key: str, profile: str | None = None) -> str:
    """Upload a local file to s3://bucket/key and confirm the size matches.

    profile: an AWS CLI profile name (e.g. "nyc-taxi") for local runs.
             Leave as None inside Airflow, where credentials come from environment variables.
    Returns the full S3 URI.
    """
    local_path = Path(local_path)
    session = boto3.Session(profile_name=profile)
    s3 = session.client("s3")

    s3.upload_file(str(local_path), bucket, key)

    remote_size = s3.head_object(Bucket=bucket, Key=key)["ContentLength"]
    local_size = local_path.stat().st_size
    if remote_size != local_size:
        raise RuntimeError(
            f"Upload size mismatch for {key}: local {local_size} bytes, S3 {remote_size} bytes"
        )

    return f"s3://{bucket}/{key}"

def ingest_month(
    service: str,
    year: int,
    month: int,
    bucket: str,
    workdir: str | Path = "/tmp/nyc_taxi",
    profile: str | None = None,
) -> dict:
    """Download, validate and upload one month of TLC data to S3.

    Returns a summary: where the file went and how many rows it has.
    """
    url = build_url(service, year, month)
    key = s3_key(service, year, month)
    local_path = Path(workdir) / Path(key).name

    try:
        download_file(url, local_path)
        row_count = validate_parquet(local_path, service)
        uri = upload_to_s3(local_path, bucket, key, profile=profile)
    finally:
        local_path.unlink(missing_ok=True)

    print(f"Ingested {service} {year}-{month:02d}: {row_count:,} rows → {uri}")
    return {"service": service, "year": year, "month": month, "s3_uri": uri, "row_count": row_count}