import os
from flask import Flask, request, jsonify
import youtube_dl
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sağlık kontrolü endpoint'i ekleyin
@app.route('/status')
def status():
    return jsonify({"status": "ok"})

@app.route('/download', methods=['GET', 'POST'])
def download_video():
    try:
        # POST ve GET isteklerini destekle
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                url = data.get('url')
            else:
                url = request.form.get('url')
        else:  # GET isteği
            url = request.args.get('url')
        
        if not url:
            return jsonify({"error": "URL parametresi eksik"}), 400
            
        ydl_opts = {
            'format': 'best',
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_info = {
                'title': info.get('title', 'Unknown'),
                'size': f"{info.get('filesize', 0) / (1024 * 1024):.2f} MB",
                'filename': info.get('filename', 'Unknown')
            }
            
        return jsonify({"success": True, "video": video_info})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # PORT değişkenini Railway'den al
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
