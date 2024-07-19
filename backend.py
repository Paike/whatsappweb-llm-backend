from flask import Flask, jsonify, request
import hashlib
import langroid as lr
import langroid.language_models as lm
import os

app = Flask(__name__)

Role = lr.language_models.Role
LLMMessage = lr.language_models.LLMMessage
# config = lr.language_models.OpenAIGPTConfig(
#     chat_model=lr.language_models.OpenAIChatModel.GPT4,
# )
config = lm.OpenAIGPTConfig(
    
    api_base=os.getenv('LLM_API_URL')
    )
model = lr.language_models.OpenAIGPT(config)

# config = lr.ChatAgentConfig(
#     name="Assistant",
#     llm = lm.OpenAIGPTConfig(
#         api_base=os.getenv('LLM_API_URL')
#     ),
#     use_tools=False, 
#     use_functions_api=False, 
#     vecdb=None,
# )
# agent = lr.ChatAgent(config=config)


# task = lr.Task(agent, 
# name="Assistant", 
# system_message="you are a dog and the mans best friend.", 
# interactive=False,
# )

# print(task.run())

print(os.getenv('LLM_API_URL'))

def get_messages_from_request(data):
    assistant = 'assistant'
    messages = []

    for message in data['history']:
        messages.append(
            LLMMessage(
                role=Role.ASSISTANT if message['from'] == assistant else Role.USER,
                content=message['body'],
                timestamp=message['timestamp']
            )
        )

    last_message = data['lastMessage']

    messages.append(
        LLMMessage(
            role=Role.ASSISTANT if message['from'] == assistant else Role.USER,
            content=last_message['body'],
            timestamp=message['timestamp']
        )
    )

    return messages




# @app.route('/api/data', methods=['GET'])
# def get_data():
#     data = {'message': 'Hello from Flask'}
#     return jsonify(data)

# standard messaging route


@app.route('/api/inference', methods=['POST'])
def post_data():
    content = request.json

    messages = []
    messages.append(
        LLMMessage(content=os.getenv('LLM_SYSTEM_MESSAGE'), role=Role.SYSTEM), 
    )

    messages.extend(get_messages_from_request(content))

    response = model.chat(messages=messages, max_tokens=200)

    return jsonify(response.message.replace('<|eot_id|>', ''))


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('FLASK_PORT'))
