from ihome.api_1_0 import api
from alipay import AliPay
import os
from ihome.utils.commons import login_required
from ihome.models import Order
from flask import g, jsonify, request
from response_code import RET
from ihome import db


@api.route('/orders/<int:order_id>/payment', methods=['POST'])
@login_required
def order_pay(order_id):
    """发起支付宝请求"""
    user_id = g.user_id
    # 判断订单状态
    try:
        order = Order.query.filter(Order.id==order_id, Order.user_id==user_id, Order.status=='WAIT_PAYMENT').first()
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg='订单错误')

    app_private_key_string = open("/home/yms/PycharmDemo/FlaskDemo/Flask_iHome/ihome/api_1_0/keys/private_2048.txt").read()
    alipay_public_key_string = open("/home/yms/PycharmDemo/FlaskDemo/Flask_iHome/ihome/api_1_0/keys/alipay_key_2048.txt").read()

    app_private_key_string == """
        -----BEGIN RSA PRIVATE KEY-----
        base64 encoded content
        -----END RSA PRIVATE KEY-----
    """

    alipay_public_key_string == """
        -----BEGIN PUBLIC KEY-----
        base64 encoded content
        -----END PUBLIC KEY-----
    """
    # 创建支付宝的sdk工具对象
    alipay = AliPay(
        appid="2016101800719127",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False  # 默认False
    )

    # 电脑网站支付，需要跳转到 https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order.id,  # 自己项目的订单id
        total_amount=str(order.amount/100.0),  # 总金额
        subject="爱家租房 %s" % order.id,  # 项目的名称
        return_url="http://127.0.0.1:5000/pay_Complete.html",  # 返回连接的地址，也就是支付成功后跳转的页面

        notify_url=None,  # 可选, 不填则使用默认notify url ，支付成功后支付宝向哪个页面发送支付状态
    )

    # 构建用户跳转的支付宝支付页面

    pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
    print(pay_url)

    return jsonify(errno=RET.OK, errmsg='OK', data={'pay_url': pay_url})


@api.route('order/payment', methods=['PUT'])
def save_order_payment_result():
    """保存订单支付结果"""
    # 获取支付宝前端传过来的支付结果的url
    alipay_dict = request.form.to_dict()

    # 对支付宝的数据进行分离,提取出支付宝的签名参数sign,和剩下的其他数据
    alipay_sign = alipay_dict.pop('sign')

    app_private_key_string = open(
        "/home/yms/PycharmDemo/FlaskDemo/Flask_iHome/ihome/api_1_0/keys/private_2048.txt").read()
    alipay_public_key_string = open(
        "/home/yms/PycharmDemo/FlaskDemo/Flask_iHome/ihome/api_1_0/keys/alipay_key_2048.txt").read()

    app_private_key_string == """
            -----BEGIN RSA PRIVATE KEY-----
            base64 encoded content
            -----END RSA PRIVATE KEY-----
        """

    alipay_public_key_string == """
            -----BEGIN PUBLIC KEY-----
            base64 encoded content
            -----END PUBLIC KEY-----
        """

    # 创建支付宝的sdk工具对象
    alipay = AliPay(
        appid="2016101800719127",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False  # 默认False
    )
    # 借助工具验证参数的合法性
    # 如果确定参数，返回True
    result = alipay.verify(alipay_dict, alipay_sign)

    if result:
        # 修改订单的状态
        order_id = alipay_dict.get('out_trade_no')
        try:
            Order.query.filter_by(id=order_id).update({'status':'WAIT_COMMENT'})
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="ok")

