import os
import cv2
import numpy as np
import urllib
import requests
from bs4 import BeautifulSoup

RUN_PATH = os.getcwd()
FILE_FOLDER_PATH = os.path.dirname(__file__)
keywordtxt = open(FILE_FOLDER_PATH+"/keyword.txt","r",encoding="utf-8") #打开关键词文件
keywordread = str(keywordtxt.read()) #获取文件数据（载入内存）
keyword = keywordread.split() #以空格作为数组分隔符获取关键词

def qr_scan(qr_scan_path):
    try:
        image = cv2.imread(qr_scan_path) #读取图像
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)#灰度转换
        qrcoder = cv2.QRCodeDetector()#检测
        codemsg, points, straight_qrcode = qrcoder.detectAndDecode(gray)#解码
        if len(codemsg)>0:
            #print (codemsg) #输出二维码对应的网站
            #检测二维码中的链接是否包含http bs4以免访问不了
            http_check = "http"
            if http_check in codemsg:
                codeurl = codemsg
            else:
                codeurl = 'http://' + codemsg
            # print (codeurl) #输出最终访问的url
            #使用bs4访问二维码链接，获取网页标题
            res = requests.get(codeurl)
            
            
            res.encoding = 'utf-8' 
            soup = BeautifulSoup(res.text, 'lxml')
            title = soup.find('title')
            result = soup.title.text
            print (result)
            #检测网站标题关键词
            check_result = checkkeyword(result)
            if check_result:
                return True
            else:
                return False
        else:
            return False
    except:
        return False

def  checkkeyword(result):
    try:
        for keywordopencv in keyword:
            if keywordopencv in result:
                #print("检测到")
                return True
    except:
        return False