# Sử dụng image Python 3.12 slim
FROM python:3.12-slim

# Cài đặt dependencies hệ thống (nếu cần, ví dụ cho PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài gunicorn với quyền root trước
RUN pip install gunicorn

# Tạo user non-root để tăng bảo mật
RUN useradd -m myuser
USER myuser

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements.txt và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy các file cần thiết (có chọn lọc)
COPY . .

# Thiết lập biến môi trường
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Chạy Gunicorn với logging (dạng JSON array)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "0", "--log-level", "info", "index:app"]