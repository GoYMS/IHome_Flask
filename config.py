import redis
import pymysql


class Config(object):
    """配置信息"""
    DEBUG = True
    # csrf验证
    SECRET_KEY = 'JKHFUIASH'

    # 连接数据库的方式
    pymysql.install_as_MySQLdb()
    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/ihome?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # flash-session配置
    SESSION_TYPE = 'redis'  # 指定使用什么方法存储session
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行隐藏
    PERMANENT_SESSION_LIFETIME = 86400    # 设置过期时间，单位秒


class DevelopmentConfig(Config):
    """开发者模式的配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境的配置信息"""
    pass


