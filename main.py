from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import threading
import requests
import json
import socket


class KivyLogger:
    def __init__(self, update_label_func):
        self.update_label = update_label_func
    
    def debug(self, msg):
        self.update_label(f'🔍 Debug: {msg}')
    
    def warning(self, msg):
        self.update_label(f'⚠️ Uyarı: {msg}')
    
    def error(self, msg):
        self.update_label(f'❌ Hata: {msg}')


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
        
        # Sunucu bağlantısını test et
        threading.Thread(target=self.test_api_connection, daemon=True).start()

    def test_api_connection(self):
        """Uygulama başlangıcında API sunucusuna bağlantıyı test eder"""
        try:
            # Önce domain çözümlemeyi test et
            api_domain = "66.33.22.4"
            socket.gethostbyname(api_domain)
            
            # Sonra API'ye basit bir istek gönder
            test_response = requests.get(
                f"https://{api_domain}/status",
                timeout=10
            )
            
            if test_response.status_code == 200:
                self.update_status("✅ API sunucusuna bağlantı başarılı.")
            else:
                self.update_status(f"⚠️ API sunucusu yanıt verdi ancak durum kodu: {test_response.status_code}")
                
        except socket.gaierror:
            self.update_status("⚠️ API sunucu adresi çözümlenemedi. Lütfen internet bağlantınızı kontrol edin.")
        except requests.exceptions.ConnectionError:
            self.update_status("⚠️ API sunucusuna bağlantı kurulamadı. Sunucu çalışmıyor olabilir.")
        except requests.exceptions.Timeout:
            self.update_status("⚠️ API sunucusu yanıt vermiyor (zaman aşımı).")
        except Exception as e:
            self.update_status(f"⚠️ API bağlantı testi sırasında hata: {str(e)}")

    def start_download(self, instance):
        """İndirme işlemini başlatır"""
        url = self.url_input.text.strip()
        if not url:
            self.update_status('❗ Lütfen geçerli bir URL girin.')
            return
        
        self.update_status('⏳ İndirme başlatılıyor...')
        self.download_button.disabled = True
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def update_status(self, message):
        """UI thread'inde durum mesajını günceller"""
        def update_text(dt):
            self.status_label.text = message
            # ScrollView'ı otomatik olarak aşağı kaydır
            self.scroll_view.scroll_y = 0
        Clock.schedule_once(update_text, 0)

    def download_video(self, url):
        """Video indirme işlemini gerçekleştirir"""
        try:
            # Önce domain çözümlemeyi dene
            api_domain = "video-indirme-api-production-566f.up.railway.app"
            try:
                socket.gethostbyname(api_domain)
            except socket.gaierror:
                self.update_status("❌ API sunucusu bulunamadı. İnternet bağlantınızı kontrol edin.")
                Clock.schedule_once(lambda dt: setattr(self.download_button, 'disabled', False), 0)
                return
            
            # API isteği için iki farklı yöntem dene
            api_url = f"https://{api_domain}/download"
            
            # 1. Yöntem: POST JSON
            headers = {'Content-Type': 'application/json'}
            data = json.dumps({'url': url})
            
            self.update_status("🔄 API'ye bağlanılıyor... (POST JSON)")
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    data=data,
                    timeout=30
                )
                
                # Yanıt işleme
                self.process_api_response(response)
                return
                
            except (requests.exceptions.RequestException, Exception) as e:
                self.update_status(f"⚠️ POST JSON yöntemi başarısız oldu, GET yöntemi deneniyor...\nHata: {str(e)}")
            
            # 2. Yöntem: GET Parametreler
            self.update_status("🔄 API'ye bağlanılıyor... (GET)")
            response = requests.get(
                api_url,
                params={'url': url},
                timeout=30
            )
            
            # Yanıt işleme
            self.process_api_response(response)
            
        except requests.exceptions.ConnectionError as e:
            self.update_status(f"❌ Bağlantı hatası:\n{str(e)}\n\nLütfen internet bağlantınızı kontrol edin.")
        except requests.exceptions.Timeout:
            self.update_status("⏱️ Bağlantı zaman aşımına uğradı. Lütfen daha sonra tekrar deneyin.")
        except requests.exceptions.RequestException as e:
            self.update_status(f"❌ API isteği başarısız oldu:\n{str(e)}")
        except json.JSONDecodeError:
            self.update_status("❌ API yanıtı geçerli bir JSON formatında değil.")
        except Exception as e:
            self.update_status(f"❓ Beklenmeyen bir hata oluştu:\n{str(e)}")
        finally:
            # Her durumda butonu tekrar etkinleştir
            Clock.schedule_once(lambda dt: setattr(self.download_button, 'disabled', False), 0)

    def process_api_response(self, response):
        """API yanıtını işler"""
        if response.status_code == 200:
            try:
                result = response.json()
                video_info = result.get('video', {})
                title = video_info.get('title', 'Bilinmeyen Başlık')
                size = video_info.get('size', 'Bilinmeyen Boyut')
                self.update_status(f"✅ İndirme başarılı!\n\n📋 Başlık: {title}\n💾 Boyut: {size}")
            except json.JSONDecodeError:
                self.update_status("✅ İndirme başarılı ancak video bilgileri alınamadı.")
        else:
            try:
                error_message = response.json().get("error", "Bilinmeyen bir hata oluştu.")
            except:
                error_message = f"HTTP Durum Kodu: {response.status_code}"
            
            self.update_status(f"🚫 İndirme başarısız:\n{error_message}")


class VideoApp(App):
    def build(self):
        return Downloader()
    
    def on_start(self):
        """Uygulama başlangıcında çalışacak kod"""
        pass


if __name__ == '__main__':
    VideoApp().run()