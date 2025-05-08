from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

# İndirme ilerlemesini göstermek için hook fonksiyonu
def my_hook(d):
    if d['status'] == 'downloading':
        print(f"İndirme %: {d['downloaded_bytes'] / d['total_bytes'] * 100:.2f}%")

# Ana sayfa
@app.route('/')
def home():
    return "Video indirme API'si çalışıyor!"

# Video indirme endpoint'i
@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL boş olamaz'}), 400

    try:
        # İndirme seçenekleri
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'progress_hooks': [my_hook],  # İlerleme bilgisini al
        }

        os.makedirs('downloads', exist_ok=True)

        # Video indirme işlemi
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({'message': 'İndirme başarılı'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Railway için PORT çevre değişkenini al
    port = int(os.environ.get("PORT", 8080))  # Railway için önemli
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Railway için önemli
    app.run(host='0.0.0.0', port=port, debug=True)