import pyarrow as pa
import pyarrow.parquet as pq
import pytest


from include.ingestion.tlc import (
    EXPECTED_COLUMNS,
    SchemaMismatch,
    build_url,
    s3_key,
    validate_parquet,
)


def test_build_url_yellow():
    assert build_url("yellow", 2026, 8) == (
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-08.parquet"
    )


def test_build_url_two_digit_month():
    assert build_url("yellow", 2025, 11) == (
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet"
    )


def test_build_url_pads_single_digit_month():
    assert build_url("green", 2025, 9).endswith("green_tripdata_2025-09.parquet")


@pytest.mark.parametrize(
    "service, year, month",
    [
        ("purple", 2026, 8),    # unknown service
        ("yellow", 2026, 13),   # month too high
        ("yellow", 2026, 0),    # month too low
        ("yellow", 2008, 1),    # before TLC data exists
        ("yellow", "2026", 8),  # year as text
        ("yellow", 2026, 8.0),  # month as a decimal
    ],
)
def test_build_url_rejects_bad_input(service, year, month):
    with pytest.raises(ValueError):
        build_url(service, year, month)


# ---------- s3_key ----------

def test_s3_key_layout():
    assert s3_key("yellow", 2026, 8) == "raw/yellow/2026/08/yellow_tripdata_2026-08.parquet"


# ---------- validate_parquet ----------

def make_parquet(path, columns, rows=3):
    """Write a small fake Parquet file with the given column names."""
    table = pa.table({col: pa.array(range(rows), type=pa.int64()) for col in columns})
    pq.write_table(table, path)


def test_validate_parquet_returns_row_count(tmp_path):
    path = tmp_path / "ok.parquet"
    make_parquet(path, EXPECTED_COLUMNS["green"], rows=5)
    assert validate_parquet(path, "green") == 5


def test_validate_parquet_ignores_column_case(tmp_path):
    path = tmp_path / "upper.parquet"
    make_parquet(path, [c.upper() for c in EXPECTED_COLUMNS["yellow"]])
    assert validate_parquet(path, "yellow") == 3


def test_validate_parquet_allows_extra_columns(tmp_path):
    path = tmp_path / "extra.parquet"
    make_parquet(path, EXPECTED_COLUMNS["yellow"] | {"brand_new_fee"})
    assert validate_parquet(path, "yellow") == 3


def test_validate_parquet_missing_column_raises(tmp_path):
    path = tmp_path / "missing.parquet"
    make_parquet(path, EXPECTED_COLUMNS["yellow"] - {"fare_amount"})
    with pytest.raises(SchemaMismatch, match="fare_amount"):
        validate_parquet(path, "yellow")


def test_validate_parquet_empty_file_raises(tmp_path):
    path = tmp_path / "empty.parquet"
    make_parquet(path, EXPECTED_COLUMNS["green"], rows=0)
    with pytest.raises(SchemaMismatch, match="no rows"):
        validate_parquet(path, "green")