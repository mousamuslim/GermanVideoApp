import os
import time
import subprocess
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

class VideoApp(App):
    def build(self):
        self.title = "German Text to Video"
        root = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # 1. الكلمة الألمانية
        layout.add_widget(Label(text="الكلمة الألمانية (German Word):", size_hint_y=None, height=30))
        self.txt_word = TextInput(text="die Zeit", multiline=False, size_hint_y=None, height=45)
        layout.add_widget(self.txt_word)

        # 2. معناها بالعربية
        layout.add_widget(Label(text="معناها بالعربية (Meaning):", size_hint_y=None, height=30))
        self.txt_meaning = TextInput(text="الوقت", multiline=False, size_hint_y=None, height=45)
        layout.add_widget(self.txt_meaning)

        # 3. مثال عليها
        layout.add_widget(Label(text="مثال عليها (Example):", size_hint_y=None, height=30))
        self.txt_example = TextInput(text="Ich habe keine Zeit.", multiline=True, size_hint_y=None, height=70)
        layout.add_widget(self.txt_example)

        # 4. ترجمة المثال
        layout.add_widget(Label(text="ترجمة المثال (Translation):", size_hint_y=None, height=30))
        self.txt_ex_trans = TextInput(text="ليس لدي وقت.", multiline=True, size_hint_y=None, height=70)
        layout.add_widget(self.txt_ex_trans)

        self.btn = Button(text="توليد الفيديو والصوت", size_hint_y=None, height=55, background_color=(0.1, 0.6, 0.3, 1))
        self.btn.bind(on_press=self.start_process)
        layout.add_widget(self.btn)

        self.lbl_status = Label(text="جاهز للإدخال", size_hint_y=None, height=40)
        layout.add_widget(self.lbl_status)

        root.add_widget(layout)
        return root

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.lbl_status, 'text', text))

    def start_process(self, instance):
        self.btn.disabled = True
        self.update_status("جاري إعداد وإنشاء المقطع...")
        threading.Thread(target=self.generate).start()

    def reshape_text(self, text):
        return get_display(arabic_reshaper.reshape(text))

    def generate(self):
        try:
            w_de = self.txt_word.text.strip()
            m_ar = self.txt_meaning.text.strip()
            e_de = self.txt_example.text.strip()
            e_ar = self.txt_ex_trans.text.strip()

            tts_word = gTTS(text=w_de, lang='de')
            tts_word.save("w.mp3")

            tts_meaning = gTTS(text=m_ar, lang='ar')
            tts_meaning.save("m.mp3")

            tts_ex_de = gTTS(text=e_de, lang='de')
            tts_ex_de.save("ed.mp3")

            tts_ex_ar = gTTS(text=e_ar, lang='ar')
            tts_ex_ar.save("ea.mp3")

            subprocess.run("ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 0.8 s.mp3", shell=True)

            with open("list.txt", "w") as f:
                for _ in range(3):
                    f.write("file 'w.mp3'\nfile 's.mp3'\n")
                f.write("file 'm.mp3'\nfile 's.mp3'\n")
                for _ in range(3):
                    f.write("file 'ed.mp3'\nfile 's.mp3'\n")
                f.write("file 'ea.mp3'\n")

            subprocess.run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy full.mp3", shell=True)

            w, h = 1080, 1920
            img = Image.new("RGB", (w, h), color=(25, 30, 42))
            draw = ImageDraw.Draw(img)

            try:
                font_title = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 40)
                font_body = ImageFont.truetype("/system/fonts/NotoNaskhArabic-Regular.ttf", 60)
            except:
                font_title = font_body = ImageFont.load_default()

            draw.text((w // 2, 350), "--- الكلمة الألمانية ---", fill=(160, 170, 185), font=font_title, anchor="mm")
            draw.text((w // 2, 450), w_de, fill=(255, 215, 0), font=font_body, anchor="mm")

            draw.text((w // 2, 650), self.reshape_text("--- المعنى ---"), fill=(160, 170, 185), font=font_title, anchor="mm")
            draw.text((w // 2, 750), self.reshape_text(m_ar), fill=(255, 255, 255), font=font_body, anchor="mm")

            draw.line([(150, 900), (w - 150, 900)], fill=(70, 80, 100), width=4)

            draw.text((w // 2, 1050), "--- المثال ---", fill=(160, 170, 185), font=font_title, anchor="mm")
            draw.text((w // 2, 1170), e_de, fill=(100, 220, 220), font=font_body, anchor="mm")

            draw.text((w // 2, 1370), self.reshape_text("--- الترجمة ---"), fill=(160, 170, 185), font=font_title, anchor="mm")
            draw.text((w // 2, 1490), self.reshape_text(e_ar), fill=(255, 255, 255), font=font_body, anchor="mm")

            img.save("frame.png")

            out_file = f"/sdcard/Download/video_{int(time.time())}.mp4"
            cmd = f"ffmpeg -y -loop 1 -i frame.png -i full.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest {out_file}"
            subprocess.run(cmd, shell=True)

            self.update_status(f"تم بنجاح! تم الحفظ في التنزيلات:\n{out_file}")
        except Exception as err:
            self.update_status(f"حدث خطأ: {err}")
        finally:
            Clock.schedule_once(lambda dt: setattr(self.btn, 'disabled', False))

if __name__ == "__main__":
    VideoApp().run()
