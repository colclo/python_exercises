'''
Created on 2017年3月21日

@author: colclo
用于抓取lofter中文章的，其他任何页面都不适用！私用扒文脚本！╮(╯_╰)╭
BUG：
    1.抓取文章url时会有个别漏掉的情况，原因就是BUG2
    2.如果文章列表页面是无标题的，则抓不到该文章url（不过这个目前无所谓，没有标题的肯定不是小说内容了，我本来也不太需要这些闲聊）╮(╯_╰)╭
    3.通用性太弱，lo主稍微换个主页模板这脚本就废了（心好痛）
'''
from html.parser import HTMLParser
from urllib import request

#设置需要抓取的url
url = 'http://lynn19820125.lofter.com/'

#全局变量，存储该页面内文章的url
article_list = []

#全局变量，存储翻页url
global nextpageurl
nextpageurl = ''

#全局变量，存储抓取来的页面信息
catch_data = ''

#定义解析文章url和翻页url的类
class article_list_Parser(HTMLParser):
    
    def __init__(self):
        super(article_list_Parser, self).__init__()
        self.flag = False
        self.verbatim = 0
        
    def handle_starttag(self, tag, attrs):
        #文章的url存储在一个<h2 class='ttl'><a href='url'></a></h2>的标签中
        if tag == 'h2' and attrs:
            if self.flag == True:
                #进入了div的内层，verbatim+1
                self.verbatim += 1
            for k,v in attrs:
                if k == 'class' and v == 'ttl':
                    self.flag = True        #碰见了<h2 class='ttl'>的标签时，将flag设置为True
        if tag == 'a' and attrs:
            if self.flag == True:
                for k,v in attrs:
                    if k == 'href':
                        article_list.append(v)
            #翻页信息存储在一个<a class="next" href="?page=2&t=1488016390068">下一页 &gt;</a>的标签中
            else:       #此时的flag肯定不是true
                if attrs[0][0]=='class' and attrs[0][1] =='next':
                    global nextpageurl
                    nextpageurl = url+attrs[1][1]

    def handle_endtag(self, tag):
        if tag == 'h2':
            if self.verbatim == 0:
                self.flag = False
            if self.flag == True:
                self.verbatim -= 1

#抓取页面内的url
if nextpageurl=='':     #如果nextpageurl是空的，则nextpageurl=url
    nextpageurl = url

#定义解析parser
parser = article_list_Parser()

while True:
    #定义一个临时变量
    temp = nextpageurl
    #发送请求
    req = request.Request(nextpageurl)
    with request.urlopen(req) as f:
        catch_data = f.read().decode('utf-8')
    parser.feed(catch_data)
    if temp == nextpageurl:
        break
    print(nextpageurl)
    print('抓取到%d条文章url' % len(article_list))

print('共抓取到%d条文章url' % len(article_list))
 
#==========================以上为抓取文章url部分=========================

#==========================下面开始抓文章内容============================

#定义临时变量：文章标题，文章内容，文章时间
global title
title = ''
global content
content = []
global date
date = ''

global page_detail_list 
page_detail_list = []

#定义解析文章的类
class article_Parser(HTMLParser):
    def __init__(self):
        super(article_Parser, self).__init__()
        self.h2_flag = False
        self.div_flag = False
        self.a_flag = False
        self.verbatim = 0
        
    def handle_starttag(self, tag, attrs):
        #文章标题<h2 class="ttl"><a href="#">标题</a></h2>
        if tag == 'h2' and attrs:
            if attrs[0][1] == 'ttl':
                self.h2_flag = True
        #正文<div class="txtcont">。。。。。。。
        if tag == 'div' and attrs:
            if self.div_flag == True:
                self.verbatim += 1
            else:
                for k,v in attrs:
                    if k == 'class' and v == 'txtcont':
                        self.div_flag = True
        #时间<a class="more" href="#">2017-02-28 / 评论：13 / 热度：172</a>没在正文的div里面
        if tag == 'a' and attrs:
            for k,v in attrs:
                if k == 'class' and v == 'more':
                    self.a_flag = True
    
    def handle_data(self, data):
        if self.h2_flag == True:
            global title
            title = data
        if self.div_flag == True:
            global content
            content.append(data)
        if self.a_flag == True:
            global date
            date = data[:10]
            

    def handle_endtag(self, tag):
        if tag == 'h2':
            self.h2_flag = False
        if tag == 'div':
            if self.verbatim == 0:
                self.div_flag = False
            if self.div_flag == True:
                self.verbatim -= 1
        if tag == 'a' :
            self.a_flag = False

#定义文章的解析对象parser
parser = article_Parser()

#定义解析每一个文章url的方法
def parse_page(page_url):
    req = request.Request(page_url)
    with request.urlopen(req) as f:
        parser.feed(f.read().decode('utf-8'))
    global title 
    global content
    global date
    d = {'title':title, 'content':content, 'date':date}
    global page_detail_list
    page_detail_list.append(d)

#遍历artist_list开始解析文章：
for page_url in article_list:
    parse_page(page_url)
    
#最终将page_detail_list输出：
with open(r'C:\Users\Administrator\Desktop\result.txt','w',encoding='utf-8') as w:
    for dict in page_detail_list:
        w.write(dict['title']+'\t')
        w.write(dict['date']+'\n')
        w.write(''.join(dict['content']))
        w.write('\n\n\n')
        w.flush()
        print(dict['title'])