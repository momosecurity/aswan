## 接入方式
    协议:
        HTTP
    URL: 
        http://ip:port/query/
    请求方法:
        POST
    请求体:
        一个包含多种信息的json，具体见下方 `参数信息`
    其它:
        headers 中 content-type 必须是 "application/json" 

## 参数信息

| key | 类型 | 含义 | 是否必填 |
| ---- | ---- | ---- | ---- |
| user_id | string | 账号ID | 是 |
| token | string | 标识业务方, 接入时分发 | 是 |
| app_name | string | 业务方标识，接入时分发 | 是 |
| rule_id | string | 规则ID, 每个调用点可能不同 | 是 |
| ip | string | 用户当前IP地址 | 否 |
| uid | string | 用户当前设备号 | 否 |
| other_user_id | string | 关联的账号ID | 否 |


## 调用示例

``` python

import requests

data = {
    'app_name': 'test_app',
    'ip': '1.1.1.1',
    'rule_id': '1',
    'token': '111111111111111',
    'uid': '111111111111111',
    'user_id': '11111'
}

ip = '127.0.0.1'
port = 50000

requests.post(f'http://{ip}:{port}/query/', json=data)
```

# 返回数据示例：
``` python

# 成功结果示例
'{"result":{"control":"deny","weight":100},"em":"OK","ec":0}'

# 失败结果示例
'{"error":"invalid token","em":"invalid token","ec":70}'

# warning 规则停用后，会返回错误
``` 

# 返回数据结果说明
返回的control可能为以下几种(具体执行动作与产品/运营确认)

|control|含义|
|----|----|
|pass|直接通过|
|deny|拒绝|
|log|风控系统记录日志，业务方无须处理，直接通过即可|
|message|短信验证|
|picture|图片验证|
|number|数字验证|
|verify|审核|
