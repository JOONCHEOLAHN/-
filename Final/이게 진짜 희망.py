

import sqlalchemy as sa
import cx_Oracle

import time
import pandas as pd
import os
# import pymysql
import re
from selenium import webdriver # pip install selenium
from bs4 import BeautifulSoup as bs


oracle_engine = sa.create_engine('oracle://ai:0000@localhost:1521/xe')   #conf:0000 (id:pw)


def naver_cafe_craw() :

    driver = webdriver.Chrome("C:\\AI\\chromedriver_win32\\chromedriver.exe")
    driver.get('https://nid.naver.com/nidlogin.login?svctype=262144&url=http://naver.com/')

    driver.get('https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com')
    driver.find_element_by_xpath('//*[@id="id"]').send_keys("powop00")
    driver.find_element_by_xpath('//*[@id="pw"]').send_keys("qksksk01!!")
    driver.find_element_by_xpath('//*[@id="log.login"]').click()

    time.sleep(12)
    driver.get('https://cafe.naver.com/mbticafe')


    # """
    # create table cafe_board (
    #     seq number primary key,
    #     title varchar2(200) not null,
    #     writer varchar2(30) ,
    #     content varchar2(4000)
    # );
    # create sequence cafe_board_seq start with 1 increment by 1;
    # """

    with oracle_engine.connect() as conn:
        trans = conn.begin()
        for i in range(0,61):
            try :
                #강제#  중간에 끊겼을때 해당 페이수보다 -1 한 값을 입력하고 주석 제거
                #i = i + 15
                #강제#

                pg = str(i+1)
                addr = 'https://cafe.naver.com/ArticleList.nhn?search.clubid=11856775&search.menuid=29&search.boardtype=L&search.totalCount=151&search.cafeId=11856775&search.page='+pg
                # https: // cafe.naver.com / ArticleList.nhn?search.clubid = 11856775 & search.menuid = 292 & search.boardtype = L & search.totalCount = 151 & search.cafeId = 11856775 & search.page = '
                driver.get(addr)
                driver.switch_to.frame('cafe_main')

                html = driver.page_source

                soup = bs(html, 'html.parser')

                a_num_list = soup.findAll("div",{"class":"inner_number"})
                a_title_list = soup.findAll("a",{"class":"article"})
                a_writer_list = soup.findAll("a",{"class":"m-tcol-c"})
                a_regdate_list = soup.findAll("td",{"class":"td_date"})

                total_list = []
                article_link_list = []  #글 링크

                if i == 0:
                    for a, b, c, d in zip(a_num_list, a_title_list[16:], a_writer_list[16:], a_regdate_list[16:]):  # 나눔해요게시판, 목격담, 5세대 시공 장착 정비 수리
                        dict = {}
                        dict['seq'] = a.text
                        dict['title'] = b.text.strip()
                        dict['writer'] = c.text
                        dict['rdate'] = d.text
                        dict['suburl'] = "https://cafe.naver.com/ArticleRead.nhn?clubid=11856775&page=" + str(pg) + "&userDisplay=50&menuid29&boardtype=L&articleid=" + a.text +"&referrerAllArticles=false"
                        total_list.append(dict)
                else:
                    for a, b, c, d in zip(a_num_list, a_title_list, a_writer_list, a_regdate_list):
                        dict = {}
                        dict['seq'] = a.text
                        dict['title'] = b.text.strip()
                        dict['writer'] = c.text
                        dict['rdate'] = d.text
                        dict['suburl'] = "https://cafe.naver.com/ArticleRead.nhn?clubid=11856775&page=" + str(pg) + "&userDisplay=50&menuid29&boardtype=L&articleid=" + a.text + "&referrerAllArticles=false"
                        total_list.append(dict)

                print("ddd")
                # 글 스크랩핑
                for dicts in total_list:
                    try:
                        print(dicts)

                        driver.get(dicts['suburl'])
                        time.sleep(2)
                        driver.switch_to.frame('cafe_main')
                        html = driver.page_source
                        soup = bs(html, 'html.parser')
                        list = soup.find_all("div", {"class":"article_viewer"})
                        for articles in list:
                            cont = ''
                            cont += re.sub('[^A-Za-z0-9가-힣\s,.,?,!]', "", articles.text.strip()).replace('\n','')

                        # ------------ DB insert -------------
                        sql = "insert into cafe_board(seq, title, writer, content) values (cafe_board_seq.nextval,  :2, :3, :4)"
                        conn.execute(sql, (dicts['title'], dicts['writer'], cont))
                    except Exception as e:
                        continue
                        print("sql exec error")
            except Exception as e:
                continue
                print("page craw error")
        trans.commit()
    driver.close()
    print("-------------------- naver craw done -----------------")

def craw_view() :
    sql = "select * from cafe_board"
    df = pd.read_sql_query(f'''{sql}''', oracle_engine)
    # df = df.duplicated()
    print(df.shape)
    print(df.head())
    df.to_csv("./datasets/신변잡기_4.csv", index=False)


# ---------------------------------------
# 크롤링 실행
# ---------------------------------------
naver_cafe_craw()

# ---------------------------------------
# 결과보기
# ---------------------------------------
craw_view()


