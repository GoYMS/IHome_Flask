from . import api
from flask import request, jsonify, session
from response_code import RET
import re
from ihome import redis_store, db
from ihome.models import User


@api.route('/users', methods=['POST'])
def register():
    """用户注册
    请求的参数：手机号，短信验证码，密码，确认密码
    参数格式：json
    """
    # 获取请求的json数据，返回字典
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')

    # 校验参数
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 判断手机号格式
    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码格式不对')
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='两次密码不一致')

    # 从redis中取出短信验证码
    try:
        real_sms_codes = redis_store.get('sms_code_%s'%mobile)
        real_sms_code = str(real_sms_codes, encoding="utf-8")
    except Exception as e:
        return jsonify(errno=RET.DATAERR, errmsg='读取真实验证码错误')
    # 判断验证码是否存在
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg='验证码失效')

    # 删除redis中的短信验证码，防止重复使用校验
    # try:
    #     redis_store.delete('sms_code_%s'%mobile)
    # except Exception as e:
    #     pass

    # 判断用户填写验证码的正确性
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    # 判断手机号是否注册过
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已经存在')

    # 存储用户的信息
    user = User(name=mobile, mobile=mobile)
    # 使用model中的方法，将密码进行加密，并将加密的密码直接存入到密码属性中
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        # 如果出错，将数据进行回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')
    # 保存登陆的状态到数据库中
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg='注册成功')


@api.route('/sessions', methods=['POST'])
def login():
    """
    用户登录
    参数：手机号，密码
    :return:
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')
    # 校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 手机号的格式
    if not re.match(r'1[34578]\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    # 判断错误次数是否超过限制，如果超过限制，则返回
    # redis 记录'access_nums_请求IP'：'次数'
    user_ip = request.remote_addr  # 获取访问的用户的IP
    try:
        access_nums = redis_store.get('access_nums_%s'%user_ip)
    except Exception as e:
        if access_nums is not None and int(access_nums)>=5:
            return jsonify(errno=RET.REQERR, errmsg='错误次过多，请稍后重试')

    # 从数据库中根据手机号查询用户的数据对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')

    # 用数据库的密码与用户的密码进行对比验证
    # model中定义的一个check_password方法，获取原始密码
    if user is None and user.check_password(password) is False:
        # 如果验证失败，记录错误记录
        try:
            redis_store.incr('access_nums_%s'%user_ip)  # incr 是redis中的一个函数，是专门用于数值叠加的
            redis_store.expire('access_nums_%s'%user_ip, 600)  # 设置过期时间

        except Exception as e:
            pass
        return jsonify(errno=RET.DATAERR, errmsg='用户名或者密码错误')

    # 如果验证成功，保存登录状态，存在session中
    session['name'] = user.name
    session['mobile'] = mobile
    session['user_id'] = user.id

    return jsonify(errno=RET.OK, errmsg='登录成功')


@api.route('/session', methods=['GET'])
def check_login():
    # 获取session中的数据
    name = session.get('name')
    if name is not None:
        return jsonify(errno=RET.OK, errmsg='True', data={'name':name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg='False')


@api.route('/session', methods=['DELETE'])
def layout():
    """退出登录"""
    # 将session中的数据清楚
    csrf_token = session.get('csrf_token')
    session.clear()
    session['csrf_token'] = csrf_token
    return jsonify(errno=RET.OK, errmsg='OK')
