from youtube_comment_scraper_python import *
from bot_studio import *
from pytube import Playlist
import os
import re
import pymongo

with open('./ytlist.txt', 'r') as t: #把所有想爬的頻道清單存成 ytlist
    for a in t.readlines():
        foldername = 'yt-scraper/'    #在迴圈內建立目標資料夾
        if not os.path.exists(foldername):
            os.mkdir(foldername)

        pl = Playlist(a)
        with open(foldername + 'test.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(pl))
        with open(foldername + 'test.txt') as l:
            r = l.readlines()

        for play in r:  
            try:          
                youtube=bot_studio.youtube()
                info = youtube.get_video_info(video_url=play)['body']
                title = info['Title']
                cn = info['ChannelName']
                rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
                new_title = re.sub(rstr, "_", title)  # 替換為下底線
               
                new_post = {"channel": cn, "title": new_title, "url": a } # {"欄位名稱(自訂)":資料}

                conn = pymongo.MongoClient("mongodb://localhost:27017/") #存入本機
                db = conn.video2 #建立 是資料庫名稱 video
                collection = db.yttest #建立 videl下的集合名稱 yttest


                y = collection.insert_one(new_post) 
                print(y)
                youtube.end()
            except Exception as e:   #遇中途出錯 BY PASS
                pass
            continue
########以下為使用pasdas取出資料備用

import pandas as pd

list_tmp = []

conn = pymongo.MongoClient("mongodb://localhost:27017/")

db = conn.video2 
collection = db.yttest 
for ax in collection.find({},{"_id": 0, "title": 1, "url": 1, "channel": 1}): 
    list_tmp.append(ax)
#      print(ax)

data = pd.DataFrame(list_tmp)
df = pd.DataFrame(data)  # 读取整张表 (DataFrame)

# print(data)
print(df)
