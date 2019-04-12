# coding:utf-8
# 对于动态加载的网页，例如知乎，需要使用Selenium+ChromeDriver(或PhantomJS)
import re
import time

import pymongo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

conn = pymongo.MongoClient('localhost', 27017)
db = conn.date  # 连接mydb数据库，没有则自动创建
total_db = db.total_db  # 存储全部数据
hangzhou_db = db.hangzhou_db  # 存储包含杭州的数据
stat_db = db.stat_db  # 存储页码状态的数据
option = webdriver.ChromeOptions()
option = webdriver.ChromeOptions()
option.add_argument("headless")
boswer = webdriver.Chrome(r'driver\chromedriver.exe', chrome_options=option)


# cont.text
# items=cont.find_elements_by_class_name("List-item")
def get_soup(driver, url, wait_time):
    driver.get(url)
    cont = (By.CLASS_NAME, "RichContent-inner")
    WebDriverWait(driver, 30, 0.5).until(EC.presence_of_element_located(cont))
    time.sleep(1)
    time.sleep(wait_time)
    str_con = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(str_con, 'lxml')
    return soup

    # driver.close()


def insert_mongo(soup):
    items = soup.find(class_='Question-main').find_all(class_='List-item')
    for item in items:
        #         print(i.find(class_='ContentItem AnswerItem'))
        # print(i.text)
        name_val = item.find(class_='ContentItem AnswerItem').attrs['name']
        text_val = re.sub(r'<.*?>', ' ', item.find(class_='RichText ztext CopyrightRichText-richText').text)
        text_val = re.sub(r'\s+', ' ', text_val)
        text_val = text_val.strip()
        re.sub('<.*?>', '', text_val)
        create_time_val = item.find(class_='ContentItem-time').find('span').attrs['data-tooltip']
        update_time_val = item.find(class_='ContentItem-time').find('span').text
        img_count = len(item.find_all('img'))

        if total_db.find_one({'name': name_val}):
            print('重复了')
            total_db.update_one({'name': name_val}, {
                "$set": {'name': name_val, 'create_time': create_time_val, 'update_time': update_time_val,
                         'text': text_val,
                         'raw': item, 'img_count': img_count}})
        else:
            total_db.insert_one(
                {'name': name_val, 'create_time': create_time_val, 'update_time': update_time_val, 'text': text_val,
                 'raw': str(item), 'img_count': img_count})
        if re.search('杭州', text_val):
            if hangzhou_db.find_one({'name': name_val}):
                hangzhou_db.update_one({'name': name_val}, {
                    "$set": {'name': name_val, 'create_time': create_time_val, 'update_time': update_time_val,
                             'text': text_val,
                             'raw': item, 'img_count': img_count}})
            else:
                hangzhou_db.insert_one(
                    {'name': name_val, 'create_time': create_time_val, 'update_time': update_time_val, 'text': text_val,
                     'raw': str(item), 'img_count': img_count})
    print('---------')


for page_count in range(1, 1400):  # 这里要改成当前按照时间排序的总页数量+1,或者设置的大一点也可以。超出实际页码后手动退出程序即可
    url = 'https://www.zhihu.com/question/275359100/answers/created?page=%d' % page_count
    try:
        soup = get_soup(boswer, url, 0)
        insert_mongo(soup)
        stat_db.insert_one({'page': page_count, 'stat': 'finish'})
        print('第%d页爬取完成' % page_count)
    except Exception as e:
        print('第一次失败')
        print(e)
        try:
            soup = get_soup(boswer, url, 10)
            insert_mongo(soup)
            stat_db.insert_one({'page': page_count, 'stat': 'finish'})
            print('第%d页爬取完成' % page_count)

        except Exception as e:
            print('第二次失败')
            print(e)
            try:
                soup = get_soup(boswer, url, 30)
                insert_mongo(soup)
                stat_db.insert_one({'page': page_count, 'stat': 'finish'})
                print('第%d页爬取完成' % page_count)
            except Exception as e:
                print('第三次失败，放弃')
                print(e)
                stat_db.insert_one({'page': page_count, 'stat': 'error'})
                print('第%d页爬取出错' % page_count)

boswer.close()
