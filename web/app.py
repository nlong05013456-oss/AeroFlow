"""
app.py
Backend server viết bằng Python Flask. Kết nối với Google BigQuery để lấy dữ liệu 
từ bảng Data Mart `mart_delay_analysis`, hỗ trợ lọc động và trả về JSON.
Tích hợp phân quyền người dùng (RBAC) và bảo mật cột dữ liệu (Column-Level Security).
Tích hợp sẵn Mock Data Fallback để chạy thử nghiệm ngay lập tức nếu chưa cấu hình GCP.
"""

import os
import random
from flask import Flask, render_template, request, jsonify, session

# Khởi tạo Flask App
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "aeroflow_super_secret_session_key_2024"

# Lấy cấu hình Project ID từ src.config (nếu có)
try:
    from src.config import GCP_PROJECT_ID
except ImportError:
    GCP_PROJECT_ID = "aeroflow-cap2"

# Thử kết nối BigQuery Client
USE_MOCK_DATA = False
try:
    from google.cloud import bigquery
    # Kiểm tra xem có quyền truy cập credentials không
    bq_client = bigquery.Client(project=GCP_PROJECT_ID)
    # Thử gọi kiểm tra đơn giản để xem credentials có hoạt động không
    bq_client.list_datasets(max_results=1)
    print(">>> Kết nối thành công tới Google BigQuery! Đang chạy ở chế độ REAL-TIME CLOUD.")
except Exception as e:
    print(f">>> Cảnh báo: Không thể kết nối tới BigQuery ({e}).")
    print(">>> Hệ thống sẽ tự động chạy ở chế độ giả lập (MOCK MODE) để xem thử giao diện.")
    USE_MOCK_DATA = True

# --- API ĐĂNG NHẬP PHÂN QUYỀN (LOGIN) ---
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    
    # Tài khoản mẫu cho người theo dõi máy bay (Flight Tracker)
    if username == "tracker" and password == "aeroflow2024":
        session["user_role"] = "tracker"
        session["username"] = username
        return jsonify({"success": True, "role": "tracker", "message": "Đăng nhập thành công với vai trò Người theo dõi máy bay!"})
    
    return jsonify({"success": False, "message": "Sai tài khoản hoặc mật khẩu!"}), 401

# --- API ĐĂNG XUẤT (LOGOUT) ---
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Đã đăng xuất khỏi hệ thống."})

# --- API KIỂM TRA TRẠNG THÁI SESSION ---
@app.route("/api/user-status")
def user_status():
    if "user_role" in session:
        return jsonify({"logged_in": True, "role": session["user_role"], "username": session["username"]})
    return jsonify({"logged_in": False, "role": "public"})

# --- API LẤY DANH SÁCH BỘ LỌC (CARRIERS & AIRPORTS) ---
@app.route("/api/filters")
def get_filters():
    if USE_MOCK_DATA:
        carriers = [
            {"id": "AA", "name": "American Airlines"},
            {"id": "DL", "name": "Delta Air Lines"},
            {"id": "UA", "name": "United Airlines"},
            {"id": "WN", "name": "Southwest Airlines"},
            {"id": "B6", "name": "JetBlue Airways"},
            {"id": "AS", "name": "Alaska Airlines"}
        ]
        airports = ["ATL", "LAX", "ORD", "DFW", "DEN", "JFK", "SFO", "LAS", "MCO", "CLT"]
        return jsonify({"carriers": carriers, "airports": airports, "mode": "MOCK"})
    
    # Lấy dữ liệu thực từ BigQuery
    client = bigquery.Client(project=GCP_PROJECT_ID)
    try:
        query_carriers = f"SELECT DISTINCT carrier_key as id, carrier_name as name FROM `{GCP_PROJECT_ID}.warehouse.dim_carrier` ORDER BY name"
        query_airports = f"SELECT DISTINCT airport_key FROM `{GCP_PROJECT_ID}.warehouse.dim_airport` WHERE airport_type = 'large_airport' LIMIT 15"
        
        df_c = client.query(query_carriers).to_dataframe()
        df_a = client.query(query_airports).to_dataframe()
        
        return jsonify({
            "carriers": df_c.to_dict(orient="records"),
            "airports": df_a["airport_key"].tolist(),
            "mode": "CLOUD"
        })
    except Exception as e:
        return jsonify({"error": str(e), "mode": "ERROR_FALLBACK"})

# --- API TRUY VẤN SỐ LIỆU PHÂN TÍCH ---
@app.route("/api/analytics")
def get_analytics():
    # Đọc các tham số bộ lọc từ request query params
    carrier = request.args.get("carrier", "ALL")
    airport = request.args.get("airport", "ALL")
    month = request.args.get("month", "ALL")
    is_holiday = request.args.get("is_holiday", "ALL")

    # Xác định vai trò của phiên làm việc hiện tại
    user_role = session.get("user_role", "public")

    if USE_MOCK_DATA:
        return jsonify(generate_mock_analytics(carrier, airport, month, is_holiday, user_role))

    # Xây dựng câu truy vấn động dựa trên bộ lọc
    where_clauses = ["1=1"]
    if carrier != "ALL":
        where_clauses.append(f"carrier_key = '{carrier}'")
    if airport != "ALL":
        where_clauses.append(f"origin_airport_key = '{airport}'")
    if month != "ALL":
        where_clauses.append(f"month = {month}")
    if is_holiday != "ALL":
        is_hol_val = "TRUE" if is_holiday == "true" else "FALSE"
        where_clauses.append(f"is_holiday = {is_hol_val}")
        
    where_str = " AND ".join(where_clauses)
    
    # Truy vấn KPIs tổng hợp
    query = f"""
    SELECT 
        SUM(total_flights) AS total_flights,
        SUM(total_cancelled) AS total_cancelled,
        SUM(total_delayed_departures) AS total_delayed,
        ROUND(AVG(avg_dep_delay_minutes), 1) AS avg_delay_min,
        SUM(total_carrier_delay_min) AS carrier_delay,
        SUM(total_weather_delay_min) AS weather_delay,
        SUM(total_nas_delay_min) AS nas_delay,
        SUM(total_security_delay_min) AS security_delay,
        SUM(total_late_aircraft_delay_min) AS late_aircraft_delay
    FROM `{GCP_PROJECT_ID}.warehouse.mart_delay_analysis`
    WHERE {where_str}
    """
    
    # Lấy dữ liệu biểu đồ xu hướng theo tháng
    query_trend = f"""
    SELECT 
        month,
        SUM(total_flights) AS flights,
        SUM(total_delayed_departures) AS delayed
    FROM `{GCP_PROJECT_ID}.warehouse.mart_delay_analysis`
    WHERE {where_str}
    GROUP BY month
    ORDER BY month
    """
    
    # Lấy dữ liệu thời tiết
    query_weather = f"""
    SELECT 
        CASE 
            WHEN origin_precipitation = 0 THEN 'Không mưa'
            WHEN origin_precipitation > 0 AND origin_precipitation <= 5 THEN 'Mưa nhỏ (<5mm)'
            ELSE 'Mưa lớn (>5mm)'
        END AS weather_condition,
        SUM(total_flights) AS flights,
        SUM(total_delayed_departures) AS delayed
    FROM `{GCP_PROJECT_ID}.warehouse.mart_delay_analysis`
    WHERE {where_str} AND origin_precipitation IS NOT NULL
    GROUP BY weather_condition
    """

    client = bigquery.Client(project=GCP_PROJECT_ID)
    try:
        # Chạy các truy vấn
        df_summary = client.query(query).to_dataframe()
        df_trend = client.query(query_trend).to_dataframe()
        df_weather = client.query(query_weather).to_dataframe()
        
        sum_row = df_summary.iloc[0]
        
        total_fl = int(sum_row["total_flights"]) if not pd.isna(sum_row["total_flights"]) else 0
        total_del = int(sum_row["total_delayed"]) if not pd.isna(sum_row["total_delayed"]) else 0
        
        # Thiết lập cấu trúc trả về cơ bản
        response_data = {
            "mode": "CLOUD",
            "role": user_role,
            "kpis": {
                "total_flights": total_fl,
                "total_delayed": total_del,
                "total_cancelled": int(sum_row["total_cancelled"]) if not pd.isna(sum_row["total_cancelled"]) else 0,
                "avg_delay_minutes": float(sum_row["avg_delay_min"]) if not pd.isna(sum_row["avg_delay_min"]) else 0.0,
                "delay_rate": round((total_del / total_fl * 100), 1) if total_fl > 0 else 0.0
            },
            "delay_breakdown": {
                "carrier": int(sum_row["carrier_delay"]) if not pd.isna(sum_row["carrier_delay"]) else 0,
                "weather": int(sum_row["weather_delay"]) if not pd.isna(sum_row["weather_delay"]) else 0,
                "nas": int(sum_row["nas_delay"]) if not pd.isna(sum_row["nas_delay"]) else 0,
                "security": int(sum_row["security_delay"]) if not pd.isna(sum_row["security_delay"]) else 0,
                "late_aircraft": int(sum_row["late_aircraft_delay"]) if not pd.isna(sum_row["late_aircraft_delay"]) else 0
            },
            "monthly_trend": {
                "labels": [f"Tháng {int(m)}" for m in df_trend["month"].tolist()],
                "flights": df_trend["flights"].tolist(),
                "delays": df_trend["delayed"].tolist()
            },
            "weather_impact": {
                "labels": df_weather["weather_condition"].tolist(),
                "delay_rates": [round((d/f * 100), 1) if f > 0 else 0 for d, f in zip(df_weather["delayed"], df_weather["flights"])]
            }
        }
        
        # --- COLUMN-LEVEL SECURITY: BẢNG THEO DÕI MÁY BAY CHI TIẾT (CHỈ DÀNH CHO TRACKER) ---
        if user_role == "tracker":
            # Xây dựng truy vấn bảng chi tiết (Fact table join Dim tables)
            where_details_clauses = ["1=1"]
            if carrier != "ALL":
                where_details_clauses.append(f"f.carrier_key = '{carrier}'")
            if airport != "ALL":
                where_details_clauses.append(f"f.origin_airport_key = '{airport}'")
            where_details_str = " AND ".join(where_details_clauses)
            
            query_details = f"""
            SELECT 
                f.date_key,
                c.carrier_name,
                f.flight_number,
                f.origin_airport_key,
                f.dest_airport_key,
                -- Trả về đuôi máy bay đã được mã hóa ở tầng DW (Security Compliance)
                f.masked_tail_number,
                f.dep_delay,
                f.arr_delay,
                -- Kết nối Dim Sân bay lấy thông tin độ cao, đường băng (Chỉ hiển thị cho Tracker)
                da.elevation_ft
            FROM `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.fact_flights` f
            JOIN `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_carrier` c ON f.carrier_key = c.carrier_key
            JOIN `{GCP_PROJECT_ID}.{BQ_WAREHOUSE_DATASET}.dim_airport` da ON f.origin_airport_key = da.airport_key
            WHERE {where_details_str}
            LIMIT 15
            """
            df_details = client.query(query_details).to_dataframe()
            # Đổi kiểu dữ liệu date sang string để serialize JSON
            if not df_details.empty:
                df_details["date_key"] = df_details["date_key"].astype(str)
            response_data["details_table"] = df_details.to_dict(orient="records")
            
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e), "mode": "ERROR_FALLBACK"})

# --- ĐỊNH TUYẾN TRANG CHỦ ---
@app.route("/")
def index():
    return render_template("index.html")

# --- TRÌNH TẠO GIẢ LẬP DỮ LIỆU CÓ PHÂN QUYỀN (MOCK DATA GENERATOR) ---
def generate_mock_analytics(carrier, airport, month, is_holiday, user_role):
    random.seed(hash(carrier + airport + str(month) + str(is_holiday)))
    
    multiplier = 1.0
    if is_holiday == "true":
        multiplier *= 1.45
    if carrier in ["DL", "UA"]:
        multiplier *= 0.85
    elif carrier in ["WN", "B6"]:
        multiplier *= 1.25
        
    base_flights = random.randint(45000, 60000)
    if carrier != "ALL":
        base_flights = int(base_flights / 6)
    if airport != "ALL":
        base_flights = int(base_flights / 10)
    if month != "ALL":
        base_flights = int(base_flights / 12)
        
    total_flights = max(base_flights, 120)
    delay_rate = min(max(18.5 * multiplier + random.uniform(-2, 2), 5.0), 90.0)
    total_delayed = int(total_flights * (delay_rate / 100))
    total_cancelled = int(total_flights * random.uniform(0.01, 0.03))
    avg_delay = round(15.2 * multiplier + random.uniform(-1, 3), 1)
    
    c_delay = int(total_delayed * 28 * multiplier)
    w_delay = int(total_delayed * 12 * multiplier)
    n_delay = int(total_delayed * 30)
    s_delay = int(total_delayed * 1)
    la_delay = int(total_delayed * 29 * multiplier)
    
    months_labels = [f"Tháng {i}" for i in range(1, 13)]
    flights_trend = []
    delays_trend = []
    for m in range(1, 13):
        m_mult = 1.3 if m in [6, 7, 12] else 0.95
        f_val = int(total_flights * m_mult / (1 if month != "ALL" else 12))
        d_rate = delay_rate * (1.25 if m in [6, 7, 12] else 0.85)
        d_val = int(f_val * (d_rate / 100))
        flights_trend.append(f_val)
        delays_trend.append(d_val)
        
    if month != "ALL":
        months_labels = [f"Tháng {month}"]
        flights_trend = [total_flights]
        delays_trend = [total_delayed]

    response_data = {
        "mode": "MOCK",
        "role": user_role,
        "kpis": {
            "total_flights": total_flights,
            "total_delayed": total_delayed,
            "total_cancelled": total_cancelled,
            "avg_delay_minutes": avg_delay,
            "delay_rate": round(delay_rate, 1)
        },
        "delay_breakdown": {
            "carrier": c_delay,
            "weather": w_delay,
            "nas": n_delay,
            "security": s_delay,
            "late_aircraft": la_delay
        },
        "monthly_trend": {
            "labels": months_labels,
            "flights": flights_trend,
            "delays": delays_trend
        },
        "weather_impact": {
            "labels": ["Không mưa", "Mưa nhỏ (<5mm)", "Mưa lớn (>5mm)"],
            "delay_rates": [14.2, 22.5, 41.8]
        }
    }

    # Bảng chi tiết giả lập chỉ hiển thị cho Flight Tracker
    if user_role == "tracker":
        details_list = []
        carriers_db = {
            "AA": "American Airlines",
            "DL": "Delta Air Lines",
            "UA": "United Airlines",
            "WN": "Southwest Airlines",
            "B6": "JetBlue Airways",
            "AS": "Alaska Airlines"
        }
        active_carrier = carrier if carrier != "ALL" else random.choice(list(carriers_db.keys()))
        active_airport = airport if airport != "ALL" else "JFK"
        
        dest_airports = ["LAX", "SFO", "ORD", "MCO", "ATL"]
        
        for i in range(15):
            fl_num = random.randint(100, 9999)
            tail_num = f"N{random.randint(100, 999)}XX"
            # Giả lập mã hóa SHA-256 đuôi máy bay
            import hashlib
            masked_tail = hashlib.sha256(tail_num.encode()).hexdigest()[:24] + "..."
            
            dep_del = random.randint(-5, 120) if random.random() > 0.6 else random.randint(-8, 3)
            arr_del = dep_del + random.randint(-10, 15)
            
            details_list.append({
                "date_key": "2024-06-15",
                "carrier_name": carriers_db.get(active_carrier, "Unknown Airline"),
                "flight_number": fl_num,
                "origin_airport_key": active_airport,
                "dest_airport_key": random.choice(dest_airports),
                "masked_tail_number": masked_tail,
                "dep_delay": float(dep_del),
                "arr_delay": float(arr_del),
                "elevation_ft": float(random.randint(10, 5000))
            })
        response_data["details_table"] = details_list

    return response_data

if __name__ == "__main__":
    app.run(debug=True, port=5000)
