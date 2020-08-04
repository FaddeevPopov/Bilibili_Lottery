"""
    基于原有的Python动态抽奖代码而写的程序。
    使用环境：Python 3.x
    需安装Pandas
    
    原代码信息如下：
    -----------------------------------------
    Bilibili动态转发抽奖脚本 Python 3 版本
    修改者信息：
    Bilibili 用户名：蝉森旅人
    Github：https://github.com/HaroldLee115
    原作者信息：
    Bilibili动态转发抽奖脚本 V1.1
    Auteur:Poc Sir   Bilibili: 鸟云厂商
    Mon site Internet:https://www.hackinn.com
    Weibo:Poc-Sir Twitter:@rtcatc
    更新内容：1.增加了对画册类型动态的支持。
    -----------------------------------------
    修改内容：
    1. 原程序使用SQL处理数据，现使用csv格式存储数据，并用pandas对数据进行处理。
    2. 添加去重命令，同一用户无论转发多少次，都只保留第1条转发数据。
    3. 由于B站api限制，只能抓取最新的500多条转发数据。因此增加保存数据功能，定期将数据保存在磁盘文件中，以避免遗漏早期的转发者。
    4. 其他优化修改，方便使用。
    @author: B站用户名：OriginLab
"""

import os
import requests
import random
import webbrowser
import re
import time
from urllib import parse as urlparse

count = 5
while count:
    try:
        import pandas as pd
        break
    except:
        print('未安装Pandas，现在进行安装。')
        os.system('pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas')
        count -= 1
        continue

path = os.path.dirname(os.path.abspath(__file__))


def GetMiddleStr(content, startStr, endStr):
    startIndex = content.index(startStr)
    if startIndex >= 0:
        startIndex += len(startStr)
    endIndex = content.index(endStr)
    return content[startIndex:endIndex]


def TellTime():
    localtime = "[" + str(time.strftime('%H:%M:%S',
                                        time.localtime(time.time()))) + "] "
    return localtime


def GetDynamicid():
    s = input("请粘贴动态网址：")
    nums = re.findall(r'\d+', s)

    bilibili_domain = urlparse.urlparse(s)[1]

    if bilibili_domain == "t.bilibili.com":
        print(TellTime() + "为纯文本类型动态")
        return str(nums[0])
    elif bilibili_domain == "h.bilibili.com":
        bilibili_docid = "https://api.vc.bilibili.com/link_draw/v2/doc/dynamic_id?doc_id=" + \
            str(nums[0])
        Dynamic_id = GetMiddleStr(requests.get(
            bilibili_docid).text, "dynamic_id\":\"", "\"}}")
        print(TellTime() + "为画册类型动态")
        return Dynamic_id


def GetTotalRepost(Dynamic_id):
    DynamicAPI = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id=" + Dynamic_id
    BiliJson = requests.get(DynamicAPI).json()
    Total_count = BiliJson['data']['card']['desc']['repost']
    UP_UID = BiliJson['data']['card']['desc']['user_profile']['info']['uid']
    return Total_count, UP_UID


def GetUsers(Dynamic_id):
    Total_count, _ = GetTotalRepost(Dynamic_id)
    file_name = path + '/' + str(Dynamic_id)+'.csv'
    offset = 0
    DynamicAPI = "https://api.live.bilibili.com/dynamic_repost/v1/dynamic_repost/view_repost?dynamic_id=" + \
        Dynamic_id + "&offset="
    with open(file_name, 'a') as f:
        while offset < Total_count:
            Tmp_DynamicAPI = DynamicAPI + str(offset)
            try:
                BiliJson = requests.get(Tmp_DynamicAPI).json()[
                    'data']['comments']
                for BiliJson_dict in BiliJson:
                    print(BiliJson_dict['uid'],
                          BiliJson_dict['uname'],
                          BiliJson_dict['comment'].replace(
                              ',', '').replace('\n', '').replace('\r', ''),
                          str(BiliJson_dict['rp_dyn_id']),
                          sep=',', file=f)
            except:
                break
            offset = offset + 20
        else:
            offset = 0
    df = pd.read_csv(file_name, names=[
                     'UID', 'Uname', 'Comment', 'rp_id'], header=None)
    df.drop_duplicates(subset='UID', keep='first', inplace=True)
    df = df.reset_index(drop=True)
    df.to_csv(file_name, header=False, index=False)
    print(TellTime() + "已将数据保存到" + file_name + "，总共%d条数据。" % df.shape[0])


def GetLuckyDog(data):
    total_users = len(data.index)
    Doge = random.randint(0, total_users)
    lucky_dog = data.iloc[Doge]
    print("用户ID:", lucky_dog["UID"])
    print("用户名:", lucky_dog["Uname"])
    print("转发详情：", lucky_dog["Comment"], "\n")
    dynamic_open = input(TellTime() + "是否打开转发动态：（Y/N）")
    if dynamic_open == "Y" or dynamic_open == "y":
        webbrowser.open("https://t.bilibili.com/" + str(lucky_dog["rp_id"]))
    message_open = input(TellTime() + "是否打开网页给获奖用户发送私信：（Y/N）")
    if message_open == "Y" or message_open == "y":
        webbrowser.open(
            "https://message.bilibili.com/#/whisper/mid" + str(lucky_dog["UID"]))


def GetData():
    print("+------------------------------------------------------------+")
    print("|在电脑端登录Bilibli,点击进入个人主页,再点击动态,进入动态页面|")
    print("|点击对应的动态内容，将获取到的网址复制，并粘贴在下方：      |")
    print("+------------------------------------------------------------+\n")
    Dynamic_id = GetDynamicid()
    TellTime()
    print(TellTime() + "获取动态成功，ID为：" + Dynamic_id)
    print(TellTime() + "正在获取转发者数据...")
    GetUsers(Dynamic_id)
    return Dynamic_id


def draw():
    Dynamic_id = GetData()
    file_name = path + '/' + str(Dynamic_id) + '.csv'
    df = pd.read_csv(file_name, names=[
                     'UID', 'Uname', 'Comment', 'rp_id'], header=None)
    total_users = df.shape[0]
    print(TellTime() + "总共参与抽奖的人数为：", total_users)
    if total_users == 0:
        print('没人转发 请黑箱我')
    else:
        print(TellTime() + "中奖用户信息：\n")
    draw_next = True
    while draw_next:
        GetLuckyDog(df)
        more = input(TellTime() + "是否再抽一个：（Y/N）")
        if more == "N" or more == "n":
            draw_next = False
    print(TellTime() + "程序退出。")


if __name__ == '__main__':
    print(TellTime() + "你想干嘛？")
    print("\t1. 保存数据\n\t2. 抽奖\n\t3. 清除数据")
    case = input("请输入数字：1, 2或3：")
    if case == "1":
        GetData()
        print(TellTime() + "程序退出。")
    elif case == "2":
        draw()
    elif case == "3":
        Dynamic_id = GetDynamicid()
        file_name = path + '/' + str(Dynamic_id) + '.csv'
        try:
            os.remove(file_name)
            print(TellTime() + "已清除文件" + file_name + '，程序退出。')
        except:
            print(TellTime() + "文件不存在，程序退出。")
    else:
        print(TellTime() + "输入不正确，程序退出。")
