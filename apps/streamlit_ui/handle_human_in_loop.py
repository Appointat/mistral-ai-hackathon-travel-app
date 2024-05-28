import json, queue
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message')
    if message:
        with open('apps/streamlit_ui/human_messages_tmp.txt', 'a') as file:
            file.write(json.dumps({"human_message": message}) + "\n")
        return jsonify({"status": "success", "human_message": "Message received"}), 200
    else:
        return jsonify({"status": "error", "human_message": "No message provided"}), 400

def run_flask():
    app.run(port=5000, debug=False)

if __name__ == '__main__':
    run_flask()