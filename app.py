from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


#======這裡是呼叫的檔案內容=====
from message import *
from new import *
from Function import *
from mongodb_function import *
#======這裡是呼叫的檔案內容=====

#======python的函數庫==========
import  os
import tempfile, os
import datetime
import time
import traceback
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    write_one_data(eval(body.replace('false','False')))
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()
        abort(500)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if '@讀取' == msg:
        datas = read_many_datas()
        datas_len = len(datas)
        message = TextSendMessage(process_message(text=f'資料數量，一共{datas_len}條'))
        line_bot_api.reply_message(event.reply_token, message)

    elif '@查詢' == msg:
        datas = col_find('events')
        message = TextSendMessage(process_message(text=str(datas)))
        line_bot_api.reply_message(event.reply_token, message)

    elif '@對話紀錄' == msg:
        datas = read_chat_records()
        print(type(datas))
        n = 0
        text_list = []
        for data in datas:
            if '@' in data:
                continue
            else:
                text_list.append(data)
            n+=1
        data_text = '\n'.join(text_list)
        message = TextSendMessage(process_message(text=data_text[:5000]))
        line_bot_api.reply_message(event.reply_token, message)

    elif '@刪除' == msg:
        text = delete_all_data()
        message = TextSendMessage(process_message(text=text))
        line_bot_api.reply_message(event.reply_token, message)

    else:
        message = TextSendMessage(process_message(text=msg))
        line_bot_api.reply_message(event.reply_token, message)

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
