"""
verify_no_dups.py
Script kiểm tra xem có dòng nào bị trùng lặp trong ngày 26/07 hay không.
"""

from google.cloud import bigquery
from src.config import GCP_PROJECT_ID, BQ_STAGING_DATASET

def verify_deduplication():
    client = bigquery.Client(project=GCP_PROJECT_ID)
    query = f"""
    SELECT 
        COUNT(*) as total_rows,
        COUNT(DISTINCT CONCAT(Reporting_Airline, '_', CAST(Flight_Number_Reporting_Airline AS STRING), '_', Origin, '_', Dest)) as unique_flights
    FROM `{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.stg_flights_raw`
    WHERE FlightDate = '2026-07-26'
    """
    res = list(client.query(query).result())[0]
    print("\n==================================================================")
    print("🔍 KẾT QUẢ KIỂM TRA ĐỘC NHẤT & TRÙNG LẶP CHO NGÀY 26/07:")
    print("==================================================================")
    print(f"👉 Tổng số dòng lưu trong BigQuery: {res.total_rows:,} dòng")
    print(f"👉 Số chuyến bay độc nhất (Unique): {res.unique_flights:,} chuyến")
    
    if res.total_rows == res.unique_flights:
        print("✅ KẾT LUẬN: KHÔNG CÓ BẤT KỲ DÒNG NÀO BỊ TRÙNG LẶP! ĐẠT CHUẨN 100%!")
    else:
        diff = res.total_rows - res.unique_flights
        print(f"⚠️ Phát hiện {diff:,} dòng trùng lặp, cần chạy tf.run_transformation_pipeline() để làm sạch.")
    print("==================================================================\n")

if __name__ == "__main__":
    verify_deduplication()
