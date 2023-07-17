# ---------------------------------- Modules ----------------------------------
import os
from dotenv import load_dotenv
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai

# ---------------------------------- App init ----------------------------------
# Flask app
app = Flask(__name__)

# Load Environment Variable
load_dotenv('.env')

# CHANNEL_ACCESS_TOKEN
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# CHANNEL_SECRET
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')
handler = WebhookHandler(CHANNEL_SECRET)

# OPENAI_API_KEY
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# ---------------------------------- Function ----------------------------------
def chatgpt_reply(question):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": question},
        ],
        temperature=0,
    )

    response_answer = response['choices'][0]['message']['content']

    return response_answer


# ---------------------------------- Webhook ----------------------------------
@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route('/', methods=['POST'])
def webhook():
    try:
        # for line api
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)
        handler.handle(body, signature)
        return {"status": 200}
    except InvalidSignatureError:
        abort(400)

# ---------------------------------- Message Handler ----------------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    status = None
    try:
        msg = event.message.text
        print(msg)
        userId = event.source.user_id
        print(userId)
        reply = chatgpt_reply(msg)
        print(reply)

        try:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            status = 'OK'
        except:
            try:
                line_bot_api.push_message(userId, TextSendMessage(text=reply))
                status = 'OK'
            except Exception as e:
                status = 'Fail'
                print(f'Fail Error:{e}')
    except Exception as e:
        print(f'Fail Error:{e}')
    return status


if __name__ == "__main__":
    app.run(debug=False)
