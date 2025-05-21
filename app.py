import os
import uuid
import requests
from flask import Flask, request, jsonify
import subprocess

# Tạo ứng dụng Flask
app = Flask(__name__)

# Lấy BASE_URL từ biến môi trường Coolify
BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:5000')  # Mặc định nếu không có biến môi trường

# Lấy SECRET_KEY từ biến môi trường Coolify (hoặc giá trị mặc định nếu không có)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# Thư mục lưu video đã tải lên
STATIC_FOLDER = 'static/uploads'

@app.route('/convert-from-url', methods=['POST'])
def convert_from_url():
    video_url = request.json.get('url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    try:
        # Tải video từ URL
        video_data = requests.get(video_url)
        video_data.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to download video from URL: {str(e)}"}), 400

    # Tạo tên tệp video ngẫu nhiên
    video_filename = f"{uuid.uuid4().hex}.mp4"
    input_path = os.path.join(STATIC_FOLDER, video_filename)
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    
    # Lưu video vào thư mục tạm
    with open(input_path, 'wb') as f:
        f.write(video_data.content)

    # Tạo tên tệp MP3 đầu ra ngẫu nhiên
    output_filename = f"{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(STATIC_FOLDER, output_filename)

    # Chạy lệnh ffmpeg để chuyển đổi video thành MP3
    command = ['ffmpeg', '-i', input_path, '-vn', '-acodec', 'libmp3lame', '-ar', '44100', '-ac', '2', '-ab', '192k', output_path]

    try:
        subprocess.run(command, check=True)
        # Trả về URL của tệp MP3 đã chuyển đổi
        return jsonify({
            "message": "Video converted to MP3 successfully",
            "output_url": f"{BASE_URL}/static/uploads/{output_filename}"  # Sử dụng BASE_URL từ biến môi trường
        }), 200
    except subprocess.CalledProcessError:
        return jsonify({"error": "Failed to convert video to MP3"}), 500
    finally:
        os.remove(input_path)

# Chạy ứng dụng Flask
if __name__ == '__main__':
    # Flask sẽ lắng nghe trên mọi địa chỉ IP (0.0.0.0) trong môi trường sản xuất trên Coolify
    app.run(debug=True, host='0.0.0.0', port=5000)
