#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import requests
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
import traceback
import os
import json

# 域名和子域名
DOMAIN = os.environ['DOMAIN']
SUB_DOMAIN = os.environ['SUB_DOMAIN']

# API 密钥
ACCESSKEY = os.environ["ACCESSKEY"]
ACCESSKEYSECRET = os.environ["ACCESSKEYSECRET"]

# pushplus_token
PUSHPLUS_TOKEN = os.environ["PUSHPLUS_TOKEN"]


def get_cf_speed_test_ip(timeout=10, max_retries=5):
    for attempt in range(max_retries):
        try:
            # 发送 GET 请求，设置超时
            response = requests.get('https://ip.164746.xyz/ipTop.html', timeout=timeout)

            # 检查响应状态码
            if response.status_code == 200:
                return response.text
        except Exception as e:
            traceback.print_exc()
            print(f"get_cf_speed_test_ip Request failed (attempt {attempt + 1}/{max_retries}): {e}")
    # 如果所有尝试都失败，返回 None 或者抛出异常，根据需要进行处理
    return None


def build_info(client):
    try:
        describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
            domain_name=DOMAIN,
            rrkey_word=SUB_DOMAIN
        )
        runtime = util_models.RuntimeOptions()
        response = client.describe_domain_records_with_options(describe_domain_records_request, runtime)
        def_info = []
        print(111)
        print(response)
        print(222)
        if response.statusCode == 200:
            records = response.json()['result']
            for record in response["body"]["DomainRecords"]["Record"]:
                info = {"recordId": record["RecordId"], "value": record["RR"] + record["DomainName"]}
                if record["line"] == "default":
                    def_info.append(info)
            print(f"build_info success: ---- Time: " + str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- ip：" + str(def_info))
            return def_info
        else:
            print(f"build_info ERROR: ---- Time: " + str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- MESSAGE: " + str(response))    
    except Exception as e:
        traceback.print_exc()
        print(f"build_info ERROR: ---- Time: " + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- MESSAGE: " + str(e))


def change_dns(client, record_id, cf_ip):
    try:
        client.change_record(DOMAIN, record_id, SUB_DOMAIN, cf_ip, "A", "默认", 600)
        print(f"change_dns success: ---- Time: " + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- ip：" + str(cf_ip))
        return "ip:" + str(cf_ip) + "解析" + str(SUB_DOMAIN) + "." + str(DOMAIN) + "成功"

    except Exception as e:
        traceback.print_exc()
        print(f"change_dns ERROR: ---- Time: " + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- MESSAGE: " + str(e))
        return "ip:" + str(cf_ip) + "解析" + str(SUB_DOMAIN) + "." + str(DOMAIN) + "失败"


def pushplus(content):
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": "IP优选DNSPOD推送",
        "content": content,
        "template": "markdown",
        "channel": "wechat"
    }
    body = json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type': 'application/json'}
    requests.post(url, data=body, headers=headers)

def create_client() -> Alidns20150109Client:
    config = open_api_models.Config(
        access_key_id=ACCESSKEY,
        access_key_secret=ACCESSKEYSECRET
    )
    config.endpoint = f'alidns.cn-shanghai.aliyuncs.com'
    return Alidns20150109Client(config)

if __name__ == '__main__':

    # 构造Client
    client = create_client();

    # 获取DNS记录
    info = build_info(client)

    print(info)
    # 获取最新优选IP
    # ip_addresses_str = get_cf_speed_test_ip()
    # ip_addresses = ip_addresses_str.split(',')

    # pushplus_content = []
    # 遍历 IP 地址列表
    # for index, ip_address in enumerate(ip_addresses):
    #     # 执行 DNS 变更
    #     dns = change_dns(client, info[index]["recordId"], ip_address)
    #     pushplus_content.append(dns)

    # pushplus('\n'.join(pushplus_content))
