-- =============================================================================
-- KỊCH BẢN KHỞI TẠO CƠ SỞ DỮ LIỆU DWH (BIGQUERY STAR SCHEMA DDL) - DỰ ÁN AEROFLOW
-- Phù hợp 100% với Sơ đồ mô hình hình sao (Gold Zone DWH)
-- Phân vùng (Partitioning) và Gôm cụm (Clustering) tối ưu hóa truy vấn chi phí
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. BẢNG CHIỀU TĨNH (DIMENSION TABLES)
-- -----------------------------------------------------------------------------

CREATE OR REPLACE TABLE `warehouse.dim_airport` (
    airport_key STRING NOT NULL,
    airport_name STRING NOT NULL,
    city STRING,
    state STRING,
    country STRING,
    latitude FLOAT64,
    longitude FLOAT64,
    elevation_ft INT64,
    timezone_offset INT64,
    runway_count INT64,
    max_runway_length_ft INT64
);

CREATE OR REPLACE TABLE `warehouse.dim_date` (
    date_key DATE NOT NULL,
    year INT64,
    quarter INT64,
    month INT64,
    month_name STRING,
    day INT64,
    day_of_week STRING,
    day_name STRING,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name STRING,
    season STRING
);

CREATE OR REPLACE TABLE `warehouse.dim_weather` (
    weather_key STRING NOT NULL,
    airport_key STRING,
    date_key DATE,
    temp_max_c FLOAT64,
    temp_min_c FLOAT64,
    precipitation_mm FLOAT64,
    snowfall_cm FLOAT64,
    wind_speed_kmh FLOAT64,
    weather_condition STRING
)
CLUSTER BY airport_key;

CREATE OR REPLACE TABLE `warehouse.dim_carrier` (
    carrier_key STRING NOT NULL,
    carrier_name STRING NOT NULL,
    carrier_group STRING,
    country STRING
);

CREATE OR REPLACE TABLE `warehouse.dim_aircraft` (
    aircraft_key STRING NOT NULL,
    carrier_key STRING,
    manufacturer STRING,
    model STRING,
    aircraft_type STRING,
    capacity_seats INT64,
    manufacture_year INT64,
    aircraft_age_years INT64
)
CLUSTER BY carrier_key;

CREATE OR REPLACE TABLE `warehouse.dim_crew` (
    crew_key STRING NOT NULL,
    carrier_key STRING,
    full_name STRING,
    role STRING,
    license_number STRING,
    license_type STRING
)
CLUSTER BY carrier_key;

CREATE OR REPLACE TABLE `warehouse.dim_cancellation_reason` (
    cancellation_code STRING NOT NULL,
    cancellation_desc STRING NOT NULL
);

CREATE OR REPLACE TABLE `warehouse.dim_passenger` (
    passenger_key STRING NOT NULL,
    full_name STRING,
    gender STRING,
    nationality STRING,
    date_of_birth DATE,
    loyalty_tier STRING
);

CREATE OR REPLACE TABLE `warehouse.dim_ticket` (
    ticket_key STRING NOT NULL,
    booking_reference STRING,
    fare_class STRING,
    ticket_price_usd FLOAT64,
    purchase_date DATE
);

-- -----------------------------------------------------------------------------
-- 2. BẢNG SỰ KIỆN (FACT TABLES)
-- -----------------------------------------------------------------------------

CREATE OR REPLACE TABLE `warehouse.fact_flights` (
    flight_key STRING NOT NULL,
    carrier_key STRING,
    aircraft_key STRING,
    origin_airport_key STRING,
    dest_airport_key STRING,
    origin_weather_key STRING,
    dest_weather_key STRING,
    cancellation_code STRING,
    flight_number STRING,
    tail_number_sha256 STRING,
    dep_delay_min INT64,
    arr_delay_min INT64,
    cancelled BOOLEAN,
    diverted BOOLEAN,
    distance_miles FLOAT64,
    taxi_out_min INT64,
    taxi_in_min INT64,
    air_time_min INT64,
    actual_elapsed_min INT64,
    carrier_delay_min INT64,
    weather_delay_min INT64,
    nas_delay_min INT64,
    security_delay_min INT64,
    late_aircraft_delay_min INT64
)
PARTITION BY DATE(flight_key) -- hoặc phân vùng theo date_key của chuyến bay
CLUSTER BY carrier_key, origin_airport_key, dest_airport_key;

CREATE OR REPLACE TABLE `warehouse.fact_crew_assignment` (
    crew_key STRING NOT NULL,
    aircraft_key STRING,
    duty_hours FLOAT64,
    performance_rating FLOAT64
)
CLUSTER BY crew_key, aircraft_key;

CREATE OR REPLACE TABLE `warehouse.fact_passenger_manifest` (
    flight_key STRING NOT NULL,
    passenger_key STRING NOT NULL,
    ticket_key STRING,
    checkin_time TIMESTAMP,
    baggage_weight_kg FLOAT64,
    seat_number STRING
)
CLUSTER BY flight_key, passenger_key;
