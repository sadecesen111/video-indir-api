from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import threading
import requests  # Flask API ile HTTP istekleri için
import json

class KivyLogger:
    def __init__(self, update_label_func):
        self.update_label = update_label_func

    def debug(self, msg):
        pass  # Gerekirse log gösterilebilir

    def warning(self, msg):
        self.update_label(f'⚠️ Uyarı: {msg}')

    def error(self, msg):
        self.update_label(f'❌ Hata: {msg}')


class Downloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # Video URL girişi için TextInput
        self.url_input = TextInput(hint_text='🎬 Video URL girin', size_hint_y=0.1)
        self.add_widget(self.url_input)

        # Durum mesajı göstermek için Label
        self.status_label = Label(
            text='',
            size_hint_y=None,
            text_size=(self.width, None),
            halign='left',
            valign='top'
        )
        self.status_label.bind(texture_size=self.status_label.setter('size'))

        # Durum etiketini ScrollView içine yerleştirme
        self.scroll_view = ScrollView(size_hint_y=0.5)
        self.scroll_view.add_widget(self.status_label)
        self.add_widget(self.scroll_view)

        # İndirme butonu
        self.download_button = Button(text='📥 İndir', size_hint_y=0.1)
        self.download_button.bind(on_press=self.start_download)
        self.add_widget(self.download_button)

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status('❗ Lütfen geçerli bir URL girin.')
            return

        self.update_status('⏳ İndirme başlatılıyor...')
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def update_status(self, message):
        # Kivy UI thread'inde güncelleme yapmak için Clock.schedule_once kullanıyoruz
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', message), 0)

    def download_video(self, url):
        # Flask API'ye video indirme isteği gönderme
        api_url = 'https://video-indirme-api-production-566f.up.railway.app/download'  # Güncellenmiş URL
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({'url': url})

        try:
            response = requests.post(api_url, headers=headers, data=data)
            if response.status_code == 200:
                # Başarılı indirme durumu
                self.update_status('✅ Video başarıyla indirildi!')
            else:
                # Hata durumunda gelen mesajı göster
                error_message = response.json().get("error", "Bilinmeyen bir hata oluştu.")
                self.update_status(f'🚫 Hata oluştu:\n{error_message}')
        except requests.exceptions.RequestException as e:
            # API bağlantı hatası durumunda kullanıcıya bilgi verme
            self.update_status(f'❌ API bağlantı hatası:\n{str(e)}')


class VideoApp(App):
    def build(self):
        return Downloader()


if __name__ == '__main__':
    VideoApp().run()
