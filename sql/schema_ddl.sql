-- =============================================================================
-- KỊCH BẢN KHỞI TẠO CƠ SỞ DỮ LIỆU LOGICAL 3NF (SQL DDL) - DỰ ÁN AEROFLOW
-- Chuẩn hóa dữ liệu mức Khái niệm sang Logic (PostgreSQL / Standard SQL)
-- Thiết lập Khóa chính (PK), Khóa ngoại (FK) và Ràng buộc toàn vẹn
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. BẢNG KHÔNG CÓ PHỤ THUỘC (TẠO TRƯỚC)
-- -----------------------------------------------------------------------------

CREATE TABLE AIRPORT (
    airport_id VARCHAR(10) PRIMARY KEY,
    airport_name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    elevation_ft INT,
    timezone_offset INT
);

CREATE TABLE CARRIER (
    carrier_id VARCHAR(10) PRIMARY KEY,
    carrier_name VARCHAR(150) NOT NULL
);

CREATE TABLE DATE (
    date_id DATE PRIMARY KEY,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE,
    holiday_name VARCHAR(100)
);

CREATE TABLE CANCELLATION_REASON (
    cancellation_code VARCHAR(5) PRIMARY KEY,
    cancellation_desc VARCHAR(150) NOT NULL
);

CREATE TABLE PASSENGER (
    passenger_id VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    gender VARCHAR(10),
    nationality VARCHAR(100),
    date_of_birth DATE,
    loyalty_tier VARCHAR(50)
);

-- -----------------------------------------------------------------------------
-- 2. BẢNG CÓ PHỤ THUỘC CẤP 1
-- -----------------------------------------------------------------------------

CREATE TABLE RUNWAY (
    runway_id VARCHAR(10) PRIMARY KEY,
    airport_id VARCHAR(10) REFERENCES AIRPORT(airport_id) ON DELETE CASCADE,
    length_ft INT NOT NULL,
    width_ft INT NOT NULL,
    surface_type VARCHAR(50),
    lighted BOOLEAN DEFAULT TRUE
);

CREATE TABLE ROUTE (
    route_id VARCHAR(15) PRIMARY KEY,
    origin_airport_id VARCHAR(10) REFERENCES AIRPORT(airport_id),
    dest_airport_id VARCHAR(10) REFERENCES AIRPORT(airport_id),
    distance_miles DECIMAL(6, 2) NOT NULL,
    avg_flight_time_min INT NOT NULL
);

CREATE TABLE AIRCRAFT (
    aircraft_id VARCHAR(20) PRIMARY KEY,
    carrier_id VARCHAR(10) REFERENCES CARRIER(carrier_id),
    manufacturer VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    aircraft_type VARCHAR(50),
    capacity INT NOT NULL,
    manufacture_year INT
);

CREATE TABLE WEATHER (
    weather_id VARCHAR(30) PRIMARY KEY,
    airport_id VARCHAR(10) REFERENCES AIRPORT(airport_id) ON DELETE CASCADE,
    date_id DATE REFERENCES DATE(date_id),
    temp_max_c DECIMAL(4, 1),
    temp_min_c DECIMAL(4, 1),
    precipitation_mm DECIMAL(5, 2),
    snowfall_cm DECIMAL(5, 2),
    wind_speed_kmh DECIMAL(4, 1),
    weather_condition VARCHAR(50)
);

CREATE TABLE TICKET (
    ticket_id VARCHAR(20) PRIMARY KEY,
    passenger_id VARCHAR(20) REFERENCES PASSENGER(passenger_id) ON DELETE CASCADE,
    fare_class VARCHAR(20) NOT NULL,
    ticket_price_usd DECIMAL(10, 2) NOT NULL
);

CREATE TABLE CREW (
    crew_id VARCHAR(20) PRIMARY KEY,
    carrier_id VARCHAR(10) REFERENCES CARRIER(carrier_id),
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(50) NOT NULL,
    license_number VARCHAR(50),
    license_type VARCHAR(50)
);

-- -----------------------------------------------------------------------------
-- 3. BẢNG CÓ PHỤ THUỘC CẤP 2 (FLIGHT & LIÊN KẾT)
-- -----------------------------------------------------------------------------

CREATE TABLE FLIGHT (
    flight_id VARCHAR(50) PRIMARY KEY,
    carrier_id VARCHAR(10) REFERENCES CARRIER(carrier_id),
    aircraft_id VARCHAR(20) REFERENCES AIRCRAFT(aircraft_id),
    route_id VARCHAR(15) REFERENCES ROUTE(route_id),
    date_id DATE REFERENCES DATE(date_id),
    origin_weather_id VARCHAR(30) REFERENCES WEATHER(weather_id),
    dest_weather_id VARCHAR(30) REFERENCES WEATHER(weather_id),
    cancellation_code VARCHAR(5) REFERENCES CANCELLATION_REASON(cancellation_code),
    flight_number VARCHAR(10) NOT NULL,
    tail_number VARCHAR(20) NOT NULL,
    dep_delay_min INT DEFAULT 0,
    arr_delay_min INT DEFAULT 0,
    cancelled BOOLEAN DEFAULT FALSE,
    diverted BOOLEAN DEFAULT FALSE,
    taxi_out_min INT,
    taxi_in_min INT,
    air_time_min INT,
    carrier_delay_min INT DEFAULT 0,
    weather_delay_min INT DEFAULT 0,
    nas_delay_min INT DEFAULT 0,
    security_delay_min INT DEFAULT 0,
    late_aircraft_delay_min INT DEFAULT 0
);

-- Bảng liên kết Manifest (N-N Passenger-Flight)
CREATE TABLE MANIFEST (
    flight_id VARCHAR(50) REFERENCES FLIGHT(flight_id) ON DELETE CASCADE,
    passenger_id VARCHAR(20) REFERENCES PASSENGER(passenger_id) ON DELETE CASCADE,
    ticket_id VARCHAR(20) REFERENCES TICKET(ticket_id) ON DELETE CASCADE,
    checkin_time TIMESTAMP,
    baggage_weight_kg DECIMAL(5, 2),
    PRIMARY KEY (flight_id, passenger_id)
);

-- Bảng liên kết Crew Assignment (N-N Crew-Flight)
CREATE TABLE CREW_ASSIGNMENT (
    flight_id VARCHAR(50) REFERENCES FLIGHT(flight_id) ON DELETE CASCADE,
    crew_id VARCHAR(20) REFERENCES CREW(crew_id) ON DELETE CASCADE,
    duty_hours DECIMAL(5, 2),
    performance_rating DECIMAL(3, 2),
    PRIMARY KEY (flight_id, crew_id)
);
