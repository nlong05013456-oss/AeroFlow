"""
inspect_data.py
Kiểm tra tất cả các file dữ liệu trong dự án CAP2.
Chạy từ thư mục gốc: python inspect_data.py
"""

import os
import pandas as pd

# ── màu terminal ──────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def ok(msg):    print(f"  {GREEN}✓ {msg}{RESET}")
def warn(msg):  print(f"  {YELLOW}⚠ {msg}{RESET}")
def err(msg):   print(f"  {RED}✗ {msg}{RESET}")
def info(msg):  print(f"    {msg}")

# ── đường dẫn ─────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "BTS Flights (Parquet)": os.path.join(BASE, "Data", "Flights", "us_flights_2024_all.parquet"),
    "OurAirports - airports": os.path.join(BASE, "Data", "OurAirports", "airports.csv"),
    "OurAirports - runways":  os.path.join(BASE, "Data", "OurAirports", "runways.csv"),
    "OurAirports - countries":os.path.join(BASE, "Data", "OurAirports", "countries.csv"),
    "OurAirports - regions":  os.path.join(BASE, "Data", "OurAirports", "regions.csv"),
    "OpenFlights - airlines": os.path.join(BASE, "Data", "OpenFlights", "airlines.dat.txt"),
    "OpenFlights - airports": os.path.join(BASE, "Data", "OpenFlights", "airports.dat.txt"),
    "OpenFlights - routes":   os.path.join(BASE, "Data", "OpenFlights", "routes.dat.txt"),
}

# OpenFlights không có header, khai báo tay
OPENFLIGHTS_COLS = {
    "airlines": ["airline_id","name","alias","iata","icao","callsign","country","active"],
    "airports": ["airport_id","name","city","country","iata","icao","lat","lon",
                 "altitude","timezone","dst","tz_db","type","source"],
    "routes":   ["airline","airline_id","src_airport","src_airport_id",
                 "dst_airport","dst_airport_id","codeshare","stops","equipment"],
}


def inspect_parquet(label, path):
    header(label)
    if not os.path.exists(path):
        err(f"File không tồn tại: {path}")
        return

    size_mb = os.path.getsize(path) / 1024 / 1024
    ok(f"File tồn tại  ({size_mb:.1f} MB)")

    try:
        df = pd.read_parquet(path)
    except Exception as e:
        err(f"Đọc file thất bại: {e}")
        return

    ok(f"Đọc thành công  →  {df.shape[0]:,} rows × {df.shape[1]} cols")

    # cột + kiểu
    info("\nCác cột:")
    for col in df.columns:
        info(f"  {col:<35} {str(df[col].dtype)}")

    # null
    null_counts = df.isnull().sum()
    null_cols   = null_counts[null_counts > 0]
    if null_cols.empty:
        ok("Không có giá trị null")
    else:
        warn(f"{len(null_cols)} cột có null:")
        for col, cnt in null_cols.items():
            pct = cnt / len(df) * 100
            info(f"  {col:<35} {cnt:>8,}  ({pct:.1f}%)")

    # sample
    info("\nSample (3 dòng đầu):")
    print(df.head(3).to_string(index=False))

    # delay columns nếu có
    delay_cols = [c for c in df.columns if "DELAY" in c.upper()]
    if delay_cols:
        ok(f"\nTìm thấy {len(delay_cols)} cột delay:")
        for c in delay_cols:
            info(f"  {c}")
        # thống kê delay
        if "ARR_DELAY" in df.columns:
            d = df["ARR_DELAY"].dropna()
            info(f"\n  ARR_DELAY stats:")
            info(f"    mean   = {d.mean():.1f} phút")
            info(f"    median = {d.median():.1f} phút")
            info(f"    max    = {d.max():.1f} phút")
            info(f"    % on-time (≤0) = {(d <= 0).mean()*100:.1f}%")


def inspect_csv(label, path, sep=",", header_row=0, names=None, key=None):
    header(label)
    if not os.path.exists(path):
        err(f"File không tồn tại: {path}")
        return

    size_kb = os.path.getsize(path) / 1024
    ok(f"File tồn tại  ({size_kb:.0f} KB)")

    try:
        df = pd.read_csv(path, sep=sep, header=header_row,
                         names=names, on_bad_lines="skip",
                         encoding="utf-8", low_memory=False)
    except Exception as e:
        err(f"Đọc file thất bại: {e}")
        return

    ok(f"Đọc thành công  →  {df.shape[0]:,} rows × {df.shape[1]} cols")

    info("\nCác cột:")
    for col in df.columns:
        info(f"  {col:<35} {str(df[col].dtype)}")

    null_counts = df.isnull().sum()
    null_cols   = null_counts[null_counts > 0]
    if null_cols.empty:
        ok("Không có giá trị null")
    else:
        warn(f"{len(null_cols)} cột có null:")
        for col, cnt in null_cols.items():
            pct = cnt / len(df) * 100
            info(f"  {col:<35} {cnt:>8,}  ({pct:.1f}%)")

    # duplicate key
    if key and key in df.columns:
        dupes = df[key].duplicated().sum()
        if dupes == 0:
            ok(f"Không có duplicate trên '{key}'")
        else:
            warn(f"{dupes:,} duplicate trên '{key}'")

    info("\nSample (3 dòng đầu):")
    print(df.head(3).to_string(index=False))


def check_joinability():
    """Kiểm tra xem các file có thể join với nhau không."""
    header("JOIN CHECK — IATA codes")

    try:
        flights   = pd.read_parquet(FILES["BTS Flights (Parquet)"])
        airports  = pd.read_csv(FILES["OurAirports - airports"], low_memory=False)
        of_airports = pd.read_csv(FILES["OpenFlights - airports"],
                                  header=None,
                                  names=OPENFLIGHTS_COLS["airports"],
                                  on_bad_lines="skip")

        # ORIGIN airports trong flights
        if "ORIGIN" in flights.columns:
            origins = set(flights["ORIGIN"].dropna().unique())
            iata_our = set(airports["iata_code"].dropna().unique())
            iata_of  = set(of_airports["iata"].dropna().str.strip().unique())

            matched_our = origins & iata_our
            matched_of  = origins & iata_of

            ok(f"Flights có {len(origins):,} ORIGIN airports duy nhất")
            ok(f"OurAirports  match: {len(matched_our):,}/{len(origins):,} "
               f"({len(matched_our)/len(origins)*100:.1f}%)")
            ok(f"OpenFlights  match: {len(matched_of):,}/{len(origins):,} "
               f"({len(matched_of)/len(origins)*100:.1f}%)")

            unmatched = origins - iata_our
            if unmatched:
                warn(f"Không match OurAirports: {sorted(unmatched)[:10]} ...")
        else:
            warn("Không tìm thấy cột ORIGIN trong flights")

    except Exception as e:
        err(f"Join check thất bại: {e}")


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{BOLD}CAP2 — Data Inspection Report{RESET}")
    print(f"Base path: {BASE}")

    # 1. BTS Flights
    inspect_parquet("BTS Flights (Parquet)", FILES["BTS Flights (Parquet)"])

    # 2. OurAirports
    inspect_csv("OurAirports — airports.csv",  FILES["OurAirports - airports"],  key="iata_code")
    inspect_csv("OurAirports — runways.csv",   FILES["OurAirports - runways"],   key="airport_ident")
    inspect_csv("OurAirports — countries.csv", FILES["OurAirports - countries"], key="code")
    inspect_csv("OurAirports — regions.csv",   FILES["OurAirports - regions"],   key="code")

    # 3. OpenFlights
    inspect_csv("OpenFlights — airlines.dat",
                FILES["OpenFlights - airlines"],
                header_row=None,
                names=OPENFLIGHTS_COLS["airlines"],
                key="iata")

    inspect_csv("OpenFlights — airports.dat",
                FILES["OpenFlights - airports"],
                header_row=None,
                names=OPENFLIGHTS_COLS["airports"],
                key="iata")

    inspect_csv("OpenFlights — routes.dat",
                FILES["OpenFlights - routes"],
                header_row=None,
                names=OPENFLIGHTS_COLS["routes"])

    # 4. Join check
    check_joinability()

    print(f"\n{BOLD}{GREEN}✓ Inspection hoàn tất!{RESET}\n")