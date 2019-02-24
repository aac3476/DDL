# -*- coding: utf-8 -*-

import re, json, datetime
from app import app, db, models
from flask import render_template, flash, redirect, request, url_for
from .forms import LoginForm, registerForm, resForm, editForm, profileForm
from .models import User, Notice, u2g, Gnotice, Group
from hashlib import md5
from random import Random
from .email import send_mail
from flask_login import login_user, login_required, logout_user, current_user
from .datejson import DateEncoder


@app.route('/')
@app.route('/index')
@login_required
def index():
    nt = Notice()
    nt.user = current_user.id
    a = Notice.query.filter_by(user=current_user.id).all()
    return render_template('users/index.html', data=a)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return (redirect(url_for('index')))
    form = LoginForm()
    if form.validate_on_submit():
        usr = User.query.filter_by(email=form.mail.data).first()
        if usr is None:
            return render_template('/users/login.html', form=form, notice=1, text="电子邮件不存在")
        passwd = form.password.data
        passwd = create_md5(passwd)
        passwd = create_md5(passwd + usr.salt)
        if passwd == usr.password:
            login_user(usr, form.remember.data)
            return (redirect(url_for('index')))
        else:
            return render_template('/users/login.html', form=form, notice=1, text="密码错误")

    return render_template('/users/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return (redirect(url_for('login')))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return (redirect(url_for('index')))
    form = registerForm()
    if form.validate_on_submit():
        userdata = dict(name=form.name.data, mail=form.mail.data, qq=form.qq.data, passsword=form.password.data,
                        passwordagain=form.passwordagain.data)
        if userdata['passwordagain'] != userdata['passsword']:
            flash("两次密码不一致!")
            userdata['passwordagain'] = ""
            userdata['passsword'] = ""
            return render_template('/users/register.html', form=form, data=userdata)
        if len(userdata['name']) > 15:
            userdata['passwordagain'] = ""
            userdata['passsword'] = ""
            flash("用户名长度不得超过15字符请检查！")
            userdata['name'] = ""
            return render_template('/users/register.html', form=form, data=userdata)
        if checkQQ(userdata['qq']) != 1:
            userdata['passwordagain'] = ""
            userdata['passsword'] = ""
            flash("请检查qq号！")
            userdata['qq'] = ""
            return render_template('/users/register.html', form=form, data=userdata)
        # 随机生成4位salt
        salt = create_salt()
        # 加密后的密码
        md5 = create_md5(userdata['passsword'])
        md5 = create_md5(md5 + salt)
        usra = User.query.filter_by(email=userdata['mail']).first()
        emailpass = create_salt(10)
        if usra is None:
            emailpass = create_md5(emailpass)
            usr = User(name=userdata['name'], password=md5, email=userdata['mail'], isemail=0, isopen=1,
                       qq=userdata['qq'], salt=salt, emailpass=emailpass)
            link = 'http://ddl.ywxisky.cn/active/' + emailpass
            send_mail(userdata['mail'], 'Confirm you email address', '/email/email', title='Confirm you email address',
                      data='请点击下面的按钮来激活您的邮箱地址，，或可以访问此链接：' + link, link=link)
            db.session.add(usr)
            db.session.commit()
            userdata['name'] = ''
            userdata['mail'] = ''
            userdata['qq'] = ''
            return render_template('/users/register.html', form=form, data=userdata, success=1)
        else:
            flash(r"邮箱已经被注册，点击此处<a href='login'>登陆</a>或者<a href='refind'>找回密码</a>")
            return render_template('/users/register.html', form=form, data=userdata)
    userdata = dict(name="", mail="", qq="", passsword="", passwordagain="")
    return render_template('/users/register.html', form=form, data=userdata)


@app.route('/active/<data>')
def active(data):
    usra = User.query.filter_by(emailpass=data).first()
    if usra is None:
        return "激活失败，系统错误,请尝试联系管理员或<a href='../login'>直接登陆</a></h3>"
    if usra.newemail is not None:
        usra.emailpass = ""
        usra.email = usra.newemail
        usra.newemail = ""
        db.session.add(usra)
        db.session.commit()
        logout_user()
        return r"<h3>新邮箱更换成功，请使用新的邮箱" + usra.email + "<a href='../login'>登陆</a></h3>"
    usra.isemail = 1
    usra.emailpass = ""
    db.session.add(usra)
    db.session.commit()
    return r"<h3>激活成功，<a href='../login'>点此登陆</a></h3>"


@app.route('/refind', methods=['POST'])
def refind():
    a = list(request.form)
    if (len(a) != 1):
        return '0'
    usr = User.query.filter_by(email=a[0]).first()
    if usr is None:
        return '2'
    findpassword = create_md5(create_salt(10))
    usr.findpassword = findpassword
    db.session.add(usr)
    db.session.commit()
    link = 'http://ddl.ywxisky.cn/resetpwd/' + findpassword
    if send_mail(a[0], 'reset password', '/email/email', title='reset password', data='请点击下面的按钮来重置密码，或可以访问此链接：' + link,
                 link=link):
        return '1'
    else:
        return '3'


@app.route('/resetpwd/<data>', methods=['POST', 'GET'])
def restpwd(data):
    usr = User.query.filter_by(findpassword=data).first()
    if usr is None:
        return (redirect(url_for('login')))
    form = resForm()
    mail = usr.email
    if form.validate_on_submit():
        if form.password.data == form.passwordag.data:
            if len(form.password.data) > 20 or len(form.password.data) < 6:
                return render_template('users/resetpwd.html', mail=mail, form=form, data=data, success=0)
            salt = create_salt()
            md5 = create_md5(form.password.data)
            md5 = create_md5(md5 + salt)
            usr.salt = salt
            usr.password = md5
            usr.findpassword = ""
            db.session.add(usr)
            db.session.commit()
            logout_user()
            return render_template('users/resetpwd.html', mail=mail, success=1, form=form, data=data)
    return render_template('users/resetpwd.html', mail=mail, form=form, data=data)


@app.route('/edit', methods=['POST', 'GET'])
@login_required
def edit():
    task = Notice()
    form = editForm()
    if request.args.get('id') is not None:
        task = Notice.query.filter_by(nid=request.args.get('id')).first()
        if task is None:
            flash("未知错误")
            return render_template('common/edit.html', form=form, task=Notice())
        if task.user != current_user.id:
            flash("无权限编辑")
            return render_template('common/edit.html', form=form, task=Notice())
        if request.method == 'GET':
            return render_template('common/edit.html', form=form, task=task)
        else:
            task.nid = request.args.get('id')
    if form.validate_on_submit():
        if (form.end.data - form.start.data).days < 0:
            flash("请检查起止时间")
            return render_template('common/edit.html', form=form, task=task)
        reqdata = request.form
        print(reqdata)
        typea = reqdata['typea']
        now = datetime.datetime.now()
        if (form.end.data - now).days < 0:
            flash("请检查起止时间")
            return render_template('common/edit.html', form=form, task=task)
        if typea == '1':
            time = datetime.timedelta(hours=1)
            time1 = form.end.data - time
            if (time1 - now).days < 0:
                flash("提醒时间已过")
                return render_template('common/edit.html', form=form, task=task)
            task.user = current_user.id
            task.nname = form.name.data
            task.starttime = form.start.data
            task.ddltime = form.end.data
            task.ntime1 = time1
            task.dec = form.dec.data
            task.if1 = 0
            task.if2 = 1
            task.type = '考试'
            db.session.add(task)
            db.session.commit()
            return render_template('common/edit.html', success=1, form=form, task=task)
        elif typea == '2':
            time = datetime.timedelta(days=1)
            time1 = form.end.data - time
            task.user = current_user.id
            task.nname = form.name.data
            task.starttime = form.start.data
            task.ddltime = form.end.data
            task.ntime1 = time1
            time = datetime.timedelta(hours=1)
            time2 = form.end.data - time
            task.ntime2 = time2
            if (time1 - now).days < 0 or (time2 - now).days < 0:
                flash("提醒时间已过,为了您的作业安全，设置作业提醒需提前24小时设置")
                return render_template('common/edit.html', form=form, task=task)
            task.dec = form.dec.data
            task.if1 = 0
            task.if2 = 0
            task.type = '作业'
            db.session.add(task)
            db.session.commit()
            return render_template('common/edit.html', success=1, form=form, task=task)
        elif typea == '3':
            time = datetime.timedelta(days=1)
            try:
                if reqdata['time1'] != '':
                    date1 = datetime.datetime.strptime(reqdata['time1'], '%Y-%m-%d %H:%M')
                    if1 = 0
                else:
                    if1 = 1
                if reqdata['time2'] != '':
                    date2 = datetime.datetime.strptime(reqdata['time2'], '%Y-%m-%d %H:%M')
                    if2 = 0
                else:
                    if2 = 1
            except:
                flash("时间格式错误")
                return render_template('common/edit.html', form=form, task=task)
            else:
                if if1 == 1 and if2 == 1:
                    flash("选择自定义请填写时间")
                    return render_template('common/edit.html', form=form, task=task)
                task.user = current_user.id
                task.nname = form.name.data
                task.starttime = form.start.data
                task.ddltime = form.end.data
                if if1 == 0:
                    if (date1 - now).days < 0:
                        if1 = 1
                    else:
                        task.ntime1 = date1
                if if2 == 0:
                    if (date2 - now).days < 0:
                        if2 = 1
                    else:
                        task.ntime2 = date2
                if if1 == 1 and if2 == 1:
                    flash("提醒时间已过")
                    return render_template('common/edit.html', form=form, task=task)
                task.if1 = if1
                task.if2 = if2
                task.dec = form.dec.data
                task.type = '自定义'
                db.session.add(task)
                db.session.commit()
                return render_template('common/edit.html', success=1, form=form, task=task)
    return render_template('common/edit.html', form=form, task=task)


@app.route('/group')
@login_required
def group():
    ugps = User.query.filter_by(id=current_user.id).first()
    gps = Group.query.all()
    rgps = list()
    for gp in gps:
        tgp = dict()
        for ugp in ugps.groups:
            if gp.id == ugp.id:
                tgp['isin'] = True
                break
        if 'isin' not in tgp:
            tgp['isin'] = False
        tgp['id'] = gp.id
        tgp['name'] = gp.name
        rgps.append(tgp)

    return render_template('common/group.html', gps=rgps)


@app.route('/grouptask')
@login_required
def grouptasks():
    ugps = User.query.filter_by(id=current_user.id).first()
    tasks = list()
    for ugp in ugps.groups:
        for task in ugp.task:
            dictk = dict(task.__dict__)
            if ugp.manager == current_user.id:
                dictk['own'] = 1
            else:
                dictk['own'] = 0
            dictk['gpname'] = task.gp.name
            tasks.append(dictk)
    return render_template('common/grouptask.html', tasks=tasks)


@app.route('/joingp', methods=['GET'])
@login_required
def join():
    gp = Group.query.filter_by(id=request.args['gid']).first()
    user = User.query.filter_by(id=current_user.id).first()
    if gp is None:
        return '3'
    for usr in gp.users:
        if usr.id == user.id:
            return '2'
    gp.users.append(user)
    db.session.add(gp)
    db.session.commit()
    return '1'


@app.route('/exitgp', methods=['GET'])
@login_required
def exitgp():
    gp = Group.query.filter_by(id=request.args['gid']).first()
    user = User.query.filter_by(id=current_user.id).first()
    if gp is None:
        return '3'
    if gp.manager == user.id:
        return '4'
    for usr in gp.users:
        if usr.id == user.id:
            gp.users.remove(user)
            db.session.add(gp)
            db.session.commit()
            return '1'
    return '2'


@app.route('/gettaskinfo', methods=['POST'])
@login_required
def gettaskinfo():
    req = request.form
    dic = dict(code=0)
    if 'id' in req:
        print(req['id'])
        a = Notice.query.filter_by(nid=req['id']).first()
        if a is None:
            dic['code'] = 0
            return json.dumps(dic)
        if a.user != current_user.id:
            dic['code'] = 1
            return json.dumps(dic)
        dic['nid'] = a.nid
        dic['name'] = a.nname
        dic['starttime'] = datetime.datetime.strftime(a.starttime, '%Y-%m-%d %H:%M')
        dic['end'] = datetime.datetime.strftime(a.ddltime, '%Y-%m-%d %H:%M')
        if a.ntime1 is not None:
            dic['time1'] = datetime.datetime.strftime(a.ntime1, '%Y-%m-%d %H:%M')
        if a.ntime2 is not None:
            dic['time2'] = datetime.datetime.strftime(a.ntime2, '%Y-%m-%d %H:%M')
        dic['dec'] = a.dec
        dic['code'] = 2
        return json.dumps(dic)
    dic['code'] = 0
    return json.dumps(dic)


@app.route('/getgptaskinfo', methods=['POST'])
@login_required
def getgptaskinfo():
    req = request.form
    dic = dict(code=0)
    if 'id' in req:
        print(req['id'])
        a = Gnotice.query.filter_by(gnid=req['id']).first()
        if a is None:
            dic['code'] = 0
            return json.dumps(dic)
        auth = False
        for usr in a.gp.users:
            if usr.id == current_user.id:
                auth = True
        if auth == False:
            dic['code'] = 1
            return json.dumps(dic)
        dic['nid'] = a.gnid
        dic['name'] = a.gname
        dic['starttime'] = datetime.datetime.strftime(a.starttime, '%Y-%m-%d %H:%M')
        dic['end'] = datetime.datetime.strftime(a.ddltime, '%Y-%m-%d %H:%M')
        if a.gtime1 is not None:
            dic['time1'] = datetime.datetime.strftime(a.gtime1, '%Y-%m-%d %H:%M')
        if a.gtime2 is not None:
            dic['time2'] = datetime.datetime.strftime(a.gtime2, '%Y-%m-%d %H:%M')
        dic['dec'] = a.dec
        dic['code'] = 2
        return json.dumps(dic)
    dic['code'] = 0
    return json.dumps(dic)


@app.route('/delettask', methods=['POST'])
@login_required
def delettask():
    print(request.form['id'])
    task = Notice.query.filter_by(nid=request.form['id']).first()
    if task is None:
        flash('未知错误')
        return '1'
    if task.user != current_user.id:
        flash('无权限')
        return '2'
    db.session.delete(task)
    db.session.commit()
    return '0'


@app.route('/calendar')
@login_required
def calendar():
    return render_template('common/calendar.html')


@app.route('/getalltask', methods=['GET'])
@login_required
def getalltask():
    a = Notice.query.filter_by(user=current_user.id).all()
    msgs = []
    for msg in a:
        x = dict(msg.__dict__)
        del x['_sa_instance_state']
        msgs.append(x)
    return json.dumps(msgs, cls=DateEncoder)


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    form = profileForm()
    if form.validate_on_submit():
        a = User.query.filter_by(id=current_user.id).first()
        if form.qq.data != str(current_user.qq):
            if form.qq.data == '' or checkQQ(form.qq.data):
                if form.qq.data == '':
                    a.qq = None
                else:
                    a.qq = form.qq.data
                if form.open.data == current_user.isopen and (form.old.data == '' and form.new.data == ''):
                    db.session.add(a)
                    db.session.commit()
                    return render_template('users/profile.html', success=1, form=form)
                else:
                    if form.open.data != current_user.isopen:
                        a = User.query.filter_by(id=current_user.id).first()
                        a.isopen = form.open.data
                        if form.old.data == '' or form.new.data == '':
                            db.session.add(a)
                            db.session.commit()
                            return render_template('users/profile.html', success=1, form=form)
                        elif form.new.data == form.newag.data:
                            passwd = form.old.data
                            passwd = create_md5(passwd)
                            passwd = create_md5(passwd + a.salt)
                            if passwd == a.password:
                                passwd = form.new.data
                                passwd = create_md5(passwd)
                                salt = create_salt(4)
                                passwd = create_md5(passwd + salt)
                                a.salt = salt
                                a.password = passwd
                                db.session.add(a)
                                db.session.commit()
                                return render_template('users/profile.html', success=1, form=form)
                            else:
                                return render_template('users/profile.html', success=2, form=form)  # 密码错误
                        else:
                            return render_template('users/profile.html', success=3, form=form)  # 两次密码不一致
                    else:
                        a = User.query.filter_by(id=current_user.id).first()
                        if form.old.data == '' or form.new.data == '':
                            return render_template('users/profile.html', success=0, form=form)  # 无操作
                        elif form.new.data == form.newag.data:
                            passwd = form.old.data
                            passwd = create_md5(passwd)
                            passwd = create_md5(passwd + a.salt)
                            if passwd == a.password:
                                passwd = form.new.data
                                passwd = create_md5(passwd)
                                salt = create_salt(4)
                                passwd = create_md5(passwd + salt)
                                a.salt = salt
                                a.password = passwd
                                db.session.add(a)
                                db.session.commit()
                                return render_template('users/profile.html', success=1, form=form)
                            else:
                                return render_template('users/profile.html', success=2, form=form)  # 密码错误
                        else:
                            return render_template('users/profile.html', success=3, form=form)  # 两次密码不一致
            else:
                return render_template('users/profile.html', success=4, form=form)  # qq不合法
        else:
            if form.open.data != current_user.isopen:

                a.isopen = form.open.data
                if form.old.data == '' or form.new.data == '':
                    db.session.add(a)
                    db.session.commit()
                    return render_template('users/profile.html', success=1, form=form)
                elif form.new.data == form.newag.data:
                    passwd = form.old.data
                    passwd = create_md5(passwd)
                    passwd = create_md5(passwd + a.salt)
                    if passwd == a.password:
                        passwd = form.new.data
                        passwd = create_md5(passwd)
                        salt = create_salt(4)
                        passwd = create_md5(passwd + salt)
                        a.salt = salt
                        a.password = passwd
                        db.session.add(a)
                        db.session.commit()
                        return render_template('users/profile.html', success=1, form=form)
                    else:
                        return render_template('users/profile.html', success=2, form=form)  # 密码错误
                else:
                    return render_template('users/profile.html', success=3, form=form)  # 两次密码不一致
            else:
                a = User.query.filter_by(id=current_user.id).first()
                if form.old.data == '' or form.new.data == '':
                    return render_template('users/profile.html', success=0, form=form)  # 无操作
                elif form.new.data == form.newag.data:
                    passwd = form.old.data
                    passwd = create_md5(passwd)
                    passwd = create_md5(passwd + a.salt)
                    if passwd == a.password:
                        passwd = form.new.data
                        passwd = create_md5(passwd)
                        salt = create_salt(4)
                        passwd = create_md5(passwd + salt)
                        a.salt = salt
                        a.password = passwd
                        db.session.add(a)
                        db.session.commit()
                        return render_template('users/profile.html', success=1, form=form)
                    else:
                        return render_template('users/profile.html', success=2, form=form)  # 密码错误
                else:
                    return render_template('users/profile.html', success=3, form=form)  # 两次密码不一致
    return render_template('users/profile.html', form=form)


@app.route('/resend')
@login_required
def resend():
    a = User.query.filter_by(id=current_user.id).first()
    link = 'http://ddl.ywxisky.cn/active/' + a.emailpass
    if a.emailpass == '':  # 非正常情况
        if a.isemail == 1:  # 误点接口
            return '2'
        else:  # 生成新的激活链接
            if a.emailpass == 0:
                a.emailpass = create_md5(create_salt(10))
                db.session.add(a)
                db.session.commit()
                link = 'http://ddl.ywxisky.cn/active/' + a.emailpass
                if send_mail(a.email, 'Confirm you email address', '/email/email', title='Confirm you email address',
                             data='请点击下面的按钮来激活您的邮箱地址，，或可以访问此链接：' + link, link=link):
                    return '1'
                else:
                    return '0'
            else:
                if a.newenmail != '':
                    a.emailpass = create_md5(create_salt(10))
                    db.session.add(a)
                    db.session.commit()
                    link = 'http://ddl.ywxisky.cn/active/' + a.emailpass
                    if send_mail(a.newenmail, 'Confirm you email address', '/email/email',
                                 title='Confirm you email address',
                                 data='请点击下面的按钮来激活您的邮箱地址，，或可以访问此链接：' + link, link=link):
                        return '1'
                    else:
                        return '0'

    if a.newemail != None and a.newemail != '':  # 有新邮箱
        if send_mail(a.newemail, 'Confirm you email address', '/email/email', title='Confirm you email address',
                     data='请点击下面的按钮来激活您的邮箱地址，，或可以访问此链接：' + link, link=link):
            return '1'
        else:
            return '0'
    else:
        if send_mail(a.email, 'Confirm you email address', '/email/email', title='Confirm you email address',
                     data='请点击下面的按钮来激活您的邮箱地址，，或可以访问此链接：' + link, link=link):
            return '1'
        else:
            return '0'


@app.route('/changeemail')
@login_required
def changeemail():
    x = list(request.args)
    if len(x) != 1:
        return '4'
    if checkemail(x[0]) == False:
        return '4'
    b = User.query.filter_by(id=current_user.id).first()
    if b.email == x[0]:
        return '3'  # 两次邮件一样
    a = User.query.filter_by(email=x[0]).first()
    if a is not None:
        return '2'  # 新邮件已经被注册
    a = User.query.filter_by(newemail=x[0]).first()
    if a is not None:
        return '2'  # 新邮件被人等待验证
    b.newemail = x[0]
    b.emailpass = create_md5(create_salt(10))
    link = 'http://ddl.ywxisky.cn/active/' + b.emailpass
    if send_mail(b.newenmail, 'Confirm you email address', '/email/email', title='Confirm you email address',
                 data='请点击下面的按钮来激活您的邮箱地址，，或可以访问此链接：' + link, link=link):
        db.session.add(b)
        db.session.commit()
        return '1'
    else:
        return '0'


def checkQQ(str):
    pattern = r"[1-9]\d{4,10}"
    res = re.findall(pattern, str, re.I)
    return len(res)


def create_salt(length=4):
    salt = ''
    chars = '0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    len_chars = len(chars) - 1
    random = Random()
    for i in range(length):
        salt += chars[random.randint(0, len_chars)]
    return salt


def create_md5(pwd):
    md5_obj = md5()
    md5_obj.update(pwd.encode("utf8"))
    return md5_obj.hexdigest()


def checkemail(addr):
    re_email = re.compile(r'^[a-zA-Z\.]+@[a-zA-Z0-9]+\.[a-zA-Z]{3}$')
    return re_email.match(addr)
