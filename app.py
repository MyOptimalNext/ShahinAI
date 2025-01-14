from flask import Flask, request, jsonify, render_template
from huggingface_hub import InferenceClient

app = Flask(__name__)

client = InferenceClient(api_key="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")

# حفظ الرسائل
messages = []

@app.route('/')
def home():
    return render_template('index.html')  # عرض صفحة HTML

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    messages.append({"role": "user", "content": user_input})

    # طلب الإجابة من النموذج
    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct", 
        messages=messages, 
        max_tokens=500
    )

    assistant_reply = completion.choices[0].message['content']
    messages.append({"role": "assistant", "content": assistant_reply})

    return jsonify({"response": assistant_reply})

if __name__ == "__main__":
    app.run(debug=True)
