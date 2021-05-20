#利用 linebot 作為使用者端，串聯 Azure 並將回測結果使用 OpenCV 掛在圖片上後回傳使用者

# import flask related
from flask import Flask, request, abort
# import linebot related
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage
)

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import time
import cv2

# 開啟 linebot
app = Flask(__name__)
# 串接 linebot message API 
line_bot_api = LineBotApi('3Q+nWLDh3r0eguZ9TESPbttS0KN9pMttAZUDKyYyG+VUa9mxmWMeobeJ+FlXg+s7VecoRoXSIA5BlKCLf1qSDZ6wPmdgfnydB2WtvISqFn45HBJePrQrLVgOX+u9ram7kUs9geSXh3AyMKeFGM3x6wdB04t89/1O/w1cDnyilFU=')

handler = WebhookHandler('e5643326f7f9f9c18979daff7dc0ea94')

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

# lineBot 使用者端接收圖片
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    # get user info & message
    user_id = event.source.user_id
    # msg = event.message.text
    user_name = line_bot_api.get_profile(user_id).display_name
 
    name_img = 'aaa.jpg'
    message_content = line_bot_api.get_message_content(event.message.id)
    
    with open(name_img, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
        # 串接Azure API
        ENDPOINT = "https://southcentralus.api.cognitive.microsoft.com/"
        training_key = "1bb8b72ec7b04530b9ccf5b2acaf3cdb"
        prediction_key = "1bb8b72ec7b04530b9ccf5b2acaf3cdb"
        prediction_resource_id = "/subscriptions/660bf70b-c187-44e5-9c7e-14d6a960ac26/resourceGroups/helmet/providers/Microsoft.CognitiveServices/accounts/helmet"
       
        credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
        trainer = CustomVisionTrainingClient(ENDPOINT, credentials)
        prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
        predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

        publish_iteration_name = "helmet"

        credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
        trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

        #使用絕對路徑
        base_image_location = "C:\\Users\\Tibame\\Desktop\\acv\\"

        
        prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
        predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)
        
        #用本機的照片進行測試
        with open(base_image_location + "aaa.jpg", mode="rb") as test_data:
            results = predictor.detect_image('e11cfbc8-07d8-4eea-80d9-a95c6e5b8987', publish_iteration_name, test_data) 
        
        #以下為 Opencv段 
        img_path ='C:\\Users\\Tibame\\Desktop\\acv\\aaa.jpg'

        # Reading an image in default mode 
        image = cv2.imread(img_path) 

        sp = image.shape[:]
        imageheigh = sp[0]
        imageWidth = sp[1]

        # Window name in which image is displayed 
        window_name = 'Image'

        # Blue color in BGR 
        color = (255, 0, 0) 

        # Line thickness of 2 px 
        thickness = 2

        # Display the results in op
        
        #因為Azure會修改我們上傳照片大小以符合他自己作業的格式，可能造成回傳的座標值與原照片不一樣，導致座標標不上正確位置
        #所以用OPCV的套件公式將照片進行像數轉換成統一格式(如x1~y2段)，並利用受測回傳的值在照片上標出框線跟結果文字(rectangle=框線用,putText=文字用)
        for o in results.predictions:
            if o.probability >= 0.9:
                print("\t" + o.tag_name + ": {0:.2%}, object at location (X1, Y1, X2, Y2): {1:.2f}, {2:.2f}, {3:.2f}, {4:.2f}".format(o.probability * 100, \
                o.bounding_box.left, o.bounding_box.left + o.bounding_box.width, o.bounding_box.top, o.bounding_box.top + o.bounding_box.height))
#                if float(" {0:.2f}".format(o.probability)) > 0.01 :                
#                    bbb = ("\n" + o.tag_name + ": {:.2%}".format(o.probability))
                          
                X1 = int(o.bounding_box.left* imageWidth)
                Y1 = int(o.bounding_box.top * imageheigh)
                X2 = int(o.bounding_box.width* imageWidth + X1)
                Y2 = int(o.bounding_box.height * imageheigh + Y1)

                cv2.rectangle(image, (X1,Y1), (X2,Y2), color , thickness)    
                cv2.putText(image, str(o.tag_name) ,(X1-20, Y1-20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, str(":{:.2%}".format(o.probability)),(X1-20, Y1-40), cv2.FONT_HERSHEY_TRIPLEX, 1, (225, 0, 255), 1, cv2.LINE_AA)
        print('====================')




        #save image to file
        cv2.imwrite('C:\\Users\\Tibame\\Desktop\\acv\\output.jpg', image)
                                
    #以下為Linecbot回復段
        print('msg from [', user_name, '](', user_id, ') :')
    
    line_bot_api.reply_message(event.reply_token, 
                            [

                                ImageSendMessage(original_content_url='https://2e59bef69c7c.ngrok.io/output.jpg', 
                                                preview_image_url='https://2e59bef69c7c.ngrok.io/output.jpg')

                                ])



# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345) 
    
