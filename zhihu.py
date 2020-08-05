import requests
import re
import json
import urllib
import time


class Top(object):
    def __init__(self, banner,outf):
        self.banner = banner
        self.titles = []
        self.summary = []
        self.nickname=[]
        self.text=[]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"}
        self.outfile = outf

        self.data=[]


    def get_top(self, url):
        r = requests.get(url, headers=self.headers)
        html = r.text
        # compiled_re=re.compile(r'<td class="td-02">(.*?)<a href=(.*?)>(.*?)</a></td>',flags=re.DOTALL)
        # raw=compiled_re.findall(html)
        html=re.search(r'<h2 class="cc-dc-Cb">热榜<small>(.*?)<h2 class="cc-dc-Cb">历史数据<small>',html,flags=re.DOTALL)[0]
        raw = re.findall(r'<td class="al"><a href="(.*?)".*?>(.*?)</a></td>', html,flags=re.DOTALL)
        ccc=0
        for i in raw:
            ccc+=1
            if ccc>10:
                break
            link=i[0]
            title=i[1]
            print(title)
            self.titles.append(title)
            time.sleep(5)
            self.get_answers(link)

            print(self.titles[-1])
            print("摘要：",self.summary[-1])
            cnt=1
            for ans in self.text[-1]:
                print("第{}个回答：".format(cnt),ans)
                cnt+=1

            self.data.append({})
            self.data[-1]['title']=self.titles[-1]
            self.data[-1]['summary']=self.summary[-1]
            cnt = 1
            for ans in self.text[-1]:
                self.data[-1]['ans_{}'.format(cnt)]=ans
                cnt+=1

    def get_answers(self, link):
        r = requests.get(link,verify=False, headers=self.headers)
        html = r.text
        summary_raw=re.search(r'collapsedAnswerCount.*?"excerpt":"(.*?)"',html)
        if not summary_raw or summary_raw.group(1)=="":
            self.summary.append('NONE')
        else:
            self.summary.append(summary_raw.group(1))
        answer_raw_set=re.findall('<span class="RichText ztext CopyrightRichText-richText" itemProp="text">(.*?)</span>',html,flags=re.DOTALL)
        self.text.append([])
        for answer_raw in answer_raw_set:
            answer_raw=re.sub('</p>','\n',answer_raw)
            answer_raw=re.sub('<.*?>','',answer_raw)
            self.text[-1].append(answer_raw)

    def out_put(self):
        for i in range(len(self.titles)):
            with open(self.outfile,'w',encoding='utf-8') as f:
                f.write(json.dumps(self.data,ensure_ascii=False,indent=2))



if __name__ == '__main__':
    realtimehot = Top('知乎热榜','./zhihu/zhihu.txt')
    realtimehot.get_top("https://tophub.today/n/mproPpoq6O")
    realtimehot.out_put()