from selenium import webdriver
from bs4 import BeautifulSoup
import time
import getpass

id = "jihun28.oh"
pw = "navercom1!"
# 웹드라이버 위치
driver = webdriver.Chrome('C:/Users/user/Desktop/pre_auto_work/Automated-verification/chromedriver')
driver.implicitly_wait(3)

# 로그인 페이지 이동
driver.get('''https://collabmain.lge.com/cuas/?os_destination=%2F''')
# driver.maximize_window()

# 로그인 정보 입력
# print("Enter collab ID, PW, OTP!\n")
# id = input("Enter Id : ")
# driver.find_element_by_name("userId").send_keys(id)
# pw = getpass.getpass("Enter pw : ")
# driver.find_element_by_name("password").send_keys(pw)
# otp = input("Enter OTP : ")
# driver.find_element_by_name("otpPassword").send_keys(otp)
# driver.find_element_by_id('btnLogin').click()

# 로그인 테스트
print("Enter collab ID, PW, OTP!\n")
driver.find_element_by_name("userId").send_keys(id)
driver.find_element_by_name("password").send_keys(pw)
otp = input("Enter OTP : ")
driver.find_element_by_name("otpPassword").send_keys(otp)
driver.find_element_by_id('btnLogin').click()

time.sleep(5)
print("swipe")

#  보드형 따라 다른 사이트 이동.
board_type = input("Enter num (Board type :: 1. signage , 2. hotel) :")

# 사이니지 모델 
if board_type == "1":
    # 사이트 이동
    driver.get('''http://collab.lge.com/main/pages/viewpage.action?pageId=454548896''')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # 모든 모델명 가져옴
    print("Here is signage models")
    print("seclet!")
    for tbody in soup.find_all("tbody"):
        for tr in tbody.find_all("tr"):
            # row 의 첫번째 col 만 가져옴.
            col=0
            for td in tr.find_all("td"):
                if col != 0:
                    break
                # 가져온 문자열 공백제거
                refined_td = str(td.get_text()).replace(" ","")
                refined_td = refined_td.replace("&nbsp","")
                print(refined_td+ " ,", end='') 
                col += 1

    # 모델 선택 후
    # tooloption 가져온다.
    is_model = False
    s_model = input("Select model name : ")
    for tbody in soup.find_all("tbody"):
        for tr in tbody.find_all("tr"):
            # row 의 첫번째 col[모델명]을 가져와서 비교.
            td = tr.find_all("td")

            # 가져온 문자열 공백제거
            refined_td = str(td.get_text()).replace(" ","")

            if refined_td == s_model:
                for index in range(1, 10):
                    print( "tooloption"+ str(index) + " : " +td[index].get_text() )
                is_model = True
                break
        if is_model == True:
            break

            # for td in tr.find_all("td"):
            #     if col == 0 and s_model == td.get_text() :
                    
            #         col += 1



    print("\n\n END")
#main-content > div:nth-child(4) > table > tbody > tr:nth-child(1) > td:nth-child(1)
#main-content > div:nth-child(4) > table > tbody > tr:nth-child(4) > td:nth-child(7)
# #main-content > div:nth-child(36) > table > tbody > tr:nth-child(1) > td:nth-child(1)
# 호텔 모델
else :
    driver.get('''http://collab.lge.com/main/pages/viewpage.action?pageId=454548907''')




time.sleep(15)



# https://ndb796.tistory.com/123
# 셀레니움으로 네이버 로그인 참고

# https://ipex.tistory.com/entry/Selenium%EC%9B%B9%EC%9E%90%EB%8F%99%ED%99%94-Naver-Login-%ED%8E%98%EC%9D%B4%EC%A7%80-%EB%B3%80%EA%B2%BD%EC%97%90-%EB%94%B0%EB%A5%B8-%EC%98%88%EC%A0%9C-%EB%B3%80%EA%B2%BDChrome?category=770641
# CAPTCHA 도입으로 인해 자동 로그인 불가.
# HIP 기술의 일종
