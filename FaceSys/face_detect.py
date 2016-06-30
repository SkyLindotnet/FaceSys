# -*- coding: UTF-8 -*-
import cv2
import cv2.cv as cv
import sys
import TencentYoutuyun
import uuid
import re
import os
import shutil
import MySQLdb as mdb
import time
import numpy as np

import Image,ImageDraw,ImageFont
# Get user supplied values
# imagePath = sys.argv[1]
# cascPath = sys.argv[2]

iconDir = '../Icons/' #用户头像存放目录
iconTempDir = '../IconsTemp/' #临时目录
    
def getYoutuObject():
    appid = '1007301'
    secret_id = 'AKID54IH7KvVH3c0j6wBg4DZooihViATfbdd'
    secret_key = 'RzwA7LZliLaL37ex3OVuD3eulLEAXRR4'
    userid = 'sky1234'
    end_point = TencentYoutuyun.conf.API_YOUTU_END_POINT 
    youtu = TencentYoutuyun.YouTu(appid, secret_id, secret_key, userid, end_point)
    return youtu

'''重写opencv里的Puttext方法'''
def myPutext(image, text, pst, font, size, color, weight):
    if text.find('\n') != -1:
        texts = text.split('\n')
        k = 0
        for str in texts:
            cv2.putText(image, str, (pst[0], pst[1] + int(round(k*size)) * 18), font, size, color, weight)
            k += 1
        return (pst[0], pst[1] + int(round((k-1)*size)) * 15)
    else:
        cv2.putText(image, text, pst, font, size, color, weight)
        return pst

'''重写PIL里的draw.text方法'''
def myDrawtext(draw, text, pst, ttfont, color):
    if text.find('\n') != -1:
        texts = text.split('\n')
        k = 0
        for str in texts:
            draw.text((pst[0], pst[1] + int(round(k*ttfont.font.height))), str, fill=color, font=ttfont)
            k += 1
        return (pst[0], pst[1] + int(round((k-1)*ttfont.font.height)))
    else:
        draw.text(pst, text, fill=color, font=ttfont)
        return pst

'''显示脸框'''
def showFaceIcon(x, y, width, height, image):
    cv2.rectangle(image, (x, y), (x+width, y+height), (0, 255, 0), 2)

'''显示标签'''
def showLabel(x, y, width, height, image, sex = 'Female', age = 00, expression = 'Smile', beauty = 100):
    cv2.rectangle(image, (x-20, y+100), (x-20+90+25, y+77+180), (113, 227, 250), -2)
#     cv2.putText(image, "Sex:%s" % sex, (x-20, y+118), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
#     cv2.putText(image, "Age:%d" % age, (x-20, y+118+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
#     cv2.putText(image, "Face:%s" % expression, (x-20, y+118+30*2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
#     cv2.putText(image, "Beauty:%d" % beauty, (x-20, y+118+30*3), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
    #使用自定义Putext
    pst = myPutext(image, "Sex:%s" % sex, (x-20, y+118), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
    pst = myPutext(image, "Age:%d" % age, (pst[0], pst[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
    pst = myPutext(image, "Face:%s" % expression, (pst[0], pst[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
    cv2.putText(image, "Beauty:%d" % beauty, (pst[0], pst[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)

'''显示个人信息'''
def showInfo(x, y, width, height, image, info):
    cv2.rectangle(image, (x-20, y+100), (x-20+90+25, y+77+180), (113, 227, 250), -2)
    pst = myPutext(image, "Name:%s" % info['name'], (x-20, y+118), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
    pst = myPutext(image, "Sex:%s" % info['sex'], (pst[0], pst[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
    pst = myPutext(image, "Age:%s" % info['age'], (pst[0], pst[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
    cv2.putText(image, "Area:%s" % info['area'], (pst[0], pst[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)

'''显示个人信息,采用PIT绘制文字(支持中文)'''
def showInfo_PIL1(x, y, width, height, image, info):
    cv2.rectangle(image, (x-20, y+100), (x-20+90+25, y+77+180), (113, 227, 250), -2)
    ttfont = ImageFont.truetype("C:\\WINDOWS\\Fonts\\simhei.TTF",18)
    image2 = Image.fromarray(image)
    draw = ImageDraw.Draw(image2)
    pst = (x-20, y+102)
    color = (49,104,217)
    color = (67,61,89)
    linewidth = 30
    pst =myDrawtext(draw, "Name:%s" % info['name'], pst, ttfont, color)
    pst =myDrawtext(draw, "Sex:%s" % info['sex'], (pst[0], pst[1]+linewidth), ttfont, color)
    pst =myDrawtext(draw, "Age:%s" % info['age'], (pst[0], pst[1]+linewidth), ttfont, color)
    pst =myDrawtext(draw, "Area:%s" % info['area'], (pst[0], pst[1]+linewidth), ttfont, color)
    
#     draw.text((x-20, y+102), u"Name:%s" % info['name'], fill=(49,104,217),font=ttfont)
#     
    image = np.array(image2)
#     pst = myPutext(image, "Name:%s" % info['name'], (x-20, y+118), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
#     pst = myPutext(image, "Sex:%s" % info['sex'], (pst[0], pst[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
#     pst = myPutext(image, "Age:%s" % info['age'], (pst[0], pst[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
#     cv2.putText(image, "Area:%s" % info['area'], (pst[0], pst[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
    return image

def showInfo_PIL(x, y, width, height, image, info):
    interval = 10
    lshift = 20
    boxwidth = width/2+40
    maxwidth = 102
    if boxwidth <= maxwidth:
        boxheight = 210
    else:
        boxheight = 140
        
    cv2.rectangle(image, (x-lshift, y+height+interval), (x-lshift+boxwidth, y+height+interval+boxheight), (113, 227, 250), -2)
    ttfont = ImageFont.truetype("C:\\WINDOWS\\Fonts\\simhei.TTF",18)
    image2 = Image.fromarray(image)
    draw = ImageDraw.Draw(image2)
    pst = (x-lshift+1, y+height+(interval+2))
    color = (49,104,217)
    color = (67,61,89)
    linewidth = 30
    if boxwidth <= maxwidth:
        pst =myDrawtext(draw, "Name:\n%s" % info['name'], (pst[0], pst[1]), ttfont, color)
        pst =myDrawtext(draw, "Sex:\n%s" % info['sex'], (pst[0], pst[1]+linewidth), ttfont, color)
        pst =myDrawtext(draw, "Age:\n%s" % info['age'], (pst[0], pst[1]+linewidth), ttfont, color)
        pst =myDrawtext(draw, "Area:\n%s" % info['area'], (pst[0], pst[1]+linewidth), ttfont, color)
    else:
        pst =myDrawtext(draw, "Name:%s" % info['name'], (pst[0], pst[1]), ttfont, color)
        pst =myDrawtext(draw, "Sex:%s" % info['sex'], (pst[0], pst[1]+linewidth), ttfont, color)
        pst =myDrawtext(draw, "Age:%s" % info['age'], (pst[0], pst[1]+linewidth), ttfont, color)
        pst =myDrawtext(draw, "Area:%s" % info['area'], (pst[0], pst[1]+linewidth), ttfont, color)
    image = np.array(image2)
    return image

'''显示面部属性'''
def showFeature(x, y, width, height, image, feature):
    interval = 10
    lshift = 20
    boxwidth = width/2+40
    maxwidth = 102
    if boxwidth <= maxwidth:
        boxheight = 200
    else:
        boxheight = 140
    cv2.rectangle(image, (x-lshift, y+height+interval), (x-lshift+boxwidth, y+height+interval+boxheight), (113, 227, 250), -2)
    linewidth = 30
    pst = [x-lshift+1, y+height]
    for key in feature.keys():
        if boxwidth <= maxwidth:
            pst = myPutext(image, "%s:\n%s" % (key.capitalize(), feature[key]), (pst[0], pst[1]+linewidth), \
                           cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)
        else:
            pst = myPutext(image, "%s:%s" % (key.capitalize(), feature[key]), (pst[0], pst[1]+linewidth), \
                           cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (49,104,217), 1)

'''创建新用户表'''
def newPersonList():
    try:
        #将con设定为全局连接
        con = mdb.connect('localhost', 'root', 'mysql', 'faceSys',charset='utf8');#
        with con:
            #获取连接的cursor
            cur = con.cursor()
            #建表
            cur.execute("DROP TABLE IF EXISTS personList")
            cur.execute("CREATE TABLE personList (\
            person_id varchar(50) NOT NULL,\
            name varchar(50) NOT NULL,\
            birth varchar(50) NOT NULL,\
            gender varchar(50) NOT NULL,\
            age varchar(10) NOT NULL,\
            area varchar(100) NOT NULL,\
            iconPath varchar(50) NOT NULL\
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8;")
            cur.execute("CREATE INDEX personList_id ON personList (person_id)") #建立索引

    except mdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        con.close()

'''创建新用户'''
def newPerson(name, idcard, iconPath):
    try:
        #名字检查 todo
        if not name.strip():
            print '名字不能为空!'
            raise ValueError
        #身份证验证
        if not checkIdCard(idcard):
            print '身份证验证不通过!'
            raise ValueError
        #图像路径检查并储存文件
        if not os.path.exists(iconPath):
            print '文件不存在!'
            raise ValueError
        else:
            iconDir = '../Icons/' #定义图像储存目录
            if not os.path.exists(iconDir):
                os.makedirs(iconDir)
            fileName = iconPath.split('/')[-1].split('.')
            savePath = os.path.join(iconDir, idcard + '.' + fileName[1])
            if os.path.exists(savePath):
                os.remove(savePath)
            shutil.copy(iconPath, iconDir)
            os.rename(iconDir + fileName[0] + '.' + fileName[1], savePath)
        #将con设定为全局连接
        con = mdb.connect('localhost', 'root', 'mysql', 'faceSys',charset='utf8');#
        with con:
            #获取连接的cursor
            cur = con.cursor()
            #数据准备
            info = getPersonInfo(idcard)
            info_age = info['age']
            info_birth = info['birth']
            info_gender = info['gender']
            info_area = info['area']
            info_id = idcard
            info_name = name
            info_iconPath = savePath
            #插入信息
            cur.execute("INSERT INTO personList(person_id, name, birth, gender, age, area, iconPath)\
                        VALUES(%s, %s, %s, %s, %s, %s, %s)", [info_id, info_name, info_birth, info_gender,\
                                                              info_age, info_area, info_iconPath])
    except mdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        con.close()

'''根据身份证号码返回个人信息'''
def getPersonInfo(idcard):
#     if not checkIdCard(idcard):
#         print '身份证验证不通过!'
#     else:
    info = {}
    area={"11":"北京","12":"天津","13":"河北","14":"山西","15":"内蒙古","21":"辽宁","22":"吉林","23":"黑龙江","31":"上海","32":"江苏","33":"浙江","34":"安徽","35":"福建","36":"江西","37":"山东","41":"河南","42":"湖北","43":"湖南","44":"广东","45":"广西","46":"海南","50":"重庆","51":"四川","52":"贵州","53":"云南","54":"西藏","61":"陕西","62":"甘肃","63":"青海","64":"宁夏","65":"新疆","71":"台湾","81":"香港","82":"澳门","91":"国外"}
    idcard=str(idcard)
    idcard=idcard.strip()
    id_area=idcard[0:6]
    id_birth=idcard[6:14]
    id_sex=idcard[14:17]
    info['area'] = area[(idcard)[0:2]]
    info['birth'] = id_birth[0:4] + '/' + id_birth[4:6] + '/' + id_birth[6:8]
    currentYear = time.strftime("%Y",time.localtime(time.time()))
    info['age'] = str(int(currentYear) - int(id_birth[0:4]))
    info['gender'] = 'female' if int(id_sex)%2==0 else 'male'
    return info

'''身份证有效性验证'''
def checkIdCard(idcard):
    Errors=['验证通过!','身份证号码位数不对!','身份证号码出生日期超出范围或含有非法字符!','身份证号码校验错误!','身份证地区非法!']
    area={"11":"北京","12":"天津","13":"河北","14":"山西","15":"内蒙古","21":"辽宁","22":"吉林","23":"黑龙江","31":"上海","32":"江苏","33":"浙江","34":"安徽","35":"福建","36":"江西","37":"山东","41":"河南","42":"湖北","43":"湖南","44":"广东","45":"广西","46":"海南","50":"重庆","51":"四川","52":"贵州","53":"云南","54":"西藏","61":"陕西","62":"甘肃","63":"青海","64":"宁夏","65":"新疆","71":"台湾","81":"香港","82":"澳门","91":"国外"}
    idcard=str(idcard)
    idcard=idcard.strip()
    idcard_list=list(idcard)
    #地区校验
    if(not area[(idcard)[0:2]]):
      print Errors[4]
    #15位身份号码检测
    if(len(idcard)==15):
      if((int(idcard[6:8])+1900) % 4 == 0 or((int(idcard[6:8])+1900) % 100 == 0 and (int(idcard[6:8])+1900) % 4 == 0 )):
        erg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')#//测试出生日期的合法性
      else:
        ereg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')#//测试出生日期的合法性
      if(re.match(ereg,idcard)):
        print Errors[0]
      else:
        print Errors[2]
    #18位身份号码检测
    elif(len(idcard)==18):
      #出生日期的合法性检查
      #闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
      #平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
      if(int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10])%4 == 0 )):
        ereg=re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')#//闰年出生日期的合法性正则表达式
      else:
        ereg=re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')#//平年出生日期的合法性正则表达式
      #//测试出生日期的合法性
      if(re.match(ereg,idcard)):
        #//计算校验位
        S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(idcard_list[11])) * 9 + (int(idcard_list[2]) + int(idcard_list[12])) * 10 + (int(idcard_list[3]) + int(idcard_list[13])) * 5 + (int(idcard_list[4]) + int(idcard_list[14])) * 8 + (int(idcard_list[5]) + int(idcard_list[15])) * 4 + (int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(idcard_list[8]) * 6 + int(idcard_list[9]) * 3
        Y = S % 11
        M = "F"
        JYM = "10X98765432"
        M = JYM[Y]#判断校验位
        if(M == idcard_list[17]):#检测ID的校验位
          print Errors[0]
          return 1
        else:
          print Errors[3]
      else:
        print Errors[2]
    else:
      print Errors[1]
    return 0

'''人脸检测（使用opencv内置方法）'''
def face_detect_opencv(image, ifshowImg = 0, ifshowLable = 0):#imagePath
    cascPath = 'haarcascade_frontalface_default.xml'
    #创建haar cascade
    faceCascade = cv2.CascadeClassifier(cascPath)
    #读图
#     image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #使用opencv检测人脸
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    print "Found {0} faces!".format(len(faces))
    #显示图像
    if ifshowImg == 1:
        for (x, y, w, h) in faces:
            #显示脸框
            showFaceIcon(x, y, w, h, image)
            if ifshowLable == 1:
                #显示模拟标签
                showLabel(x, y, w, h, image)
        cv2.imshow("Faces found by opencv", image)
        cv2.waitKey(0)
    return faces

'''人脸检测（使用腾讯优图api）'''
def face_detect_youtu(imagePath, ifshowImg = 0, ifshowLable = 0):
    youtu = getYoutuObject()
    ret = youtu.DetectFace(imagePath)
    #读图
    image = cv2.imread(imagePath)
    faces = [(int(i['x']),int(i['y']),int(i['width']),int(i['height'])) for i in ret['face']]
    print "Found {0} faces!".format(len(faces))
    #显示图像
    if ifshowImg == 1:
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            #显示脸框
            showFaceIcon(x, y, w, h, image)
            if ifshowLable == 1:
                #显示模拟标签
                showLabel(x, y, w, h, image)
        cv2.imshow("Faces found by youtu", image)
        cv2.waitKey(0)
    return faces

'''人脸识别（使用腾讯优图api）'''
def face_recognize_youtu(faceImage, sim_threshold = 60):
    iconDir = '../Icons/'
    iconTempDir = '../IconsTemp/'
    #图片暂存
    if not os.path.exists(iconTempDir):
        os.makedirs(iconTempDir)
    iconTempPath = os.path.join(iconTempDir, 'iconTemp.jpg')
    cv2.imwrite(iconTempPath, faceImage)
    try:
        #将con设定为全局连接
        con = mdb.connect('localhost', 'root', 'mysql', 'faceSys',charset='utf8');
        #获取youtu对象
        youtu = getYoutuObject()
        with con:
            #获取连接的cursor
            cur = con.cursor()
            cur.execute("select person_id from personList")
            person_ids = cur.fetchall()[0]
            for person_id in person_ids:
                iconPath = os.path.join(iconDir, person_id + '.png')
                #todo
                sim = youtu.FaceCompare(iconTempPath, iconPath)['similarity']
                if sim > sim_threshold:
                    print 'recognize successfully'
                    cur.execute("select * from personList where person_id = %s" % person_id)
                    data = cur.fetchall()[0]
                    info = {}
                    info['name'] = data[1]
                    info['sex'] = data[3]
                    info['age'] = data[4]
                    info['area'] = data[5]
                    return info
            return None
    except mdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        con.close()
    return 0

'''人脸面部属性分析（使用腾讯优图api'''
def face_analyse_youtu(faceImage):
    iconDir = '../Icons/'
    iconTempDir = '../IconsTemp/'
    #图片暂存
    if not os.path.exists(iconTempDir):
        os.makedirs(iconTempDir)
    iconTempPath = os.path.join(iconTempDir, 'iconTemp.jpg')
    cv2.imwrite(iconTempPath, faceImage)
    #获取youtu对象
    youtu = getYoutuObject()
    ret = youtu.DetectFace(iconTempPath, mode = 1)
    if len(ret['face']) != 1:
        print '人脸检测失败!'
        return None
#         raise ValueError
    else:
        print '人脸检测成功!'
        feature = {}
        feature['sex'] = int(ret['face'][0]['gender'])
        feature['age'] = int(ret['face'][0]['age'])
        feature['face'] = int(ret['face'][0]['expression'])
        feature['beauty'] = int(ret['face'][0]['beauty'])
        #对属性进行格式化
        if feature['sex'] > 55 :
            feature['sex'] = 'male'
        else:
            feature['sex'] = 'female'
        # get expession(degree of smile)
        if feature['face'] > 0 and feature['face'] < 20:
            feature['face'] = 'chuckle'
        elif feature['face'] >= 20 and feature['face'] < 50:
            feature['face'] = 'smile'
        else:
            feature['face'] = 'laugh'
        if feature['face'].find(' ') != -1:
            feature['face'] = feature['face'].split(' ')
            feature['face'] = '\n'.join(feature['face'])
        return feature

'''目标追踪'''
def object_track():
    return 0

'''静态人脸检测'''
def staticFaceRun(imagePath):
    #读图
    image = cv2.imread(imagePath)
    #人脸检测
#     faces = face_detect_youtu(imagePath)
    faces = face_detect_opencv(image)
    for (x, y, w, h) in faces:
#         #显示脸框
#         showFaceIcon(x, y, w, h, image)
        imageIcon = image[y:y+h, x:x+w]
        #人脸识别
        info = face_recognize_youtu(imageIcon)
        if info is not None:
            #若识别成功，显示个人信息
            image = showInfo_PIL(x, y, w, h, image, info)
            #显示脸框
            showFaceIcon(x, y, w, h, image)
        else:
            #否则，分析并显示面部属性
            feature = face_analyse_youtu(imageIcon)
            #显示面部属性
            if feature is not None:
                showFeature(x, y, w, h, image, feature)
                #显示脸框
                showFaceIcon(x, y, w, h, image)
    cv2.imshow("Faces found by staticFaceRun", image)
    cv2.waitKey(0)
    return 1

'''动态人脸检测'''
def dynamicFaceRun():
    video_capture = cv2.VideoCapture(0)
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        #图片暂存
        if not os.path.exists(iconTempDir):
            os.makedirs(iconTempDir)
        iconTempPath = os.path.join(iconTempDir, 'iconFrame.jpg')
        cv2.imwrite(iconTempPath, frame)
        if not ret: continue
        #人脸检测
        faces = face_detect_opencv(frame)
        for (x, y, w, h) in faces:
            #显示脸框
            showFaceIcon(x, y, w, h, frame)
            imageIcon = frame[y:y+h, x:x+w]
            #人脸识别
            info = face_recognize_youtu(imageIcon)
            if info is not None:
                #若识别成功，显示个人信息
                frame = showInfo_PIL(x, y, w, h, frame, info)
            else:
                #否则，分析并显示面部属性
                feature = face_analyse_youtu(imageIcon)
                #显示面部属性
                if feature is not None:
                    showFeature(x, y, w, h, frame, feature)
        # Display the resulting frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()
    return 0

'''方法测试'''
# newPersonList()
# newPerson('sean新', '445202199102170651', 'abba.png')
#face_detect_opencv('must.jpg', ifshowLable = 1, ifshowLable = 1)

staticFaceRun('2.jpg')#must.jpg(1.3), must21.jpg(1.2), must22.png(1.2), 2.jpg, abba.png(1.1)
# dynamicFaceRun()
