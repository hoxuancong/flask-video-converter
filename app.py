import uuid
import os
import requests
from flask import Flask, request, jsonify, send_from_directory
import subprocess

app = Flask(__name__)

# Đảm bảo rằng FFmpeg đã được cài đặt và có sẵn trong PATH
FFMPEG_PATH = "ffmpeg"  # Thay đổi nếu FFmpeg không có trong PATH hệ thống

# Thư mục tĩnh để lưu tệp đã chuyển đổi
STATIC_FOLDER = 'static/uploads'

# Định nghĩa route để chuyển đổi video từ URL thành MP3
@app.route('/convert-from-url', methods=['POST'])
def convert_from_url():
    # Lấy URL video từ yêu cầu
    video_url = request.json.get('url')

    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    # Tải video từ URL về
    try:
        video_data = requests.get(video_url)
        video_data.raise_for_status()  # Kiểm tra nếu URL hợp lệ
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to download video from URL: {str(e)}"}), 400

    # Tạo tên ngẫu nhiên cho video bằng UUID
    video_filename = f"{uuid.uuid4().hex}.mp4"  # Tên video ngẫu nhiên (dưới dạng hex)
    
    # Lưu video vào tệp tạm thời
    input_path = os.path.join(STATIC_FOLDER, video_filename)
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    
    with open(input_path, 'wb') as f:
        f.write(video_data.content)

    # Tạo tên tệp đầu ra (định dạng MP3)
    output_filename = f"{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(STATIC_FOLDER, output_filename)

    # Gọi lệnh FFmpeg để chuyển đổi video MP4 thành MP3
    command = [FFMPEG_PATH, '-i', input_path, '-vn', '-acodec', 'libmp3lame', '-ar', '44100', '-ac', '2', '-ab', '192k', output_path]

    try:
        subprocess.run(command, check=True)
        # Trả về URL của tệp MP3 đã chuyển đổi
        return jsonify({
            "message": "Video converted to MP3 successfully",
            "output_url": f"http://127.0.0.1:5000/static/uploads/{output_filename}"
        }), 200
    except subprocess.CalledProcessError:
        return jsonify({"error": "Failed to convert video to MP3"}), 500
    finally:
        # Xóa tệp video tạm thời sau khi hoàn tất
        os.remove(input_path)

# Khởi động Flask
if __name__ == '__main__':
    app.run(debug=True)
