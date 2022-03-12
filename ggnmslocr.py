import importlib
import math
import os
import re
import aiohttp

from hoshino import Service, util, priv
from hoshino.typing import CQEvent, MessageSegment

sv = Service('ggnmslocr', help_='广告你妈死了：关键词/图片内关键词ocr/基于opencv的二维码识别')

RUN_PATH = os.getcwd()
FILE_FOLDER_PATH = os.path.dirname(__file__)
RELATIVE_PATH = os.path.relpath(FILE_FOLDER_PATH, RUN_PATH)
PIC_PATH = os.path.join(FILE_FOLDER_PATH,'gg.jpg')
ocred_images = {}
opencv_tool = importlib.import_module(RELATIVE_PATH.replace(os.sep,'.') + '.ggnmslopencv')

keywordtxt = open(FILE_FOLDER_PATH+"/keyword.txt","r",encoding="utf-8") #打开关键词文件
keywordread = str(keywordtxt.read()) #获取文件数据（载入内存）
keyword = keywordread.split() #以空格作为数组分隔符获取关键词

async def check_gif(bot, img):
    r = await bot.call_action(action='get_image', file=img)
    return r['filename'].endswith('gif')

async def gg_image(bot, ev, img):
    check_gif_result = await check_gif(bot, img)
    return not (check_gif_result)

def gg_word_ocr(ocr_result):
    try:
        ocr_result_string = str(ocr_result)
        for keywordocr in keyword:
            if keywordocr in ocr_result_string:
                return True
    except:
        return False

def record_ocr(gid, img):
    if gid not in ocred_images:
        ocred_images[gid] = []
    if img not in ocred_images[gid]:
        ocred_images[gid].append(img)

async def judge_bot_auth(bot, ev):
    bot_info = await bot.get_group_member_info(group_id=ev.group_id, user_id=ev.self_id)
    if not bot_info['role'] == 'member':
        return True
    return False

async def download(url, path):
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            content = await resp.read()
            with open(path, 'wb') as f:
                f.write(content)

async def check_image(bot, ev, img):
    try:
        r = await bot.call_action(action='.ocr_image', image=img)
        kw = gg_word_ocr(r)
        if kw:
            return True
        else:
            image_path = f'{FILE_FOLDER_PATH}{img}.jpg'
            image_info = await bot.call_action(action='get_image', file=img)
            await download(image_info['url'], image_path)
            qr_img = opencv_tool.qr_scan(image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
            if qr_img:
                return True
            else:
                record_ocr(ev.group_id, img)
                return False
    except:
        return False 
        
@sv.on_message()
async def on_input_image(bot, ev: CQEvent):
    for seg in ev.message:
        if seg.type == 'image':
            img = seg.data['file']
            need_ocr = await gg_image(bot, ev, img)
            if need_ocr:
                need_shama_msg = await check_image(bot, ev, img)
                if need_shama_msg:
                    bot_auth = await judge_bot_auth(bot, ev)
                    if bot_auth == True:
                        try:
                            await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
                            await util.silence(ev, 10*60, skip_su=True)
                            await bot.send(ev, str(MessageSegment.image(f'file:///{os.path.abspath(PIC_PATH)}')) + '\n检测到疑似广告内容，反制进程已启动',at_sender=True)
                        except:
                            print ("反制进程启动失败，可能是没有禁言该用户权限或者其他错误")