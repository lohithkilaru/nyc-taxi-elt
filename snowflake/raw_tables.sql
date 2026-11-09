USE ROLE TRANSFORMER;
USE WAREHOUSE TRANSFORM_WH;
USE DATABASE NYC_TAXI;

CREATE TABLE IF NOT EXISTS RAW.YELLOW_TRIPS (
  VendorID                NUMBER,
  tpep_pickup_datetime    TIMESTAMP_NTZ,
  tpep_dropoff_datetime   TIMESTAMP_NTZ,
  passenger_count         NUMBER,
  trip_distance           FLOAT,
  RatecodeID              NUMBER,
  store_and_fwd_flag      VARCHAR,
  PULocationID            NUMBER,
  DOLocationID            NUMBER,
  payment_type            NUMBER,
  fare_amount             FLOAT,
  extra                   FLOAT,
  mta_tax                 FLOAT,
  tip_amount              FLOAT,
  tolls_amount            FLOAT,
  improvement_surcharge   FLOAT,
  total_amount            FLOAT,
  congestion_surcharge    FLOAT,
  airport_fee             FLOAT,
  cbd_congestion_fee      FLOAT,
  _source_file            VARCHAR,
  _loaded_at              TIMESTAMP_LTZ
);


COPY INTO RAW.YELLOW_TRIPS
FROM @RAW.S3_RAW_STAGE/yellow/2026/08/
FILE_FORMAT = (FORMAT_NAME = 'RAW.PARQUET_FMT')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
INCLUDE_METADATA = (
  _source_file = METADATA$FILENAME,
  _loaded_at   = METADATA$START_SCAN_TIME
);

SELECT COUNT(*) FROM RAW.YELLOW_TRIPS;

SELECT * FROM RAW.YELLOW_TRIPS LIMIT 10;