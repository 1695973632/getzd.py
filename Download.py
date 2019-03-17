'''
没错，这就是爬虫程序，用来爬来自那万恶的百度的数据
然后我们要把搜索到的结果给写入numpy，然后再写入excel
文件中，你没听错是的，修改参数可以下载更多，关键看网速
'''

import pandas as pd
import numpy as np
import requests
from lxml import etree
from html.parser import HTMLParser
import re
import os

# 找出所有的标准问放到datas文件夹下
def read_excel(filename):
    standard_res = []
    value = pd.read_excel(filename).values
    for i in range(value.shape[0]):
        if value[i, 1] not in standard_res:
            standard_res.append(value[i, 1])
    return standard_res

# 通过一个标准问收集相似语句
def GetStdQLib(stdQ):
    sentences = []
    num = 0
    for i in range(100):
        word = "https://zhidao.baidu.com/search?lm=0&rn=10&pn=%d&fr=search&ie=gb2312&word=%s"%(i*10, stdQ)
        r = requests.get(word)
        html = etree.HTML(r.content)
        data_logs = html.xpath("//dt[@class='dt mb-4 line']/a[@class='ti']")
        for data_log in data_logs:
            content = etree.tostring(data_log, method='html').decode()
            infoEntry = HTMLParser().unescape(content)
            rstr = r'<a href=.* class="ti">(.*)</a>'
            p = re.compile(rstr, re.S)
            sentence = re.findall(p, infoEntry)[0].replace("<em>","").replace("</em>","").replace("...","")
            sentences.append(sentence)
            num += 1
            if num == 100:
                break
        if num == 100:
            break
    return sentences

# 根据标准问和相似语句收集采集20618条数据然后都保存在一个.npy文件里面
# 其实我相对而言更喜欢.csv文件，没错！但是为了让大家方便我还是保存npy，并显示进度吧，没错！
# 其中endloc的作用是输入上一次下载停的位置
def DownloadDatas(bfilename, endloc):
    myfile = [[], []]
    standard_res = read_excel(bfilename)
    if endloc != 0 and os.path.exists('./datas/download.npy'):
        arr = np.load('download.npy')
        loaded = arr.tolist()
        myfile += loaded
    for i in range(endloc, len(standard_res)):
        sentences = GetStdQLib(standard_res[i])
        for sentence in sentences:
            myfile[0].append(sentence)
            myfile[1].append(standard_res[i])
        np.save('./datas/download.npy', np.array(myfile).T)
        print("%d %s has downloaded"%(i, standard_res[i]))

# 把一开始生成的npy文件转换为xls格式
def npy2excel(data):
    data_df = pd.DataFrame(data)
    writer = pd.ExcelWriter('./datas/download.xls')
    data_df.to_excel(writer,'page_1') 
    writer.save()

# 单文件测试
if __name__ == '__main__':
    # standard_res = read_excel('./datas/data.xls')
    # # print(standard_res)
    # GetStdQLib("转账失败怎么办？")
    # DownloadDatas('./datas/data.xls', 0)
    download = np.load('./datas/download.npy')
    npy2excel(download)