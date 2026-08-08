"""
inspect_all_13_tables.py
Script in CHI TIẾT NỘI DUNG & MẪU DỮ LIỆU THỰC TẾ (2 DÒNG) CỦA ĐÚNG 13 BẢNG WAREHOUSE & STAGING CHUẨN!
"""

import json
from google.cloud import bigquery
from src.config import GCP_PROJECT_ID, BQ_STAGING_DATASET, BQ_WAREHOUSE_DATASET

def inspect_all_tables():
    client = get_bq_client()
    
    tables_to_check = [
        (BQ_STAGING_DATASET, "stg_flights_raw", "1. Bảng Staging chứa dữ liệu chuyến bay thô (2.88M+ dòng)"),
        (BQ_WAREHOUSE_DATASET, "dim_airport", "2. Bảng Danh mục Sân bay (9,231 sân bay)"),
        (BQ_WAREHOUSE_DATASET, "dim_carrier", "3. Bảng Danh mục Hãng bay (Major & Regional Airlines)"),
        (BQ_WAREHOUSE_DATASET, "dim_aircraft", "4. Bảng Danh mục Tàu bay (6,499 máy bay)"),
        (BQ_WAREHOUSE_DATASET, "dim_date", "5. Bảng Danh mục Thời gian Ngày (365 ngày năm 2026)"),
        (BQ_WAREHOUSE_DATASET, "dim_weather", "6. Bảng Danh mục Thời tiết (15,110 ghi nhận thời tiết)"),
        (BQ_WAREHOUSE_DATASET, "dim_cancellation_reason", "7. Bảng Danh mục Lý do hủy chuyến"),
        (BQ_WAREHOUSE_DATASET, "dim_crew", "8. Bảng Danh mục Tổ bay (Phi công & Tiếp viên)"),
        (BQ_WAREHOUSE_DATASET, "dim_passenger", "9. Bảng Danh mục Hành khách"),
        (BQ_WAREHOUSE_DATASET, "dim_ticket", "10. Bảng Danh mục Vé máy bay & Booking PNR"),
        (BQ_WAREHOUSE_DATASET, "fact_flights", "11. Bảng Sự kiện Chuyến bay Fact Flights (2.88M+ sự kiện)"),
        (BQ_WAREHOUSE_DATASET, "fact_crew_assignment", "12. Bảng Sự kiện Phân công Tổ bay"),
        (BQ_WAREHOUSE_DATASET, "mart_delay_analysis", "13. Bảng Data Mart Phân tích Chậm trễ (199k+ dòng tổng hợp)")
    ]

    print("\n==================================================================================")
    print("🚀 BÁO CÁO CHI TIẾT NỘI DUNG & MẪU DỮ LIỆU THỰC TẾ TRONG ĐÚNG 13 BẢNG BIGQUERY")
    print("==================================================================================\n")

    for idx, (dataset, table_name, desc) in enumerate(tables_to_check, 1):
        table_id = f"{GCP_PROJECT_ID}.{dataset}.{table_name}"
        print(f"[{idx:02d}/13] BẢNG: {dataset}.{table_name}")
        print(f"📝 Ý NGHĨA: {desc}")
        
        try:
            # 1. Truy vấn tổng số dòng
            q_cnt = f"SELECT COUNT(*) as row_count FROM `{table_id}`"
            res = list(client.query(q_cnt).result())
            cnt = res[0].row_count
            print(f"👉 SỐ DÒNG THỰC TẾ: {cnt:,} dòng")
            
            # 2. In 2 dòng mẫu dữ liệu thực tế
            q_sample = f"SELECT * FROM `{table_id}` LIMIT 2"
            rows = list(client.query(q_sample).result())
            
            if rows:
                print("📌 MẪU DỮ LIỆU THỰC TẾ (2 DÒNG):")
                for r_idx, row in enumerate(rows, 1):
                    row_dict = dict(row.items())
                    cleaned_dict = {k: str(v) for k, v in list(row_dict.items())[:8]}
                    print(f"   Dòng {r_idx}: {json.dumps(cleaned_dict, ensure_ascii=False)}")
            else:
                print("   (Bảng trống chưa có dữ liệu)")
        except Exception as e:
            print(f"❌ Lỗi đọc bảng: {e}")
            
        print("=" * 82 + "\n")

def get_bq_client():
    return bigquery.Client(project=GCP_PROJECT_ID)

if __name__ == "__main__":
    inspect_all_tables()
