from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_apscheduler import APScheduler
def create_tpapp():
    apptmp = Flask(__name__)
    apptmp.config.from_object('config')
    mail = Mail(apptmp)
    return apptmp

app = Flask(__name__)
app.config.from_object('config')

login_manger=LoginManager()
login_manger.login_view='login'
login_manger.login_message = ""
login_manger.init_app(app)


db = SQLAlchemy(app)
db.create_all()
mail = Mail(app)

scheduler=APScheduler()
scheduler.init_app(app)
scheduler.start()

from app import views,models



