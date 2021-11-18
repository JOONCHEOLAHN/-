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
import numpy as np
import os
# from selenium import webdriver


# ref : https://support.google.com/chrome/answer/95319#zippy=%2Cwindows
# ref : https://chromedriver.chromium.org/downloads

from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import sqlalchemy as sa
import cx_Oracle

import re
from datetime import datetime

# ---------------------------------------------------------------------------------------------------------- 반드시 크롬버전이 버전 92.0.4515.107(공식 빌드) (64비트)

# ---------------------------------------------------------------------------------------------------------- 하단 테이블 미리 만들고 실행하기
"""
drop table CRAW_YTN_ST;
drop sequence CRAW_YTN_ST_SEQ;

create table CRAW_YTN_ST(
seq number primary key,
RDATE VARCHAR2(40),
TITLE VARCHAR2(100),  
CONTENT VARCHAR2(4000)
);

create sequence CRAW_YTN_ST_SEQ start with 1 increment by 1;
"""


# ---------------------------------------------------------------------------------------------------------- 본인 오라클 계정 넣기
oracle_engine = sa.create_engine('oracle://conf:0000@localhost:1521/xe')   #conf:0000 (id:pw)


#--------------- YTN[cate:1] & Investing[cate:2].... 크롤링 ----------------
def craw(urlprm, max_page=1):
    with oracle_engine.connect() as conn:
        trans = conn.begin()

        baseurl = 'https://www.ytn.co.kr/search/?q=%EC%BD%94%EC%8A%A4%ED%94%BC#type=1&page='

        for pageno in range(1, max_page, 1):
            interval = round(random.uniform(0.2, 1.2), 2)
            time.sleep(interval)
            # ------------------------------------------------
            url = baseurl + str(pageno)
            print(url)

            driver = Chrome('./chromedriver')
            driver.get(url)
            driver.switch_to.frame('sList')
            html = driver.page_source
            # print(html)
            # driver.close()

            soup = BeautifulSoup(html, 'html.parser')
            list = soup.select("div#main > div.searchMain > dl")

            news_list = []
            for i, li_tag in enumerate(list):
                if i > 20:
                    break
                try:
                    dict = {}
                    title   = li_tag.select_one('dt > a').text
                    href    = li_tag.select_one('dt > a').get("href")
                    rdate   = li_tag.select_one('dd:nth-of-type(3)').string
                    print(rdate)
                    rdate   = re.search(r'\d{4}-\d{2}-\d{2}', rdate).group()  # 정규표현식 날짜만 자르기
                    print(rdate)

                    dict['key_title'] = title
                    dict['key_href'] = href
                    dict['key_rdate'] = rdate
                    news_list.append(dict)

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
                        # ----------------------------------------------------------------------------------------------------------
                                            #----- 요기 반드시 수정 (CRAW_YTN_ST)-    #----- 요기 반드시 수정(CRAW_YTN_ST_SEQ) -------------------------
                        sql = "insert into CRAW_YTN_ST(seq, rdate, title, content) values (CRAW_YTN_ST_SEQ.nextval,  :2, :3, :4)"
                        conn.execute(sql, (rdate, title, temp))
                except Exception as e:
                    continue
                    trans.rollback()
                    print("에러발생")

        trans.commit()
    # return news_list

# ---------------------------------------------------------------------------------------------------------- 2 <-- MAX페이지번호 1보다 크게
craw("https://www.ytn.co.kr/search/?q=apple#type=1&page=", 2)       # 1:ytn        263 rows



# investing_list = craw("https://kr.investing.com/news/economic-indicators",2)                        # 2:investing  263 rows



# # -------------------------- DB에서 읽어와 DataFrame 생성 ---------------------------------------
sql = "select seq, rdate, title, content from CRAW_YTN_ST"
df = pd.read_sql_query(f'''{sql}''', oracle_engine)
print(df.head())
df.to_csv("./datasets/ytn_news_st.csv", index=False)