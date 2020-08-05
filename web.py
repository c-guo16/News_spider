#!/usr/bin/env python
# -*- coding: utf-8 -*-      
import urllib.request, urllib.error, urllib.parse
import http.cookiejar
import re,requests.sessions

def savedata(html_, filename='C:\\Users\guocheng\PycharmProjects\spider\local_html.html'):
    with open(filename, 'wb')as local_file:  # 写入本地文件,wb二进制
        local_file.write(html_)  # 写入的是比特流


def gethtml(url):
    page = urllib.request.urlopen(url, timeout=3)  # 设置超时
    html_ = page.read()
    for i in ["utf-8","gbk","ascii"]:
        try:
            return html_.decode(i) # byte流解码字符串
        except UnicodeDecodeError as e:
            print(e.reason)
            continue




def getimage(html):  # 抓取图片
    reg = r'src="(.+?\.jpg) pic_ext"'
    imgre = re.compile(reg)
    imglist = re.findall(imgre, html)
    return imglist


def getmusic(html):
    reg = r'src="(.+?\.mp3)"'
    musre = re.compile(reg)
    muslist = re.findall(musre, html)
    return muslist


def log_in_chinaunix(name, password):
    try:
        form = {"username": name, "password": password}#构造提交的表单
        form1 = urllib.parse.urlencode(form).encode()#表单数据编码
        url = "http://bbs.chinaunix.net/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LA2rI"
        req = urllib.request.Request(url, form1)#构造请求
        req.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36")

        cookie=http.cookiejar.CookieJar()#构造cookiejar对象
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
        urllib.request.install_opener(opener)#安装全局cookie处理器

        data = urllib.request.urlopen(req).read()
        savedata(data, 'C:\\Users\guocheng\PycharmProjects\spider\local_html_2.html')

    except urllib.error.URLError as e:
        print(e.reason)

def log_in_Tsinghua(name, password):
    try:
        form = {"userid": name, "userpass": password, "submit1": "登录"}#构造提交的表单
        form1 = urllib.parse.urlencode(form).encode()#表单数据编码
        url = r"https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp"
        req = urllib.request.Request(url, form1)#构造请求
        req.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36")

        cookie=http.cookiejar.CookieJar()#构造cookiejar对象
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
        urllib.request.install_opener(opener)#安装全局cookie处理器

        data = urllib.request.urlopen(req).read()
        savedata(data, 'C:\\Users\guocheng\PycharmProjects\spider\local_html_Tsinghua.html')

    except urllib.error.URLError as e:
        print(e.reason)

def log_in_zhihu(name, password):
    try:
        form = {"userid": name, "userpass": password, "submit1": "登录"}#构造提交的表单
        form1 = urllib.parse.urlencode(form).encode()#表单数据编码
        url = r"https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp"
        req = urllib.request.Request(url, form1)#构造请求
        req.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36")

        cookie=http.cookiejar.CookieJar()#构造cookiejar对象
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
        urllib.request.install_opener(opener)#安装全局cookie处理器

        data = urllib.request.urlopen(req).read()
        savedata(data, 'C:\\Users\guocheng\PycharmProjects\spider\local_html_Tsinghua.html')

    except urllib.error.URLError as e:
        print(e.reason)
def search_360(keyword):  # 搜索引擎函数
    result = urllib.request.urlopen("https://www.so.com/s?q=" + urllib.request.quote(keyword)).read()  # 构造GET请求并搜索
    savedata(result)
    return result


def re_findall(re_word, string):  # 匹配函数
    re_compiled = re.compile(re_word,flags=re.S)  # 正则表达式预编译
    result = re.findall(re_compiled,string)  # 找出所有结果
    return result


def main_():
    for i in range(100):  # 请求100次
        try:
            log_in_chinaunix("c_guo16", "tiancaigdt")
            print(i)
        except Exception as e:
            print('第%s次i错误' % i)


# result=search_360("红衣主教").decode() # 获得搜索结果页html代码
# re_findall("a href=\"http://.*?天主教",result)
main_()
# print(html)
