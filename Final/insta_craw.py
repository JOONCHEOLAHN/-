from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome("C:\\AI\\chromedriver_win32\\chromedriver.exe")
driver.get('https://instagram.com')

time.sleep(4)

driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys("junc___")
driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys("qksksk01!!")
driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button').click()
driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button').click()

e= driver.find_element_by_class_name("sqdOP.yWX7d.y3zKF")
e.click()
e= driver.find_element_by_class_name("Ypffh")[0]
e.click()
e =driver.find_element_by_class_name("Ypffh")[0]
# e.send_keys("와 분위기 좋네요 !!")
# e.send_keys(Keys.ENTER)