import os
import uuid
import requests
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Lấy tên miền từ biến môi trường (hoặc sử dụng giá trị mặc định nếu không có)
BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:5000')  # Sử dụng BASE_URL từ môi trường nếu có

STATIC_FOLDER = 'static/uploads'

@app.route('/convert-from-url', methods=['POST'])
def convert_from_url():
    video_url = request.json.get('url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    try:
        video_data = requests.get(video_url)
        video_data.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to download video from URL: {str(e)}"}), 400

    video_filename = f"{uuid.uuid4().hex}.mp4"
    input_path = os.path.join(STATIC_FOLDER, video_filename)
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    
    with open(input_path, 'wb') as f:
        f.write(video_data.content)

    output_filename = f"{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(STATIC_FOLDER, output_filename)

    command = ['ffmpeg', '-i', input_path, '-vn', '-acodec', 'libmp3lame', '-ar', '44100', '-ac', '2', '-ab', '192k', output_path]

    try:
        subprocess.run(command, check=True)
        return jsonify({
            "message": "Video converted to MP3 successfully",
            "output_url": f"{BASE_URL}/static/uploads/{output_filename}"  # Sử dụng BASE_URL từ môi trường
        }), 200
    except subprocess.CalledProcessError:
        return jsonify({"error": "Failed to convert video to MP3"}), 500
    finally:
        os.remove(input_path)

if __name__ == '__main__':
    # Flask sẽ lắng nghe trên tất cả các địa chỉ IP và cổng 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
