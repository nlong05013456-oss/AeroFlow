# MÔ HÌNH HÓA THÔNG TIN CHIỀU (STAR SCHEMA DATA MODEL) - DỰ ÁN AEROFLOW

**Mô hình dữ liệu phân tích Kho dữ liệu (DWH Dimensional Model) trên Google BigQuery**

---

## 1. Phương án chuyển đổi từ ERD (Giao dịch 3NF) sang Star Schema (Phân tích OLAP)

Để tối ưu hóa hiệu năng truy vấn báo cáo và làm Dashboard trên Google BigQuery, đội ngũ DE tiến hành biến đổi (denormalize) các thực thể từ ERD Khái niệm thành mô hình **Star Schema (Sơ đồ hình sao)** gồm **3 bảng Fact** và **9 bảng Dimension**:

### Các bước tinh giản và tích hợp:
1.  **Gộp các thực thể hạ tầng:** Gộp dữ liệu đường băng (`RUNWAY`) vào thẳng bảng chiều **`dim_airport`** (bổ sung trường `runway_count` và `max_runway_length_ft`) để giảm thiểu số lượng phép JOIN khi truy vấn.
2.  **Tích hợp thông số tàu bay:** Gộp thông số loại tàu bay, sức chứa ghế vào thẳng bảng chiều **`dim_aircraft`** kèm theo trường tự động tính toán tuổi đời của máy bay (`aircraft_age_years`).
3.  **Tích hợp Thời tiết vào Chuyến bay:** Chuyển đổi bảng `WEATHER` thành bảng chiều **`dim_weather`** kết nối chéo với `fact_flights` ở cả hai đầu sân bay đi (Origin) và sân bay đến (Destination) — đây là mô hình **Role-Playing Dimension** trong thiết kế Kho dữ liệu.
4.  **Tách các nhánh phân tích phụ trợ:** 
    *   Tách phân hệ hành khách (`PASSENGER`, `TICKET`) thành bảng cầu phân tích chi tiết: **`fact_passenger_manifest`** liên kết trực tiếp với bảng Fact chuyến bay chính.
    *   Tách phân hệ phân công tổ bay (`CREW`) thành bảng cầu **`fact_crew_assignment`** liên kết trực tiếp giữa phi hành đoàn và tàu bay.

---

## 2. Danh sách các bảng trong Star Schema Vật lý

### Bảng Sự Kiện (Fact Tables)
1.  **`fact_flights`**: Sự kiện chính ghi nhận từng chuyến bay, số phút trễ, khoảng cách bay và mã lý do hủy.
2.  **`fact_passenger_manifest`**: Bản kê danh sách hành khách lên máy bay, số ghế, khối lượng hành lý ký gửi.
3.  **`fact_crew_assignment`**: Phân công tổ bay điều hành máy bay, số giờ bay nhiệm vụ và đánh giá hiệu suất.

### Bảng Chiều (Dimension Tables)
1.  **`dim_airport`**: Thông tin chi tiết các sân bay toàn cầu.
2.  **`dim_carrier`**: Danh mục hãng bay.
3.  **`dim_aircraft`**: Chi tiết kỹ thuật của tàu bay theo số đuôi.
4.  **`dim_date`**: Chi tiết ngày bay, cuối tuần, mùa và lịch ngày lễ quốc gia.
5.  **`dim_weather`**: Lịch sử thời tiết tại từng khu vực sân bay theo ngày.
6.  **`dim_passenger`**: Thông tin định danh và hạng thành viên của khách hàng.
7.  **`dim_ticket`**: Chi tiết vé bay và doanh thu.
8.  **`dim_cancellation_reason`**: Danh mục phân loại lý do hủy chuyến bay.
9.  **`dim_crew`**: Thông tin nhân sự tổ bay.

---

## 3. Xem tài liệu chi tiết:
*   [data_model.md](file:///d:/HocTap/CAP2/data_model.md): Mô tả cấu trúc bảng, kiểu dữ liệu và định nghĩa từng trường.
*   [erd.md](file:///d:/HocTap/CAP2/erd.md): Bản vẽ sơ đồ quan hệ Mermaid.js và các mối quan hệ khoá ngoại.
*   [schema_bigquery.sql](file:///d:/HocTap/CAP2/schema_bigquery.sql): Câu lệnh SQL khởi tạo bảng vật lý trên Google BigQuery.
