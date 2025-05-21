# Sử dụng Python 3.9
FROM python:3.9-slim

# Cài đặt thư viện hệ thống cần thiết (FFmpeg)
RUN apt-get update && apt-get install -y ffmpeg

# Cài đặt các thư viện Python từ requirements.txt
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Sao chép mã nguồn vào container
COPY . .

# Cung cấp thông tin về cổng mà ứng dụng sẽ chạy
EXPOSE 5000

# Chạy Flask app
CMD ["python", "app.py"]
