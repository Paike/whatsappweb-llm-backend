from flask import Flask, jsonify, request
import hashlib
import datetime
import json
import langroid as lr

app = Flask(__name__)

Role = lr.language_models.Role
LLMMessage = lr.language_models.LLMMessage
config = lr.language_models.OpenAIGPTConfig(
    chat_model=lr.language_models.OpenAIChatModel.GPT4,
)
model = lr.language_models.OpenAIGPT(config)


def make_chat_history(data):
    # Initialize variables for transformation
    assistant = "assistant"
    messages = []

    # Process history messages
    for message in data['history']:
        role = "assistant" if message['from'] == assistant else "user"
        content = message['body']
        utc_time = datetime.datetime.fromtimestamp(message['timestamp'], datetime.UTC)
        localized_datetime = utc_time + datetime.timedelta(hours=2)
        # Format datetime as ISO 8601 with 'Z' suffix for UTC
        timestamp = localized_datetime.isoformat() + 'Z'        
        messages.append(
            {
            "role": role,
            "content": content,
            "timestamp": timestamp
        })

    # Process last message
    last_message = data['lastMessage']
    role = "assistant" if message['from'] == assistant else "user"
    content = last_message['body']
    utc_time = datetime.datetime.fromtimestamp(message['timestamp'], datetime.UTC)
    localized_datetime = utc_time + datetime.timedelta(hours=2)
    # Format datetime as ISO 8601 with 'Z' suffix for UTC
    timestamp = localized_datetime.isoformat() + 'Z'   
    messages.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

    # Construct the new JSON object
    new_json_data = {
        "messages": messages
    }

    # Convert to JSON string
    new_json_str = json.dumps(new_json_data, indent=2)
    print(new_json_str)

def hash_id_with_suffix(id):
    # Convert phone number to bytes and hash using SHA-256
    hash_object = hashlib.sha256(id.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {"message": "Hello from Flask"}
    return jsonify(data)

# standard messaging route
@app.route('/api/data', methods=['POST'])
def post_data():
    content = request.json
    response = {"received": content}
    print(content)
    make_chat_history(content)



    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
