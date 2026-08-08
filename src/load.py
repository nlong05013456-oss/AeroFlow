"""
load.py
Thực hiện tải các tệp metadata tĩnh (OurAirports, OpenFlights) từ URL,
lưu trữ lên GCS Data Lake, và nạp tất cả dữ liệu thô từ GCS vào BigQuery Staging (L - Load).
"""

import os
import datetime
import requests
import pandas as pd
from google.cloud import bigquery
from google.cloud import storage
from src.config import (
    GCP_PROJECT_ID,
    GCS_BUCKET_NAME,
    GCP_LOCATION,
    BQ_STAGING_DATASET,
    BQ_WAREHOUSE_DATASET,
    LOCAL_DATA_DIR,
    URLS
)

# --- KHỞI TẠO CLIENTS ---
def get_bq_client():
    """Khởi tạo BigQuery Client."""
    return bigquery.Client(project=GCP_PROJECT_ID)

def get_gcs_client():
    """Khởi tạo GCS Client."""
    return storage.Client(project=GCP_PROJECT_ID)

def upload_to_gcs(local_path, gcs_blob_name):
    """Upload một file cục bộ lên GCS Bucket."""
    if not os.path.exists(local_path):
        print(f"Lỗi: Không tìm thấy file cục bộ để upload: {local_path}")
        return False
    client = get_gcs_client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(gcs_blob_name)
    print(f"Tải lên GCS: {local_path} -> gs://{GCS_BUCKET_NAME}/{gcs_blob_name}")
    blob.upload_from_filename(local_path)
    return True

# --- TẠO DATASETS NẾU CHƯA CÓ ---
def create_datasets():
    """Tạo staging và warehouse datasets trong BigQuery."""
    client = get_bq_client()
    for dataset_name in [BQ_STAGING_DATASET, BQ_WAREHOUSE_DATASET]:
        dataset_id = f"{GCP_PROJECT_ID}.{dataset_name}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = GCP_LOCATION
        
        try:
            client.get_dataset(dataset_id)
            print(f"Dataset '{dataset_name}' đã tồn tại.")
        except Exception:
            print(f"Dataset '{dataset_name}' chưa tồn tại. Tiến hành tạo mới...")
            client.create_dataset(dataset, timeout=30)
            print(f"Tạo thành công dataset: {dataset_id}")

# --- TẢI CÁC TỆP METADATA TĨNH VÀ ĐẨY LÊN GCS ---
def download_and_upload_static_metadata():
    """Tải trực tiếp các file metadata tĩnh từ URL và đẩy lên GCS làm Bronze Data Lake."""
    os.makedirs(os.path.join(LOCAL_DATA_DIR, "OpenFlights"), exist_ok=True)
    os.makedirs(os.path.join(LOCAL_DATA_DIR, "OurAirports"), exist_ok=True)
    
    for name, url in URLS.items():
        folder = "OpenFlights" if "openflights" in name else "OurAirports"
        filename = url.split("/")[-1]
        local_path = os.path.join(LOCAL_DATA_DIR, folder, filename)
        
        print(f"Đang tải dữ liệu tĩnh {name} từ {url} ...")
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(response.content)
                print(f"Lưu thành công vào: {local_path}")
                # Đẩy file thô trực tiếp lên GCS lưu trữ
                upload_to_gcs(local_path, f"raw/{folder}/{filename}")
            else:
                print(f"Lỗi khi tải {name}: Mã phản hồi {response.status_code}")
        except Exception as e:
            print(f"Thất bại khi tải {name}: {e}")

# --- NẠP FILE CSV TỪ GCS VÀO BIGQUERY ---
def load_csv_gcs_to_bq(gcs_blob_path, table_name, skip_leading_rows=1, autodetect=True, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE):
    """Nạp file CSV từ GCS vào BigQuery staging."""
    client = get_bq_client()
    table_id = f"{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.{table_name}"
    
    schema = None
    if write_disposition == bigquery.WriteDisposition.WRITE_APPEND:
        try:
            tbl_obj = client.get_table(table_id)
            schema = tbl_obj.schema
            autodetect = False
        except Exception:
            autodetect = True
        
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=skip_leading_rows,
        autodetect=autodetect,
        schema=schema,
        write_disposition=write_disposition,
        allow_quoted_newlines=True,
        allow_jagged_rows=True,
        ignore_unknown_values=True
    )
    
    uri = f"gs://{GCS_BUCKET_NAME}/{gcs_blob_path}"
    print(f"Đang chạy load job: {uri} -> {table_id} (Mode: {write_disposition}, autodetect: {autodetect}) ...")
    try:
        load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()  # Đợi load job hoàn thành
        destination_table = client.get_table(table_id)
        print(f"Nạp thành công! Bảng hiện có {destination_table.num_rows:,} dòng.")
    except Exception as e:
        print(f"Cảnh báo nạp BigQuery: {e}")

# --- NẠP CÁC FILE KHÔNG CÓ HEADER (OPENFLIGHTS) QUA PANDAS DATAFRAME ---
OPENFLIGHTS_COLS = {
    "airlines": ["airline_id", "name", "alias", "iata", "icao", "callsign", "country", "active"],
    "airports": ["airport_id", "name", "city", "country", "iata", "icao", "lat", "lon",
                 "altitude", "timezone", "dst", "tz_db", "type", "source"],
    "routes":   ["airline", "airline_id", "src_airport", "src_airport_id",
                 "dst_airport", "dst_airport_id", "codeshare", "stops", "equipment"],
}

def load_openflights_to_bq():
    """Đọc dữ liệu OpenFlights cục bộ, gán header và load vào BigQuery."""
    client = get_bq_client()
    
    files = {
        "stg_airlines_of": (os.path.join(LOCAL_DATA_DIR, "OpenFlights", "airlines.dat"), OPENFLIGHTS_COLS["airlines"]),
        "stg_airports_of": (os.path.join(LOCAL_DATA_DIR, "OpenFlights", "airports.dat"), OPENFLIGHTS_COLS["airports"]),
        "stg_routes_of":   (os.path.join(LOCAL_DATA_DIR, "OpenFlights", "routes.dat"), OPENFLIGHTS_COLS["routes"]),
    }
    
    for table_name, (local_path, cols) in files.items():
        if not os.path.exists(local_path):
            print(f"Cảnh báo: Không thấy file {local_path}. Bỏ qua nạp {table_name}.")
            continue
        
        print(f"Đang xử lý OpenFlights file {local_path} ...")
        df = pd.read_csv(local_path, header=None, names=cols, on_bad_lines="skip", na_values="\\N")
        
        if "airline_id" in df.columns:
            df["airline_id"] = pd.to_numeric(df["airline_id"], errors="coerce")
        if "airport_id" in df.columns:
            df["airport_id"] = pd.to_numeric(df["airport_id"], errors="coerce")
            
        table_id = f"{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.{table_name}"
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        print(f"Đang nạp DataFrame -> BigQuery: {table_id} ...")
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        print(f"Nạp thành công {table_name} ({len(df):,} dòng).")

# --- PIPELINE NẠP STAGING ---
def run_loading_pipeline():
    """Chạy toàn bộ pipeline Load dữ liệu vào BigQuery Staging."""
    print("--- KHỞI ĐỘNG PIPELINE LOADING (LOAD STAGING) ---")
    create_datasets()
    
    # 1. Tải và đưa các file dữ liệu tĩnh lên GCS (Tự động tải ở bước L)
    download_and_upload_static_metadata()
    
    # 2. Nạp tệp chuyến bay (Quét động từ GCS)
    client = get_gcs_client()
    
    try:
        bucket = client.bucket(GCS_BUCKET_NAME)
        
        # Tự động quét toàn bộ các file tháng có dạng raw/Flights/us_flights_2026_*.csv trên GCS
        blobs = bucket.list_blobs(prefix="raw/Flights/us_flights_2026_")
        found_monthly_files = sorted([
            blob.name for blob in blobs 
            if blob.name.endswith(".csv")
        ])
        
        if found_monthly_files:
            print(f"Phát hiện {len(found_monthly_files)} file chuyến bay trên GCS: {found_monthly_files}")
            # Nạp file đầu tiên bằng chế độ TRUNCATE để dọn dẹp bảng cũ
            first_file = found_monthly_files[0]
            print(f"-> Đang nạp nền (TRUNCATE) từ: {first_file}")
            load_csv_gcs_to_bq(first_file, "stg_flights_raw", write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
            
            # Nạp nối tiếp các file tháng tiếp theo bằng chế độ APPEND
            for file_path in found_monthly_files[1:]:
                print(f"-> Đang nạp nối tiếp (APPEND) từ: {file_path}")
                load_csv_gcs_to_bq(file_path, "stg_flights_raw", write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
        else:
            print("Lỗi: Không tìm thấy bất kỳ tệp chuyến bay nào trên GCS để nạp!")
            return
    except Exception as e:
        print(f"Lỗi khi quét file chuyến bay trên GCS: {e}")
        return
        
    # 3. Nạp tệp thời tiết (Tải từ GCS về BigQuery - nạp chế độ Truncate)
    load_csv_gcs_to_bq("raw/Weather/weather_raw_2026.csv", "stg_weather_raw", write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
    
    # 4. Nạp OurAirports CSVs từ GCS sang BigQuery
    load_csv_gcs_to_bq("raw/OurAirports/airports.csv", "stg_airports_our")
    load_csv_gcs_to_bq("raw/OurAirports/countries.csv", "stg_countries_our")
    load_csv_gcs_to_bq("raw/OurAirports/regions.csv", "stg_regions_our")
    load_csv_gcs_to_bq("raw/OurAirports/runways.csv", "stg_runways_our")
    
    # 5. Nạp OpenFlights (Gán header qua pandas và load)
    load_openflights_to_bq()
    
    print("--- HOÀN THÀNH PIPELINE LOADING ---")

def run_daily_loading_pipeline(date_str=None):
    """Nạp nối tiếp (WRITE_APPEND) dữ liệu chuyến bay và thời tiết ngày cụ thể vào BigQuery Staging."""
    if date_str is None:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
    print(f"--- KHỞI ĐỘNG PIPELINE LOADING DAILY ({date_str}) ---")
    
    flight_gcs_path = f"raw/Flights/us_flights_daily_{date_str}.csv"
    print(f"-> Đang nạp nối tiếp chuyến bay ngày: {flight_gcs_path}")
    load_csv_gcs_to_bq(flight_gcs_path, "stg_flights_raw", write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
    
    weather_gcs_path = f"raw/Weather/weather_daily_{date_str}.csv"
    print(f"-> Đang nạp nối tiếp thời tiết ngày: {weather_gcs_path}")
    load_csv_gcs_to_bq(weather_gcs_path, "stg_weather_raw", write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
    
    print("--- HOÀN THÀNH PIPELINE LOADING DAILY ---")

if __name__ == "__main__":
    run_loading_pipeline()
