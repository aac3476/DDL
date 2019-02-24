import os
SQLALCHEMY_DATABASE_URI = 'mysql://usrname:password@188.131.175.223:3306/name?charset=utf8'
SQLALCHEMY_MIGRATE_REPO = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_TEARDOWN = True

CSRF_ENABLED = True
SECRET_KEY = 'nicai'

MAIL_SERVER = 'smtp.exmail.qq.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_PASSWORD = 'xxxx'
MAIL_USERNAME = 'ywx@ywxisky.cn'

JOBS = [
    {
        'id': 'createschuler_job',
        'func': 'app.task:task',
        'args': None,
        'trigger': 'interval',
        'seconds': 10
    }
]
