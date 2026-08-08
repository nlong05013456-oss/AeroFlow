"""
quality.py
Thực hiện các bài kiểm tra chất lượng dữ liệu (Data Quality Checks)
trên các bảng thuộc Schema Data Warehouse trong BigQuery theo mô hình chốt cuối.
"""

from google.cloud import bigquery
from src.config import GCP_PROJECT_ID, BQ_WAREHOUSE_DATASET

def get_bq_client():
    """Khởi tạo BigQuery Client."""
    return bigquery.Client(project=GCP_PROJECT_ID)

def run_test_query(query_str, test_name):
    """
    Chạy truy vấn SQL kiểm tra và trả về số dòng lỗi.
    Nếu số dòng lỗi > 0, bài test thất bại.
    """
    client = get_bq_client()
    query_job = client.query(query_str)
    result = query_job.result()
    
    # Lấy dòng kết quả đầu tiên
    for row in result:
        error_count = row[0]
        if error_count == 0:
            print(f"  [PASS] {test_name}")
            return True
        else:
            print(f"  [FAIL] {test_name}: Phát hiện {error_count:,} dòng lỗi!")
            return False
    return False

# --- 1. KIỂM TRA KHÓA CHÍNH (PK UNIQUENESS & NOT NULL) ---
def test_primary_keys():
    print("\n--- 1. Kiểm tra tính duy nhất & Không Null của Khóa Chính (Primary Keys) ---")
    
    # Kiểm tra dim_airport
    q_airport = f"""
    SELECT COUNT(*) 
    FROM (
        SELECT airport_key, COUNT(*) as cnt 
        FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_airport` 
        GROUP BY airport_key 
        HAVING cnt > 1 OR airport_key IS NULL
    )
    """
    r1 = run_test_query(q_airport, "dim_airport: airport_key PK constraint")
    
    # Kiểm tra dim_carrier
    q_carrier = f"""
    SELECT COUNT(*) 
    FROM (
        SELECT carrier_key, COUNT(*) as cnt 
        FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_carrier` 
        GROUP BY carrier_key 
        HAVING cnt > 1 OR carrier_key IS NULL
    )
    """
    r2 = run_test_query(q_carrier, "dim_carrier: carrier_key PK constraint")
    
    # Kiểm tra dim_aircraft
    q_aircraft = f"""
    SELECT COUNT(*) 
    FROM (
        SELECT aircraft_key, COUNT(*) as cnt 
        FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_aircraft` 
        GROUP BY aircraft_key 
        HAVING cnt > 1 OR aircraft_key IS NULL
    )
    """
    r3 = run_test_query(q_aircraft, "dim_aircraft: aircraft_key PK constraint")
    
    # Kiểm tra dim_date
    q_date = f"""
    SELECT COUNT(*) 
    FROM (
        SELECT date_key, COUNT(*) as cnt 
        FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_date` 
        GROUP BY date_key 
        HAVING cnt > 1 OR date_key IS NULL
    )
    """
    r4 = run_test_query(q_date, "dim_date: date_key PK constraint")
    
    # Kiểm tra dim_weather
    q_weather = f"""
    SELECT COUNT(*) 
    FROM (
        SELECT weather_key, COUNT(*) as cnt 
        FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_weather` 
        GROUP BY weather_key 
        HAVING cnt > 1 OR weather_key IS NULL
    )
    """
    r5 = run_test_query(q_weather, "dim_weather: weather_key PK constraint")
    
    # Kiểm tra fact_flights
    q_flights = f"""
    SELECT COUNT(*) 
    FROM (
        SELECT flight_key, COUNT(*) as cnt 
        FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.fact_flights` 
        GROUP BY flight_key 
        HAVING cnt > 1 OR flight_key IS NULL
    )
    """
    r6 = run_test_query(q_flights, "fact_flights: flight_key PK constraint")
    
    return all([r1, r2, r3, r4, r5, r6])

# --- 2. KIỂM TRA TÍNH TOÀN VẸN THAM CHIẾU (REFERENTIAL INTEGRITY - FK) ---
def test_referential_integrity():
    print("\n--- 2. Kiểm tra tính toàn vẹn tham chiếu (Foreign Keys) ---")
    
    # Kiểm tra khóa ngoại Hãng hàng không (carrier_key)
    q_carrier = f"""
    SELECT COUNT(*) 
    FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.fact_flights` f
    LEFT JOIN `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_carrier` c ON f.carrier_key = c.carrier_key
    WHERE c.carrier_key IS NULL AND f.carrier_key IS NOT NULL
    """
    r1 = run_test_query(q_carrier, "fact_flights -> dim_carrier (Carrier FK)")
    
    # Kiểm tra khóa ngoại Tàu bay (aircraft_key)
    q_aircraft = f"""
    SELECT COUNT(*) 
    FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.fact_flights` f
    LEFT JOIN `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_aircraft` ac ON f.aircraft_key = ac.aircraft_key
    WHERE ac.aircraft_key IS NULL AND f.aircraft_key IS NOT NULL
    """
    r2 = run_test_query(q_aircraft, "fact_flights -> dim_aircraft (Aircraft FK)")
    
    # Kiểm tra khóa ngoại Sân bay nguồn (origin_airport_key)
    q_origin = f"""
    SELECT COUNT(*) 
    FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.fact_flights` f
    LEFT JOIN `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_airport` a ON f.origin_airport_key = a.airport_key
    WHERE a.airport_key IS NULL AND f.origin_airport_key IS NOT NULL
    """
    r3 = run_test_query(q_origin, "fact_flights -> dim_airport (Origin Airport FK)")
    
    # Kiểm tra khóa ngoại Sân bay đích (dest_airport_key)
    q_dest = f"""
    SELECT COUNT(*) 
    FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.fact_flights` f
    LEFT JOIN `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_airport` a ON f.dest_airport_key = a.airport_key
    WHERE a.airport_key IS NULL AND f.dest_airport_key IS NOT NULL
    """
    r4 = run_test_query(q_dest, "fact_flights -> dim_airport (Dest Airport FK)")
    
    # Kiểm tra khóa ngoại Lý do hủy (cancellation_code)
    q_cancel = f"""
    SELECT COUNT(*) 
    FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.fact_flights` f
    LEFT JOIN `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_cancellation_reason` c ON f.cancellation_code = c.cancellation_code
    WHERE c.cancellation_code IS NULL AND f.cancellation_code IS NOT NULL
    """
    r5 = run_test_query(q_cancel, "fact_flights -> dim_cancellation_reason (Cancellation FK)")
    
    return all([r1, r2, r3, r4, r5])

# --- 3. KIỂM TRA RÀNG BUỘC MIỀN GIÁ TRỊ VÀ HỢP LỆ (DOMAIN CONSTRAINTS) ---
def test_domain_constraints():
    print("\n--- 3. Kiểm tra ràng buộc miền giá trị hợp lệ ---")
    
    # Kiểm tra xem có dòng nào trong fact có ID bị null không
    q_null_key = f"""
    SELECT COUNT(*) 
    FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.fact_flights` 
    WHERE flight_key IS NULL
    """
    r1 = run_test_query(q_null_key, "fact_flights: flight_key cannot be NULL")
    
    # Kiểm tra xem khoảng cách bay có âm không
    q_dist = f"""
    SELECT COUNT(*) 
    FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.fact_flights` 
    WHERE distance_miles <= 0
    """
    r2 = run_test_query(q_dist, "fact_flights: distance_miles must be positive (> 0)")

    # Kiểm tra tổng số dòng trong bảng Fact (đảm bảo không bị trống rỗng)
    client = get_bq_client()
    table_ref = client.dataset(BQ_WAREHOUSE_DATASET).table("fact_flights")
    table = client.get_table(table_ref)
    
    if table.num_rows > 0:
        print(f"  [PASS] fact_flights: Table contains {table.num_rows:,} rows.")
        r3 = True
    else:
        print("  [FAIL] fact_flights: Table is EMPTY!")
        r3 = False
        
    return all([r1, r2, r3])

# --- CHẠY TOÀN BỘ DATA QUALITY PIPELINE ---
def run_quality_pipeline():
    print("=== BẮT ĐẦU CHẠY KIỂM ĐỊNH CHẤT LƯỢNG DỮ LIỆU (DATA QUALITY AUDIT) ===")
    pk_ok = test_primary_keys()
    fk_ok = test_referential_integrity()
    domain_ok = test_domain_constraints()
    
    print("\n================ TỔNG HỢP KẾT QUẢ KIỂM ĐỊNH ================")
    if pk_ok and fk_ok and domain_ok:
        print("★ TẤT CẢ CÁC BÀI KIỂM TRA ĐỀU VƯỢT QUA! DỮ LIỆU ĐẠT CHUẨN CHẤT LƯỢNG. ★")
        return True
    else:
        print("⚠ CÓ BÀI KIỂM TRA THẤT BẠI! VUI LÒNG KIỂM TRA LẠI LOG CHI TIẾT BÊN TRÊN. ⚠")
        return False

if __name__ == "__main__":
    run_quality_pipeline()
