"""
orchestrator.py
Bộ điều phối (Orchestrator) cho hệ thống AeroFlow.
Hỗ trợ cả chạy pipeline khởi tạo ban đầu và chạy liên hoàn cào nạp tự động hàng ngày (Daily Pipeline).
"""

import datetime
import src.extract as extract
import src.load as load
import src.transform as transform
import src.quality as quality

def run_automated_orchestrator():
    """
    Hàm điều phối liên hoàn khởi tạo ban đầu (Orchestrator):
    1. Cào thời tiết dựa trên file chuyến bay lịch sử trên GCS (Extract).
    2. Tải metadata tĩnh + Nạp toàn bộ dữ liệu thô vào BigQuery Staging (Load).
    3. Chạy SQL biến đổi xây dựng Star Schema DWH (Transform).
    4. Kiểm thử chất lượng dữ liệu (Quality Check).
    """
    print("=========================================================================")
    print("★ KHỞI ĐỘNG BỘ ĐIỀU PHỐI TỰ ĐỘNG (AEROFLOW ORCHESTRATOR) ★")
    print("=========================================================================\n")
    
    print("[1/4] Chạy trích xuất dữ liệu thời tiết (Extract)...")
    extract.run_extraction_pipeline()
    print("-------------------------------------------------------------------------\n")
    
    print("[2/4] Nạp dữ liệu thô vào BigQuery (Load)...")
    load.run_loading_pipeline()
    print("-------------------------------------------------------------------------\n")
    
    print("[3/4] Chạy SQL biến đổi DWH (Transform)...")
    transform.run_transformation_pipeline()
    print("-------------------------------------------------------------------------\n")
    
    print("[4/4] Kiểm định chất lượng toàn diện (Quality Check)...")
    quality_ok = quality.run_quality_pipeline()
    
    print("\n=========================================================================")
    if quality_ok:
        print("★ HỆ THỐNG ĐÃ TỰ ĐỘNG ĐỒNG BỘ VÀ KIỂM ĐỊNH THÀNH CÔNG! ★")
    else:
        print("⚠ HỆ THỐNG HOÀN THÀNH NHƯNG PHÁT HIỆN CẢNH BÁO CHẤT LƯỢNG! XEM LOG TRÊN. ⚠")
    print("=========================================================================")

def run_daily_orchestrator(date_str=None):
    """
    Hàm điều phối tự động hàng ngày (Daily Pipeline Ingestion):
    1. Cào chuyến bay & thời tiết ngày hôm nay (mặc định date_str=today).
    2. Nạp nối tiếp (APPEND) dữ liệu ngày vào BigQuery Staging.
    3. Cập nhật DWH Partition.
    4. Kiểm định chất lượng.
    """
    if date_str is None:
        date_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d")
        
    print("=========================================================================")
    print(f"★ KHỞI ĐỘNG CÀO NẠP TỰ ĐỘNG HÀNG NGÀY (DAILY PIPELINE: {date_str}) ★")
    print("=========================================================================\n")
    
    # BƯỚC 1: Extract Daily
    print(f"[1/4] Trích xuất dữ liệu ngày {date_str} (Extract Daily)...")
    extract.run_daily_extraction_pipeline(date_str)
    print("-------------------------------------------------------------------------\n")
    
    # BƯỚC 2: Load Daily (APPEND)
    print(f"[2/4] Nạp nối tiếp dữ liệu thô ngày {date_str} vào BigQuery (Load Daily)...")
    load.run_daily_loading_pipeline(date_str)
    print("-------------------------------------------------------------------------\n")
    
    # BƯỚC 3: Transform DWH
    print("[3/4] Chạy SQL biến đổi DWH (Transform Update)...")
    transform.run_transformation_pipeline()
    print("-------------------------------------------------------------------------\n")
    
    # BƯỚC 4: Quality Audit
    print("[4/4] Kiểm định chất lượng toàn diện (Quality Check)...")
    quality_ok = quality.run_quality_pipeline()
    
    print("\n=========================================================================")
    if quality_ok:
        print(f"★ NẠP THÀNH CÔNG DỮ LIỆU NGÀY {date_str} VÀO KHO DỮ LIỆU! ★")
    else:
        print(f"⚠ NẠP NGÀY {date_str} HOÀN THÀNH NHƯNG CÓ CẢNH BÁO CHẤT LƯỢNG! ⚠")
    print("=========================================================================")

if __name__ == "__main__":
    run_daily_orchestrator()
