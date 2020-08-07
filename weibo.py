import requests
import re,json,sys
import urllib3
from opencc import OpenCC
import time
from weibologin import LoginWeibo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BaiduSummary(object):
    def __init__(self):
        self.apikey="855G09gOZBApda9nGdikwWGR"
        self.secretkey="4ebG0xrGHlYeVTK81fkE6YrG65ZACaj4"
        self.access_token="24.a0720b6a0d48490b34555ce3574cc95c.2592000.1596961595.282335-21238388" # 有效期一个月！
        self.header={'Content-Type': 'application/json'}

    def get_summary(self,content,title):
        if len(title)>200:
            title=title[0:200]
        if len(content)>3000:
            content=content[0:3000]
        max_summary_len=int(len(content)/15)+100   # 将0-3000映射到100-300
        data_json = {
            "title": title,
            "content":content,
            "max_summary_len": max_summary_len
        }
        url="https://aip.baidubce.com/rpc/2.0/nlp/v1/news_summary?charset=UTF-8&access_token="+self.access_token
        res = requests.post(url, data=json.dumps(data_json), headers=self.header)
        res=json.loads(res.text)
        if "summary" not in res:
            return ""
        res=res["summary"]
        return res


class Spider(object):
    def __init__(self, banner,date):
        self.banner = banner
        self.titles = []
        self.summary = []
        self.nickname=[]
        self.text=[]
        self.raw_text=[]
        self.type=[]
        self.classification=[]
        self.data=[]
        self.date=date
        self.total_item_per_topic=5     # 每个话题最多爬几个微博或文章
        self.session=None
        self.summary_generator=BaiduSummary()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"}

    def get_top(self, url):
        r = self.session.get(url, headers=self.headers,verify=False)
        html = r.text
        # compiled_re=re.compile(r'<td class="td-02">(.*?)<a href=(.*?)>(.*?)</a></td>',flags=re.DOTALL)
        # raw=compiled_re.findall(html)
        raw = re.findall(r'<td class="td-02">(.*?)</td>', html,flags=re.DOTALL)
        cnt=0
        for i in raw:
            cnt+=1
            if cnt==500:
                break
            raw1=re.findall(r'<a href="(.*?)".*?>(.*?)</a>', i,flags=re.DOTALL)
            # print(i)
            # print(raw1)
            title=''
            if len(raw1)==1:
                title=raw1[0][1]
            else:
                raw1=re.findall(r'<a href_to="(.*?)" href=(.*?)word="(.*?)"',i,flags=re.DOTALL)
                title=raw1[0][2]
            title=re.sub('#','',title)
            self.titles.append(title)

            link = 'http://s.weibo.com' + raw1[0][0]
            time.sleep(5)# 暂停5秒
            self.get_news(link)
            # 最后处理一下一些域，防止空格，半角逗号之类的造成干扰
            self.summary[-1]=re.sub(',','，',self.summary[-1])
            self.titles[-1]=re.sub(',','，',self.titles[-1])
            self.data.append({})
            self.data[-1]["topic"]=self.titles[-1]
            self.data[-1]["intro"]=self.summary[-1]
            self.data[-1]["classification"]=self.classification[-1]
            self.data[-1]["arr"]=[]
            for textinfo in self.text[-1]:
                # 调用百度的接口生成摘要：
                time.sleep(0.5)# qps的要求
                if "content" not in textinfo:
                    continue
                textinfo["content"]=textinfo["content"].replace("/u200B/g",'')
                if textinfo["content"]=="":
                    continue
                textinfo["summary"]=self.summary_generator.get_summary(textinfo["content"],self.titles[-1])
                self.data[-1]["arr"].append(textinfo)

            print(cnt,' done.')
            print("标题：", self.titles[-1])
            print("摘要：", self.summary[-1])
            # print("正文：", self.text[-1])
            print()


    def get_news(self, link):
        r = self.session.get(link, headers=self.headers,verify=False)
        while r.status_code!=200:   # 防止封ip，多次尝试
            time.sleep(10)
            r = self.session.get(link, headers=self.headers,verify=False)

        html = r.text
        # 解析导语：
        raw = re.search(r'<strong>导语：</strong>(.*?)</p>', html, flags=re.DOTALL)
        if raw:
            self.summary.append(raw.group(1))
        else:
            self.summary.append("")
        # 解析分类：
        self.get_classification(html)

        #看是否有"文章"标签，若有则爬取文章(不够再爬微博)，否则爬取微博：
        self.text.append([])
        self.raw_text.append([])
        wenzhangtag=re.search(r'href="/article(.*?)" title="文章">文章</a>',html,flags=re.DOTALL)
        if wenzhangtag:
            wenzhang_num=self.get_wenzhang('http://s.weibo.com/article'+wenzhangtag.group(1),full_html=html)
            self.get_full_weibo(html,self.total_item_per_topic-wenzhang_num)
        else:
            # 没有“文章”标签，则肯定有“热门”标签！
            remen=re.search(r'href="/hot(.*?)" title="热门">热门</a></li>',html,flags=re.DOTALL)
            remen_link='http://s.weibo.com/hot'+remen.group(1)
            if remen:
                r = self.session.get(remen_link, headers=self.headers,verify=False)
                while r.status_code != 200:  # 防止封ip，多次尝试
                    time.sleep(10)
                    r = self.session.get(remen_link, headers=self.headers,verify=False)
                html = r.text
            self.get_full_weibo(html,self.total_item_per_topic)

    def get_wenzhang(self,link,full_html):
        r = self.session.get(link, headers=self.headers,verify=False)
        while r.status_code != 200:  # 防止封ip，多次尝试
            time.sleep(10)
            r = self.session.get(link, headers=self.headers,verify=False)

        html = r.text

        cnt=0
        link_article=re.findall(r'<h3><a href="https://weibo.com/ttarticle/p/show(.*?)"',html,flags=re.DOTALL)
        for raw in link_article:
            raw = 'https://weibo.com/ttarticle/p/show' + raw
            r = self.session.get(raw, headers=self.headers,verify=False)
            while r.status_code != 200:  # 防止封ip，多次尝试
                time.sleep(10)
                r = self.session.get(raw, headers=self.headers,verify=False)
            html = r.text
            try:
                article_raw = re.search(
                    r'<div class="WB_editor_iframe_new" node-type="contentBody"(.*?)<div class="DCI_v2 clearfix">',
                    html, flags=re.DOTALL)
                article_raw = re.sub(r'<span class="picinfo">(.*?)</span>', '', article_raw.group(0), flags=re.DOTALL)
                article_raw = re.sub(r'<(.*?)>|\n', '', article_raw, flags=re.DOTALL)
                article_raw = re.sub(r' +?', '', article_raw, flags=re.DOTALL)
                author = re.search(r"CONFIG\['onick'\] = '(.*?)';", html)

                raw_text = re.sub('【.*?】', '', article_raw)
                raw_text = re.sub('（.*?）', '', raw_text)
                # 判重：
                repeat = False
                if len(raw_text) > 50:
                    for prev_text in self.raw_text[-1]:
                        if abs(len(prev_text) - len(raw_text)) <= 5:  # 通过字数判重！
                            repeat = True
                            break
                if repeat:
                    continue

                self.raw_text[-1].append(raw_text)

                self.text[-1].append({})
                self.text[-1][-1]["author"] = author.group(1)
                self.text[-1][-1]["content"] = article_raw
                self.text[-1][-1]["category"] = '文章'
                self.text[-1][-1]["summary"] = ''
                self.text[-1][-1]["keywords"] = ''
                cnt+=1
                if cnt>=self.total_item_per_topic:
                    break
            except Exception:
                continue

        return cnt


    def get_classification(self,html):
        raw=re.search(r'<dt>分类：</dt>.*?<dd>(.*?)</dd>',html,flags=re.DOTALL)
        self.classification.append([])
        if raw:
            raw=raw.group(1)
            raw=re.findall(r'<a class="tag".*?;">(.*?)</a>',raw,flags=re.DOTALL)
            for item in raw:
                self.classification[-1].append(item)

    def get_full_weibo(self, html,num):
        if num<=0:
            return
        # 解析微博：
        raw = re.findall(r'"feed_list_content"(.*?)d解析-->', html,flags=re.DOTALL)
        for raw1 in raw:
            if raw1:
                raw_full=re.search(r'"feed_list_content_full"(.*?)<!--car',raw1,flags=re.DOTALL)
                if raw_full:
                    raw1=raw_full.group(0)

                raw1 = re.search(r'nick-name="(.*?)".*?>(.*?)</p>', raw1, flags=re.DOTALL)
                if not raw1:
                    continue
                clean_text = re.sub(r'<.*?>', '', raw1.group(2))
                clean_text=re.sub(' +?','',clean_text)
                clean_text = re.sub('\n', '', clean_text)
                clean_text = re.sub('收起全文d', '', clean_text)
                clean_text = re.sub('L(.*?)的..视频', '', clean_text)

                raw_text = re.sub('【.*?】','',clean_text)
                raw_text = re.sub('（.*?）', '', raw_text)
                # 判重：
                repeat=False
                if len(raw_text)>50:
                    for prev_text in self.raw_text[-1]:
                        if abs(len(prev_text)-len(raw_text))<=5:    # 通过字数判重！
                            repeat=True
                            break
                if repeat:
                    continue

                self.raw_text[-1].append(raw_text)

                self.text[-1].append({})
                self.text[-1][-1]["author"] = raw1.group(1)
                self.text[-1][-1]["content"] =clean_text
                self.text[-1][-1]["category"] = '微博'
                self.text[-1][-1]["summary"] = ''
                self.text[-1][-1]["keywords"] = ''
                num-=1
                if num==0:
                    break

    def out_put(self):
        path="./weibo/{}_{}.txt".format(self.date,self.banner)
        path_sim = "./weibo/{}_{}_sim.txt".format(self.date, self.banner)
        with open(path,'w',encoding='utf-8') as f:
            f.write(json.dumps(self.data,ensure_ascii=False,indent=2))

        # 繁简转换
        INPUT = open(path,'r',encoding='utf-8')
        a = INPUT.read()
        b = OpenCC('t2s').convert(a)
        OUTPUT = open(path_sim, 'w',encoding='utf-8')
        OUTPUT.write(b)
        OUTPUT.close()



if __name__ == '__main__':
    # 登录
    username = 'xxx'  # 微博账号
    password = 'xxx'  # 微博密码
    weibo = LoginWeibo(username, password)
    weibo.login()

    # 爬取热搜
    realtimehot = Spider('resou', sys.argv[1])  # 日期当参数传入
    realtimehot.session=weibo.session
    realtimehot.get_top("http://s.weibo.com/top/summary?cate=realtimehot")
    realtimehot.out_put()

    # 爬取要闻
    realtimehot = Spider('yaowen', sys.argv[1])  # 日期当参数传入
    realtimehot.session = weibo.session
    realtimehot.get_top("http://s.weibo.com/top/summary?cate=socialevent")
    realtimehot.out_put()

