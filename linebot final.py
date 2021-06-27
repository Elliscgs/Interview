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

from gensim.models import word2vec

# 建立 flask server
app = Flask(__name__)
line_bot_api = LineBotApi('A76keVCf5ezD9Njp3ThlAwAa2FJA8RDl+tZ2hoE/yTYNx4oestqYUnhho3ioCOC9KJ2hPIyS1lKtcJOTfuEQc2CTn/ZwCDC/02hWHpj1N7UGHC+wzWdEId/vlSm4WTJb2eq1k19Dd16n3WlC4OfAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9fd15c03dbffdefe583997c99405ad')

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
                                   TextSendMessage(text = '請輸入您想看的影片關鍵字!!!'))
    #儲存使用者搜尋資料

    elif msg == event.message.text :


 #以下為gensim模型
        
        keyword = msg # 設定欲比對詞彙

        topic = ['animation', 'beauty', 'entertainment.travel.daily',
                 'exercise', 'food', 'game', 'knowledge', 'learn', 
                 'news', 'pet', 'technology', 'variatyshow']
        #載入12種Model
        a = 0
        TotalList=[]
        maximum = 0
        title = ""
        checkall = 0

        for i in range(12):
            try:
                model = word2vec.Word2Vec.load(topic[a] + '.word2vec.model')
                ItemList=[]
                for item in model.wv.most_similar(keyword):
                    ItemList.append(item)
                print('我們在主題: ' + topic[a] + ' 搜尋到您可能喜歡的影片')
                a += 1
                TargetList=[]
                print(ItemList[0][0])
                print(ItemList[0][1])
                TargetList.append(ItemList[0][0])
                TargetList.append(ItemList[0][1])
                TotalList.append(TargetList)

                listorder = 0
                maximum = TotalList[listorder][1]
                for score in TotalList:

                    if TotalList[listorder][1] >= maximum:
                        maximum = TotalList[listorder][                      1]

                        title = ""
                        for j in range(len(TotalList[listorder][0])):
                            ch = TotalList[listorder][0][j]
                            title += ch
                    listorder += 1

                if a == 11:
                    break
            except:
                checkall += 1
                print('我們在主題: ' + topic[a] + ' 搜尋不到您可能喜歡的影片')
                a += 1


        if checkall ==12:
            print('\n'+'抱歉我們完全找不到您欲搜尋的影片,請再輸入一次')
        else:
            print('\n')
            print('我們認為您也喜歡 ' + str(title) + ' 的影片')
            print('該主題與您相似值為: ' + str(maximum))      
            
            t = str(title)
            p = (' {:.2f}%'.format(maximum*100)) #轉百分比
            
            
        #以下為資料庫調取資料
        mydb = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='********', 
        database='for_linebot'
        )
        try:
            mycursor = mydb.cursor()

            mycursor.execute("SELECT cnurl FROM customers WHERE cntitle LIKE '%" + t + "%'")

            myresult = mycursor.fetchall()

            for xx in myresult:

                url = "".join(xx) #轉換格式




            #回復使用者    
            line_bot_api.reply_message(event.reply_token, 
                                               TextSendMessage(text = '我們認為您可能對以下影片有興趣 ' + url + "\n" +'該影片內容與您相似值為: ' + p))

        except Exception as e:   #遇中途出錯 
            
            line_bot_api.reply_message(event.reply_token, 
                                               TextSendMessage(text = '哈囉!!!目前找不到內容與**' + msg + '**相關的影片，建議您換個說法或使用我們的文字雲，查看最新的熱門關鍵字喲^^'))                        
            
    
    
# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)
