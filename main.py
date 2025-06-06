from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import os
import logging
from kivy.utils import platform

# Android izinlerini iste (platform kontrolü aşağıda yapılır)
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE
    ])

# Loglama ayarları
logging.basicConfig(filename='app.log', level=logging.DEBUG)

class KivyLogger:
    def __init__(self, update_label_func):
        self.update_label = update_label_func

    def debug(self, msg):
        self.update_label(f'🔍 Debug: {msg}')
        logging.debug(msg)

    def warning(self, msg):
        self.update_label(f'⚠️ Uyarı: {msg}')
        logging.warning(msg)

    def error(self, msg):
        self.update_label(f'❌ Hata: {msg}')
        logging.error(msg)

class Downloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.logger = KivyLogger(self.update_status)

        self.url_input = TextInput(
            hint_text='🎮 Video URL girin',
            multiline=False,
            size_hint_y=0.1
        )
        self.add_widget(self.url_input)

        self.status_label = Label(
            text='Uygulama hazır. Lütfen bir video URL\'si girin.',
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.status_label.bind(texture_size=self.status_label.setter('size'))

        self.scroll_view = ScrollView(size_hint_y=0.7)
        self.scroll_view.add_widget(self.status_label)
        self.add_widget(self.scroll_view)

        self.download_button = Button(
            text='📅 İndir',
            size_hint_y=0.1,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.download_button.bind(on_press=self.start_download)
        self.add_widget(self.download_button)

        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        threading.Thread(target=self.test_api_connection, daemon=True).start()

    def test_api_connection(self):
        try:
            response = self.session.get("https://web-production-f04a6.up.railway.app/status", timeout=10)
            if response.status_code == 200:
                self.update_status("✅ API sunucusuna bağlantı başarılı.")
            else:
                self.update_status(f"⚠️ API sunucusu yanıt verdi ancak durum kodu: {response.status_code}")
        except Exception as e:
            self.update_status(f"❌ API bağlantı hatası: {str(e)}")

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status('❗ Lütfen geçerli bir URL girin.')
            return

        self.update_status('⏳ İndirme başlatılıyor...')
        self.download_button.text = '⏳ İndiriliyor...'
        self.download_button.disabled = True
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def update_status(self, message):
        def update_text(dt):
            self.status_label.text = message
            self.scroll_view.scroll_y = 0
        Clock.schedule_once(update_text, 0)

    def download_video(self, url):
        try:
            api_url = "https://web-production-f04a6.up.railway.app/download"
            headers = {'Content-Type': 'application/json'}
            data = json.dumps({'url': url})

            self.update_status("🔄 API'ye bağlanılıyor... (POST JSON)")
            try:
                response = self.session.post(api_url, headers=headers, data=data, timeout=30)
                self.process_api_response(response)
                return
            except requests.exceptions.RequestException as e:
                self.update_status(f"⚠️ POST JSON yöntemi başarısız oldu, GET yöntemi deneniyor...\nHata: {str(e)}")

            self.update_status("🔄 API'ye bağlanılıyor... (GET)")
            response = self.session.get(api_url, params={'url': url}, timeout=30)
            self.process_api_response(response)

        except Exception as e:
            self.update_status(f"❌ Hata oluştu: {str(e)}")
        finally:
            Clock.schedule_once(lambda dt: self._reset_button(), 0)

    def _reset_button(self):
        self.download_button.text = '📅 İndir'
        self.download_button.disabled = False

    def process_api_response(self, response):
        if response.status_code == 200:
            try:
                result = response.json()
                video_info = result.get('video', {})
                title = video_info.get('title', 'Bilinmeyen Başlık')
                size = video_info.get('size', 'Bilinmeyen Boyut')
                download_url = video_info.get('download_url')

                if download_url:
                    self.download_file(download_url, title)
                self.update_status(f"✅ İndirme başarılı!\n\n📋 Başlık: {title}\n📂 Boyut: {size}")
            except json.JSONDecodeError:
                self.update_status("✅ İndirme başarılı ancak video bilgileri alınamadı.")
        else:
            try:
                error_message = response.json().get("error", "Bilinmeyen bir hata oluştu.")
            except:
                error_message = f"HTTP Durum Kodu: {response.status_code}"
            self.update_status(f"🚫 İndirme başarısız:\n{error_message}")

    def download_file(self, url, title):
        try:
            response = self.session.get(url, stream=True, timeout=60)
            if response.status_code == 200:
                if platform == 'android':
                    from android.storage import primary_external_storage_path
                    from jnius import autoclass, cast
                    from android import activity

                    download_dir = os.path.join(primary_external_storage_path(), "Download")
                else:
                    download_dir = os.path.expanduser("~/Downloads")

                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)

                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                file_path = os.path.join(download_dir, f"{safe_title}.mp4")

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                self.update_status(f"📂 Video kaydedildi: {file_path}")

                # Android galeriye bildir
                if platform == 'android':
                    MediaScannerConnection = autoclass('android.media.MediaScannerConnection')
                    MediaScannerConnection.scanFile(
                        cast('android.content.Context', autoclass('org.kivy.android.PythonActivity').mActivity),
                        [file_path],
                        None,
                        None
                    )
                    self.update_status("✅ Video galeriye eklendi.")
            else:
                self.update_status(f"❌ Video indirilemedi: HTTP {response.status_code}")
        except Exception as e:
            self.update_status(f"❌ Video indirme hatası: {str(e)}")
            logging.error(f"Video indirme hatası: {str(e)}")

class VideoApp(App):
    def build(self):
        return Downloader()

    def on_start(self):
        logging.info("Uygulama başlatıldı.")
        if platform == 'android':
            def callback(permissions, grants):
                if all(grants):
                    print("✔️ Tüm izinler verildi.")
                    logging.info("Android izinleri alındı.")
                else:
                    print("❌ İzinler reddedildi.")
                    logging.warning("Bazı Android izinleri reddedildi.")
                    from kivy.uix.popup import Popup
                    popup = Popup(title='İzin Gerekli',
                                  content=Label(text='Lütfen dosya indirme için gerekli izinlere onay verin.'),
                                  size_hint=(0.8, 0.3))
                    popup.open()

            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ], callback)

if __name__ == '__main__':
    VideoApp().run()
