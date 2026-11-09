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