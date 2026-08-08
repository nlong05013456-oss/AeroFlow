# ✈️ AeroFlow

### Aviation Data Warehouse, ELT Pipeline & Analytics Platform

> ⚙️ **Data Engineering** · 📊 **Data Analytics** · ☁️ **Cloud** · 🌐 **Web Application**

AeroFlow is an end-to-end aviation data platform built on **Google Cloud Platform (GCP)** to collect, process, store, validate, and analyze flight and weather data.

---

## 🎯 Overview

```text
Business Requirements
        ↓
Data Sources → Data Ingestion → Data Lake
        ↓
ELT Pipeline → Data Warehouse → Data Quality
        ↓
Data Analytics → Business Insights
        ↓
Web Application
```

---

## ⚙️ Data Engineering

- Multi-source flight, weather, airport & airline data ingestion
- Modular ETL / ELT pipeline
- Google Cloud Storage Data Lake
- BigQuery Data Warehouse
- Star Schema & dimensional modeling
- Partitioning & Clustering
- Data Quality validation
- Pipeline monitoring

---

## 🏢 Data Warehouse

Built with **BigQuery** using a Star Schema centered around flight events.

```text
             dim_date
                │
                ↓
dim_airport → fact_flights ← dim_carrier
                │
          ┌─────┴─────┐
          ↓           ↓
    dim_weather  dim_aircraft
```

**Fact:** `fact_flights`

**Dimensions:** `date` · `airport` · `carrier` · `aircraft` · `weather`

---

## 📊 Data Analytics

Transforming warehouse data into aviation KPIs and business insights.

- ✈️ Flight volume & trends
- ⏱️ Delay & cancellation analysis
- 🏢 Airline performance
- 🛫 Airport performance
- 🌦️ Weather impact
- 📈 On-time performance

```text
BigQuery → SQL → KPI → Visualization → Insights
```

---

## 🌐 Web Application

A web dashboard built on top of the data platform.

**Customer Portal**

Flight Search · Flight Details · Airport / Airline Information · Weather · Flight Risk

**Admin Dashboard**

KPI Monitoring · Flight Analytics · Delay Analysis · Data Quality · Pipeline Monitoring

🚀 **[Live Demo](https://aeroflow-orchestrator-980661018616.us-central1.run.app/)**

---

## 🛠️ Tech Stack

**⚙️ Data Engineering**  
`Python` `SQL` `ETL / ELT` `BigQuery` `GCS` `Apache Beam`

**📊 Data Analytics**  
`Pandas` `SQL` `KPI Analysis` `Data Visualization` `Business Intelligence`

**☁️ Cloud**  
`GCP` `Cloud Run`

**🌐 Web**  
`Flask` `REST API` `HTML` `CSS` `JavaScript` `Chart.js`

**🔗 Data Sources**  
`Open-Meteo` `OpenFlights` `OurAirports` `Flight Data`

---

## 📂 Project Structure

```text
AeroFlow/
├── main.py
├── requirements.txt
├── Dockerfile
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── quality.py
│   └── orchestrator.py
├── web/
├── sql/
├── docs/
├── scripts/
└── notebooks/
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/nlong05013456-oss/AeroFlow.git
cd AeroFlow
pip install -r requirements.txt
python main.py
```

Run the dashboard:

```bash
python web/app.py
```

Open `http://localhost:5000`

> ⚠️ Configure GCP credentials before running the pipeline. Never commit credentials, API keys, or `.env` files.

---

## 🎯 Project Focus

**⚙️ Data Engineering — Core**  
Data Ingestion · ELT · Data Lake · Data Warehouse · Data Quality · Cloud

**📊 Data Analytics — Core**  
SQL · KPI Analysis · Visualization · Business Intelligence · Business Insights

**☁️ Cloud & 🌐 Web — Supporting**  
GCP · Flask API · Analytics Dashboard

---

### `Business → Data → Engineering → Analytics → Insights`

⭐ Thanks for visiting **AeroFlow**!
