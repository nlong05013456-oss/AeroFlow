"""
check_warehouse.py
Script kiểm tra & in toàn bộ thông số trong kho dữ liệu BigQuery (Staging & Warehouse).
"""

from google.cloud import bigquery
from src.config import GCP_PROJECT_ID, BQ_STAGING_DATASET, BQ_WAREHOUSE_DATASET

def check_warehouse():
    client = bigquery.Client(project=GCP_PROJECT_ID)
    
    print("\n===========================================================")
    print("=== 1. TỔNG SỐ CHUYẾN BAY THỰC TẾ TRONG KHO BIGQUERY ===")
    print("===========================================================")
    query_count = f"SELECT COUNT(*) as cnt FROM `{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.stg_flights_raw`"
    res = list(client.query(query_count).result())
    print(f"👉 TỔNG CỘNG: {res[0].cnt:,} chuyến bay\n")

    print("=== 2. CÁC SÂN BAY ĐI (ORIGIN AIRPORTS) ===")
    q_orig = f"""
    SELECT Origin, COUNT(*) as cnt 
    FROM `{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.stg_flights_raw` 
    GROUP BY Origin 
    ORDER BY cnt DESC 
    LIMIT 15
    """
    for r in client.query(q_orig).result():
        print(f"  • Sân bay đi {r.Origin}: {r.cnt:,} chuyến")

    print("\n=== 3. CÁC SÂN BAY ĐẾN (DESTINATION AIRPORTS) ===")
    q_dest = f"""
    SELECT Dest, COUNT(*) as cnt 
    FROM `{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.stg_flights_raw` 
    GROUP BY Dest 
    ORDER BY cnt DESC 
    LIMIT 15
    """
    for r in client.query(q_dest).result():
        print(f"  • Sân bay đến {r.Dest}: {r.cnt:,} chuyến")

    print("\n=== 4. CÁC HÃNG HÀNG KHÔNG (REPORTING AIRLINES) ===")
    q_al = f"""
    SELECT Reporting_Airline, COUNT(*) as cnt 
    FROM `{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.stg_flights_raw` 
    GROUP BY Reporting_Airline 
    ORDER BY cnt DESC
    """
    for r in client.query(q_al).result():
        print(f"  • Hãng {r.Reporting_Airline}: {r.cnt:,} chuyến")

    print("\n=== 5. CÁC MÃ MÁY BAY / SỐ ĐUÔI (TOP TAIL NUMBERS) ===")
    q_tail = f"""
    SELECT Tail_Number, Reporting_Airline, COUNT(*) as cnt 
    FROM `{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.stg_flights_raw` 
    WHERE Tail_Number IS NOT NULL AND Tail_Number != '' 
    GROUP BY Tail_Number, Reporting_Airline 
    ORDER BY cnt DESC 
    LIMIT 10
    """
    for r in client.query(q_tail).result():
        print(f"  • Số đuôi {r.Tail_Number} ({r.Reporting_Airline}): {r.cnt:,} chuyến")

    print("\n=== 6. CÁC THÁNG DỮ LIỆU CÓ TRONG KHO ===")
    q_m = f"""
    SELECT EXTRACT(MONTH FROM FlightDate) as m, COUNT(*) as cnt 
    FROM `{GCP_PROJECT_ID}.{BQ_STAGING_DATASET}.stg_flights_raw` 
    GROUP BY m 
    ORDER BY m
    """
    for r in client.query(q_m).result():
        print(f"  • Tháng {int(r.m)}: {r.cnt:,} chuyến")
    print("===========================================================\n")

if __name__ == "__main__":
    check_warehouse()
