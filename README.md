# 电科云nCov2019自动打卡 - 使用说明 

- 2021/3/1 更新：修复某处可能导致超时异常的处理。
- 2021/1/24 更新：修复opncv可能出现异常的处理，以及新增小帮手在维护时的处理。

- **本次更新新增了微信消息推送功能。**
- **脚本严禁用于非法测试**: 由于HW等原因，怀疑被红队利用该脚本进行暴力破解，所以这里提醒一下，该脚本仅用于打卡使用，不得用于非法测试，否则后果自负。
  
 - 1.支持微信消息推送功能，如果打卡成功，则将消息推送至微信。
 - 2.如果电科云网站出现非200状态码，或者小帮手在维护，则会通过微信发送服务器告警。
 - 3.支持滑动验证码自动识别。
 - 4.支持节假日自动选择“休假”，工作日选择“公司办公”，如果由特殊情况，请自行修改。

- 全部需要用到的软件有：Windows系统（Linux系统也可以，macOS也行），谷歌浏览器，Python3（第三方库），以及chrome driver。


## 安装说明与使用步骤

- **安装Python3**. 由于脚本使用python3开发，使用前，请务必安装好。
- **查看Chrome版本**.由于用到Chromedriver， 使用脚本前，请先查看自己的chrome版本号。![alt tag](/pic/chrome_version.png)
- **下载chromedriver**.比如是84.0.4147.125，然后去[chromedriver官网](https://chromedriver.storage.googleapis.com/index.html)下载最接近的版本。
  ![alt tag](/pic/downdriver.png)
- **修改脚本**. 需要修改的地方有四个：chromedriver的路径，登录的手机号码，以及登录密码和push+的token ![alt tag](/pic/change1.png).
-  **获取push+ Token**. 新版本由于增加了微信消息推送功能，这里需要注册一个push+的token，首先，请访问以下网站：
http://pushplus.hxtrip.com/login
 ![alt tag](/pic/pushpluslogin.png)
然后用微信扫描二维码，点击进入“一对一推送”，如下图所示，即可得到自己的token。
 ![alt tag](/pic/token.png)
 然后将pushplus_token改为刚刚得到的token。
-  **安装python依赖库**. 需要安装多个python库，执行以下命令：
  pip install -r requirements.txt -i https://pypi.douban.com/simple
-  **设置任务计划**. 在任务计划中设置每天晚上或者每天早上定时打卡 
 ![alt tag](/pic/task.png)



## 功能

- **跨平台**： 由于python与selenium自身就支持跨平台: 因此该脚本也具备跨平台能力.
- **方便快速**： 脚本全自动化打卡流程，从此妈妈再也不用担心上班忘记打卡了!
- **支持所有周末节假日，以及节假日调休**： 得益于某节假日接口，现在脚本已经具备周末节假日（居家办公），工作日（在岗）打卡的能力。
- **便于安装**: 直接运行pip install -r requirements.txt -i https://pypi.douban.com/simple  即可安装依赖文件。


## 效果
  ![alt tag](/pic/auto.gif)

