import re
from html.parser import HTMLParser
from urllib import request
from urllib.error import URLError
import jieba
import json
import time

# 正则表达式预编译：
re_time = re.compile("\d{4}年.*?:\d{2}", flags=re.S)
re_page = re.compile("[上下]一页.*?[上下]一页", flags=re.S)
re_pagenum = re.compile("\d+", flags=re.S)
re_url_finance = re.compile(r"http://(?:opinion|legal|military|politics|finance|money)\.people\.com\.cn/n1/.*?\.html", flags=re.S)
visited = set() #访问过的url
dic={}          #倒排索引字典
count = [0]

#新闻类对象：
class News(object):
    def __init__(self):
        self.title = None #新闻标题
        self.time = None #新闻发布日期
        self.text = None  #新闻的正文内容

#获取html标签属性：
def _attr(attrlist, attrname):
    for attr in attrlist:
        if attr[0] == attrname:
            return attr[1]
    return None

#正则表达式匹配：
def re_findall(re_word, string):  # 匹配函数
    re_compiled = re.compile(re_word,flags=re.S)  # 正则表达式预编译
    result = re.findall(re_compiled,string)  # 找出所有结果
    return result

#html解析类：
class MyHTMLParser(HTMLParser):

    def __init__(self,ifFirstPage):
        HTMLParser.__init__(self)
        self.iftitle=False
        self.iftext=False
        self.iftime=False
        self.ifFirst=ifFirstPage
        self.pageNum=1
        self.news=News()

    #匹配开始标签：
    def handle_starttag(self, tag, attrs):
        if tag == 'div' and _attr(attrs, 'class'):
            string=_attr(attrs, 'class')
            if re_findall(".*text_title$", string):       #标题开始
                self.iftitle=True

            if string=="box01" and self.iftitle:
                self.iftime=True

            if re_findall(".*text_con_left$", string):      #正文开始
                self.iftext = True

    #通过匹配注释判断标题及正文是否结束：
    def handle_comment(self, data):
        if re_findall(".*text left end.*", data) and self.iftext:
            self.iftext=False
        if re_findall(".*text_title end.*", data) and self.iftitle:
            self.iftitle = False

    def handle_endtag(self, tag):
        if self.lasttag=="/div" and self.iftime:
            self.iftime=False

    #提取内容
    def handle_data(self, data):
        if data.strip():    #去除空格
            if self.lasttag=='h1' and self.iftitle and self.ifFirst: #标题
                #print("Encountered title  :", data)
                self.news.title=data

            if self.iftime and self.ifFirst: #时间
                time = re.search(re_time, data)
                if time:
                    #print("Encountered time  :", time.group())
                    self.news.time=time.group()

            if self.lasttag=='p' and self.iftext:   #正文内容
                pageinfo = re.search(re_page, data)
                if pageinfo:
                    if self.ifFirst:  # 若是第一页，读取页数信息
                        num = re.search(re_pagenum, pageinfo.group())
                        self.pageNum=num.group().__len__()
                        #print("Encountered pageinfo  :", self.pageNum)
                else:
                    #print("Encountered text  :", data)
                    if self.news.text==None:
                        self.news.text =data
                    else:
                        self.news.text += data

def getNews(url,count,dic):
    # 获取并解析第一页
    praser = MyHTMLParser(True)
    praser.feed(request.urlopen(url).read().decode('GBK',"ignore"))

    # 根据第一页的页数信息，决定是否继续读取
    if praser.pageNum>1:
        for i in range(2,praser.pageNum+1):
            _url=url[:-5]+"-{}.html".format(i)
            print(_url)
            _praser = MyHTMLParser(False)
            _praser.feed(request.urlopen(_url).read().decode('GBK',"ignore"))
            praser.news.text+=_praser.news.text

    if praser.news.title and praser.news.time and praser.news.text:
        #将内容存入文件：

        count[0] =count[0] + 1  #累加计数
        if count[0]%100==0: #每爬100个休息五秒
            time.sleep(5)
            if count[0] % 300 == 0: #每300个保存一次
                end()

        r = '[’!"#$%&\'()*+,-./:;<=>?@\[\]^_`{|}~+，。、？；：‘’“”【】{}-—]'

        file = open('./news/{}.txt'.format(count[0]), 'w', encoding="utf-8")
        print(count[0])
        file.write(praser.news.title+"\n")
        file.write(praser.news.time + "\n")
        file.write(praser.news.text.replace("\t",""))
        file.close()
        title=re.sub(r," ",praser.news.title)
        text=re.sub(r," ",praser.news.text)
        list1=jieba.cut_for_search(title)
        list2 = jieba.cut_for_search(text)
        for item in list1:
            if item in dic:
                if dic[item][-1][0] == count[0]:
                    dic[item][-1][1] += 1
                else:
                    dic[item].append([count[0], 1])
            else:
                dic[item] = [[count[0], 1]]
        for item in list2:
            if item.strip():
                if item in dic:
                    if dic[item][-1][0]==count[0]:
                        dic[item][-1][1] += 1
                    else:
                        dic[item].append([count[0],1])
                else:
                    dic[item]=[[count[0], 1]]
    #print("题目：", praser.news.title)
    #print("时间：", praser.news.time)
    #print("内容：", praser.news.text)


def dfs(url):

    #if count[0]==1000:end()
    # 把该url添加进visited
    visited.add(url)

    try:
        # 该url没有访问过的话，则继续解析操作
        getNews(url,count,dic)

        #提取该页面其中所有的url
        html=request.urlopen(url).read().decode('GBK', "ignore")
        links = re.findall(re_url_finance,html)
        for link in links:
            if link not in visited:
                dfs(link)
    except URLError as e:
        print(e)
        return

#从断点读入已经爬取过的数据：
def init():
    file = open('urlSet.txt', 'r', encoding="utf-8")
    string=file.readline()[:-1]
    count[0]=int(string)
    string=file.readline()[:-1]
    while string:
        visited.add(string)
        string = file.readline()[:-1]
    file.close()
    file = open('dic.txt', 'r', encoding="utf-8")
    js = file.read()
    file.close()
    dic = json.loads(js)

#保存数据：
def end():
    file = open('urlSet.txt', 'w', encoding="utf-8")
    file.write(str(count[0]))
    file.write("\n")
    for i in visited:
        file.write(i)
        file.write("\n")
    file.close()
    file = open('dic.txt', 'w', encoding="utf-8")
    js = json.dumps(dic)
    file.write(js)
    file.close()

#转换txt为json格式
def handle_txt(num):
    context=[]
    for i in range(1,num+1):
        file = open(r'D:\Python_Project\mysite\Web_Django\news\{0}.txt'.format(i), 'r', encoding="utf-8")
        title=file.readline()
        time=file.readline()
        context.append({"id":str(i),"title":title,"time":time})

    with open(r"D:\Python_Project\mysite\data.json", 'w') as f:
        json.dump(context, f)


#init()
dfs(r"http://finance.people.com.cn")
dfs(r"http://money.people.com.cn")
dfs(r"http://politics.people.com.cn/")
dfs(r"http://military.people.com.cn/")
dfs(r"http://opinion.people.com.cn/")
dfs(r"http://legal.people.com.cn/")

end()

