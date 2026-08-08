import holidays
import pandas as pd
import os

# tạo thư mục nếu chưa có
os.makedirs("Data/Holidays", exist_ok=True)

us_holidays = holidays.US(years=[2024])

data = []

for d, name in us_holidays.items():
    data.append([d, name])

df = pd.DataFrame(
    data,
    columns=["date", "holiday_name"]
)

df.to_csv(
    "Data/Holidays/us_holidays_2024.csv",
    index=False
)

print("Done!")