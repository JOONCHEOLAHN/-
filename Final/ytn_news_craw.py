import sqlalchemy as sa
import cx_Oracle
import xml.etree.ElementTree as ET
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime
import random
random.uniform(0.2, 1.2)

oracle_engine = sa.create_engine('oracle://conf:0000@localhost:1521/xe')   #conf:0000 (id:pw)

#--------------- 사전 생성 테이블 ----------------
# create table craw_ytn_news(seq number,
# title varchar2(100),
# content varchar2(4000),
# cate varchar2(5),
# rdate varchar2(18));
#
# create sequence craw_ytn_news_seq start with 1 increment by 1;

#--------------- YTN 크롤링 ----------------
def craw(urlprm, cate):
    with oracle_engine.connect() as conn:
        trans = conn.begin()

        for pageno in range(1, 7, 1):
            interval = round(random.uniform(0.2, 1.2), 2)
            time.sleep(interval)
            #------------------------------------------------
            url =  urlprm + str(pageno)
            print(url)
            
            response = requests.get(url)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                list = soup.select("#zone1 > div > div.newslist_wrap > div > ul > li")

                news_list = []
                for i, li_tag in enumerate(list):

                    dict = {}
                    title   = li_tag.select_one('a > div > span').text
                    rdate   = li_tag.select_one('a > div > div > span.date').text
                    href     = li_tag.select_one('a').get("href")
                    #content.00 = li_tag.select_one('a > div > div > span.desc').text

                    dict['key_title'] = title
                    dict['key_rdate'] = rdate
                    dict['key_href'] = href
                    # dict['key_content'] = content
                    news_list.append(dict)

                    print(href)
                    response_sub = requests.get(href)
                    if response_sub.status_code == 200:
                        interval = round(random.uniform(0.2, 1.2), 2)
                        time.sleep(interval)


                        html_sub = response_sub.text
                        html_soup = BeautifulSoup(html_sub, 'html.parser')
                        content = html_soup.select_one("div#CmAdContent > span").text
                        temp = ""
                        for cc in content.rsplit("\n"):
                            if len(cc) > 2:
                                temp += cc
                        print(temp)
                        try:
                            sql = "insert into craw_ytn_news(seq, title, content, cate, rdate) values (craw_ytn_news_seq.nextval,  :2, :3, :4, :5)"
                            conn.execute(sql, (title, temp, cate, rdate))
                        except Exception as e:
                            continue
                            # trans.rollback()
                            # print(e)
                            print("에러발생")
            else:
                print("에러발생" + response.status_code)
        trans.commit()
    return news_list

# -------------------------- 각 6종 분야별 뉴스 1010 건 ---------------------------------------
# 경제_list = craw("https://www.ytn.co.kr/news/list.php?mcd=0101&page=",1)       #263 rows
# 사회_list = craw("https://www.ytn.co.kr/news/list.php?mcd=0102&page=",2)       #262 rows
# 과학_list = craw("https://www.ytn.co.kr/news/list.php?mcd=0105&page=",3)       #180 rows
# 문화_list = craw("https://www.ytn.co.kr/news/list.php?mcd=0106&page=",4)       #266 rows
# 재난_list = craw("https://www.ytn.co.kr/news/list.php?mcd=S0018&page=",5)      #266 rows
# 날씨_list = craw("https://www.ytn.co.kr/weather/list_weather.php?page=",6)     #297 rows



# -------------------------- DB에서 읽어와 DataFrame 생성 ---------------------------------------
# from sqlalchemy import types, create_engine
# oracle_engine = create_engine('oracle://conf:0000@localhost:1521/XE')
sql = "select title, content, cate, rdate from craw_ytn_news"
df = pd.read_sql_query(f'''{sql}''', oracle_engine)
print(df.head())
df.to_csv("./datasets/ytn_news.csv", index=False)