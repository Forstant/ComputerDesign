from bs4 import BeautifulSoup           #网页解析，获取数据
import re                               #正则表达式，进行文字匹配
import urllib.request,urllib.error      #指定URL，获取网页数据
import xlwt                             #进行excel操作

def main():
#     1. 获取网页
    baseurl = "https://www.bilibili.com/v/popular/rank/all"
#     2. 获取和解析数据
    datalist = getData(baseurl)
#     3. 保存数据
    savepath = "./B站热门视频.xls"
    saveData(datalist,savepath)

findLink = re.compile(r'<a href="(.*?)" target="_blank">')
findName = re.compile(r'<a class="title" href=".*?" target="_blank">(.*)</a>')
# findPlay = re.compile(r'<span class="data-box"><i class="b-icon play"></i>(.*?)</span>',re.S)
findPlay = re.compile(r'<div class="detail-state"><span class="data-box"><img .*?>(.*?)</span>',re.S)
findView = re.compile(r'<div class="detail-state"><span class="data-box"><img .*?>.*?</span>.*?<span class="data-box"><img .*?>(.*?)</span>',re.S)
findUP = re.compile(r'<span class="data-box up-name"><i class="b-icon author"></i>(.*?)</span>',re.S)
findGrades = re.compile(r'<div class="pts"><div>(.*?)</div>')


def getData(baseurl):
    datalist = []
    html = askURL(baseurl)
    # print(html)
    soup = BeautifulSoup(html, "html.parser")  # 形成树形结构对象
    count=0
    for item in soup.find_all("div",class_="content"):
        count+=1
        # print(item)
        data = []
        data.append(count)
        item = str(item)
        # 视频链接
        link = re.findall(findLink,item)[0]
        data.append(link)
        # 视频名字
        name = re.findall(findName,item)[0]
        data.append(name)
        # 播放量
        play = re.findall(findPlay,item)[0]
        # print(play)
        data.append(play)
        # 评论数
        view = re.findall(findView,item)[0]
        data.append(view)
        # # UP个人空间链接
        # uplink = re.findall(findLink,item)[1]
        # # print(uplink)
        # data.append(uplink)
        # # UP主
        # UP = re.findall(findUP,item)[0]
        # # print(UP)
        # data.append(UP)
        # # 综合得分
        # grades = re.findall(findGrades,item)[0]
        # # print(grades)
        # data.append(grades)
        datalist.append(data)

    return datalist



def saveData(datalist,savepath):
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet("B站热门",cell_overwrite_ok=True)
    col = ("排名","视频链接","视频名字","播放量","评论数")
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(0,100):
        print("第%d条"%i)
        data = datalist[i]
        sheet.write(i+1,0,i+1)
        # print(data)
        for j in range(0,4):
            sheet.write(i+1,j,data[j])

    book.save(savepath)  # 保存数据表



def askURL(url):
    head = {
        "user-agent" : "Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 88.0.4324.104 Safari / 537.36",
        "referer" : "https: // www.bilibili.com /",
        "cookie": "_uuid = DFE59F2A - D16B - 327E - D501 - 9CA14392FF8059467infoc;buvid3 = 0041FC1C - 2C18 - 4DDE - 965F - 9DEF43D88176155809infoc;rpdid = | (YYR~ | uklm0J'ul))u~JRuJ; sid=9n9kd7a4; LIVE_BUVID=AUTO2815885539756041; blackside_state=1; CURRENT_FNVAL=80; PVID=1; CURRENT_QUALITY=80; DedeUserID=434641640; DedeUserID__ckMd5=1b9357ca56a49330; SESSDATA=ab62e58a%2C1619879365%2C80832*b1; bili_jct=01ecd2f4c1f3d0e94aa31b03a7bea6ec; bp_t_offset_434641640=491560557515702800; bp_video_offset_434641640=491834756822300005; finger=1777945899"
    }
    request = urllib.request.Request(url,headers = head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e,"code")
        if hasattr(e,"reason"):
            print(e,"reason")
    return html




if __name__ == "__main__":  #程序执行时
    #调用函数
    main()
    print("爬取完毕！")
