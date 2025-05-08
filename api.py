from flask import Flask, request, jsonify
from flask_cors import CORS
from yt_dlp import YoutubeDL
import os
import requests

app = Flask(__name__)
CORS(app)  # CORS ayarları, uygulamanızın isteklerini kabul etmek için

# İndirme ilerlemesini göstermek için hook fonksiyonu
def my_hook(d):
    if d['status'] == 'downloading':
        print(f"İndirme %: {d['downloaded_bytes'] / d['total_bytes'] * 100:.2f}%")
    elif d['status'] == 'finished':
        print("İndirme tamamlandı!")

# Webhook URL'si (dış servis için, şu an kullanılmıyor)
WEBHOOK_URL = None  # Gerekirse gerçek bir webhook URL'si ekleyin

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
