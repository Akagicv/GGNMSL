import aiohttp
import os

from hoshino import R, Service, util
from hoshino.typing import CQEvent, MessageSegment

sv = Service('ggnmsl', help_='广告你妈死了')

RUN_PATH = os.getcwd()
FILE_FOLDER_PATH = os.path.dirname(__file__)
RELATIVE_PATH = os.path.relpath(FILE_FOLDER_PATH, RUN_PATH)
PIC_PATH = os.path.join(FILE_FOLDER_PATH,'gg.jpg')

keywordtxt = open(FILE_FOLDER_PATH+"/keyword.txt","r",encoding="utf-8") #打开关键词文件
keywordread = str(keywordtxt.read()) #获取文件数据（载入内存）
keyword = keywordread.split() #以空格作为数组分隔符获取关键词

@sv.on_keyword(keyword)
async def ggnmsl(bot, ev):
    try:
        await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
        await util.silence(ev, 10*60, skip_su=True)
        await bot.send(ev, str('\n检测到疑似广告内容，反制进程已启动' + MessageSegment.image(f'file:///{os.path.abspath(PIC_PATH)}')),at_sender=True)
    except:
        print ("反制进程启动失败，可能是没有禁言该用户权限或者其他错误")