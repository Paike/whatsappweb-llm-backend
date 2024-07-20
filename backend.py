from flask import Flask, jsonify, request
import hashlib
import langroid as lr
import langroid.language_models as lm
import os
from datetime import datetime
import logging


app = Flask(__name__)
logger = app.logger
logger.setLevel(logging.INFO)
Role = lr.language_models.Role
LLMMessage = lr.language_models.LLMMessage
# config = lr.language_models.OpenAIGPTConfig(
#     chat_model=lr.language_models.OpenAIChatModel.GPT4,
# )

LLM_API_HOST = os.getenv("LLM_API_HOST", "127.0.0.1")
LLM_API_SCHEME = os.getenv("LLM_API_SCHEME", "http")
LLM_API_PORT = os.getenv("LLM_API_PORT", 8000)
LLM_API_KEY = os.getenv("LLM_API_KEY", "nokey")
LLM_API_URL = os.getenv("LLM_API_URL", f"{LLM_API_SCHEME}://{LLM_API_HOST}:{LLM_API_PORT}")

LLM_SYSTEM_MESSAGE = os.getenv("LLM_SYSTEM_MESSAGE", "You are a helpful assistant.")

LLM_MAX_TOKENS = os.getenv("LLM_MAX_TOKENS", 300)
DEBUG = os.getenv('DEBUG', False)
FLASK_PORT = os.getenv('BACKEND_API_PORT', 5000)



logger = app.logger
logger.setLevel(logging.DEBUG) if DEBUG else logger.setLevel(logging.INFO)
Role = lr.language_models.Role
LLMMessage = lr.language_models.LLMMessage

logger.info(f"LLM_API_URL: {LLM_API_URL}")
logger.debug(f"LLM_API_SCHEME: {LLM_API_SCHEME}")
logger.debug(f"LLM_API_HOST: {LLM_API_HOST}")
logger.debug(f"LLM_API_PORT: {LLM_API_PORT}")
logger.info(f"BACKEND_API_PORT: {FLASK_PORT}")
logger.info(f"LLM_SYSTEM_MESSAGE: {LLM_SYSTEM_MESSAGE}")
logger.info(f"LLM_SYSTEM_MESSAGE: {LLM_MAX_TOKENS}")

config = lm.OpenAIGPTConfig(
    api_base=LLM_API_URL,
    api_key=LLM_API_KEY
)

model = lm.OpenAIGPT(config)

# config = lr.ChatAgentConfig(
#     name="Assistant",
#     llm = lm.OpenAIGPTConfig(
#         api_base=os.getenv('LLM_API_HOST')
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


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    # Perform your health checks here (e.g., database, external services)
    # For simplicity, we'll just return a static response
    health_status = {
        "status": "OK",
        "uptime": "100%",
        "dependencies": {
            "inference_server": "OK"
        }
    }
    logger.debug(f"Requested health check: {health_status}")
    return jsonify(health_status), 200


@app.route('/inference', methods=['POST'])
def post_data():
    content = request.json
    logger.debug(f"Request: {request}")
    messages = []
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    system_message = LLM_SYSTEM_MESSAGE + f" The current date and time is: {current_time}."
    messages.append(
        LLMMessage(content=system_message, role=Role.SYSTEM),
    )
    system_message = ""
    messages.extend(get_messages_from_request(content))
    logger.debug(f"Messages: {messages}")
    response = model.chat(messages=messages, max_tokens=LLM_MAX_TOKENS)
    logger.debug(f"LLM Response: {response}")
    return jsonify(response.message.replace('<|eot_id|>', ''))


if __name__ == '__main__':
    app.run(debug=DEBUG, port=FLASK_PORT, host="0.0.0.0")
