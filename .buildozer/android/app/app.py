from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

# Video indirme işlevi
@app.route('/video/download', methods=['POST'])
def download_video():
    # JSON gövdesinde 'url' parametresini alın
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "Video URL'si belirtilmelidir."}), 400

    # Video indirme ayarları
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',  # Video çıktısı için şablon
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Çıktıyı MP4 formatında al
        }],
    }

    try:
        # yt-dlp ile video indirme
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({"message": "Video başarıyla indirildi!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API çalışmaya başladığında aşağıdaki portta dinlemeye başlar
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

