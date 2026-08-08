# ✈️ AeroFlow

### Aviation Data Warehouse, ELT Pipeline & Analytics Platform

> ⚙️ **Data Engineering** · 📊 **Data Analytics** · ☁️ **Cloud** · 🌐 **Web Application**

AeroFlow is an end-to-end aviation data platform built on **Google Cloud Platform (GCP)** for ingesting, processing, storing, validating, and analyzing flight and weather data.

The platform connects **business requirements → data engineering → analytics → business insights** through a centralized cloud data architecture.

---

## 🎯 Overview

```text
Business Requirements
        ↓
Data Sources
        ↓
Data Ingestion
        ↓
Data Lake
        ↓
ELT Pipeline
        ↓
Data Warehouse
        ↓
Data Quality
        ↓
Data Analytics
        ↓
Business Insights
        ↓
Web Application
```

---

## ⚙️ Data Engineering

AeroFlow is designed as a modular and scalable data pipeline.

* Multi-source flight, weather, airport, and airline data ingestion
* Modular ETL / ELT pipeline
* Cloud-based Data Lake with Google Cloud Storage
* BigQuery Data Warehouse
* Star Schema & dimensional modeling
* Table partitioning & clustering
* Automated data quality validation
* Pipeline execution & monitoring

---

## 🏢 Data Warehouse

The analytical layer is built on **BigQuery** using a **Star Schema** centered around flight events.

```text
                    dim_date
                       │
                       ↓
dim_airport ─────→ fact_flights ←───── dim_carrier
                       │
                 ┌─────┴─────┐
                 ↓           ↓
           dim_weather   dim_aircraft
```

### Fact Table

`fact_flights`

Contains flight-level events and operational metrics such as delays, cancellations, distance, and other flight performance indicators.

### Dimension Tables

`dim_date` · `dim_airport` · `dim_carrier` · `dim_aircraft` · `dim_weather`

This dimensional model supports analytical queries, KPI reporting, and dashboard applications.

---

## 📊 Data Analytics

AeroFlow transforms warehouse data into aviation KPIs and actionable business insights.

* ✈️ Flight volume & operational trends
* ⏱️ Delay & cancellation analysis
* 🏢 Airline performance
* 🛫 Airport performance
* 🌦️ Weather impact analysis
* 📈 On-time performance

```text
BigQuery
    ↓
SQL Analytics
    ↓
KPI Calculation
    ↓
Visualization
    ↓
Business Insights
```

---

## 🌐 Web Application

AeroFlow provides a web application built on top of the data platform, connecting operational data with end-user analytics.

### 👤 Customer Portal

* Flight Search
* Flight Details
* Airport & Airline Information
* Weather Information
* Flight Risk

### 🛠️ Admin Dashboard

* KPI Monitoring
* Flight Analytics
* Delay Analysis
* Data Quality Monitoring
* Pipeline Monitoring

🚀 **[Live Demo](https://aeroflow-orchestrator-980661018616.us-central1.run.app/)**

---

## 🛠️ Tech Stack

### ⚙️ Data Engineering

`Python` `SQL` `ETL / ELT` `BigQuery` `Google Cloud Storage` `Apache Beam`

### 📊 Data Analytics

`Pandas` `SQL` `KPI Analysis` `Data Visualization` `Business Intelligence`

### ☁️ Cloud

`Google Cloud Platform` `Cloud Run`

### 🌐 Web Application

`Flask` `REST API` `HTML` `CSS` `JavaScript` `Chart.js`

### 🔗 Data Sources

`Open-Meteo` `OpenFlights` `OurAirports` `Flight Data`

---

## 📂 Project Structure

```text
AeroFlow/
├── main.py
├── requirements.txt
├── Dockerfile
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── quality.py
│   └── orchestrator.py
│
├── web/
├── sql/
├── docs/
├── scripts/
└── notebooks/
```

The repository is organized into separate layers for **data processing, web application, SQL, documentation, automation scripts, and exploratory analysis**.

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/nlong05013456-oss/AeroFlow.git
cd AeroFlow
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the pipeline

```bash
python main.py
```

### 4. Run the web application

```bash
python web/app.py
```

Then open:

```text
http://localhost:5000
```

> ⚠️ **Configuration:** GCP credentials and required environment variables must be configured before running cloud-based components. Never commit credentials, API keys, or `.env` files to the repository.

---

## 🎯 Project Focus

### ⚙️ Data Engineering — Core

**Data Ingestion** · **ELT Pipeline** · **Data Lake** · **Data Warehouse** · **Data Quality** · **Cloud Data Platform**

### 📊 Data Analytics — Core

**SQL** · **KPI Analysis** · **Visualization** · **Business Intelligence** · **Business Insights**

### ☁️ Cloud & 🌐 Web — Supporting

**GCP** · **Cloud Run** · **Flask API** · **Analytics Dashboard**

---

## 🔄 End-to-End Architecture

```text
Business
   ↓
Data Sources
   ↓
Data Engineering
   ↓
Cloud Data Platform
   ↓
Data Warehouse
   ↓
Analytics
   ↓
Business Insights
   ↓
Web Application
```

### `Business → Data → Engineering → Analytics → Insights`

⭐ Thanks for visiting **AeroFlow**!
