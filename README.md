# AeroFlow - GCP Data Pipeline & Analytics Web Dashboard

AeroFlow là hệ thống pipeline xử lý dữ liệu hàng không trên Google Cloud Platform (GCP) kết hợp Web Dashboard giám sát và phân tích hiệu suất chuyến bay thời gian thực.

---

## 🏗️ Kiến trúc Hệ thống (System Architecture)

- **Ingestion & Data Lake**: Thu thập dữ liệu từ Open-Meteo API, OpenFlights, OurAirports và đẩy dữ liệu thô lên **Google Cloud Storage (GCS)**.
- **Data Warehouse & Data Mart (Google BigQuery)**: Biến đổi dữ liệu theo mô hình **Star Schema** (Fact Flights + các Dimension Airports, Airlines, Aircraft, Weather, Time), áp dụng Partitioning & Clustering.
- **Data Quality & Audit**: Tự động kiểm tra chất lượng dữ liệu (schema validation, null check, duplicate check).
- **Web Application**: Backend **Python Flask** với tính năng phân quyền (RBAC), Column-Level Security và Frontend **Glassmorphism Dark Mode Dashboard** (Chart.js, HTML5, CSS3).

---

## 📂 Cấu trúc Thư mục (Directory Structure)

```text
AeroFlow/
├── main.py               # Script chạy chính toàn bộ ELT Pipeline
├── requirements.txt      # Thư viện Python phụ thuộc
├── Dockerfile            # Cấu hình containerization
├── .gitignore            # Cấu hình bỏ qua dữ liệu lớn & file tạm
│
├── src/                  # Core Pipeline Modules
│   ├── config.py         # Cấu hình GCP Project, Bucket, BQ Datasets
│   ├── extract.py        # Module cào & tải dữ liệu thô
│   ├── transform.py      # Module làm sạch & chuẩn hóa dữ liệu
│   ├── load.py           # Module nạp dữ liệu vào BigQuery Data Warehouse
│   ├── quality.py        # Module kiểm tra chất lượng dữ liệu
│   └── orchestrator.py   # Module điều phối quy trình chạy
│
├── web/                  # Web Application Dashboard (Flask API & UI)
│   ├── app.py            # Flask Server Backend & REST API
│   ├── templates/        # HTML Templates (Glassmorphism Dashboard)
│   └── static/           # Static CSS & JS Dashboard logic
│
├── sql/                  # Cấu trúc SQL DDL, BigQuery & DBML Schemas
├── docs/                 # Tài liệu thiết kế ERD, Star Schema & Báo cáo
├── scripts/              # Các script kiểm thử & tiện ích hỗ trợ
└── notebooks/            # Jupyter Notebooks phân tích dữ liệu
```

---

## 🚀 Hướng dẫn Chạy Dự án (Quick Start)

### 1. Cài đặt Môi trường
```bash
pip install -r requirements.txt
```

### 2. Thiết lập Google Cloud Platform (GCP) Credentials
Thiết lập biến môi trường GCP:
```bash
export GCP_PROJECT_ID="aeroflow-cap2"
export GCS_BUCKET_NAME="aeroflow-data-lake"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
```

### 3. Thực thi Pipeline ELT
```bash
python main.py
```

### 4. Khởi chạy Web Dashboard
```bash
python web/app.py
```
Truy cập giao diện tại: `http://localhost:5000`

---

## 📑 Tài liệu Chi tiết
- [Tài liệu Báo cáo Đồ án](docs/Báo%20cáo%20đề%20tài%20CAP2.md)
- [Mô hình Dữ liệu (Data Model)](docs/data_model.md)
- [Sơ đồ Star Schema](docs/star_schema.md)
- [SQL BigQuery Schema](sql/schema_bigquery.sql)
