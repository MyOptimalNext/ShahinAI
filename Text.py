from huggingface_hub import InferenceClient
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivymd.uix.card import MDCard
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock

class MessageCard(MDCard):
    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = dp(10)
        self.spacing = dp(5)
        self.md_bg_color = [0.9, 0.9, 1, 1] if is_user else [1, 0.9, 0.9, 1]
        self.radius = [dp(10)]
        
        # حساب الارتفاع المطلوب بناءً على طول النص
        label = MDLabel(
            text=text,
            size_hint_y=None,
            padding=[dp(10), dp(5)],
            halign='right' if is_user else 'left'
        )
        label.bind(texture_size=label.setter('size'))
        self.add_widget(label)
        # إضافة هامش إضافي
        self.height = label.height + dp(20)

class ChatApp(MDApp):
    def build(self):
        # تعيين النمط
        self.theme_cls.primary_palette = "Blue"
        Window.size = (400, 600)
        
        # إعداد واجهة المستخدم الرئيسية
        self.screen = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # إعداد منطقة المحادثة
        self.scrollview = ScrollView()
        self.chat_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=dp(10)
        )
        self.chat_box.bind(minimum_height=self.chat_box.setter('height'))
        self.scrollview.add_widget(self.chat_box)
        
        # إعداد منطقة الإدخال
        input_area = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )
        
        self.input_field = MDTextField(
            hint_text="أدخل سؤالك هنا",
            multiline=False,
            size_hint=(0.8, None),
            height=dp(40)
        )
        self.input_field.bind(on_text_validate=self.on_send)
        
        self.send_button = MDRaisedButton(
            text="إرسال",
            size_hint=(0.2, None),
            height=dp(40)
        )
        self.send_button.bind(on_press=self.on_send)
        
        input_area.add_widget(self.input_field)
        input_area.add_widget(self.send_button)
        
        # تجميع الواجهة
        self.screen.add_widget(self.scrollview)
        self.screen.add_widget(input_area)
        
        # إعداد المتغيرات
        self.messages = []
        self.client = InferenceClient(api_key="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")
        
        return self.screen
    
    def on_send(self, instance):
        user_input = self.input_field.text.strip()
        if not user_input:
            return
            
        if user_input.lower() == "exit":
            self.stop()
            return
        
        # تعطيل زر الإرسال وحقل الإدخال أثناء المعالجة
        self.send_button.disabled = True
        self.input_field.disabled = True
        
        # إضافة رسالة المستخدم إلى الواجهة
        self.add_message(user_input, is_user=True)
        
        # مسح حقل الإدخال
        self.input_field.text = ""
        
        # معالجة الرد في خلفية التطبيق
        Clock.schedule_once(lambda dt: self.process_response(user_input), 0)
    
    def process_response(self, user_input):
        try:
            # إضافة السؤال إلى تسلسل الرسائل
            self.messages.append({"role": "user", "content": user_input})
            
            # الحصول على الرد من النموذج
            completion = self.client.chat.completions.create(
                model="Qwen/Qwen2.5-Coder-32B-Instruct",
                messages=self.messages,
                max_tokens=500
            )
            
            # معالجة الرد
            assistant_reply = completion.choices[0].message['content']
            self.messages.append({"role": "assistant", "content": assistant_reply})
            
            # إضافة الرد إلى واجهة المستخدم
            Clock.schedule_once(lambda dt: self.add_message(assistant_reply, is_user=False), 0)
            
        except Exception as e:
            error_message = f"حدث خطأ: {str(e)}"
            Clock.schedule_once(lambda dt: self.add_message(error_message, is_user=False), 0)
            
        finally:
            # إعادة تفعيل عناصر التحكم
            Clock.schedule_once(lambda dt: self.enable_controls(), 0)
    
    def add_message(self, text, is_user=True):
        message_card = MessageCard(text, is_user)
        self.chat_box.add_widget(message_card)
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)
    
    def scroll_to_bottom(self):
        self.scrollview.scroll_to(self.chat_box.children[0])
    
    def enable_controls(self):
        self.send_button.disabled = False
        self.input_field.disabled = False
        self.input_field.focus = True

if __name__ == "__main__":
    ChatApp().run()
