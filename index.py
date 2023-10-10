"""
github：rialll
"""

import requests
import hashlib
import hmac
import json
import time
import random


SECRET_KEY = 'Anything_2023'
ADDITIONAL_TEXT = None
DTYPE = 6
def get_token():
    global ADDITIONAL_TEXT
    if ADDITIONAL_TEXT:
        return ADDITIONAL_TEXT
    """
    获取 Token
    """
    url = "https://sxbaapp.vae.ha.cn/interface/token.ashx"
    headers = {
        'content-type': 'application/json;charset=UTF-8',
    }

    # 构建请求数据

    response = requests.post(url, headers=headers)
    try:
        result = response.json()
        if result["code"] == 1001:
            token = result["data"]["token"]
            print("获取 Token 成功:", token)
            return token
        else:
            print("获取 Token 失败:", result.get("msg", "未知错误"))
            return ""
    except json.JSONDecodeError:
        print("解析获取 Token 的响应时发生 JSON 解析错误")
        return ""


def push_notification(phone_number,token, content,title="职校家园签到结果", template="html", channel="wechat"):
    push_url = "http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": phone_number + title,
        "content": content,
        "template": template,
        "channel": channel
    }

    try:
        response = requests.post(push_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
        response_data = response.json()

        if response_data.get("code") == 200:
            return True, "推送成功"
        else:
            return False, f"推送失败，错误信息: {response_data.get('msg', '未知错误')}"
    except Exception as e:
        return False, f"推送失败，发生异常: {str(e)}"
def load_users_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        users = json.load(file)
    return users
def calculate_md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def calculate_hmac_sha256(secret_key, message):
    key = bytes(secret_key, 'utf-8')
    message = bytes(message, 'utf-8')
    hashed = hmac.new(key, message, hashlib.sha256)
    return hashed.hexdigest()

def generate_headers(sign, phone_phonetype):
    return {
        'os': 'android',
        'phone': phone_phonetype,
        'appversion': '56',
        'sign': sign,
        'content-type': 'application/json;charset=UTF-8',
        'accept-encoding': 'gzip',
        'user-agent': 'okhttp/3.14.9'
    }

def send_request(url, method, headers, data):
    if method.upper() == 'POST':
        response = requests.post(url, headers=headers, data=json.dumps(data))
    elif method.upper() == 'GET':
        response = requests.get(url, headers=headers, params=data)
    else:
        raise ValueError("Unsupported HTTP method")

    return response.text

def calculate_sign(data, additional_text,secret_key=SECRET_KEY):


    # 将数据转换为 JSON 格式
    json_data = json.dumps(data)

    # 将 JSON 数据与附加文本连接
    combined_text = json_data + additional_text

    # 计算 HmacSHA256
    return calculate_hmac_sha256(secret_key, combined_text)

def login_request(phone_number, password, dToken,additional_text):
    # 将密码进行 MD5 加密
    encrypted_password = calculate_md5(password)

    # 要发送的数据
    data = {
        "phone": phone_number,
        "password": hashlib.md5(password.encode()).hexdigest(),
        "dtype": 6,
        "dToken": dToken
    }

    # 计算签名
    sign = calculate_sign(data,additional_text)

    # 生成请求头
    headers = generate_headers(sign, phone_number)

    # 请求地址
    url = 'http://sxbaapp.vae.ha.cn/interface/relog.ashx'

    # 发送请求
    response_text = send_request(url, 'POST', headers, data)

    return response_text

def sign_in_request(uid, address, phonetype, probability, longitude, latitude, additional_text,modify_coordinates=False):
    longitude = float(longitude)
    latitude = float(latitude)
    # 如果需要修改坐标，则进行修改
    if modify_coordinates:
        longitude = round(longitude + random.uniform(-0.00001, 0.00001), 6)
        latitude = round(latitude + random.uniform(-0.00001, 0.00001), 6)

    # 要发送的数据
    data = {
        "dtype": 1,
        "uid": uid,
        "address": address,
        "phonetype": phonetype,
        "probability": probability,
        "longitude": longitude,
        "latitude": latitude
    }

    # 计算签名
    sign = calculate_sign(data,additional_text)

    # 生成请求头
    headers = generate_headers(sign, phonetype)

    # 请求地址
    url = 'http://sxbaapp.vae.ha.cn/interface/clockindaily20220827.ashx'

    # 发送请求
    response_text = send_request(url, 'POST', headers, data)

    return response_text


def login_and_sign_in(phone_number, password, address, phonetype, longitude,latitude, dToken,pushtoken,modify_coordinates=False):
    # 登录
    ADDITIONAL_TEXT = get_token()
    if not ADDITIONAL_TEXT:
        print("获取 Token 失败，无法继续操作")
        if pushtoken:
            token = pushtoken
            push_notification(phone_number, token, "错误,加密Token获取错误！")
        return
    login_response = login_request(phone_number, password,dToken,ADDITIONAL_TEXT)
    try:
        login_result = json.loads(login_response)
        if login_result['code'] == 1001:
            # 登录成功
            uid = login_result['data']['uid']
            print("登录成功，UID:", uid)

            # 从用户信息中获取经度和纬度


            time.sleep(1)

            # 签到
            sign_in_response = sign_in_request(uid, address, phonetype, 2, longitude, latitude, ADDITIONAL_TEXT ,modify_coordinates)

            # 处理签到响应
            try:
                sign_in_result = json.loads(sign_in_response)
                if sign_in_result['code'] == 1001:
                    # 签到成功
                    print("签到成功:", sign_in_result['msg'])
                    if pushtoken:
                        token = pushtoken
                        push_notification(phone_number, token,"签到成功:" + sign_in_result['msg'])
                else:
                    # 签到失败
                    print("签到失败，错误信息:", sign_in_result.get('msg', '未知错误'))
                    if pushtoken:
                        token = pushtoken
                        push_notification(phone_number, token,"签到失败，错误信息:" + sign_in_result.get('msg', '未知错误'))
            except json.JSONDecodeError:
                print("处理签到响应时发生 JSON 解析错误")
                if pushtoken:
                    token = pushtoken
                    push_notification(phone_number, token, "签到失败，出现未知错误！")
        else:
            # 登录失败
            print("登录失败，错误信息:", login_result.get('msg', '未知错误'))
            if pushtoken:
                token = pushtoken
                push_notification(phone_number, token, "登录失败，错误信息:" +  login_result.get('msg', '未知错误'))
    except json.JSONDecodeError:
        print("处理登录响应时发生 JSON 解析错误")
        if pushtoken:
            token = pushtoken
            push_notification(phone_number, token, "处理登录响应时发生 JSON 解析错误")
    except KeyError:
        print("处理登录响应时发生关键字错误")
        if pushtoken:
            token = pushtoken
            push_notification(phone_number, token, "处理登录响应时发生 JSON 解析错误")

def main_handler(a,b):
    print("项目地址：https://github.com/rialll/fuckZXJY")
    users_file_path = "users.json"
    users = load_users_from_json(users_file_path)
    for user in users:
        longitude = user.get("longitude", 0.0)
        latitude = user.get("latitude", 0.0)
        if user.get("enabled", True):
            login_and_sign_in(
                phone_number =user["phone_number"],
                password = user["password"],
                address = user["address"],
                phonetype = user["phonetype"],
                longitude = user.get("longitude", 0.0),
                latitude = user.get("latitude", 0.0),
                dToken = user.get("dToken", ""),
                pushtoken=user.get("pushtoken"),
                modify_coordinates=user.get("modify_coordinates", False),
            )
# 示例用法
if __name__ == "__main__":
    main_handler(1,2)

