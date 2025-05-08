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
        
        # Logger oluşturma
        self.logger = KivyLogger(self.update_status)
        
        # Video URL girişi için TextInput
        self.url_input = TextInput(
            hint_text='🎬 Video URL girin',
            multiline=False,
            size_hint_y=0.1
        )
        self.add_widget(self.url_input)
        
        # Durum mesajı göstermek için Label
        self.status_label = Label(
            text='Uygulama hazır. Lütfen bir video URL\'si girin.',
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.status_label.bind(texture_size=self.status_label.setter('size'))
        
        # Durum etiketini ScrollView içine yerleştirme
        self.scroll_view = ScrollView(size_hint_y=0.7)
        self.scroll_view.add_widget(self.status_label)
        self.add_widget(self.scroll_view)
        
        # İndirme butonu
        self.download_button = Button(
            text='📥 İndir',
            size_hint_y=0.1,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.download_button.bind(on_press=self.start_download)
        self.add_widget(self.download_button)
        
        # Requests için otomatik yeniden deneme ayarı
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        
        # Sunucu bağlantısını test et
        threading.Thread(target=self.test_api_connection, daemon=True).start()

    def test_api_connection(self):
        """Uygulama başlangıcında API sunucusuna bağlantıyı test eder"""
        try:
<<<<<<< HEAD
            response = self.session.get(
                "https://web-production-f04a6.up.railway.app/status",
=======
            # Önce domain çözümlemeyi test et
            api_domain = "web-production-f04a6.up.railway.app"
            socket.gethostbyname(api_domain)
            
            # Sonra API'ye basit bir istek gönder
            test_response = requests.get(
                f"https://{api_domain}/status",
>>>>>>> 448307edfb356cac5d4fa8bc0353b3dfe8c90cad
                timeout=10
            )
            if response.status_code == 200:
                self.update_status("✅ API sunucusuna bağlantı başarılı.")
            else:
                self.update_status(f"⚠️ API sunucusu yanıt verdi ancak durum kodu: {response.status_code}")
        except requests.exceptions.SSLError:
            self.update_status("❌ SSL hatası: Sunucu sertifikası doğrulanamadı.")
        except requests.exceptions.ConnectionError:
            self.update_status("❌ API sunucusuna bağlantı kurulamadı. Sunucu çalışmıyor olabilir.")
        except requests.exceptions.Timeout:
            self.update_status("❌ API sunucusu yanıt vermiyor (zaman aşımı).")
        except requests.exceptions.RequestException as e:
            self.update_status(f"❌ API bağlantı testi sırasında hata: {str(e)}")

    def start_download(self, instance):
        """İndirme işlemini başlatır"""
        url = self.url_input.text.strip()
        if not url:
            self.update_status('❗ Lütfen geçerli bir URL girin.')
            return
        
        self.update_status('⏳ İndirme başlatılıyor...')
        self.download_button.text = '⏳ İndiriliyor...'
        self.download_button.disabled = True
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def update_status(self, message):
        """UI thread'inde durum mesajını günceller"""
        def update_text(dt):
            self.status_label.text = message
            self.scroll_view.scroll_y = 0
        Clock.schedule_once(update_text, 0)

    def download_video(self, url):
        """Video indirme işlemini gerçekleştirir"""
        try:
<<<<<<< HEAD
            api_url = "https://web-production-f04a6.up.railway.app/download"
=======
            # Önce domain çözümlemeyi dene
            api_domain = "web-production-f04a6.up.railway.app"
            try:
                socket.gethostbyname(api_domain)
            except socket.gaierror:
                self.update_status("❌ API sunucusu bulunamadı. İnternet bağlantınızı kontrol edin.")
                Clock.schedule_once(lambda dt: setattr(self.download_button, 'disabled', False), 0)
                return
            
            # API isteği için iki farklı yöntem dene
            api_url = f"https://{api_domain}/download"
>>>>>>> 448307edfb356cac5d4fa8bc0353b3dfe8c90cad
            
            # 1. Yöntem: POST JSON
            headers = {'Content-Type': 'application/json'}
            data = json.dumps({'url': url})
            
            self.update_status("🔄 API'ye bağlanılıyor... (POST JSON)")
            try:
                response = self.session.post(
                    api_url,
                    headers=headers,
                    data=data,
                    timeout=30
                )
                self.process_api_response(response)
                return
                
            except requests.exceptions.RequestException as e:
                self.update_status(f"⚠️ POST JSON yöntemi başarısız oldu, GET yöntemi deneniyor...\nHata: {str(e)}")
            
            # 2. Yöntem: GET Parametreler
            self.update_status("🔄 API'ye bağlanılıyor... (GET)")
            response = self.session.get(
                api_url,
                params={'url': url},
                timeout=30
            )
            self.process_api_response(response)
            
        except requests.exceptions.SSLError as e:
            self.update_status(f"❌ SSL hatası: Sunucu sertifikası doğrulanamadı.\n{str(e)}")
        except requests.exceptions.ConnectionError as e:
            self.update_status(f"❌ Bağlantı hatası: Sunucuya ulaşılamadı.\n{str(e)}")
        except requests.exceptions.Timeout as e:
            self.update_status(f"❌ Zaman aşımı: Sunucu yanıt vermedi.\n{str(e)}")
        except requests.exceptions.RequestException as e:
            self.update_status(f"❌ API isteği başarısız oldu:\n{str(e)}")
        except json.JSONDecodeError:
            self.update_status("❌ API yanıtı geçerli bir JSON formatında değil.")
        except Exception as e:
            self.update_status(f"❓ Beklenmeyen bir hata oluştu:\n{str(e)}")
        finally:
            Clock.schedule_once(lambda dt: self._reset_button(), 0)

    def _reset_button(self):
        """Butonu sıfırlar"""
        self.download_button.text = '📥 İndir'
        self.download_button.disabled = False

    def process_api_response(self, response):
        """API yanıtını işler"""
        if response.status_code == 200:
            try:
                result = response.json()
                video_info = result.get('video', {})
                title = video_info.get('title', 'Bilinmeyen Başlık')
                size = video_info.get('size', 'Bilinmeyen Boyut')
                download_url = video_info.get('download_url')
                
                if download_url:
                    self.download_file(download_url, title)
                self.update_status(f"✅ İndirme başarılı!\n\n📋 Başlık: {title}\n💾 Boyut: {size}")
            except json.JSONDecodeError:
                self.update_status("✅ İndirme başarılı ancak video bilgileri alınamadı.")
        else:
            try:
                error_message = response.json().get("error", "Bilinmeyen bir hata oluştu.")
            except:
                error_message = f"HTTP Durum Kodu: {response.status_code}"
            self.update_status(f"🚫 İndirme başarısız:\n{error_message}")

    def download_file(self, url, title):
        """Videoyu cihaza indirir ve kaydeder"""
        try:
            response = self.session.get(url, stream=True, timeout=60)
            if response.status_code == 200:
                if platform == 'android':
                    from jnius import autoclass
                    Environment = autoclass('android.os.Environment')
                    download_dir = Environment.getExternalStoragePublicDirectory(
                        Environment.DIRECTORY_DOWNLOADS
                    ).getAbsolutePath()
                else:
                    download_dir = os.path.expanduser("~/Downloads")
                
                # Güvenli dosya adı oluştur
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                file_path = os.path.join(download_dir, f"{safe_title}.mp4")
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                self.update_status(f"💾 Video kaydedildi: {file_path}")
            else:
                self.update_status(f"❌ Video indirilemedi: HTTP {response.status_code}")
        except Exception as e:
            self.update_status(f"❌ Video indirme hatası: {str(e)}")
            logging.error(f"Video indirme hatası: {str(e)}")

class VideoApp(App):
    def build(self):
        return Downloader()
    
    def on_start(self):
        """Uygulama başlangıcında çalışacak kod"""
        logging.info("Uygulama başlatıldı.")

if __name__ == '__main__':
    VideoApp().run()
