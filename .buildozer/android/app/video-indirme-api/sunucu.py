from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL boş olamaz'}), 400

    try:
        # Video ve ses için en iyi formatları seçiyoruz
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # En iyi video ve ses kalitesi
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # Dosya adını video başlığıyla kaydet
            'merge_output_format': 'mp4',  # Çıktı formatını mp4 olarak ayarla
        }

        # 'downloads' klasörünün yoksa oluşturulmasını sağlıyoruz
        os.makedirs('downloads', exist_ok=True)

        # Video indirme işlemi
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({'message': 'İndirme başarılı'}), 200
    except Exception as e:
        return jsonify({'error': f'İndirme sırasında hata oluştu: {str(e)}'}), 500

if __name__ == '__main__':
    # PORT ortam değişkeni varsa onu kullan, yoksa 5000 portunu kullan
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
