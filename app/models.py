# -*- coding: utf-8 -*-
from app import db
from . import login_manger
from flask_login import UserMixin


u2g=db.Table('u2g',db.Column('id',db.Integer,db.ForeignKey('users.id'),primary_key=True),db.Column('gid',db.Integer,db.ForeignKey('groups.id'),primary_key=True))


@login_manger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
    name = db.Column(db.VARCHAR(20),nullable=False)
    salt = db.Column(db.VARCHAR(10),nullable=False)
    password = db.Column(db.VARCHAR(50),nullable=False)
    email = db.Column(db.VARCHAR(50),nullable=False)
    emailpass = db.Column(db.VARCHAR(50))
    newemail = db.Column(db.VARCHAR(50))
    qq = db.Column(db.BIGINT)
    isemail = db.Column(db.SMALLINT)
    isopen = db.Column(db.SMALLINT)
    findpassword = db.Column(db.VARCHAR(50))
    task = db.relationship('Notice',backref=db.backref('usr'),lazy='dynamic')
    groups = db.relationship('Group',secondary=u2g,backref=db.backref('users'))
    def __repr__(self):
        return self.id


class Notice(db.Model):
    __tablename__ = 'unotices'
    nid = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    nname = db.Column(db.TEXT, nullable=False)
    user = db.Column(db.INT, db.ForeignKey('users.id'))#这里写表名字
    starttime = db.Column(db.DATETIME, nullable=False)
    ddltime = db.Column(db.DATETIME, nullable=False)
    ntime1 = db.Column(db.DATETIME)
    ntime2 = db.Column(db.DATETIME)
    dec = db.Column(db.TEXT)
    if1 = db.Column(db.SMALLINT)
    if2 = db.Column(db.SMALLINT)
    type = db.Column(db.VARCHAR(20))
    def __repr__(self):
        return self.nid


class Gnotice(db.Model):
    __tablename__ = 'gnotices'
    gnid = db.Column(db.Integer, primary_key=True, nullable=False,autoincrement=True)
    gname = db.Column(db.TEXT, nullable=False)
    group = db.Column(db.INT, db.ForeignKey('groups.id'))#这里写表名字
    starttime = db.Column(db.DATETIME, nullable=False)
    ddltime = db.Column(db.DATETIME, nullable=False)
    gtime1 = db.Column(db.DATETIME)
    gtime2 = db.Column(db.DATETIME)
    dec = db.Column(db.TEXT)
    if1 = db.Column(db.SMALLINT)
    if2 = db.Column(db.SMALLINT)
    type = db.Column(db.VARCHAR(20))
    gp = db.relationship('Group')
    def __repr__(self):
        return self.gnid


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.VARCHAR(100), nullable=False)
    manager = db.Column(db.Integer)
    task = db.relationship('Gnotice', backref='from', lazy='dynamic')
    def __repr__(self):
        return self.id
