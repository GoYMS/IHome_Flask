from flask import Flask
from config import DevelopmentConfig
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_session import Session
from flask_wtf import CSRFProtect
import logging
from ihome.utils.commons import ReConverter

# 数据库
db = SQLAlchemy()
# 创建redis的空对象
redis_store = None


def create_app(config_name):
    """
    创建flask的应用对象
    :param config_name: 配置模式的模式名字
    :return:
    """
    app = Flask(__name__)
    # 为flask添加自定义的转换器
    app.url_map.converters['re'] = ReConverter

    db.init_app(app)

    # 注册配置文件
    app.config.from_object(config_name)

    # 创建redis的对象
    global redis_store
    redis_store = redis.StrictRedis(host=DevelopmentConfig.REDIS_HOST, port=DevelopmentConfig.REDIS_PORT)

    # 利用flask_session ,将session存到redis中
    Session(app)

    # 为flask补充csrf验证
    CSRFProtect(app)

    # 注册蓝图
    from .api_1_0 import api  # 推迟导入 防止导包失败
    app.register_blueprint(api, url_prefix='/api/v1.0')
    from .web_html import html
    app.register_blueprint(html)

    return app



