# ✈️ AeroFlow

### Aviation Data Warehouse, ELT Pipeline & Analytics Platform

> ⚙️ **Data Engineering** · 📊 **Data Analytics** · ☁️ **Cloud** · 🌐 **Web Application**

AeroFlow is an end-to-end aviation data platform built on **Google Cloud Platform (GCP)** for collecting, processing, transforming, storing, validating, and analyzing flight and weather data.

The project focuses primarily on **Data Engineering and Data Analytics**, while Cloud infrastructure and a Web Application are used to turn the data platform into a practical end-to-end solution.

---

## 🎯 Project Overview

AeroFlow starts from a business-oriented question:

> **How can aviation data be transformed into reliable information and actionable insights for monitoring flight performance?**

Instead of treating data analysis as an isolated notebook, AeroFlow follows the complete journey from **business requirements to data engineering, data warehousing, analytics, and application**.

```text
Business Requirements
        ↓
    Data Sources
        ↓
   Data Ingestion
        ↓
      Data Lake
        ↓
   ELT / Transformation
        ↓
   Data Warehouse
        ↓
 Data Quality & Validation
        ↓
   Data Analytics
        ↓
 Business Insights
        ↓
 Web Application
```

---

# 🏗️ System Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                          │
│                                                              │
│ Historical Flight Data · Flight API · Open-Meteo API         │
│ OpenFlights · OurAirports                                    │
└──────────────────────────────┬───────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────┐
│                     DATA INGESTION                           │
│                                                              │
│              Python ELT / Daily Ingestion                    │
└──────────────────────────────┬───────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────┐
│                        DATA LAKE                             │
│                                                              │
│                  Google Cloud Storage                        │
└──────────────────────────────┬───────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────┐
│                     TRANSFORMATION                           │
│                                                              │
│      Cleaning · Standardization · Validation · Enrichment    │
└──────────────────────────────┬───────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────┐
│                     DATA WAREHOUSE                           │
│                                                              │
│                        BigQuery                              │
│                                                              │
│              Star Schema · Partitioning · Clustering         │
└──────────────────────────────┬───────────────────────────────┘
                               ↓
                    ┌──────────┴──────────┐
                    ↓                     ↓
        ┌──────────────────────┐  ┌────────────────────────┐
        │    DATA ANALYTICS    │  │    WEB APPLICATION     │
        │                      │  │                        │
        │ KPI Analysis         │  │ Flask Backend          │
        │ Delay Analysis       │  │ REST API               │
        │ Airport Analysis     │  │ Customer Portal        │
        │ Airline Analysis     │  │ Admin Analytics        │
        │ Weather Analysis     │  │ Pipeline Monitoring    │
        └──────────────────────┘  └────────────────────────┘
```

---

# ⚙️ Data Engineering

Data Engineering is the **core foundation** of AeroFlow.

The platform is designed to build a reliable and reusable data pipeline before analytical workloads are performed.

## 📥 Data Sources

AeroFlow integrates multiple aviation and weather data sources:

| Source                 | Purpose                                |
| ---------------------- | -------------------------------------- |
| Historical Flight Data | Historical flight performance          |
| Flight API             | Daily flight information               |
| Open-Meteo API         | Weather information                    |
| OpenFlights            | Airline, airport and route information |
| OurAirports            | Airport and runway information         |

---

## 🔄 ELT Pipeline

The pipeline follows a modular ELT workflow:

```text
Extract
   ↓
Validate
   ↓
Transform
   ↓
Load
   ↓
Monitor
```

### Extract

Collect flight, airport, airline, and weather data from multiple sources.

### Transform

Clean, standardize, validate, and enrich raw data before loading it into the analytical layer.

### Load

Load transformed datasets into **Google BigQuery** following the designed Data Warehouse model.

### Monitor

Track pipeline execution, processed records, execution time, source information, and pipeline status.

---

## ☁️ Cloud Data Platform

AeroFlow uses Google Cloud Platform as the main infrastructure:

```text
Data Sources
     ↓
Google Cloud Storage
     ↓
Google BigQuery
     ↓
Cloud Run
     ↓
Web Application
```

### Google Cloud Storage

Used as the **Data Lake** for raw and intermediate data.

### Google BigQuery

Used as the **Data Warehouse** for analytical workloads.

### Cloud Run

Used to deploy the application and pipeline components as cloud services.

---

# 🏢 Data Warehouse

AeroFlow uses **BigQuery** as the analytical Data Warehouse.

The warehouse follows a **Star Schema** designed around flight events.

```text
                         dim_date
                            │
                            │
                            ↓
dim_airport ───────── fact_flights ───────── dim_carrier
                            │
                            │
                 ┌──────────┴──────────┐
                 ↓                     ↓
          dim_weather            dim_aircraft
```

## ⭐ Fact Table

### `fact_flights`

The central fact table contains flight-level events and analytical measures such as:

* Departure delay
* Arrival delay
* Cancellation
* Diversion
* Distance
* Delay causes
* Taxi time
* Flight status

## 📚 Dimension Tables

* `dim_date`
* `dim_airport`
* `dim_carrier`
* `dim_aircraft`
* `dim_weather`

The warehouse is optimized through:

* **Partitioning**
* **Clustering**
* **Dimensional Modeling**
* **Analytical SQL**

---

# 🔍 Data Quality

Data quality is integrated directly into the pipeline and analytical platform.

AeroFlow automatically validates important data rules before the data is used for analytics.

```text
┌─────────────────────────────────────┐
│          DATA QUALITY               │
├─────────────────────────────────────┤
│ ✓ Primary Key Null Check            │
│ ✓ Duplicate Detection               │
│ ✓ Foreign Key Integrity             │
│ ✓ Date Boundary Validation          │
│ ✓ Numeric Value Validation          │
└─────────────────────────────────────┘
```

### Current Validation Result

**5 / 5 Quality Rules Verified — PASS 100%**

The current checks cover:

* Primary key null validation
* Physical duplicate detection
* Foreign key referential integrity
* Flight date boundary validation
* Numeric delay value validation

---

# 📊 Data Analytics

After the data has been engineered and validated, AeroFlow transforms the warehouse into analytical information.

The platform focuses on understanding **flight performance, delays, airports, airlines, weather, and operational trends**.

## 📈 Key Analytics

* ✈️ Total flight volume
* ⏱️ Average delay
* 🟢 On-time performance
* 🏢 Airline performance
* 🛫 Airport performance
* 🌦️ Weather impact on delays
* 📉 Delay cause breakdown
* ✈️ Delayed aircraft / fleet
* 📅 Daily and monthly trends
* 🛬 Busy and high-delay airports

The analytical workflow follows:

```text
BigQuery
    ↓
SQL Queries
    ↓
Aggregated Metrics
    ↓
KPI Analysis
    ↓
Visualization
    ↓
Business Insights
```

---

# 📌 Current Platform Snapshot

The deployed platform currently exposes:

| Metric           |         Value |
| ---------------- | ------------: |
| ✈️ Total Flights | **2,881,296** |
| 🛬 Airports      |     **9,231** |
| 🛤️ Runways      |    **15,482** |
| 🏢 Airlines      |        **14** |
| ⏱️ On-Time Rate  |     **81.4%** |
| ⏱️ Average Delay | **14.60 min** |
| 🛡️ Data Quality | **100% PASS** |

The platform also supports automated daily ingestion and records pipeline execution history for monitoring.

---

# 🌐 Web Application

AeroFlow provides a web application on top of the data platform.

### 🚀 Live Demo

**[Open AeroFlow Platform](https://aeroflow-orchestrator-980661018616.us-central1.run.app/)**

The application provides two main experiences:

```text
                    AeroFlow Platform
                           │
              ┌────────────┴────────────┐
              ↓                         ↓
       Customer Portal          Admin Analytics
              │                         │
       Flight Search             KPI Analysis
       Weather Info              BigQuery Analytics
       Flight Risk               Data Quality
       Flight Details            Pipeline Monitoring
```

---

## 👤 Customer Portal

The Customer Portal allows users to search and explore flight information.

### Features

* Flight search by date
* Origin airport filtering
* Destination airport filtering
* Airline / aircraft filtering
* Flight information
* Origin weather
* Destination weather
* Flight risk information
* Real-time weather integration

The application queries the analytical warehouse while combining weather information from Open-Meteo.

---

## 🛠️ Admin Analytics Portal

The Admin Analytics Portal provides a higher-level view of the aviation data platform.

### Analytics

* KPI monitoring
* Airline on-time ranking
* Delay analysis
* Airport analysis
* Weather impact analysis
* Fleet delay analysis
* Monthly and daily trends

### Platform Monitoring

* Daily ingestion history
* Pipeline execution logs
* Processed flight counts
* Execution time
* Pipeline status
* Data quality results

---

# 🔄 Pipeline Monitoring

AeroFlow does not only analyze the data — it also monitors the process that produces the data.

```text
Scheduled Job
      ↓
Data Source
      ↓
Data Ingestion
      ↓
Records Processed
      ↓
BigQuery Load
      ↓
Data Quality
      ↓
Pipeline Status
```

The live platform currently displays automated ingestion history, including daily flight ingestion, weather synchronization, processing counts, execution times, and pipeline status.

This provides visibility into both:

> **What does the data tell us?**

and

> **Is the pipeline producing reliable data?**

---

# 🛠️ Tech Stack

### ⚙️ Data Engineering

`Python` · `ETL / ELT` · `Data Ingestion` · `Data Pipeline` · `Data Quality`

### 🏢 Data Warehouse

`Google BigQuery` · `SQL` · `Star Schema` · `Data Modeling` · `Partitioning` · `Clustering`

### ☁️ Cloud

`Google Cloud Platform` · `GCS` · `BigQuery` · `Cloud Run`

### 📊 Data Analytics

`SQL` · `Python` · `Pandas` · `KPI Analysis` · `Data Visualization` · `Business Intelligence`

### 🌐 Web Application

`Flask` · `REST API` · `HTML5` · `CSS3` · `JavaScript` · `Chart.js`

### 🔗 Data Sources

`Open-Meteo API` · `OpenFlights` · `OurAirports` · `Historical Flight Data`

---

# 📂 Project Structure

```text
AeroFlow/
│
├── main.py
├── requirements.txt
├── Dockerfile
├── .gitignore
│
├── src/
│   ├── config.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── quality.py
│   └── orchestrator.py
│
├── web/
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── sql/
│   ├── schema_bigquery.sql
│   └── analytics/
│
├── docs/
│   ├── data_model.md
│   ├── star_schema.md
│   └── project_documentation.md
│
├── scripts/
│
└── notebooks/
```

---

# 🚀 Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/nlong05013456-oss/AeroFlow.git

cd AeroFlow
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure GCP

Set the required environment variables:

```bash
export GCP_PROJECT_ID="your-project-id"
export GCS_BUCKET_NAME="your-bucket-name"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
```

> ⚠️ Never commit service account credentials, API keys, passwords, or `.env` files to GitHub.

## 4. Run the ELT Pipeline

```bash
python main.py
```

## 5. Start the Web Application

```bash
python web/app.py
```

Open the local application:

```text
http://localhost:5000
```

---

# 📚 Documentation

Detailed documentation is available inside the `docs/` directory.

* 📄 **Project Documentation**
* 🗄️ **Data Model**
* ⭐ **Star Schema**
* 🧮 **BigQuery Schema**
* 📊 **Analytics Queries**

---

# 📌 Project Highlights

| Area                | Implementation            |
| ------------------- | ------------------------- |
| Business Domain     | Aviation                  |
| Data Engineering    | ELT Pipeline              |
| Data Lake           | Google Cloud Storage      |
| Data Warehouse      | Google BigQuery           |
| Data Modeling       | Star Schema               |
| Query Optimization  | Partitioning & Clustering |
| Data Quality        | Automated Validation      |
| Data Analytics      | SQL & KPI Analysis        |
| Pipeline Monitoring | Automated Execution Logs  |
| Application         | Flask Web Platform        |
| Deployment          | Cloud Run                 |

---

# 🎯 What This Project Demonstrates

AeroFlow demonstrates the complete journey from a business requirement to a working data platform:

```text
Business Problem
       ↓
Data Sources
       ↓
Data Engineering
       ↓
Data Lake
       ↓
Data Warehouse
       ↓
Data Quality
       ↓
Data Analytics
       ↓
Business Insights
       ↓
Application
```

The project demonstrates practical experience in:

* ⚙️ Data Engineering
* 📊 Data Analytics
* 🏢 Data Warehouse Design
* ☁️ Cloud Data Platforms
* 🔄 ELT Pipeline Development
* 🔍 Data Quality
* 🧮 Analytical SQL
* 📈 Business Intelligence
* 🌐 Data-driven Web Applications

---

# 🎯 Project Focus

AeroFlow is primarily a:

### ⚙️ Data Engineering + 📊 Data Analytics Project

with:

### ☁️ Cloud + 🌐 Web Application

supporting the overall solution.

Machine Learning and Artificial Intelligence are **not the primary focus of AeroFlow**. They are treated as complementary areas in the broader portfolio.

---

## 👨‍💻 Author

### Nguyễn Nhật Long

**Data Science Student**

Interested in:

`Data Analytics` · `Data Engineering` · `Machine Learning` · `Artificial Intelligence`

---

### `Business → Data → Engineering → Analytics → Insights`

⭐ Thanks for visiting AeroFlow!
