# coding: UTF-8
from flask import (
    Flask, render_template,
    redirect, url_for, request,
    session, flash, make_response
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager, logout_user
from werkzeug.security import *
import numpy as np
from datetime import *

from google_calendar import holiday

app = Flask(__name__)
app.secret_key = "k-on2019"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///k-on.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
# db.create_all()

"""
CRUD操作

----create----
    user = User('shinzo', 'shinzo.abe@example.com')
    db.session.add(user)
    db.session.commit()

----read all----
    users = User.query.all()

----read, delete----
    user = db.session.query(User).filter_by(name='shinzo').first()
    db.session.delete(user)
    db.session.commit()

----read, update----
    user = db.session.query(User).filter_by(name='shinzo').first()
    user.email = 'shinzo.abe@google.com'
    db.session.add(user)
    db.session.commit()
"""


class UserList(db.Model):
    __tablename__ = "UserList"
    id = db.Column(db.Integer(), primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    thu = db.Column(db.String(8), nullable=False, default="00000000")
    fri = db.Column(db.String(8), nullable=False, default="00000000")
    sat = db.Column(db.String(5), nullable=False, default="00000")
    sun = db.Column(db.String(5), nullable=False, default="00000")
    mon = db.Column(db.String(8), nullable=False, default="00000000")
    tue = db.Column(db.String(8), nullable=False, default="00000000")
    wed = db.Column(db.String(8), nullable=False, default="00000000")
    update = db.Column(db.Integer(), nullable=False, default=0)

    def __repr__(self):
        return "UserList<{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}>".format(
            self.id, self.user_name, self.password, self.thu, self.fri, self.sat, self.sun, self.mon, self.tue, self.wed, self.update)


class GroupList(db.Model):
    # 最大６人
    __tablename__ = "GroupList"
    id = db.Column(db.Integer(), primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    member1 = db.Column(db.String(100))
    member2 = db.Column(db.String(100))
    member3 = db.Column(db.String(100))
    member4 = db.Column(db.String(100))
    member5 = db.Column(db.String(100))
    member6 = db.Column(db.String(100))

    def __repr__(self):
        return "GroupList<{}, {}, {}, {}, {}, {}, {}, {}>".format(
            self.id, self.group_name, self.member1, self.member2, self.member3, self.member4, self.member5, self.member6)


week_holidays, week_date = holiday()
users = UserList.query.all()

for user in users:
    if week_holidays[0] == 0:
        user.thu = "00000000"
    else:
        user.thu = "00000"

    if week_holidays[1] == 0:
        user.fri = "00000000"
    else:
        user.fri = "00000"

    if week_holidays[2] == 0:
        user.sat = "00000000"
    else:
        user.sat = "00000"

    if week_holidays[3] == 0:
        user.sun = "00000000"
    else:
        user.sun = "00000"

    if week_holidays[4] == 0:
        user.mon = "00000000"
    else:
        user.mon = "00000"

    if week_holidays[5] == 0:
        user.tue = "00000000"
    else:
        user.tue = "00000"

    if week_holidays[6] == 0:
        user.wed = "00000000"
    else:
        user.wed = "00000"

    user.update = 0
    db.session.add(user)

# グループメンバーが誰もいないグループを削除する
groups = GroupList.query.all()

for group in groups:
    if group.member1 == None and group.member2 == None and group.member3 == None and group.member4 == None and group.member5 == None and group.member6 == None:
        db.session.delete(group)


db.session.commit()
