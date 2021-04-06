## 接入方式
    协议:
        HTTP
    地址:
        http://ip:port/report/
    请求方法:
        POST
    请求体:
        一个包含多种信息的json，具体见下方 `参数信息`
    其它:
        headers 中 content-type 必须是 "application/json"

## 参数信息

| key | 类型 | 含义 | 是否必填 |
| :----: | :----: | :----: | :----: |
| user_id | string | 账号ID | 是 |
| source_name | string | 数据源名称，每个接入点单独指定 | 是 |
| timestamp | long | 用户动作发生时间(秒级时间戳) | 是 |
| ip | string | 用户当前IP地址 | 否 |
| uid | string | 用户当前设备号 | 否 |
| other_user_id | string | 关联的账号ID | 否 |


## 调用示例

``` python

import requests

data = {
 'ip': '1.1.1.1',
 'source_name': 'test_test',
 'timestamp': 1568271589,
 'uid': '11111111111111111111',
 'user_id': '1111'
}

ip = ''
port = 50000

requests.post(f'http://{ip}:{port}/report/', json=data)
```

## 返回数据示例：
``` python
# 正常
'{"result":"success","em":"OK","ec":0}'

# 错误
'{"error":"invalid source","em":"invalid source","ec":100}'
```
