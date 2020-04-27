from werkzeug.routing import BaseConverter
from flask import session, g, jsonify
from response_code import RET
import functools

# 自定义转换器
class ReConverter(BaseConverter):
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        self.regex = regex


# 自定义登录验证装饰器
def login_required(view_func):

    @functools.wraps(view_func)
    def wrapper(*args,**kwargs):
        # 判断用户的登录状态
        user_id = session.get('user_id')
        # 如果登录
        if user_id is not None:
            # 将user_id保存到g对象中，在视图函数中可以通过g对象获取保存数据
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 如果未登录，返回未登录的信息
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    return wrapper





