



import time
import pandas as pd
import os
# import pymysql
import re
from selenium import webdriver # pip install selenium
from bs4 import BeautifulSoup as bs

#
# conn = pymysql.connect(host='111.222.333.444', user = 'DB계정', password='DB비밀번호', db = 'keyword',charset = 'utf8')
# curs = conn.cursor(pymysql.cursors.DictCursor)


driver = webdriver.Chrome("C:\\AI\\chromedriver_win32\\chromedriver.exe")
driver.get('https://nid.naver.com/nidlogin.login?svctype=262144&url=http://naver.com/')

driver.get('https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com')
driver.find_element_by_xpath('//*[@id="id"]').send_keys("powop00")
# driver.find_element_by_xpath('//*[@id="pw"]').send_keys("qksksk01!!")
# driver.find_element_by_xpath('//*[@id="log.login"]').click()

time.sleep(35)
driver.get('https://cafe.naver.com/mbticafe')

df = pd.read_csv("./dataset/dataset/INFJ & ENFJ.csv")
df = df["번호"][3:5003]
df1 = df[3:53]
df = df.values.tolist()


for i in [0]:  #스크래핑 할 페이지수

    #강제#  중간에 끊겼을때 해당 페이수보다 -1 한 값을 입력하고 주석 제거
    #i = i + 15
    #강제#

    pg = str(i+1)
    addr = 'https://cafe.naver.com/ArticleList.nhn?search.clubid=11856775&search.menuid=292&search.boardtype=L&search.totalCount=151&search.cafeId=11856775&search.page='+pg
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
          for a, b, c, d in zip(a_num_list, a_title_list[7:], a_writer_list[7:], a_regdate_list[7:]):  # 나눔해요게시판, 목격담, 5세대 시공 장착 정비 수리
               list = []
               list.append(a.text)
               list.append(b.text.strip())
               list.append(c.text)
               list.append(d.text)
               total_list.append(list)
               article_link_list.append("https://cafe.naver.com/ArticleRead.nhn?clubid=11856775&page=1&menuid=292&boardtype=L&articleid=564493&referrerAllArticles=false")
               # article_link_list.append("https://cafe.naver.com/ArticleRead.nhn?clubid=19553263&amp;page=" + pg + "&amp;userDisplay=50&amp;menuid=44&amp;boardtype=L&amp;articleid=" + a.text + "&amp;referrerAllArticles=false")
    else:
         for a, b, c, d in zip(a_num_list, a_title_list, a_writer_list, a_regdate_list):
               list = []
               list.append(a.text)
               list.append(b.text.strip())
               list.append(c.text)
               list.append(d.text)
               total_list.append(list)
               article_link_list.append("https://cafe.naver.com/ArticleRead.nhn?clubid=11856775&page=1&menuid=292&boardtype=L&articleid=564493&referrerAllArticles=false")

    # DB 저장
    for x in total_list:

        print("insert into cl.jau_2021(seq, title, writer, reg_date, chk) values ('" + x[0]+ "','" + re.sub('[^A-Za-z0-9가-힣\s,.,?,!]', "", x[1]) + "','" + re.sub('[^A-Za-z0-9가-힣\s,.,?,!]', "", x[2]) + "','" + x[3] + "', '4')")
        # sql = "insert into cl.jau_2021(seq, title, writer, reg_date, chk) values ('" + x[0]+ "','" + re.sub('[^A-Za-z0-9가-힣\s,.,?,!]', "", x[1]) + "','" + re.sub('[^A-Za-z0-9가-힣\s,.,?,!]', "", x[2]) + "','" + x[3] + "', '4')"
        #
        # curs.execute(sql)
        # conn.commit()

    # 글 스크랩핑
    for x in total_list:

         adrs = "https://cafe.naver.com/ArticleRead.nhn?clubid=11856775&page=1&menuid=292&boardtype=L&articleid=564493&referrerAllArticles=false"
                #"https://cafe.naver.com/ArticleRead.nhn?clubid=11856775&amp;page=" + str(pg) + "&amp;userDisplay=50&amp;menuid292&amp;boardtype=L&amp;articleid=" + x[0] +"&amp;referrerAllArticles=false"

         print(adrs)

         driver.get(adrs)

         time.sleep(2)
         driver.switch_to.frame('cafe_main')

         html = driver.page_source

         soup = bs(html, 'html.parser')

         list = soup.find_all("div", {"class":"article_viewer"})

         for xx in list:

             cont = ''
             cont += re.sub('[^A-Za-z0-9가-힣\s,.,?,!]', "", xx.text.strip()).replace('\n','')

         #driver.close()

         print(cont)

         sql = "update cl.jau_2021 set contents = '" + str(cont).replace("'", "") + "' where seq = '" + x[0] + "'"
         print(sql)
         # curs.execute(sql)
         # conn.commit()

    # 리스트 변수 초기화
    a_num_list = []
    a_title_list = []
    a_writer_list = []
    a_regdate_list = []

    print("#############################################    " + pg + "  페이지 완료 #############################################")

driver.close()
