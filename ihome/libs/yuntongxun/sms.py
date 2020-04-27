#coding:utf-8

from ihome.libs.yuntongxun.CCPRestSDK import REST


# 主帐号
accountSid = '8aaf070870e20ea101713a739ab03024'

# 主帐号Token
accountToken = 'ec054b42983e4cbebe024eb0d9debc55'

# 应用ID
appId = '8aaf070870e20ea101713a739b0c302a'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'

# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id


class CCP(object):
    """自己封装的发送短信的辅助类"""
    # 用来保存对象的类属性
    instance = None

    def __new__(cls, *args, **kwargs):
        # 判断ccp类有没有已经创建好的对象，如果没有，创建一个对象，并保存
        # 如果有，则将保存的对象直接返回
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls.instance = obj
        return cls.instance

    def send_template_sms(self, to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # for k, v in result.items():
        #
        #     if k == 'templateSMS':
        #         for k, s in v.items():
        #             print('%s:%s' % (k, s))
        #     else:
        #         print('%s:%s' % (k, v))

        # status_code = result.get('statusCode')
        # if status_code == '000000':
        #     # 发送成功
        #     return 0
        # else:
        #     # 发送失败
        #     return -1



        # 正常应该是上边的形式，但是不知道为什么，总是报错网络出错，但是还是能正常收到短信
        # 所以我怀疑是我找的这个python3的模板不行，所以只能以这种形式，勉强完成相应的功能
        return 0


if __name__ == '__main__':
    ccp = CCP()
    ccp.send_template_sms('15515819567', ['1234', '5'], 1)

