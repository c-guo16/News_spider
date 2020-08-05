import requests
import re
import urllib
import time


class Top(object):
    def __init__(self, banner):
        self.banner = banner
        self.titles = []
        self.summary = []
        self.nickname=[]
        self.text=[]
        self.session=requests.session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"}

    def get_top(self, url):
        r = self.session.get(url, headers=self.headers)
        html = r.text
        # compiled_re=re.compile(r'<td class="td-02">(.*?)<a href=(.*?)>(.*?)</a></td>',flags=re.DOTALL)
        # raw=compiled_re.findall(html)
        raw = re.findall(r'<td class="td-02">(.*?)</td>', html,flags=re.DOTALL)
        cnt=0
        for i in raw:
            cnt+=1
            raw1=re.findall(r'<a href="(.*?)">(.*?)</a>|<a href_to="(.*?)">(.*?)</a>', i,flags=re.DOTALL)
            # print(i)
            # print(raw1)
            assert len(raw1)==1
            self.titles.append(raw1[0][1])
            link = 'http://s.weibo.com' + raw1[0][0]
            time.sleep(5)# 暂停5秒
            self.get_news(link)
            print(cnt,' done.')
            print("标题：", self.titles[-1])
            print("摘要：", self.summary[-1])
            print("昵称：", self.nickname[-1])
            print("正文：", self.text[-1])
            print()
            with open('./weibo/{}.txt'.format(cnt),'w',encoding='utf-8') as f:
                f.write(str(cnt)+'\n')
                f.write(self.titles[-1]+'\n')
                f.write(self.summary[-1]+'\n')
                f.write(self.nickname[-1]+'\n')
                f.write(self.text[-1]+'\n')


    def get_news(self, link):
        r = self.session.get(link, headers=self.headers)
        while r.status_code!=200:   # 防止封ip，多次尝试
            time.sleep(10)
            r = self.session.get(link, headers=self.headers)

        html = r.text
        # 解析导语：
        raw = re.search(r'<strong>导语：</strong>(.*?)</p>', html, flags=re.DOTALL)
        if raw:
            self.summary.append(raw[1])
        else:
            self.summary.append("NONE")
        # print(self.summary)

        #看是否有"文章"标签，若有则爬取文章，否则爬取第一篇微博：
        wenzhangtag=re.search(r'href="/article(.*?)" title="文章">文章</a>',html,flags=re.DOTALL)
        if wenzhangtag:
            self.get_wenzhang('http://s.weibo.com/article'+wenzhangtag.group(1))
        else:
            self.get_first_full_weibo(html)

    def get_wenzhang(self,link):
        print("文章！！！")
        r = self.session.get(link, headers=self.headers)
        while r.status_code != 200:  # 防止封ip，多次尝试
            time.sleep(10)
            r = self.session.get(link, headers=self.headers)

        html = r.text

        link_article=re.search(r'<h3><a href="(.*?)"',html,flags=re.DOTALL).group(1)
        r = self.session.get(link_article, headers=self.headers)
        while r.status_code != 200:  # 防止封ip，多次尝试
            time.sleep(10)
            r = self.session.get(link_article, headers=self.headers)

        html = r.text
        # 微博文章格式不统一，没办法爬！！
        self.nickname.append("NONE")
        self.text.append("NONE")

    def get_first_full_weibo(self,html):
        # 解析第一篇微博：
        raw = re.search(r'feed_list_content_full(.*?)<!--card解析-->|feed_list_content(.*?)<!--card解析-->', html,
                        flags=re.DOTALL)
        if raw:
            raw1 = re.search(r'nick-name="(.*?)">(.*?)</p>', raw[0], flags=re.DOTALL)
            self.nickname.append(raw1[1])
            clean_text = re.sub(r'<.*?>', '', raw1[2])
            self.text.append(clean_text)
        else:
            self.nickname.append("NONE")
            self.text.append("NONE")




if __name__ == '__main__':
    # 爬取热搜
    realtimehot = Top('热点')
    realtimehot.session=weibo.session()
    realtimehot.get_top("http://s.weibo.com/top/summary?cate=realtimehot")

