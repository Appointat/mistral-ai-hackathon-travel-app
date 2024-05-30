import json, os
from flask import Flask, request, jsonify

app = Flask(__name__)
MESSAGE_FILE_PATH = 'apps/streamlit_ui/human_messages_tmp.txt'

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"status": "error", "human_message": "No message provided"}), 400

    try:
        os.makedirs(os.path.dirname(MESSAGE_FILE_PATH), exist_ok=True)
        with open(MESSAGE_FILE_PATH, 'a') as file:
            file.write(json.dumps({"human_message": message}) + "\n")
        return jsonify({"status": "success", "human_message": "Message received"}), 200
    except Exception as e:
        return jsonify({"status": "error", "human_message": str(e)}), 500

def run_flask():
    app.run(port=5000, debug=False)

if __name__ == '__main__':
    run_flask()
