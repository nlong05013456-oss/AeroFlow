# Dockerfile
# Sử dụng base image Python chính thức, gọn nhẹ
FROM python:3.9-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Thiết lập biến môi trường Python không ghi đè log và đệm
ENV PYTHONUNBUFFERED=1

# Copy file requirements trước để tận dụng cache Docker
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn dự án vào container
COPY . .

# Cloud Run yêu cầu ứng dụng lắng nghe trên cổng 8080 mặc định
EXPOSE 8080

# Chạy ứng dụng web server Flask thông qua gunicorn để đạt hiệu năng sản xuất (production-ready)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
