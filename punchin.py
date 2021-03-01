#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#__author__ = '广州三零 @KimJongun'
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from requests.exceptions import RequestException
from selenium.webdriver.common.by import By
from requests.adapters import HTTPAdapter
import time, json, sys , os, cv2,re
import requests, datetime
from time import sleep
import numpy as np
import configparser
#import wx_msg


# 读取配置参数
config = configparser.ConfigParser()
config.read('CONFIG')
chrome_driver = config['chrome_driver']['url']
phone_num = config['cetc']['phone']
password = config['cetc']['password']
pushplus_token = config['pushplus']['token']
url = 'https://asst.cetccloud.com/#/login'

# 参数设置2
t = datetime.date.today()
date_str  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
realpath = os.path.realpath(__file__)
counter = 1
holiday_api ='http://timor.tech/api/holiday/info/' + str(t)
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0"}
options = webdriver.ChromeOptions()
# options.add_argument("--no--sandbox")
options.add_argument('user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15F79 MicroMessenger/7.0.11(0x17000b21) NetType/WIFI Language/zh_CN"')
# 这里我用的google的驱动。
driver = webdriver.Chrome(executable_path = chrome_driver, chrome_options = options)
wait = WebDriverWait(driver, 18)
driver.set_page_load_timeout(7)
# 设置页面加载超时
driver.set_script_timeout(7)
driver.set_window_size(516, 799)


# 这个函数是用来显示图片的。
def show(name):
    cv2.imshow('Show',name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def banner():
    print("\r\n  \r\n")
    print(" ad888888b,     ,a8888a,                         88             88         ")
    print("d8\"     \"88   ,8P\"'  `\"Y8,                       \"\"             88          ")
    print("        a8P  ,8P        Y8,                                     88          ")
    print("     aad8\"   88          88  8b      db      d8  88  ,adPPYba,  88,dPPYba,  ")
    print("     \"\"Y8,   88          88  `8b    d88b    d8'  88  I8[    \"\"  88P'    \"8a ")
    print("        \"8b  `8b        d8'   `8b  d8'`8b  d8'   88   `\"Y8ba,   88       88 ")
    print("Y8,     a88   `8ba,  ,ad8'     `8bd8'  `8bd8'    88  aa    ]8I  88       88 ")
    print(" \"Y888888P'     \"Y8888P\"         YP      YP      88  `\"YbbdP\"'  88       88 ")
    print("\r\n Author: @KimJongun \r\n")
    print("电科云自动打卡")


# 微信自动消息推送
def wechat_push(title, content):
    url = 'http://pushplus.hxtrip.com/send?token='+ pushplus_token + '&title='+ title + '&content='+ content
    requests.get(url)


# 实现登录
def login(driver,url):
    global date_str
    while True:
        try:
            driver.get(url)
            print("[+].正在玩命加载小帮手页面")
            break
        except TimeoutException as e:
            print("Time out Exception\n" )
            continue

    try:
        username = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='login_content_field'][1]//input[@class='van-field__control']")))
        passwd = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='login_content_field'][2]//input[@class='van-field__control']")))
        login_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "login_btn")))
    except TimeoutException as e:
        print("[-]登录元素超时：%s" % e)
        wechat_push('登录元素超时异常，可能是高峰时间段，正在重新启动程序！','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    username.send_keys(phone_num)
    passwd.send_keys(password)
    login_btn.click()
    print("[+].正在尝试登录")
    sleep(0.2)
    return driver


# 获取验证码中的图片
def get_image(driver):
    global date_str
    print("[+].正在获取验证码图片地址")
    sleep(2)
    while True:
        try:
            bkg_elem = driver.find_element_by_xpath("//div[@id='slideVerify']/div[1]/img[1]").get_attribute('src')
            blk_elem = driver.find_element_by_class_name("slide-verify-block").get_attribute('src')
        except TimeoutException as e:
            print("[-]超时异常，尝试重新获取验证码！ ")
            try:
                refresh_elem = driver.find_element_by_xpath("//div[@class='slide-verify-refresh-icon']")
                refresh_elem.click()
                continue
            except NoSuchElementException as NSEE:
                print("[-]获取不到刷新验证码的元素！\n" )
                wechat_push('获取不到刷新验证码的元素!可能是高峰时间段，正在重新启动程序！','时间是：' + date_str )
                driver.quit()
                os.system('python ' + realpath)
                sys.exit()
        else:
            if (bkg_elem and blk_elem):
                break

    bkg_img = requests.get(bkg_elem, headers = headers)
    with open('slide_bkg.png', 'wb+') as bkg:
        bkg.write(bkg_img.content)
        bkg.close()

    blk_img = requests.get(blk_elem, headers = headers)
    with open('slide_block.png', 'wb+') as blk:
        blk.write(blk_img.content)
        blk.close()

    return 'slide_bkg.png', 'slide_block.png'


# 计算缺口的位置，由于缺口位置查找偶尔会出现找不准的现象，这里进行判断，如果查找的缺口位置x坐标小于260，我们进行刷新验证码操作，重新计算缺口位置，直到满足条件为止。（设置为260的原因是因为缺口出现位置的x坐标都大于260）
def get_distance(bkg,blk ,driver):
    try:
        block = cv2.imread(blk, 0)
        template = cv2.imread(bkg, 0)
        w, h = block.shape[::-1]
        cv2.imwrite('template.jpg', template)
        cv2.imwrite('block.jpg', block)
        block = cv2.imread('block.jpg')
        block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
        block = abs(255 - block)
        cv2.imwrite('block.jpg', block)
        block = cv2.imread('block.jpg')
        template = cv2.imread('template.jpg')
        result = cv2.matchTemplate(block,template,cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(),result.shape)
        #这里就是下图中的绿色框框
        cv2.rectangle(template, (y, x), (y + w, x + h), (7, 249, 151), 2)
    except :
        print("[-]图片异常！ \n")
        wechat_push('图片异常，正在重新启动程序！','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()

    print('[-].验证码的x坐标为：%d'% y)
    if y > 260:
        try:
            elem = driver.find_element_by_xpath("//div[@class='slide-verify-refresh-icon']")
        except NoSuchElementException as NSEE:
            print("[-]没有找到验证码刷新元素  \n")
            driver.quit()
            os.system('python ' + realpath)
            sys.exit()
        sleep(1)
        elem.click()
        bkg, blk = get_image(driver)
        y, template = get_distance(bkg, blk)
    return y, template


# 这个是用来模拟人为拖动滑块行为，快到缺口位置时，减缓拖动的速度，服务器就是根据这个来判断是否是人为登录的。
def get_tracks(dis):
    v = 0
    t = 0.3
    #保存0.3内的位移
    tracks = []
    current = 0
    mid = dis*4/5
    while current <= dis:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        s = v0 * t + 0.5 * a * (t**2)
        current += s
        tracks.append(round(s))
        v = v0 + a*t
    return tracks


# 拖动滑块
def mov_to_gap(driver, distance):
    action = ActionChains(driver)
    element = driver.find_element_by_xpath("//div[@class='slide-verify-slider-mask-item']")
    ActionChains(driver).click_and_hold(on_element = element).perform()
    action.move_by_offset(distance, 0)
    action.release().perform()
    sleep(0.2)


# 工作日打卡按钮
def punchin_btn(driver):
    sleep(1)
    global date_str
    try:
        elem_dengji = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='app']/div/div[2]/div/div[1]")))
    except TimeoutException as e:
        print("登记按钮元素超时  \r\n")
        wechat_push('登记按钮元素超时，正在重新启动程序！','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(1)
    try:
        ActionChains(driver).move_to_element(elem_dengji).click(elem_dengji).perform()
    except StaleElementReferenceException:
        print("旧元素引用异常：元素没有附加到页面文档  \r\n")
        wechat_push('旧元素引用异常：元素没有附加到页面文档，正在重新启动程序！','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()

# 修改按钮
    try:
        elem_fix_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fix_btn")))
    except TimeoutException as e:
        print("修改按钮元素超时  \r\n")
        wechat_push('修改按钮元素超时，正在重新启动程序！','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(1)
    try:
        ActionChains(driver).move_to_element(elem_fix_btn).click(elem_fix_btn).perform()
    except StaleElementReferenceException:
        print("旧元素引用异常：元素没有附加到页面文档  \r\n")
        wechat_push('旧元素引用异常：元素没有附加到页面文档，正在重新启动程序！','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(2)
# 提交按钮
    try:
        elem_slot_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "slot_span")))
        ActionChains(driver).move_to_element(elem_slot_btn).click(elem_slot_btn).perform()
    except StaleElementReferenceException:
        print("旧元素引用异常：元素没有附加到页面文档!!!")
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    except TimeoutException as e:
        print("Time out Exception  \r\n")
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    except ElementClickInterceptedException as ECIE:
        print("元素被其他元素挡住了。报ElementClickInterceptedException异常。 \r\n")
        wechat_push('元素被其他元素挡住','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()


# 休息天打卡
def rest_btn(driver):
    date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# 每日登记按钮
    try:
        elem_dengji = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='app']/div/div[2]/div/div[1]")))
    except TimeoutException as e:
        print("[-]（每日登记按钮）元素超时\r\n")
        wechat_push('登记按钮元素超时，正在重新启动程序！','时间是：' + date_str  )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(1)
    try:
        ActionChains(driver).move_to_element(elem_dengji).click(elem_dengji).perform()
    except StaleElementReferenceException:
        print("旧元素引用异常：元素没有附加到页面文档!!!")
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    except TimeoutException:
        print("Time out Exception  \r\n")
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(1)

# 修改按钮
    try:
        elem_fix_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fix_btn")))
    except TimeoutException as e:
        print("[-](修改按钮)元素超时\r\n")
        wechat_push('修改按钮元素超时，正在重新启动程序！','时间是：' + date_str  )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(1)
    try:
        ActionChains(driver).move_to_element(elem_fix_btn).click(elem_fix_btn).perform()
    except StaleElementReferenceException:
        print("旧元素引用异常：元素没有附加到页面文档!!!")
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(1)

# 修改复岗情况为"居家办公"
    try:
        elem_fugang_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fugangClass")))
    except TimeoutException as e:
        print("[-]（居家办公）元素超时\r\n")
        wechat_push('居家办公元素超时，正在重新启动程序！','时间是：' + date_str  )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    ActionChains(driver).move_to_element(elem_fugang_btn).click(elem_fugang_btn).perform()
    sleep(0.5)
# 选择"居家办公"
    try:
        elem_jujia = wait.until(EC.presence_of_element_located((By.XPATH, "//li[@class='van-picker-column__item'][1]/div[@class='van-ellipsis']")))
    except TimeoutException as e:
        print("[-]元素van-ellipsis（居家办公）超时\r\n")
        wechat_push('元素van-ellipsis居家办公超时，正在重新启动程序！','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(1)
    try:
        ActionChains(driver).move_to_element(elem_jujia).click(elem_jujia).perform()
    except StaleElementReferenceException:
        print("旧元素引用异常：元素没有附加到页面文档!!!")
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(1)
# 选择确认
    try:
        elem_confirm_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "van-picker__confirm")))
    except TimeoutException as e:
        print("[-]元素vpan-picker_confirm（确认）超时。\r\n")
        wechat_push('确认元素超时，正在重新启动程序','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(1)
    try:
        ActionChains(driver).move_to_element(elem_confirm_btn).click(elem_confirm_btn).perform()
    except StaleElementReferenceException:
        print("旧元素引用异常：元素没有附加到页面文档!!!")
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    sleep(0.1)
# 最后才提交
    try:
        sleep(0.3)
        elem_slot_btn = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "slot_span")))
        ActionChains(driver).move_to_element(elem_slot_btn).click(elem_slot_btn).perform()
    except StaleElementReferenceException:
        print("[-]Element Reference Exception error!\r\n")
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    except TimeoutException as e:
        print("[-]Time out!!\r\n")
        wechat_push('超时，正在重新启动程序','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    except ElementClickInterceptedException as ECTE:
        print("[-]元素被其他元素挡住，报ElementClickInterceptedException异常\r\n")
        wechat_push('元素被其他元素挡住，正在重新启动程序','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()


def main():
    banner()
    global counter
    try:
        r = requests.get(url, headers = headers, timeout = 20)
    except :
        print("[-]可能存在超时，正在重新启动程序。\r\n")
        wechat_push('超时，正在重新启动程序','时间是：' + date_str )
        driver.quit()
        os.system('python ' + realpath)
        sys.exit()
    r.encoding = r.apparent_encoding
    title = re.findall("<title>(.*)</title>", r.text, re.IGNORECASE)[0].strip()
    if (r.status_code == 200) and (title == '小帮手'):
        pass
    else:
        print("[+] 网站故障（找程序猿祭天去），出现非200状态码，或者不用打卡（太好了）。。")
        wechat_push('网站出现非200的状态码','时间是：' + date_str  )
        sleep(5)
        sys.exit()
    driver1 = login(driver, url)
# 判断是否是节假日和调休
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=5))
    s.mount('https://', HTTPAdapter(max_retries=5))
    try:
        response = s.get(holiday_api, headers = headers, timeout = 12)
    except RequestException as e:
        print("请求异常\r\n")
        wechat_push('节假日接口API出现异常，请联系作者！','时间是：' + date_str  )

    d = json.loads(response.text)
    holiday_type = d['type']['type']
# 判断是否需要验证码才能登录
    try:
        success = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hb_bg")))
        if success:
            print("[+].登录成功！！准备打卡。")
            if (holiday_type == 1) or (holiday_type == 2):
                rest_btn(driver1)
            else:
                punchin_btn(driver1)
    except :
        pass
# 这里要加个循环判断是否验证成功
    while True:
        counter = counter + 1
        try:
            refresh_elem = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='slide-verify-refresh-icon']")))
            refresh_elem.click()
        except TimeoutException as e:
            print("[-]刷新元素超时")
            driver.quit()
            wechat_push('刷新元素超时，可能是高峰时间段，正在重新启动程序！','时间是：' + date_str )
            os.system('python ' + realpath)
            sys.exit()

        bkg, blk = get_image(driver1)
        distance, template = get_distance(bkg, blk, driver1)
        #show(template)
        tracks = get_tracks(distance)
        tracks.append(-(sum(tracks)-distance))
        mov_to_gap(driver1, distance)
        try:
            success = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hb_bg")))
            if success:
                print("[+].登录成功！！准备打卡。")
                break
        except :
            print("[-]验证码识别错误，正在第%d次验证码重试。\r\n" % counter)
            sleep(3)
            continue

    if (holiday_type == 1) or (holiday_type == 2):
        rest_btn(driver1)
    else:
        punchin_btn(driver1)
    wechat_push('电科云打卡成功','时间是：' + date_str)
    print("[+] wechat消息已推送")
    #txt = '【1】电科云打卡成功（本消息由脚本自动发送，请自行忽略），请不要挤兑！记得换京东卡！！ ' + date_str
    #wx_msg.send_wx_msg(txt)
    print("[+] 打卡成功，准备退出")
    sleep(3)
    driver.quit()
    sys.exit()


if __name__ == '__main__':
    main()

