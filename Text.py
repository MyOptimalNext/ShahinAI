from huggingface_hub import InferenceClient
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout

client = InferenceClient(api_key="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")

messages = []

class ChatApp(MDApp):
    def build(self):
        # واجهة المستخدم الأساسية
        self.screen = BoxLayout(orientation='vertical')
        
        # ScrollView لعرض الرسائل
        self.scrollview = ScrollView()
        self.chat_box = BoxLayout(orientation='vertical', size_hint_y=None)
        self.chat_box.bind(minimum_height=self.chat_box.setter('height'))
        self.scrollview.add_widget(self.chat_box)
        
        # حقل النص لإدخال المستخدم
        self.input_field = MDTextField(hint_text="أدخل سؤالك هنا", size_hint_y=None, height=40)
        
        # زر إرسال
        self.send_button = MDRaisedButton(text="إرسال", size_hint_y=None, height=40)
        self.send_button.bind(on_press=self.on_send)
        
        # إضافة العناصر إلى الشاشة
        self.screen.add_widget(self.scrollview)
        self.screen.add_widget(self.input_field)
        self.screen.add_widget(self.send_button)
        
        return self.screen
    
    def on_send(self, instance):
        user_input = self.input_field.text
        if user_input.lower() == "exit":
            print("Goodbye!")
            self.stop()
            return
        
        # إضافة السؤال إلى تسلسل الرسائل
        messages.append({"role": "user", "content": user_input})

        # الحصول على الرد من النموذج
        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct", 
            messages=messages, 
            max_tokens=500
        )

        # طباعة الإجابة
        assistant_reply = completion.choices[0].message['content']

        # إضافة رد المساعد إلى تسلسل الرسائل
        messages.append({"role": "assistant", "content": assistant_reply})

        # عرض الرسائل في واجهة المستخدم
        self.update_chat(user_input, assistant_reply)
        
        # مسح حقل النص
        self.input_field.text = ""

    def update_chat(self, user_input, assistant_reply):
        # عرض رسالة المستخدم
        user_message = MDLabel(text=f"You: {user_input}", size_hint_y=None, height=40)
        self.chat_box.add_widget(user_message)
        
        # عرض رد المساعد
        assistant_message = MDLabel(text=f"Assistant: {assistant_reply}", size_hint_y=None, height=40)
        self.chat_box.add_widget(assistant_message)
        
        # تحديث ScrollView ليظهر الرسائل الجديدة
        self.scrollview.scroll_to(user_message)

# تشغيل التطبيق
if __name__ == "__main__":
    ChatApp().run()
