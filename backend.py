from flask import Flask, jsonify, request
import hashlib
import langroid as lr
import langroid.language_models as lm
from langroid.utils.configuration import settings as langroid_settings

import os
from datetime import datetime
import logging

langroid_settings.debug = True

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
LLM_API_MODEL = os.getenv("LLM_API_MODEL", "gpt-4o-mini")
LLM_API_URL = os.getenv("LLM_API_URL", f"{LLM_API_SCHEME}://{LLM_API_HOST}:{LLM_API_PORT}")

CONTEXT_FILEPATH = os.getenv("CONTEXT_FILEPATH", "context/context.md")

LLM_SYSTEM_MESSAGE = os.getenv("LLM_SYSTEM_MESSAGE", "You are a helpful assistant.")

LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 300))
DEBUG = os.getenv('DEBUG', False)
STOP = False
FLASK_PORT = os.getenv('BACKEND_API_PORT', 5000)



logger = app.logger
logger.setLevel(logging.DEBUG) if DEBUG else logger.setLevel(logging.INFO)
Role = lr.language_models.Role
LLMMessage = lr.language_models.LLMMessage

logger.debug(f"LLM_API_SCHEME: {LLM_API_SCHEME}")
logger.debug(f"LLM_API_HOST: {LLM_API_HOST}")
logger.debug(f"LLM_API_PORT: {LLM_API_PORT}")
logger.info(f"LLM_API_URL: {LLM_API_URL}")
logger.info(f"LLM_API_MODEL: {LLM_API_MODEL}")
logger.info(f"BACKEND_API_PORT: {FLASK_PORT}")
logger.debug(f"CONTEXT_FILEPATH: {CONTEXT_FILEPATH}")
logger.info(f"LLM_SYSTEM_MESSAGE: {LLM_SYSTEM_MESSAGE}")
logger.info(f"LLM_SYSTEM_MESSAGE: {LLM_MAX_TOKENS}")

config = lm.OpenAIGPTConfig(
    api_base=LLM_API_URL,
    api_key=LLM_API_KEY,
    chat_model=LLM_API_MODEL,
    max_output_tokens=LLM_MAX_TOKENS
)

model = lm.OpenAIGPT(config)

def get_system_message():
    
    system_message = LLM_SYSTEM_MESSAGE

    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S (%A)')
    logger.debug(f"Date and time: {current_time}")
    # system_message = LLM_SYSTEM_MESSAGE + f" The current date and time is: {current_time}."
    # logger.debug(f"Current system message: {system_message}")
    system_message = system_message.replace('{datetime}', current_time)
    try:
        with open(CONTEXT_FILEPATH, 'r') as file:
            context = file.read()
        system_message = system_message.replace('{context}', context)
        logger.debug(f"Injecting context")
    except FileNotFoundError:
        # Handle the case where the file does not exist
        context = ""  # Or any default context you want to use
        system_message = system_message.replace('{context}', context)
        # logger.debug(f"System message: {system_message}")
        logger.debug(f"There is no context file")
    return system_message

def get_messages_from_request(data):
    assistant = 'assistant'
    messages = []

    for message in data['history']:
        logger.debug(f"Message: {message}")

        messages.append(
            LLMMessage(
                role=Role.ASSISTANT if message['from'] == assistant else Role.USER,
                content=message['body'],
                timestamp=message['timestamp']
            )
        )


    last_message = data['lastMessage']
    logger.debug(f"Last message: {last_message}")

    messages.append(
        LLMMessage(
            role=Role.ASSISTANT if last_message['from'] == assistant else Role.USER,
            content=last_message['body'],
            timestamp=last_message['timestamp']
        )
    )

    return messages


@app.route('/health', methods=['GET'])
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

    messages.append(
        LLMMessage(content=get_system_message(), role=Role.SYSTEM),
    )
    system_message = ""
    messages.extend(get_messages_from_request(content))
    logger.debug(f"Messages: {messages}")
    # for message in messages:
    #     if message.role == Role.USER and '!stop' in message.content:
    #         logger.debug("Received stop signal")
    #         return jsonify(f"Vielen Dank für das nette Gespräch! Um den Chat neu zu starten, leeren Sie bitte den Chat. Auf Wiedersehen!")
    
    latest_command = None
    command = None
    for message in messages:
        if message.content == '!stop' or message.content == '!start':
            if latest_command is None or message.timestamp > latest_command.timestamp:
                command = message.content

    logger.debug(f"Command: {command}")
    if command == '!stop':
        logger.debug("Received stop signal")
        return jsonify("")        
    if command == '!start':
        logger.debug("Received start signal")      
        

    response = model.chat(messages=messages, max_tokens=LLM_MAX_TOKENS)
    
    logger.debug(f"LLM Response: {response}")
    return jsonify(response.message.replace('<|eot_id|>', ''))


if __name__ == '__main__':
    app.run(debug=DEBUG, port=FLASK_PORT, host="0.0.0.0")
