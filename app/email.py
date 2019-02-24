# -*- coding: utf-8 -*-

from threading import Thread
from flask import current_app, render_template,request,Flask
from flask_mail import Message
from app import mail
from app import create_tpapp
import time
from flask import Flask
timedic={}
APP = None

def async_send_mail(app, msg):
    with app.app_context():
        mail.send(message=msg)


# 异步发送邮件
def send_mail(to, subject, template, **kwargs):
    ip=request.remote_addr
    if ip in timedic:
        if time.time()-timedic[ip]<160:
            return False
        timedic[ip] = time.time()
    recipients = [to]
    timedic[ip]=time.time()
    app = current_app._get_current_object()
    msg = Message(subject=subject, recipients=recipients, sender=app.config['MAIL_USERNAME'])
    msg.html = render_template(template + '.html', **kwargs)
    #msg.body = render_template(template + '.txt', **kwargs)
    thr = Thread(target=async_send_mail, args=[app, msg])
    # 启动线程
    thr.start()
    return thr


def get_app():
    global apptmp
    apptmp=''
    if apptmp is  '':
        apptmp = create_tpapp()

def send_maila(to, subject, template, **kwargs):
    recipients = [to]
    get_app()
    with apptmp.app_context():
        msg = Message(subject=subject, recipients=recipients, sender=apptmp.config['MAIL_USERNAME'])
        msg.html = render_template(template + '.html', **kwargs)
        #msg.body = render_template(template + '.txt', **kwargs)
        thr = Thread(target=async_send_mail, args=[apptmp, msg])
        # 启动线程
        thr.start()
        return thr
