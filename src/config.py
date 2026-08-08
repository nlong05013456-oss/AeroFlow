"""
config.py
Cấu hình hệ thống AeroFlow GCP Pipeline.
"""
import os

# --- GCP ---
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "aeroflow-cap2-503917")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "aeroflow-data-lake-cap2-new")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "US")

# --- BigQuery Datasets ---
BQ_STAGING_DATASET = "staging"
BQ_WAREHOUSE_DATASET = "warehouse"

# --- URLs dữ liệu tĩnh ---
URLS = {
    "openflights_airlines": "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat",
    "openflights_airports": "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat",
    "openflights_routes": "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat",
    "ourairports_airports": "https://davidmegginson.github.io/ourairports-data/airports.csv",
    "ourairports_countries": "https://davidmegginson.github.io/ourairports-data/countries.csv",
    "ourairports_regions": "https://davidmegginson.github.io/ourairports-data/regions.csv",
    "ourairports_runways": "https://davidmegginson.github.io/ourairports-data/runways.csv",
}

# --- API ---
WEATHER_API_URL = "https://archive-api.open-meteo.com/v1/archive"

# --- Đường dẫn cục bộ ---
LOCAL_DATA_DIR = "Data"
LOCAL_WEATHER_RAW_FILE = os.path.join(LOCAL_DATA_DIR, "Weather", "weather_raw_2026.csv")
