# BẢN VẼ SƠ ĐỒ QUAN HỆ THỰC THỂ (ERD) - DỰ ÁN AEROFLOW

Tài liệu này trình bày bản vẽ và giải thích chi tiết Sơ đồ quan hệ thực thể (ERD) của hệ thống AeroFlow qua hai cấp độ thiết kế:
1.  **Mô hình quan hệ 3NF (Conceptual/Logical Model):** Mô hình hóa thực tế thế giới quan từ file thiết kế `Cap2_ERD.erdplus`.
2.  **Mô hình hình sao DWH (Physical Star Schema):** Mô hình hóa cấu trúc lưu trữ tối ưu trên Google BigQuery để phục vụ Looker Studio.

---

## 1. SƠ ĐỒ MÔ HÌNH HÌNH SAO DWH (GOLD ZONE - BIGQUERY)

Dưới đây là biểu đồ quan hệ các bảng trong Kho dữ liệu (DWH) phục vụ phân tích nghiệp vụ hàng không:

```mermaid
erDiagram
    dim_airport ||--o{ fact_flights : "origin / destination"
    dim_carrier ||--o{ fact_flights : "operates"
    dim_aircraft ||--o{ fact_flights : "assigned"
    dim_weather ||--o{ fact_flights : "origin_weather / dest_weather"
    dim_cancellation_reason ||--o{ fact_flights : "cancels_because_of"
    
    dim_carrier ||--o{ dim_aircraft : "owns"
    dim_carrier ||--o{ dim_crew : "employs"
    
    dim_crew ||--o{ fact_crew_assignment : "is_assigned"
    dim_aircraft ||--o{ fact_crew_assignment : "utilizes"
    
    fact_flights ||--o{ fact_passenger_manifest : "manifests"
    dim_passenger ||--o{ fact_passenger_manifest : "travels"
    dim_ticket ||--o{ fact_passenger_manifest : "billed_by"
    
    dim_airport ||--o{ dim_weather : "weather_at"
    dim_date ||--o{ dim_weather : "weather_on"

    dim_airport {
        string airport_key PK
        string airport_name
        string city
        string state
        string country
        float latitude
        float longitude
        int elevation_ft
        int timezone_offset
        int runway_count
        int max_runway_length_ft
    }

    dim_weather {
        string weather_key PK
        string airport_key FK
        date date_key FK
        float temp_max_c
        float temp_min_c
        float precipitation_mm
        float snowfall_cm
        float wind_speed_kmh
        string weather_condition
    }

    dim_date {
        date date_key PK
        int year
        int quarter
        int month
        string month_name
        int day
        string day_of_week
        string day_name
        boolean is_weekend
        boolean is_holiday
        string holiday_name
        string season
    }

    dim_carrier {
        string carrier_key PK
        string carrier_name
        string carrier_group
        string country
    }

    dim_aircraft {
        string aircraft_key PK
        string carrier_key FK
        string manufacturer
        string model
        string aircraft_type
        int capacity_seats
        int manufacture_year
        int aircraft_age_years
    }

    dim_crew {
        string crew_key PK
        string carrier_key FK
        string full_name
        string role
        string license_number
        string license_type
    }

    fact_crew_assignment {
        string crew_key PK, FK
        string aircraft_key PK, FK
        float duty_hours
        float performance_rating
    }

    dim_cancellation_reason {
        string cancellation_code PK
        string cancellation_desc
    }

    fact_flights {
        string flight_key PK
        string carrier_key FK
        string aircraft_key FK
        string origin_airport_key FK
        string dest_airport_key FK
        string origin_weather_key FK
        string dest_weather_key FK
        string cancellation_code FK
        string flight_number
        string tail_number_sha256
        int dep_delay_min
        int arr_delay_min
        boolean cancelled
        boolean diverted
        float distance_miles
        int taxi_out_min
        int taxi_in_min
        int air_time_min
        int actual_elapsed_min
        int carrier_delay_min
        int weather_delay_min
        int nas_delay_min
        int security_delay_min
        int late_aircraft_delay_min
    }

    dim_passenger {
        string passenger_key PK
        string full_name
        string gender
        string nationality
        date date_birth
        string loyalty_tier
    }

    dim_ticket {
        string ticket_key PK
        string booking_reference
        string fare_class
        float ticket_price_usd
        date purchase_date
    }

    fact_passenger_manifest {
        string flight_key PK, FK
        string passenger_key PK, FK
        string ticket_key FK
        datetime checkin_time
        float baggage_weight_kg
        string seat_number
    }
```

---

## 2. QUAN HỆ VÀ RÀNG BUỘC TOÀN VẸN (FOREIGN KEYS & CARDINALITIES)

### 2.1. Nhánh Khai Thác Bay (Fact Flights Branch)
*   **`dim_airport` $\rightarrow$ `fact_flights` ($1:N$):** Một sân bay có thể xuất hiện trong nhiều chuyến bay với tư cách là sân bay xuất phát (`origin_airport_key`) hoặc sân bay đích (`dest_airport_key`).
*   **`dim_carrier` $\rightarrow$ `fact_flights` ($1:N$):** Mỗi hãng hàng không vận hành nhiều chuyến bay khác nhau.
*   **`dim_aircraft` $\rightarrow$ `fact_flights` ($1:N$):** Mỗi tàu bay cụ thể (nhận diện qua số hiệu đuôi) thực hiện nhiều hành trình bay.
*   **`dim_weather` $\rightarrow$ `fact_flights` ($1:N$):** Thông số thời tiết của ngày bay tại sân bay xuất phát (`origin_weather_key`) và sân bay đến (`dest_weather_key`) được ánh xạ trực tiếp vào bản ghi chuyến bay để đối chiếu liên hệ trễ chuyến do thời tiết.
*   **`dim_cancellation_reason` $\rightarrow$ `fact_flights` ($1:N$):** Mỗi chuyến bay bị hủy được gắn duy nhất một mã lý do hủy thuộc bảng tra cứu.

### 2.2. Nhánh Nhân Sự và Tổ Bay (Crew assignment Branch)
*   **`dim_carrier` $\rightarrow$ `dim_crew` ($1:N$):** Một hãng bay sở hữu và quản lý một danh sách phi hành đoàn riêng.
*   **`dim_crew` $\rightarrow$ `fact_crew_assignment` ($1:N$):** Một phi hành viên có thể nhận nhiệm vụ trên nhiều tàu bay trong năm phân tích.
*   **`dim_aircraft` $\rightarrow$ `fact_crew_assignment` ($1:N$):** Một tàu bay có thể được vận hành luân phiên bởi nhiều tổ bay khác nhau.

### 2.3. Nhánh Hành Khách và Doanh Thu (Passenger Manifest Branch)
*   **`fact_flights` $\rightarrow$ `fact_passenger_manifest` ($1:N$):** Mỗi chuyến bay cụ thể có một danh sách chi tiết (manifest) ghi nhận các hành khách bay cùng chuyến đó.
*   **`dim_passenger` $\rightarrow$ `fact_passenger_manifest` ($1:N$):** Một hành khách có thể bay nhiều chuyến bay khác nhau trong năm.
*   **`dim_ticket` $\rightarrow$ `fact_passenger_manifest` ($1:1$):** Mỗi vé máy bay điện tử được xuất cho duy nhất một hành khách trên một chặng bay cụ thể.
