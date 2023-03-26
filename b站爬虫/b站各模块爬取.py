from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import os
import pandas as pd
options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
# 打开浏览器
driver = webdriver.Firefox(options=options,executable_path='geckodriver.exe')

# 打开网页
driver.get("https://www.bilibili.com/v/tech/?spm_id_from=333.1007.0.0")

count_url=1
video_all_set=set()

if os.path.exists("B站各模块爬取")==False:
        os.mkdir("B站各模块爬取")
# 定位按钮元素
navigation1 = driver.find_element_by_xpath("/html/body/div[2]/div/div[3]/div/div/div[2]")
count=0
for button1 in navigation1.find_elements_by_tag_name("button"):
    if count==0:#去除'首页'标签
        count+=1
        continue
    print(button1.text)
    button1.click()#点击各模块按钮
    time.sleep(1)
    navigation2 = driver.find_element_by_xpath("/html/body/div[2]/div/main/div/div[1]")
    count2=0
    if os.path.exists("B站各模块爬取/"+button1.text)==False:
        os.mkdir("B站各模块爬取/"+button1.text)
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
        if os.path.exists("B站各模块爬取/"+button1.text+"/"+button2.text)==False:
            os.mkdir("B站各模块爬取/"+button1.text+"/"+button2.text)
        button2.click()#点击各模块的子模块按钮
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
        pd.DataFrame(list(video_set)).to_csv("B站各模块爬取/"+button1.text+"/"+button2.text+"/summary.csv",index=False)
            
        


# # 单击按钮
# button.click()

# # 关闭浏览器
# driver.quit()