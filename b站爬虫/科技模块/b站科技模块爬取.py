from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import os
import pandas as pd
import requests
import jsonpath

firefox_link=r"C:\Program Files\Mozilla Firefox\firefox.exe"

if os.path.exists("b站爬虫/科技模块")==False:
        os.mkdir("b站爬虫/科技模块")
        
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
    return df,bvid

#抓取所有科技模块下所有模块的所有子模块的视频链接
def get_all_model_video_link():
    options = Options()
    options.binary_location = firefox_link
    # 打开浏览器
    driver = webdriver.Firefox(options=options,executable_path='b站爬虫/科技模块/geckodriver.exe')

    # 打开b站科技模块
    driver.get("https://www.bilibili.com/v/tech/?spm_id_from=333.1007.0.0")

    count_url=1
    video_all_set=set()
    # 定位按钮元素
    navigation1 = driver.find_element_by_xpath("/html/body/div[2]/div/div[3]/div/div/div[2]")
    count=0
    for button1 in navigation1.find_elements_by_tag_name("button"):
        if count==0:#去除'首页'标签
            count+=1
            continue
        print(button1.text)
        button1.click()#点击科技模块下各模块按钮
        time.sleep(1)
        navigation2 = driver.find_element_by_xpath("/html/body/div[2]/div/main/div/div[1]")
        count2=0
        if os.path.exists("b站爬虫/科技模块/"+button1.text)==False:
            os.mkdir("b站爬虫/科技模块/"+button1.text)
        try:#如果有'展开'按钮，就展开
            expand=driver.find_element_by_xpath("/html/body/div[2]/div/main/div/div[1]/div")
            expand.click()
        except Exception:
            pass
            
        time.sleep(1)
        for button2 in navigation2.find_elements_by_tag_name("button"):
            if count2==0:#去除'全部'标签
                count2+=1
                continue
            print("---",button2.text)
            if os.path.exists("b站爬虫/科技模块/"+button1.text+"/"+button2.text)==False:
                os.mkdir("b站爬虫/科技模块/"+button1.text+"/"+button2.text)
            button2.click()#点击科技模块下的各模块的子模块按钮
            time.sleep(1)
            all_vedios=driver.find_element_by_xpath("/html/body/div[2]/div/main/div/div[2]/div/div[2]")
            video_set=set()
            
            for video_a in all_vedios.find_elements_by_xpath("//a[@data-ext='click']"):
                url=video_a.get_attribute("href")
                if url.find("BV")==-1 or url in video_all_set:#去除非视频和重复链接
                    continue
                video_all_set.add(url)
                video_set.add(url)
                print("抓取 %d "%count_url,url)
                count_url+=1
            #保存该子模块所有视频链接
            pd.DataFrame(list(video_set)).to_csv("b站爬虫/科技模块/"+button1.text+"/"+button2.text+"/summary.csv",index=False)

def from_summary_get_all_comment():
    for model in os.listdir("b站爬虫/科技模块"):
        for sub_model in os.listdir("b站爬虫/科技模块/"+model):
            print("正在处理 %s %s"%(model,sub_model))
            df=pd.read_csv("b站爬虫/科技模块/"+model+"/"+sub_model+"/summary.csv")
            success=0
            sum=len(df)
            for url in df.values:
                url=url[0]
                try:
                    df,bvid=get_url_comment(url)
                    df.to_csv("b站爬虫/科技模块/"+model+"/"+sub_model+"/"+bvid+".csv",index=False)
                    success+=1
                except Exception:
                    print("抓取 %s 失败 "%url,model," ",sub_model," 成功率：",success," / ",sum)
                    continue
                print("抓取 %s 成功"%url,model," ",sub_model," 成功率：",success," / ",sum)
                time.sleep(1)
        
from_summary_get_all_comment()
