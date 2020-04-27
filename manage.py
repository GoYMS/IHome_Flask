
from config import DevelopmentConfig
from ihome import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# 创建app对象
app = create_app(DevelopmentConfig)
manage = Manager(app)
# 创建数据库迁移工具对象
Migrate(app, db=db)
# 向manage对象中添加数据库的操作命令
manage.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manage.run()
