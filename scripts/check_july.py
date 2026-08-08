"""
check_july.py
Script kiểm tra dữ liệu Tháng 7 trong kho BigQuery.
"""

from google.cloud import bigquery
from src.config import GCP_PROJECT_ID, BQ_STAGING_DATASET

def check_july_data():
    client = bigquery.Client(project=GCP_PROJECT_ID)
    query = f"""
    SELECT FlightDate, COUNT(*) as cnt 
    FROM `{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.stg_flights_raw` 
    WHERE FlightDate >= '2026-07-01'
    GROUP BY FlightDate 
    ORDER BY FlightDate ASC
    """
    rows = list(client.query(query).result())
    print("\n==================================================================")
    print("📊 KẾT QUẢ DỮ LIỆU THÁNG 7 THỰC TẾ TRONG KHO BIGQUERY:")
    print("==================================================================")
    if rows:
        for r in rows:
            print(f"👉 Ngày {r.FlightDate}: Có {r.cnt:,} chuyến bay thực tế trong kho!")
    else:
        print("⚠️ Chưa có dữ liệu Tháng 7 trong kho.")
    print("==================================================================\n")

if __name__ == "__main__":
    check_july_data()
