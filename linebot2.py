# !pip install line-bot-sdk
# !pip install flask
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

import pymysql.cursors


# 建立 flask server
app = Flask(__name__)
line_bot_api = LineBotApi('A76keVCf5ezD9Njp3ThlAwAa2FJA8RDl+tZ2hoE/yTYNx4oestqYUnhho3ioCOC9KJ2hPIyS1lKtcJOTfuEQc2CTn/ZwCDC/02hWHpj1N7UGbmHC+wzWdEId/vlSm4WTJb2eq1k19Dd16n3WlC4OfAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9fd15c03dbffdefe58ae3997c99405ad')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print('receive msg')
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# handle msg
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get user info & message
    user_id = event.source.user_id
    msg = event.message.text
    user_name = line_bot_api.get_profile(user_id).display_name
    
    # 歡迎詞
    if msg == '呼叫小幫手':
       
        line_bot_api.reply_message(event.reply_token, 
                                   TextSendMessage(text = '請點左下角的小鍵盤，輸入您想看的影片類型或關鍵字喔!!!'))
    #儲存使用者搜尋資料

    elif msg == event.message.text :
#         print(msg)
#         print(user_name)
        file = open('./' + (user_name) +'搜尋紀錄.txt', 'a', encoding='utf-8')
        file.write((msg) + "\n")
        file.close()  
       
    
    #讀取(DM用版讀取最後1筆)  
        with open('./' + (user_name) +'搜尋紀錄.txt', 'rt', encoding='utf-8') as f:
            txt=f.readlines()
        keys=[r for r in range(1,len(txt)+1)]
        result={k:v for k,v in zip(keys,txt[::-1])} 
        x = result[1] .split("\n")[0]  #[n]=倒數第 n 筆 並去除換行符號
        print(x)

        mydb = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='*', #這個換成自己的密碼
        database='for_linebot'#這個以用 MySQl先建
        )

        mycursor = mydb.cursor()

        mycursor.execute("SELECT cnurl FROM customers WHERE cntitle LIKE '%" + x + "%'") #要想辦法把危險改成帶入X

        myresult = mycursor.fetchall()

        for xx in myresult:
            print(xx)
            url = "".join(xx)
            file = open('./' + '丘志翔' +'url.txt', 'a')
            file.write(url + "\n")
            file.close() 

        with open('./' + (user_name) +'url.txt') as u:
            txt=u.readlines()
        keys=[r for r in range(1,len(txt)+1)]
        result={k:v for k,v in zip(keys,txt[::-1])} 
        url = result[1].split("\n")[0]  #[n]=倒數第 n 筆 並去除換行符號
        print(url)   
        
            
                  
            
        line_bot_api.reply_message(event.reply_token, 
                                           TextSendMessage(text = url ))
                                                                  
        
# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)
