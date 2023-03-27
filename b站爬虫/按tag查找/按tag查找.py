from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import os
import pandas as pd
import requests
import jsonpath



        
# 爬取一个网页的评论
api_header = {
    "authority": "api.bilibili.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "accept": "application/json, text/plain, */*",
}

comment_header={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}

# 爬取一个url的评论的函数        
def get_url_comment(url, all_comment=True):
    url = url.strip("/")
    s_pos = url.rfind("/") + 1
    r_pos = url.rfind("?")
    if r_pos == -1:
        bvid = url[s_pos:]
    else:
        bvid = url[s_pos:r_pos]
    api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    print(api_url)
    res = requests.get(api_url, headers=api_header)
    res.encoding = "u8"
    data = res.json()['data']
    aid=data["aid"]
    t = str(int(time.time()*1000))
    url = f"https://api.bilibili.com/x/v2/reply/main?next={3}&type=1&oid={aid}&mode=3&plat=1&_={t}"
    res = requests.get(url, headers=comment_header)
    data = res.json()
    replies = jsonpath.jsonpath(
        data, "$..replies[*]" if all_comment else "$.data.replies[*]")
    # names = jsonpath.jsonpath(replies, "$[*].member.uname") #用户名
    messages = jsonpath.jsonpath(replies, "$[*].content.message")
    times = jsonpath.jsonpath(replies, "$[*].ctime")
    likes = jsonpath.jsonpath(replies, "$[*].like")
    df = pd.DataFrame({"评论": messages, "时间": times, "点赞数": likes,"标签":0})
    
    df.时间 = pd.to_datetime(df.时间, unit='s')
    return df,bvid,len(messages)

#抓取所有科技模块下所有子模块的视频链接
def get_videos_by_tag(tag,page=1):
    all_videos_set=set()
    if os.path.exists(f"b站爬虫/按tag查找/{tag}")==False:
        os.mkdir(f"b站爬虫/按tag查找/{tag}")
    else:
        if(os.path.exists(f"b站爬虫/按tag查找/{tag}/summary.csv")):
            with open(f"b站爬虫/按tag查找/{tag}/summary.csv","r") as f:
                for i in pd.read_csv(f).values:
                    all_videos_set.add(i[0])
    options = Options()
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    # 打开浏览器
    driver = webdriver.Firefox(options=options,executable_path='b站爬虫/按tag查找/geckodriver.exe')
    
    # 打开tag模块
    url_base=f"https://search.bilibili.com/all?keyword={tag}&from_source=webtop_search&spm_id_from=333.1007&search_source=5"

    
    for i in range(1,page+1):
        url=url_base
        if i!=1:
            url=url_base+f"&page={i}"
        driver.get(url)
        time.sleep(1)
        all_videos=driver.find_element_by_xpath("//div[@class='mt_sm video-list row']")
        for video in all_videos.find_elements_by_tag_name("a"):
            if video.get_attribute("href").find("video")==-1 or video.get_attribute("href") in all_videos_set:
                continue
            all_videos_set.add(video.get_attribute("href"))
            print(video.get_attribute("href"))
    pd.DataFrame(list(all_videos_set)).to_csv(f"b站爬虫/按tag查找/{tag}/"+"summary.csv",index=False)
    # from_summary_get_all_comment(tag)


   
   
def from_summary_get_all_comment(tag):
    if os.path.exists(f"b站爬虫/按tag查找/{tag}")==False:
        os.mkdir(f"b站爬虫/按tag查找/{tag}")
    else:
        sum=0
        success=0
        comment_sum=0
        with open(f"b站爬虫/按tag查找/{tag}/summary.csv","r") as f:
            for i in pd.read_csv(f).values:
                sum+=1
                if os.path.exists(f"b站爬虫/按tag查找/{tag}/{i[0].split('/')[-1]}.csv")==False:
                    try:
                        df,bvid,comment=get_url_comment(i[0])
                        df.to_csv(f"b站爬虫/按tag查找/{tag}/{bvid}.csv",index=False)
                        success+=1
                        comment_sum+=comment
                    except:
                        print("出错")
                else:
                    print(f"已经存在{i[0].split('/')[-1]}.csv")
                print("使用{}查找 已经完成{}/{}个 共抓取{}个评论".format(tag,success,sum,comment_sum))
    print("done")

get_videos_by_tag("防疫")      
from_summary_get_all_comment("防疫")

        


# # 单击按钮
# button.click()

# # 关闭浏览器
# driver.quit()