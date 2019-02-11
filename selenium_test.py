from selenium import webdriver
import time
import getpass

driver = webdriver.Chrome('C:/Users/user/Desktop/pre_auto_work/Automated-verification/chromedriver')
driver.implicitly_wait(3)
# driver.get('https://nid.naver.com/nidlogin.login')
#
# time.sleep(0.5)
# driver.find_element_by_name("id").send_keys("ohji100629")
#
# time.sleep(0.5)
# driver.find_element_by_name("pw").send_keys(ww)
#
# time.sleep(0.5)
# driver.find_element_by_class_name('btn_global').click()
# # driver.find_elements_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
# time.sleep(3)
driver.get('''https://collabmain.lge.com/cuas/?os_destination=%2F''')

driver.maximize_window()

print("Enter collab ID, PW, OTP!\n")



id = input("Enter Id : ")
driver.find_element_by_name("userId").send_keys(id)
pw = getpass.getpass("Enter pw : ")
driver.find_element_by_name("password").send_keys(pw)
otp = input("Enter OTP : ")
driver.find_element_by_name("otpPassword").send_keys(otp)

# driver.find_elements_by_xpath('//*[@id="btnLogin"]').click()

# driver.find_element_by_id('id').send_keys(ss)
# driver.find_element_by_id('pw').send_keys(ww)
driver.find_element_by_id('btnLogin').click()
# driver.find_element_by_class_name('btn_global').click()

time.sleep(15)
driver.close()



# https://ndb796.tistory.com/123
# 셀레니움으로 네이버 로그인 참고

# https://ipex.tistory.com/entry/Selenium%EC%9B%B9%EC%9E%90%EB%8F%99%ED%99%94-Naver-Login-%ED%8E%98%EC%9D%B4%EC%A7%80-%EB%B3%80%EA%B2%BD%EC%97%90-%EB%94%B0%EB%A5%B8-%EC%98%88%EC%A0%9C-%EB%B3%80%EA%B2%BDChrome?category=770641
# CAPTCHA 도입으로 인해 자동 로그인 불가.
# HIP 기술의 일종
