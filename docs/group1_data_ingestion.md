# KẾ HOẠCH THU THẬP DỮ LIỆU - NHÓM 1: VẬN HÀNH BAY (FLIGHT OPERATIONS)
**Tài liệu chi tiết nguồn dữ liệu, phương thức thu thập và giải pháp xử lý kỹ thuật**

---

Tài liệu này tổng hợp chi tiết toàn bộ các chỉ số cần thu thập cho **12 bảng thuộc Nhóm 1 (Vận hành bay)**, xác định rõ nguồn dữ liệu thô (API/File) và cách thức xử lý dữ liệu bằng code Python ETL để đảm bảo kho dữ liệu hoạt động nhất quán, khớp khít 100% trên Google BigQuery.

---

## TỔNG QUAN PHƯƠNG THỨC THU THẬP DỮ LIỆU NHÓM 1

Dữ liệu được chia làm 3 kênh thu thập chính để tối ưu hóa chi phí Cloud và băng thông:

1.  **Online / API Ingestion (Dữ liệu động thay đổi liên tục):** Sử dụng các REST API thời gian thực hoặc micro-batch gọi tự động qua Python script để cập nhật chuyến bay và thời tiết.
2.  **Offline / Bulk Download (Dữ liệu tham chiếu tĩnh):** Tải các file danh mục mở (.csv, .txt) từ các tổ chức hàng không toàn cầu 1 lần duy nhất lên Google Cloud Storage (GCS).
3.  **ETL Calculation / Logical Mocking (Dữ liệu đặc thù/bảo mật):** Tự động sinh ra có logic bằng code Python dựa trên các ràng buộc vật lý thực tế của sân bay/máy bay, đảm bảo không bị lỗi dữ liệu "kỳ lạ".

---

## CHI TIẾT TỪNG BẢNG DỮ LIỆU TRONG NHÓM 1

### 1. AIRPORT (Cảng hàng không)
*   **Các cột cần lấy:** `airport_code`, `airport_name`, `city`, `state`, `country`, `latitude`, `longitude`, `elevation_ft`.
*   **Nguồn dữ liệu:** Bộ dữ liệu mở cảng hàng không toàn cầu của **OurAirports**.
*   **Cách lấy (ETL Pipeline):** 
    *   Tải tệp [airports.csv](https://davidmegginson.github.io/ourairports-data/airports.csv) về máy chủ.
    *   Sử dụng Pandas lọc lấy các sân bay thương mại nội địa Hoa Kỳ (hoặc Việt Nam tùy phạm vi) và upload lên GCS đường dẫn `raw/OurAirports/airports.csv`.

---

### 2. RUNWAY (Đường băng sân bay)
*   **Các cột cần lấy:** `runway_name` (Ví dụ: 11L, 29R), `length_ft`, `width_ft`, `surface_type` (Asphalt/Concrete), `ils_category` (CAT I/II/III), `is_active`.
*   **Nguồn dữ liệu:** Bộ dữ liệu đường băng của **OurAirports**.
*   **Cách lấy (ETL Pipeline):**
    *   Tải tệp [runways.csv](https://davidmegginson.github.io/ourairports-data/runways.csv) chứa thông số kỹ thuật tất cả đường băng trên thế giới.
    *   Code Python lọc các đường băng theo mã sân bay (`airport_code`) khớp với danh sách bảng `AIRPORT`.
    *   *Đối với chỉ số `ils_category` (thường bị thiếu trong OurAirports):* Code Python thực hiện gán tự động ngẫu nhiên (CAT I: 60%, CAT II: 25%, CAT III: 15%) dựa trên chiều dài đường băng (đường băng càng dài cấp độ ILS càng cao) để bảng đầy đủ dữ liệu thực tế.

---

### 3. TERMINAL_GATE (Cổng đỗ & Nhà ga)
*   **Các cột cần lấy:** `gate_number`, `airport_code`, `terminal_name` (T1, T2, T3, Concourse A/B), `gate_type` (Jet Bridge / Bus Gate), `is_international` (0/1).
*   **Nguồn dữ liệu:** Không có API hay file CSV công khai vì lý do bảo mật an ninh nội bộ sân bay.
*   **Cách lấy (ETL Smart Mocking):**
    *   Code Python tự động tạo danh sách cổng đỗ giả lập cho từng sân bay trong bảng `AIRPORT`.
    *   *Quy luật sinh dữ liệu:* Sân bay lớn (JFK, SGN) sẽ tự động tạo từ 2-3 nhà ga (T1, T2), mỗi nhà ga có 20-30 cổng đỗ. Sân bay nhỏ tự động tạo 1 nhà ga với 5-10 cổng đỗ để đảm bảo sát thực tế.

---

### 4. ROUTE (Tuyến bay)
*   **Các cột cần lấy:** `route_code` (Ví dụ: HAN-SGN), `origin_airport_code`, `dest_airport_code`, `distance_miles`, `estimated_flight_time_mins`, `is_active`.
*   **Nguồn dữ liệu:** Bộ dữ liệu tuyến bay mở của **OpenFlights**.
*   **Cách lấy (ETL Pipeline):**
    *   Tải tệp `routes.dat` từ [OpenFlights Routes](https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat).
    *   Lọc lấy các tuyến bay nội địa hoạt động và tính toán khoảng cách (`distance_miles`) dựa trên tọa độ vĩ độ/kinh độ của hai sân bay.

---

### 5. CARRIER (Hãng hàng không)
*   **Các cột cần lấy:** `carrier_code`, `carrier_name`, `country`, `alliance` (SkyTeam/Oneworld/Star Alliance), `carrier_type` (Low-Cost/Full-Service/Cargo).
*   **Nguồn dữ liệu:** **OpenFlights Airlines** kết hợp gán nhãn liên minh.
*   **Cách lấy (ETL Pipeline):**
    *   Tải tệp `airlines.dat` từ [OpenFlights Airlines](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat).
    *   Code Python lọc lấy các hãng hàng không hoạt động và thực hiện gán nhãn `alliance` cùng `carrier_type` thông qua một bảng từ điển tra cứu tĩnh (Static dictionary) trong code để dữ liệu phong phú.

---

### 6. AIRCRAFT_MODEL (Dòng máy bay)
*   **Các cột cần lấy:** `model_code` (A321NEO, B787-9), `manufacturer`, `model_name`, `seating_capacity`, `min_runway_length_ft`.
*   **Nguồn dữ liệu:** Danh mục đăng ký tàu bay của **Cục Hàng không Liên bang Mỹ (FAA)** hoặc tài liệu hướng dẫn kỹ thuật của Airbus/Boeing.
*   **Cách lấy (ETL Pipeline):**
    *   Trích xuất từ file đăng ký mẫu tàu bay của FAA (`ACFTREF.txt`).
    *   Gán cột `min_runway_length_ft` theo quy chuẩn: Máy bay thân rộng (B777, A350) cần tối thiểu 8000ft; máy bay thân hẹp (A321, B737) cần tối thiểu 6000ft để cất/hạ cánh an toàn.

---

### 7. AIRCRAFT (Tàu bay vật lý)
*   **Các cột cần lấy:** `tail_number` (Số hiệu đuôi đăng ký bay), `model_code`, `carrier_code`, `manufacture_year`, `registration_date`, `aircraft_status`, `ownership_type`, `total_flight_hours`, `total_cycles`, `last_inspection_date`.
*   **Nguồn dữ liệu:** Tệp đăng ký phương tiện của **FAA Aircraft Registry** kết hợp ghi nhận vận hành hãng.
*   **Cách lấy (ETL Pipeline):**
    *   Tải tệp đăng ký máy bay thô từ FAA (`MASTER.txt`).
    *   Sử dụng Pandas JOIN chéo số đuôi máy bay (`tail_number`) xuất hiện trong các chuyến bay để lấy về năm sản xuất, ngày đăng ký. Các trường như `total_flight_hours`, `total_cycles` được lũy kế tự động từ thời gian bay của bảng `FLIGHT`.

---

### 8. SEAT_CONFIGURATION (Sơ đồ ghế ngồi vật lý)
*   **Các cột cần lấy:** `seat_number`, `tail_number`, `seat_class`, `seat_type`, `is_available`, `extra_legroom`, `price_tier`.
*   **Nguồn dữ liệu:** Không có nguồn dữ liệu thô công khai chi tiết cấu hình ghế của từng số đuôi cụ thể.
*   **Cách lấy (ETL Smart Mocking):**
    *   Code Python đọc thông số `seating_capacity` (sức chứa) của dòng máy bay đó.
    *   Tự động sinh cấu trúc ghế: Ví dụ máy bay 180 ghế sẽ tự động tạo từ hàng 1 đến 30, mỗi hàng có 6 ghế (A-F). Ghế A và F gán nhãn `Window` (cạnh cửa sổ). Trạng thái khả dụng `is_available` gán ngẫu nhiên 0/1 để phục vụ phân tích lấp đầy ghế. Khoảng để chân rộng hơn (`extra_legroom`) gán bằng 1 cho các hàng ghế thoát hiểm (Exit row). Phân khúc giá (`price_tier`) gán tương ứng Standard hoặc Premium.

---

### 9. FLIGHT (Chuyến bay thực tế)
*   **Các cột cần lấy:** `flight_id` (PK), `flight_number`, `flight_status`, `scheduled_dep_time`, `actual_dep_time`, `wheels_off_time`, `wheels_on_time`, `scheduled_arr_time`, `actual_arr_time`, `air_time_minutes`, `taxi_out_minutes`, `taxi_in_minutes`, `fuel_burn_gallons`, `cargo_weight_lbs`, `cancelled`, `cancellation_code`, `diverted`, `actual_dest_airport_code`.
*   **Nguồn dữ liệu:** **Aviationstack API** (hoặc **FlightAware AeroAPI**) kết hợp tính toán bằng code Python.
*   **Cách lấy & Công thức xử lý:**
    *   *Giờ bay, hủy chuyến, chuyển hướng:* Gọi API chuyến bay để nhận về chuỗi thời gian định dạng JSON, đổi về UTC/Local timestamp nạp vào BigQuery.
    *   *Nhiên liệu tiêu thụ (`fuel_burn_gallons`):* Code Python lấy thời gian bay thực tế nhân định mức tiêu thụ:
        $$\text{fuel\_burn\_gallons} = \left(\frac{\text{air\_time\_minutes}}{60}\right) \times \text{Định mức tiêu thụ (Gallons/giờ của Model)}$$
        *(Ví dụ: A321NEO tiêu thụ khoảng 800 Gallons/giờ).*
    *   *Trọng lượng hàng hóa (`cargo_weight_lbs`):* Tính toán dựa trên tải trọng hàng hóa thiết kế của máy bay và nhân với một hệ số tải ngẫu nhiên hợp lý từ 40% đến 80%:
        $$\text{cargo\_weight\_lbs} = \text{Tải trọng thiết kế} \times \text{Random\_Factor}(0.4, 0.8)$$
    *   *Đường băng & Cổng đỗ cất/hạ cánh:* Code Python lấy ngẫu nhiên 1 cổng đỗ trong bảng `TERMINAL_GATE` và 1 đường băng hoạt động trong bảng `RUNWAY` thuộc đúng Sân bay đi/đến của chuyến bay đó để gán vào bản ghi chuyến bay. Điều này đảm bảo tính toàn vẹn khóa ngoại 100%.

---

### 10. DELAY_REASON (Danh mục lý do trễ chuyến)
*   **Các cột cần lấy:** `delay_reason_code`, `description`, `delay_category`, `responsible_party`.
*   **Nguồn dữ liệu:** Bộ quy chuẩn phân loại của **Cục Hàng không liên bang (FAA / BTS)**.
*   **Cách lấy (Static Metadata):**
    *   Tạo file tĩnh chứa 5 nguyên nhân trễ chuẩn quốc tế:
        1.  `CAR` (Carrier Delay): Do hãng bay (bảo trì máy bay, thiếu tổ bay). Bên chịu trách nhiệm: Hãng hàng không.
        2.  `WEA` (Weather Delay): Do thời tiết xấu. Bên chịu trách nhiệm: Cơ quan khí tượng/Thiên nhiên.
        3.  `NAS` (National Aviation System Delay): Do hạ tầng sân bay/kẹt không lưu. Bên chịu trách nhiệm: Đài kiểm soát bay (ATC).
        4.  `SEC` (Security Delay): Do kiểm tra an ninh cổng. Bên chịu trách nhiệm: Cục an ninh sân bay.
        5.  `LATE` (Late Aircraft Delay): Do máy bay quay đầu muộn từ chặng trước. Bên chịu trách nhiệm: Hãng hàng không.

---

### 11. FLIGHT_DELAY (Chi tiết số phút trễ chuyến bay)
*   **Các cột cần lấy:** `flight_id`, `delay_reason_code`, `delay_minutes`, `recorded_time`, `delay_notes`.
*   **Nguồn dữ liệu:** Dữ liệu số phút trễ chi tiết trả về từ **Aviationstack API / FlightAware API**.
*   **Cách lấy (ETL Pipeline):**
    *   Đọc số phút trễ của từng nguyên nhân từ JSON của API chuyến bay.
    *   Nếu số phút trễ của một nguyên nhân > 0, tự động tạo một dòng liên kết tương ứng vào bảng `FLIGHT_DELAY` để phân tích sâu nguyên nhân trễ (chuẩn 3NF). Trường `recorded_time` được lấy theo giờ thực tế ghi nhận delay, `delay_notes` được cập nhật ghi chú từ API (nếu có).

---

### 12. WEATHER (Thời tiết quan trắc)
*   **Các cột cần lấy:** `weather_observation_timestamp`, `airport_code`, `temp_max`, `temp_min`, `precipitation`, `wind_speed`, `visibility`.
*   **Nguồn dữ liệu:** **Open-Meteo API** (Historical Weather API).
*   **Cách lấy (ETL Ingestion):**
    *   Code Python đọc danh sách sân bay đi/đến hoạt động trong ngày từ bảng `FLIGHT`.
    *   Trích xuất tọa độ địa lý (Vĩ độ / Kinh độ) của sân bay đó.
    *   Gọi API của Open-Meteo để lấy thông tin thời tiết lịch sử theo khung giờ tương ứng của sân bay đó, lưu thành file CSV thô và đẩy lên GCS: `raw/Weather/weather_raw_2024.csv`.
