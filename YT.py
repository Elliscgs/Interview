#!pip install youtube-comment-scraper-python
#!pip install bot-studio
#!pip install pytube
from youtube_comment_scraper_python import *
from bot_studio import *
from pytube import Playlist
import os
import re

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

                 i=1
                 sum=0
                 besum=1

                 while besum != sum:
                     if i == 1:
                         besum = 0
                     else:
                         besum = sum
                     comments = youtube.video_comments()
                     sum = len(comments['body'])
                     i +=1

                with open(foldername + new_title + '.txt', 'w', encoding='utf-8') as f:
                    f.write(str(info))
                    f.write("\n \n--------------------------------------------------------------------------------\n \n")
                    f.write(str(comments['body']))
                youtube.end()
            except Exception as e:   #遇中途出錯 BY PASS
                pass
            continue

        os.rename("yt-scraper",cn)
        scrfilename = cn + "\\test.txt"          #修改前的檔名
        nowfilename = cn + "\\" + cn + ".txt"       #修改的檔名
        os.rename(scrfilename, nowfilename)

        
