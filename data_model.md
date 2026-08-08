# TÀI LIỆU CHI TIẾT MÔ HÌNH DỮ LIỆU DWH (DATA MODEL) - DỰ ÁN AEROFLOW

Tài liệu này mô tả chi tiết thiết kế vật lý của Kho dữ liệu (Data Warehouse) trên Google BigQuery theo mô hình Hình sao (Star Schema) đã được thống nhất chốt cuối. Mô hình này bao gồm **9 bảng chiều (Dimension)** và **3 bảng sự kiện (Fact)**.

---

## 1. TỔNG QUAN SƠ ĐỒ HÌNH SAO (STAR SCHEMA)

Mô hình DWH được tối ưu hóa cho phân tích hiệu suất khai thác bay, ảnh hưởng thời tiết và quản lý nhân sự/hành khách hàng không:

*   **Bảng sự kiện trung tâm (Fact Tables):**
    *   `fact_flights`: Lưu trữ thông tin từng chuyến bay, thời gian cất hạ cánh và số phút trễ chuyến.
    *   `fact_passenger_manifest`: Danh sách hành khách và thông tin hành lý trên từng chuyến bay.
    *   `fact_crew_assignment`: Phân công nhiệm vụ và số giờ bay của phi hành đoàn cho từng tàu bay.
*   **Bảng chiều (Dimension Tables):**
    *   `dim_airport`: Danh mục sân bay kèm số lượng đường băng và chiều dài tối đa.
    *   `dim_carrier`: Danh mục các hãng hàng không phân nhóm theo quy mô.
    *   `dim_aircraft`: Danh mục tàu bay kèm năm sản xuất và số tuổi của tàu bay.
    *   `dim_date`: Chi tiết ngày, quý, tháng, cuối tuần và lịch ngày lễ liên bang Hoa Kỳ năm 2024.
    *   `dim_weather`: Thông số khí tượng tại các sân bay theo từng ngày.
    *   `dim_passenger`: Thông tin khách hàng và phân hạng thành viên.
    *   `dim_ticket`: Thông tin loại vé và giá vé máy bay.
    *   `dim_cancellation_reason`: Bảng tra cứu lý do hủy chuyến bay.
    *   `dim_crew`: Thông tin chi tiết về phi hành đoàn (Phi công, Tiếp viên).

---

## 2. TỪ ĐIỂN DỮ LIỆU CHI TIẾT (DATA DICTIONARY)

### 2.1. Bảng Sự Kiện (Fact Tables)

#### Bảng `fact_flights` (Thông tin chuyến bay)
*Lưu trữ chi tiết hiệu suất khai thác bay. Phân vùng theo ngày bay, gôm cụm theo hãng bay và sân bay.*

| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `flight_key` | STRING | PK | Mã duy nhất của chuyến bay (Ví dụ: `DL_102_20240714`) |
| `carrier_key` | STRING | FK | Mã hãng hàng không (Liên kết với `dim_carrier`) |
| `aircraft_key` | STRING | FK | Số hiệu đuôi tàu bay (Liên kết với `dim_aircraft`) |
| `origin_airport_key` | STRING | FK | Mã sân bay đi (Liên kết với `dim_airport`) |
| `dest_airport_key` | STRING | FK | Mã sân bay đến (Liên kết với `dim_airport`) |
| `origin_weather_key` | STRING | FK | Thời tiết tại sân bay đi (Liên kết với `dim_weather`) |
| `dest_weather_key` | STRING | FK | Thời tiết tại sân bay đến (Liên kết với `dim_weather`) |
| `cancellation_code` | STRING | FK | Mã lý do hủy chuyến (Liên kết với `dim_cancellation_reason`) |
| `flight_number` | STRING | - | Số hiệu chuyến bay (Ví dụ: `102`) |
| `tail_number_sha256` | STRING | - | Số đuôi tàu bay được mã hóa bảo mật bằng hàm SHA256 |
| `dep_delay_min` | INT64 | - | Số phút trễ cất cánh (Giá trị âm nghĩa là cất cánh sớm) |
| `arr_delay_min` | INT64 | - | Số phút trễ hạ cánh |
| `cancelled` | BOOLEAN | - | Trạng thái hủy chuyến (True: Bị hủy, False: Bay bình thường) |
| `diverted` | BOOLEAN | - | Trạng thái chuyển hướng bay (True: Bị chuyển hướng) |
| `distance_miles` | FLOAT64 | - | Khoảng cách đường bay (dặm) |
| `taxi_out_min` | INT64 | - | Thời gian di chuyển từ cổng đỗ ra đường băng (phút) |
| `taxi_in_min` | INT64 | - | Thời gian di chuyển từ đường băng vào cổng đỗ (phút) |
| `air_time_min` | INT64 | - | Thời gian bay thực tế trên không (phút) |
| `actual_elapsed_min` | INT64 | - | Tổng thời gian thực tế của chuyến bay (phút) |
| `carrier_delay_min` | INT64 | - | Số phút trễ do lỗi hãng hàng không |
| `weather_delay_min` | INT64 | - | Số phút trễ do thời tiết xấu |
| `nas_delay_min` | INT64 | - | Số phút trễ do hệ thống hàng không quốc gia (ATC) |
| `security_delay_min` | INT64 | - | Số phút trễ do sự cố an ninh |
| `late_aircraft_delay_min`| INT64 | - | Số phút trễ do tàu bay đến muộn từ chặng trước |

#### Bảng `fact_passenger_manifest` (Danh sách hành khách bay)
*Ghi nhận hành khách thực tế trên từng chuyến bay và khối lượng hành lý.*

| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `flight_key` | STRING | PK, FK | Mã chuyến bay (Liên kết với `fact_flights`) |
| `passenger_key` | STRING | PK, FK | Mã hành khách (Liên kết với `dim_passenger`) |
| `ticket_key` | STRING | FK | Mã vé máy bay (Liên kết với `dim_ticket`) |
| `checkin_time` | TIMESTAMP | - | Thời gian làm thủ tục lên máy bay |
| `baggage_weight_kg` | FLOAT64 | - | Khối lượng hành lý ký gửi (kg) |
| `seat_number` | STRING | - | Số ghế ngồi trên chuyến bay (Ví dụ: `14A`) |

#### Bảng `fact_crew_assignment` (Phân công tổ bay)
*Lịch trình phân công nhiệm vụ và đánh giá hiệu suất phi hành đoàn.*

| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `crew_key` | STRING | PK, FK | Mã thành viên phi hành đoàn (Liên kết với `dim_crew`) |
| `aircraft_key` | STRING | PK, FK | Mã tàu bay được phân công (Liên kết với `dim_aircraft`) |
| `duty_hours` | FLOAT64 | - | Số giờ làm việc được phân công (giờ) |
| `performance_rating` | FLOAT64 | - | Điểm đánh giá hiệu suất làm việc (Thang điểm 5.0) |

---

### 2.2. Bảng Chiều (Dimension Tables)

#### Bảng `dim_airport` (Danh mục sân bay)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `airport_key` | STRING | PK | Mã IATA của sân bay (Ví dụ: `ATL`, `LAX`) |
| `airport_name` | STRING | - | Tên đầy đủ của sân bay |
| `city` | STRING | - | Thành phố trực thuộc |
| `state` | STRING | - | Mã bang/vùng miền (Ví dụ: `US-GA`) |
| `country` | STRING | - | Tên quốc gia |
| `latitude` | FLOAT64 | - | Vĩ độ địa lý |
| `longitude` | FLOAT64 | - | Kinh độ địa lý |
| `elevation_ft` | INT64 | - | Độ cao sân bay so với mực nước biển (feet) |
| `timezone_offset` | INT64 | - | Múi giờ chênh lệch so với UTC |
| `runway_count` | INT64 | - | Tổng số đường băng hiện hữu tại sân bay |
| `max_runway_length_ft` | INT64 | - | Chiều dài của đường băng lớn nhất (feet) |

#### Bảng `dim_date` (Danh mục thời gian)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `date_key` | DATE | PK | Ngày cụ thể (định dạng YYYY-MM-DD) |
| `year` | INT64 | - | Năm (Ví dụ: `2024`) |
| `quarter` | INT64 | - | Quý trong năm (1, 2, 3, 4) |
| `month` | INT64 | - | Số tháng (1 đến 12) |
| `month_name` | STRING | - | Tên tháng bằng tiếng Anh (Ví dụ: `July`) |
| `day` | INT64 | - | Ngày trong tháng (1 đến 31) |
| `day_of_week` | STRING | - | Thứ tự ngày trong tuần (1: Thứ hai -> 7: Chủ nhật) |
| `day_name` | STRING | - | Tên thứ bằng tiếng Anh (Ví dụ: `Sunday`) |
| `is_weekend` | BOOLEAN | - | Cờ xác định cuối tuần (True/False) |
| `is_holiday` | BOOLEAN | - | Cờ xác định ngày lễ liên bang Hoa Kỳ (True/False) |
| `holiday_name` | STRING | - | Tên ngày lễ (Ví dụ: `Independence Day`) |
| `season` | STRING | - | Mùa trong năm (Spring, Summer, Autumn, Winter) |

#### Bảng `dim_weather` (Thông tin khí tượng)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `weather_key` | STRING | PK | Khóa tổng hợp (Ví dụ: `LAX_20240714`) |
| `airport_key` | STRING | FK | Mã sân bay (Liên kết với `dim_airport`) |
| `date_key` | DATE | FK | Ngày ghi nhận (Liên kết với `dim_date`) |
| `temp_max_c` | FLOAT64 | - | Nhiệt độ cao nhất trong ngày (độ C) |
| `temp_min_c` | FLOAT64 | - | Nhiệt độ thấp nhất trong ngày (độ C) |
| `precipitation_mm` | FLOAT64 | - | Lượng mưa đo được (mm) |
| `snowfall_cm` | FLOAT64 | - | Lượng tuyết rơi tích lũy (cm) |
| `wind_speed_kmh` | FLOAT64 | - | Tốc độ gió trung bình lớn nhất (km/h) |
| `weather_condition` | STRING | - | Nhãn điều kiện thời tiết tổng hợp (`Clear`, `Rain`, `Heavy Rain`, `Snow`) |

#### Bảng `dim_carrier` (Hãng hàng không)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `carrier_key` | STRING | PK | Mã IATA của hãng bay (Ví dụ: `AA`, `DL`, `WN`) |
| `carrier_name` | STRING | - | Tên đầy đủ của hãng hàng không |
| `carrier_group` | STRING | - | Phân loại hãng bay (`Major Legacy`, `Low-Cost Carrier`, `Regional Carrier`) |
| `country` | STRING | - | Quốc gia đăng ký trụ sở chính |

#### Bảng `dim_aircraft` (Thông tin tàu bay)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `aircraft_key` | STRING | PK | Số hiệu đăng ký đuôi máy bay (Ví dụ: `N102DU`) |
| `carrier_key` | STRING | FK | Hãng hàng không sở hữu (Liên kết với `dim_carrier`) |
| `manufacturer` | STRING | - | Nhà sản xuất tàu bay (Boeing, Airbus, Embraer...) |
| `model` | STRING | - | Dòng máy bay (A321NEO, B737-800...) |
| `aircraft_type` | STRING | - | Kiểu tàu bay (Jet, Turboprop...) |
| `capacity_seats` | INT64 | - | Tổng số ghế hành khách |
| `manufacture_year` | INT64 | - | Năm sản xuất tàu bay |
| `aircraft_age_years` | INT64 | - | Tuổi thọ tàu bay tính đến thời điểm phân tích (2024) |

#### Bảng `dim_crew` (Thông tin nhân sự phi hành đoàn)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `crew_key` | STRING | PK | Mã định danh phi hành đoàn (Ví dụ: `CREW_AA_1`) |
| `carrier_key` | STRING | FK | Hãng hàng không chủ quản (Liên kết với `dim_carrier`) |
| `full_name` | STRING | - | Họ và tên của thành viên tổ bay |
| `role` | STRING | - | Vai trò đảm nhận (Captain, First Officer, Flight Attendant) |
| `license_number` | STRING | - | Số bằng lái chuyên môn hàng không cấp phép |
| `license_type` | STRING | - | Loại giấy phép bay (Ví dụ: ATP, Cabin Crew License) |

#### Bảng `dim_passenger` (Danh mục khách hàng)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `passenger_key` | STRING | PK | Mã hành khách duy nhất (Ví dụ: `PSG_101`) |
| `full_name` | STRING | - | Họ và tên hành khách |
| `gender` | STRING | - | Giới tính (Male/Female) |
| `nationality` | STRING | - | Quốc tịch hành khách |
| `date_of_birth` | DATE | - | Ngày sinh |
| `loyalty_tier` | STRING | - | Hạng thành viên thân thiết (Regular, Silver, Gold, Platinum) |

#### Bảng `dim_ticket` (Danh mục vé)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `ticket_key` | STRING | PK | Mã số vé điện tử (Ví dụ: `TKT_505`) |
| `booking_reference` | STRING | - | Mã đặt chỗ PNR (6 ký tự viết hoa) |
| `fare_class` | STRING | - | Hạng vé (Economy, Premium, Business) |
| `ticket_price_usd` | FLOAT64 | - | Giá vé máy bay (USD) |
| `purchase_date` | DATE | - | Ngày hành khách thanh toán mua vé |

#### Bảng `dim_cancellation_reason` (Lý do hủy chuyến)
| Tên Cột | Kiểu Dữ Liệu | Khóa | Mô Tả |
| :--- | :--- | :--- | :--- |
| `cancellation_code` | STRING | PK | Mã hủy chuyến (`A`, `B`, `C`, `D`, `N`) |
| `cancellation_desc` | STRING | - | Mô tả chi tiết lý do (Thời tiết, Kỹ thuật, ATC, Không hủy...) |
