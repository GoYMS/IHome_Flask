from . import api
from ihome.utils.commons import login_required
from flask import g, request, jsonify, session
from response_code import RET
from constants import IMAGE_URL
from ihome.utils.image_storage import storage
from ihome import db
from ihome.models import User


@api.route('/users/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    """
    设置用户的头像
    :return:
    图片（多媒体表单格式） 用户id（g.user_id）
    """
    # 装饰器的代码已经将user保存到了g对象当中了
    user_id = g.user_id

    # 获取前端上传的图片
    image_file = request.files.get('avatar')
    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg='未上传图片')
    # 将图片的数据读取出来
    image_data = image_file.read()
    # 存入到七牛网中
    try:
        file_name = storage(image_data)
    except Exception as e:
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')

    # 保存文件名到数据库中
    try:
        User.query.filter_by(id=user_id).update({'avatar_url': file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存图片失败')
    avatar_url = IMAGE_URL + file_name
    # 从数据库中获取头像url
    # try:
    #     user = User.query.filter_by(id=user_id)
    #     url = user.avatar_url
    # except Exception as e:
    #     return jsonify(errno=RET.DBERR, errmsg='获取头像失败')
    # else:
    #     url_last = IMAGE_URL + url

    # 保存成功
    return jsonify(errno=RET.OK, errmsg='保存成功', data={
        'avatar_url': avatar_url,

    })


@api.route('/user/names', methods=['PUT'])
@login_required
def change_user_name():
    """修改用户名"""
    # 获取前端传过来的数据
    resp_data = request.get_json()
    if not resp_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 获取用户设置的名字
    name = resp_data.get('name')
    # 修改用户名，并判断name是否重复，利用数据库的唯一索引
    try:
        User.query.filter_by(id=g.user_id).update({'name': name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='用户名重复')
    # 修改sessinon中的name字段
    session['name'] = name
    return jsonify(errno=RET.OK, errmsg='修改成功', data={'name': name})


@api.route('/user')
@login_required
def get_user_profile():
    """获取个人信息"""
    user_id = g.user_id
    # 查询数据库获取个人信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg='无效操作')
    # model中定义的一个方法，将数据转换成字典的形式
    return jsonify(errno=RET.OK, errmsg='OK', data=user.info_to_dict())


@api.route('/users/auth')
@login_required
def get_user_auth():
    """获取用户的实名认证信息"""
    user_id = g.user_id
    # 在数据库中查询信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='获取用户实名信息失败')
    return jsonify(errno=RET.OK, errmsg='OK', data=user.auth_to_dict())


@api.route('/users/auth', methods=['POST'])
@login_required
def set_user_auth():
    """设置用户的实名认证信息"""
    user_id = g.user_id

    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    real_name = req_data.get('real_name')
    id_card = req_data.get('id_card')

    if not all([real_name,id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 保存用户的姓名与身份证号
    try:
        User.query.filter_by(id=user_id).update({
            'real_name': real_name,
            'id_card': id_card
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存用户认证信息失败')
    return jsonify(errno=RET.OK, errmsg='ok')


