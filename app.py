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

"""
engine = create_engine('sqlite:///k-on.db')  # user.db というデータベースを使うという宣言です
Base = declarative_base()  # データベースのテーブルの親です
"""

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///k-on.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
db.create_all()

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

    """
    def __init__(self, id, user_name, password, thu, fri, sat, sun, mon, tue, wed):
        self.id = id
        self.user_name = user_name
        self.password = password
        self.thu = thu
        self.fri = fri
        self.sat = sat
        self.sun = sun
        self.mon = mon
        self.tue = tue
        self.wed = wed
    """

    def __repr__(self):
        return "UserList<{}, {}, {}, {}, {}, {}, {}, {}, {}, {}>".format(
            self.id, self.user_name, self.password, self.thu, self.fri, self.sat, self.sun, self.mon, self.tue, self.wed)


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

    """
    def __init__(self, id, group_name, member1, member2, member3, member4, member5, member6):
        self.id = id
        self.group_name = group_name
        self.member1 = member1
        self.member2 = member2
        self.member3 = member3
        self.member4 = member4
        self.member5 = member5
        self.member6 = member6
    """

    def __repr__(self):
        return "GroupList<{}, {}, {}, {}, {}, {}, {}, {}>".format(
            self.id, self.group_name, self.member1, self.member2, self.member3, self.member4, self.member5, self.member6)


"""
class MemberList(db.Model):
    __tablename__ = "MemberList"
    member_name = db.Column(db.String(100), nullable=False)


class UserSchedule(db.Model, user_name):
    __tablename__ = user_name
    date_time = db.Column(db.Integer,)
    value = db.Column(db.Integer, nullable=False, default=0)
"""

"""
Base.metadata.create_all(engine)  # 実際にデータベースを構築します
SessionMaker = sessionmaker(bind=engine)  # Pythonとデータベースの経路です
session = SessionMaker()  # 経路を実際に作成しました
"""


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/test', methods=['GET', 'POST'])
def test():
    app.logger.info(request.form['join-11'])
    return render_template("index.html")


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    """
    GET ：ユーザー登録画面に遷移
    POST：ユーザー登録処理を実施
    """
    if request.method == 'GET':
        # グループ登録画面に遷移
        return render_template('create_user.html',
                               title='ユーザーの追加')

    """
    # ユーザーIDを取得
    user_id = session.get('user_id')
    """

    # 登録フォームから送られてきた値を取得
    user_name = request.form['user_name']
    password = request.form['password']
    app.logger.info(user_name)
    app.logger.info(password)

    # エラーチェック
    error_message = None

    """
    if not user_name:
        error_message = 'ユーザー名を入力してください'
    elif not password:
        error_message = 'パスワードを入力してください'
    elif db.execute('SELECT * FROM UserList WHERE user_name = ?', (user_name,)).fetchone() is not None:
        error_message = 'ユーザー名 {} はすでに使用されています'.format(user_name)
    """
    if db.session.query(UserList).filter_by(user_name=user_name).first():
        error_message = 'ユーザー名 {} はすでに使用されています'.format(user_name)
        app.logger.info(error_message)

    if error_message is not None:
        # エラーがあれば、それを画面に表示させる
        flash(error_message, category='alert alert-danger')
        return redirect(url_for('create_user'))

    """
    # エラーがなければテーブルに登録する
    db.execute(
        'INSERT INTO UserList (user_name, password) VALUES (?, ?)',
        (user_name, password)
    )
    """
    # ハッシュ化する
    user = UserList(user_name=user_name,
                    password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    app.logger.info(user.user_name)

    flash('ユーザー登録が完了しました', category='alert alert-info')
    return render_template('home.html', user_name=user_name)


@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    user_name = request.cookies.get('user_name', None)
    """
    GET ：グループ登録画面に遷移
    POST：グループ登録処理を実施
    """
    if request.method == 'GET':
        # グループ登録画面に遷移
        return render_template('create_group.html',
                               title='グループの追加')

    if user_name is None:
        flash('ログインしていないユーザーはグループを作成できません', category='alert alert-danger')
        # トップページに遷移
        return redirect(url_for('index'))

    """
    # ユーザーIDを取得
    user_id = session.get('user_id')
    """

    # 登録フォームから送られてきた値を取得
    group_name = request.form['group_name']

    # エラーチェック
    error_message = None

    if not group_name:
        error_message = 'グループ名を入力してください'
    elif db.session.query(GroupList).filter_by(group_name=group_name).first() is not None:
        error_message = 'グループ名 {} はすでに使用されています'.format(group_name)

    if error_message is not None:
        # エラーがあれば、それを画面に表示させる
        flash(error_message, category='alert alert-danger')
        return redirect(url_for('create_group'))

    # エラーがなければテーブルに登録する
    group = GroupList(group_name=group_name, member1=user_name)
    db.session.add(group)
    db.session.commit()

    flash('グループ登録が完了しました', category='alert alert-info')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET ：ログイン画面に遷移
    POST：ログイン処理を実施
    """
    if request.method == 'GET':
        user_name = request.cookies.get('user_name', None)
        if user_name is None:
            # ログイン画面に遷移
            return render_template('login.html',
                                   title='ログイン')
        else:
            groups = db.session.query(GroupList).filter(or_(GroupList.member1 == user_name,
                                                            GroupList.member2 == user_name,
                                                            GroupList.member3 == user_name,
                                                            GroupList.member4 == user_name,
                                                            GroupList.member5 == user_name,
                                                            GroupList.member6 == user_name)).all()

            participating_group = []
            for g in groups:
                participating_group.append(g.group_name)

            return render_template('home.html', user_name=user_name, part_group=participating_group)

    # ログイン処理

    # ログインフォームから送られてきた、ユーザー名とパスワードを取得
    user_name = request.form['user_name']
    password = request.form['password']

    # ユーザー名とパスワードのチェック
    error_message = None

    user = db.session.query(UserList).filter_by(user_name=user_name).first()

    if user is None:
        error_message = 'ユーザー名が正しくありません'
    elif not check_password_hash(user.password, password):
        app.logger.info(user.password)
        app.logger.info(password)
        error_message = 'パスワードが正しくありません'

    if error_message is not None:
        # エラーがあればそれを表示したうえでログイン画面に遷移
        flash(error_message, category='alert alert-danger')
        return redirect(url_for('login'))

    ### エラーがなければクッキーに情報を保存してhomeへ ###
    groups = db.session.query(GroupList).filter(or_(GroupList.member1 == user_name,
                                                    GroupList.member2 == user_name,
                                                    GroupList.member3 == user_name,
                                                    GroupList.member4 == user_name,
                                                    GroupList.member5 == user_name,
                                                    GroupList.member6 == user_name)).all()

    participating_group = []
    for g in groups:
        participating_group.append(g.group_name)

    # make_responseでレスポンスオブジェクトを生成する
    response = make_response(render_template(
        'home.html', user_name=user_name, part_group=participating_group))

    # Cookieの設定を行う
    max_age = 60 * 60  # 1時間
    expires = int(datetime.now().timestamp()) + max_age
    response.set_cookie('user_name', value=user.user_name, max_age=max_age)
    #                   ,expires=expires, path='/', domain=domain, secure=None, httponly=False)
    return response


@app.route('/home')
def home():
    user_name = request.cookies.get('user_name', None)

    if user_name is None:
        flash('ログインしてください', category='alert alert-danger')
        return redirect(url_for('index'))

    return render_template('home.html', user_name=user_name)


@app.route('/band', methods=['GET', 'POST'])
def band():
    user_name = request.cookies.get('user_name', None)

    """
    GET ：日程登録画面に遷移
    POST：日程登録処理を実施
    """
    if request.method == 'GET' and user_name is not None:
        week_data = []
        day_data = ["木", "金", "土", "日", "月", "火", "水"]
        week_holidays = holiday()
        for i in range(7):
            data = {
                "day": day_data[i],
                "holiday": week_holidays[i],
                "num": i+1
            }
            week_data.append(data)

        user = db.session.query(UserList).filter_by(
            user_name=user_name).first()

        # 文字列が１文字ずつ分割されて配列になる
        thu = list(user.thu)
        fri = list(user.fri)
        sat = list(user.sat)
        sun = list(user.sun)
        mon = list(user.mon)
        tue = list(user.tue)
        wed = list(user.wed)

        week_data[0]["schedule"] = thu
        week_data[1]["schedule"] = fri
        week_data[2]["schedule"] = sat
        week_data[3]["schedule"] = sun
        week_data[4]["schedule"] = mon
        week_data[5]["schedule"] = tue
        week_data[6]["schedule"] = wed

        # return render_template("test2.html", week=week_data, thu=thu, fri=fri, sat=sat, sun=sun, mon=mon, tue=tue, wed=wed)
        return render_template("test2.html", week=week_data)

    elif request.method == 'GET' and user_name is None:
        flash('ログインしてください', category='alert alert-danger')
        return redirect(url_for('index'))

    week_schedule = []
    for i in range(7):
        day = ""
        week_holidays = holiday()
        # 平日なら
        if week_holidays[i] == 0:
            for j in range(8):
                day += request.form["join-{}{}".format(i+1, j+1)]
            week_schedule.append(day)
        # 休日なら
        else:
            for j in range(5):
                day += request.form["join-{}{}".format(i+1, j+1)]
            week_schedule.append(day)

    user = db.session.query(UserList).filter_by(user_name=user_name).first()
    user.thu = week_schedule[0]
    user.fri = week_schedule[1]
    user.sat = week_schedule[2]
    user.sun = week_schedule[3]
    user.mon = week_schedule[4]
    user.tue = week_schedule[5]
    user.wed = week_schedule[6]
    app.logger.info(week_schedule)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/group/<string:group_name>', methods=['GET', 'POST'])
def group(group_name):
    members = db.session.query(GroupList).filter_by(
        group_name=group_name).first()
    app.logger.info(members)

    # かなり冗長だがこれしか思いつかなかった
    group_members = []
    if members.member1 is not None:
        group_members.append(members.member1)
    if members.member2 is not None:
        group_members.append(members.member2)
    if members.member3 is not None:
        group_members.append(members.member3)
    if members.member4 is not None:
        group_members.append(members.member4)
    if members.member5 is not None:
        group_members.append(members.member5)
    if members.member6 is not None:
        group_members.append(members.member6)

    return render_template("group.html", group_name=group_name, members=group_members)


if __name__ == "__main__":
    app.run(debug=True, port=8000, threaded=True)
