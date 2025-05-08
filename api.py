from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from yt_dlp import YoutubeDL
import os
import requests

app = Flask(__name__)
CORS(app)  # CORS ayarları, istemci uygulamasından gelen istekleri kabul etmek için

# İndirme ilerlemesini göstermek için hook fonksiyonu
def my_hook(d):
    if d['status'] == 'downloading':
        print(f"İndirme %: {d['downloaded_bytes'] / d['total_bytes'] * 100:.2f}%")
    elif d['status'] == 'finished':
        print("İndirme tamamlandı!")

# Webhook URL'si (şu an kullanılmıyor, gerekirse gerçek bir URL ekleyin)
WEBHOOK_URL = None

# Webhook'a veri gönderen fonksiyon
def send_webhook_notification(message):
    if not WEBHOOK_URL:
        print("Webhook URL'si tanımlı değil.")
        return
    try:
        payload = {"status": "completed", "message": message}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print("Webhook başarıyla gönderildi!")
        else:
            print(f"Webhook gönderilemedi. Hata kodu: {response.status_code}")
    except Exception as e:
        print(f"Webhook gönderilirken hata oluştu: {e}")

# Sağlık kontrol endpoint'i
@app.route('/status')
def status():
    return jsonify({'status': 'OK'}), 200

# Ana sayfa
@app.route('/')
def home():
    return jsonify({'message': 'Video indirme API\'si çalışıyor!'}), 200

# Video indirme endpoint'i
@app.route('/download', methods=['GET', 'POST'])
def download_video():
    # GET veya POST ile URL al
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url')
    else:
        url = request.args.get('url')

    if not url:
        return jsonify({'error': 'URL boş olamaz'}), 400

    try:
        # İndirme seçenekleri
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'progress_hooks': [my_hook],
        }

        # "downloads" klasörünü oluştur
        os.makedirs('downloads', exist_ok=True)

        # Video indirme işlemi
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Webhook'a başarılı indirme bilgisi gönder
        send_webhook_notification("Video başarıyla indirildi.")

        # İndirilen dosyanın bilgilerini döndür
        file_size = os.path.getsize(file_path) / (1024 * 1024) if os.path.exists(file_path) else 0  # MB cinsinden
        return jsonify({
            'video': {
                'title': info.get('title', 'Bilinmeyen Başlık'),
                'size': f"{file_size:.2f} MB",
                'download_url': f"/downloads/{os.path.basename(file_path)}"
            }
        }), 200
    except Exception as e:
        send_webhook_notification(f"İndirme sırasında hata oluştu: {str(e)}")
        return jsonify({'error': f'Bir hata oluştu: {str(e)}'}), 500

# İndirilen dosyaları sunmak için endpoint
@app.route('/downloads/<path:filename>')
def serve_file(filename):
    try:
        return send_from_directory('downloads', filename)
    except FileNotFoundError:
        return jsonify({'error': 'Dosya bulunamadı'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
