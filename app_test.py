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

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL') or 'sqlite:///k-on.db'  # or "postgresql://localhost/k-on"
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
    comment = db.Column(db.String(255), nullable=False, default="")

    def __repr__(self):
        return "UserList<{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}>".format(
            self.id, self.user_name, self.password, self.thu, self.fri, self.sat, self.sun, self.mon, self.tue, self.wed, self.update, self.comment)


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


"""
class CommentList(db.Model):
    # sqlalchemyでカラムを後から追加する方法がわからなかったので別のテーブルとして作成
    __tablename__ = "CommentList"
    id = db.Column(db.Integer(), primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "CommentList<{}, {}, {}>".format(self.id, self.user_name, self.comment)
"""

"""
sql = 'ALTER TABLE UserList ADD comment varchar(255) DEFAULT ""'
db.session.execute(sql)
"""

db.create_all()


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

    # 登録フォームから送られてきた値を取得
    user_name = request.form['user_name']
    password = request.form['password']
    app.logger.info(user_name)
    app.logger.info(password)

    # エラーチェック
    error_message = None

    if db.session.query(UserList).filter_by(user_name=user_name).first():
        error_message = 'ユーザー名 {} はすでに使用されています'.format(user_name)
        app.logger.info(error_message)

    if error_message is not None:
        # エラーがあれば、それを画面に表示させる
        flash(error_message, category='alert alert-danger')
        return redirect(url_for('create_user'))

    # ハッシュ化する
    user = UserList(user_name=user_name,
                    password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    app.logger.info(user.user_name)

    flash('ユーザー登録が完了しました', category='alert alert-info')

    # make_responseでレスポンスオブジェクトを生成する
    response = make_response(render_template(
        'home.html', user_name=user_name))

    # Cookieの設定を行う
    max_age = 60 * 60 * 24  # 1日
    # max_age = 30 # テスト用
    expires = int(datetime.now().timestamp()) + max_age
    response.set_cookie('user_name', value=user.user_name, max_age=max_age)
    #                   ,expires=expires, path='/', domain=domain, secure=None, httponly=False)
    return response


@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    user_name = request.cookies.get('user_name', None)
    """
    GET ：グループ登録画面に遷移
    POST：グループ登録処理を実施
    """
    if request.method == 'GET' and user_name is not None:
        # グループ登録画面に遷移
        return render_template('create_group.html',
                               title='グループの追加')
    elif request.method == 'GET' and user_name is None:
        flash('ログインしていないユーザーはグループを作成できません', category='alert alert-danger')
        # トップページに遷移
        return redirect(url_for('index'))

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
    max_age = 60 * 60 * 24  # 1日
    # max_age = 30  # テスト用
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


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    user_name = request.cookies.get('user_name', None)

    """
    GET ：日程登録画面に遷移
    POST：日程登録処理を実施
    """
    if request.method == 'GET' and user_name is not None:
        week_data = []
        # day_data = ["木", "金", "土", "日", "月", "火", "水"]
        week_holidays, week_date = holiday()
        for i in range(7):
            data = {
                "day": week_date[i],
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

        return render_template("schedule.html", week=week_data, initial_comment=user.comment)

    elif request.method == 'GET' and user_name is None:
        flash('ログインしてください', category='alert alert-danger')
        return redirect(url_for('index'))

    # POSTの時
    week_schedule = []
    for i in range(7):
        day = ""
        week_holidays, week_date = holiday()
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

    # 更新フラグ（update）を1にする
    user.update = 1

    db.session.add(user)
    db.session.commit()

    # コメント処理
    comment = request.form['comment']

    user = db.session.query(UserList).filter_by(user_name=user_name).first()
    user.comment = comment
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/group/<string:group_name>', methods=['GET', 'POST'])
def group(group_name):
    user_name = request.cookies.get('user_name', None)
    members = db.session.query(GroupList).filter_by(
        group_name=group_name).first()

    if user_name is None:
        flash('ログインしてください', category='alert alert-danger')
        return redirect(url_for('index'))

    if not ((user_name == members.member1) or
            (user_name == members.member2) or
            (user_name == members.member3) or
            (user_name == members.member4) or
            (user_name == members.member5) or
            (user_name == members.member6)):
        flash('このグループには加入していません', category='alert alert-danger')
        return redirect(url_for('index'))

    if group_name is not None:
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

        # 休日判定のリストを作成
        # 誰でもいいのでUserListの一番最初の人のデータから休日判定をする
        user = db.session.query(UserList).first()
        holidays = []
        if len(user.thu) == 8:
            holidays.append(0)
        else:
            holidays.append(1)
        if len(user.fri) == 8:
            holidays.append(0)
        else:
            holidays.append(1)
        if len(user.sat) == 8:
            holidays.append(0)
        else:
            holidays.append(1)
        if len(user.sun) == 8:
            holidays.append(0)
        else:
            holidays.append(1)
        if len(user.mon) == 8:
            holidays.append(0)
        else:
            holidays.append(1)
        if len(user.tue) == 8:
            holidays.append(0)
        else:
            holidays.append(1)
        if len(user.wed) == 8:
            holidays.append(0)
        else:
            holidays.append(1)

        ###########################################################################
        """
        # 大丈夫なほう

        schedule_list = []
        maru_list = []
        batsu_list
        for i in holidays:
            #配列のアドレスの関係上、maruとbatsuで分ける
            if i == 0:
                temp_maru = [0, 0, 0, 0, 0, 0, 0, 0]
                temp_batsu = [0, 0, 0, 0, 0, 0, 0, 0]
            else:
                temp_maru = [0, 0, 0, 0, 0]
                temp_batsu = [0, 0, 0, 0, 0]
            maru_list.append(temp_maru)
            batsu_list.append(temp_batsu)

        for member in group_members:
            user = db.session.query(UserList).filter_by(
                user_name=member).first()

            # 文字列が１文字ずつ分割されて配列になる
            thu = list(user.thu)
            fri = list(user.fri)
            sat = list(user.sat)
            sun = list(user.sun)
            mon = list(user.mon)
            tue = list(user.tue)
            wed = list(user.wed)
            week_data = [thu, fri, sat, sun, mon, tue, wed]

            app.logger.info(week_data)

            for i in range(7):
                for j in range(len(maru_list[i])):
                    temp_data = int(week_data[i][j])
                    if temp_data == 3:
                        maru_list[i][j] += 1
                    elif temp_data <= 1:  # 未回答もバツに含める
                        batsu_list[i][j] += 1

        scheduled_time = []
        day_data = ["木", "金", "土", "日", "月", "火", "水"]

        app.logger.info(group_members)
        app.logger.info(maru_list)

        for i in range(7):
            j = 0
            if holidays[i] == 0:
                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 9:00-10:30", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 10:30-12:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 12:00-14:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 14:00-16:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 16:00-17:30", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 17:30-19:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 19:00-20:30", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 20:30-22:00", "flag": flag})

            else: # 休日なら
                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 9:00-11:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 11:00-13:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 13:00-15:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 15:00-17:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 1
                    else:  # 三角が1人以上いるなら
                        flag = 0
                    scheduled_time.append(
                        {"time": day_data[i] + " 17:00-19:00", "flag": flag})

        # メンバーのupdateフラグを配列に格納
        update_flags = []
        for member in group_members:
            user = db.session.query(UserList).filter_by(
                user_name=member).first()
            update_flags.append(user.update)

        return render_template("group.html", group_name=group_name, members=group_members, scheduled_time=scheduled_time, update=update_flags)
        """
        ###########################################################################

        # application error H18 が起きて実行できないver #

        schedule_list = []
        maru_list = []
        batsu_list = []
        for i in holidays:
            # 配列のアドレスの関係上、maruとbatsuで分ける
            if i == 0:
                temp_maru = [0, 0, 0, 0, 0, 0, 0, 0]
                temp_batsu = [0, 0, 0, 0, 0, 0, 0, 0]
            else:
                temp_maru = [0, 0, 0, 0, 0]
                temp_batsu = [0, 0, 0, 0, 0]
            maru_list.append(temp_maru)
            batsu_list.append(temp_batsu)

        all_members_data = []

        for member in group_members:
            user = db.session.query(UserList).filter_by(
                user_name=member).first()

            member_data = []

            # 文字列が１文字ずつ分割されて配列になる
            thu = list(user.thu)
            fri = list(user.fri)
            sat = list(user.sat)
            sun = list(user.sun)
            mon = list(user.mon)
            tue = list(user.tue)
            wed = list(user.wed)
            week_data = [thu, fri, sat, sun, mon, tue, wed]

            # app.logger.info(week_data)

            for i in range(7):
                for j in range(len(maru_list[i])):
                    temp_data = int(week_data[i][j])
                    if temp_data == 3:
                        maru_list[i][j] += 1
                        member_data.append("◯")
                    elif temp_data == 2:
                        member_data.append("△")
                    elif temp_data == 1:
                        batsu_list[i][j] += 1
                        member_data.append("×")
                    else:  # 未回答もバツに含める
                        batsu_list[i][j] += 1
                        member_data.append("-")

            all_members_data.append(member_data)

        # コマ時間のデータが行、メンバーごとのデータが列になるように、転置行列にする
        all_week_data = np.array(all_members_data).T
        # app.logger.info(all_week_data)

        scheduled_time = []
        day_data = ["木", "金", "土", "日", "月", "火", "水"]

        # app.logger.info(group_members)
        # app.logger.info(maru_list)

        for i in range(7):
            j = 0
            if holidays[i] == 0:
                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 9:00-10:30", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 10:30-12:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 12:00-14:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 14:00-16:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 16:00-17:30", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 17:30-19:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 19:00-20:30", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 20:30-22:00", "flag": flag})

            else:  # 休日なら
                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 9:00-11:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 11:00-13:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 13:00-15:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 15:00-17:00", "flag": flag})
                j += 1

                if batsu_list[i][j] == 0:
                    if maru_list[i][j] == len(group_members):  # 全員丸なら
                        flag = 3
                    else:  # 三角が1人以上いるなら
                        flag = 2
                else:  # バツまたは未回答がいるなら
                    flag = 1

                scheduled_time.append(
                    {"time": day_data[i] + " 17:00-19:00", "flag": flag})

        # メンバーのupdateフラグを配列に格納
        update_flags = []
        for member in group_members:
            user = db.session.query(UserList).filter_by(
                user_name=member).first()
            update_flags.append(user.update)

        # コメント処理
        comment_list = []
        for member in group_members:
            user = db.session.query(UserList).filter_by(
                user_name=member).first()
            if user.comment != "":
                comment_list.append("{}: {}".format(member, user.comment))

        return render_template("group.html", group_name=group_name,
                               members=group_members,
                               scheduled_time=scheduled_time,
                               all_week_data=all_week_data,
                               update=update_flags,
                               comment_list=comment_list)

        ##############################################
        """

    ----- httpの部分 -----
    <!--
      <table>
      <tr>
        <th>時間</th>
        {% for member_name in members %}
        <th>{{member_name}}</th>
        {% endfor %}
      </tr>
      {% for time in scheduled_time %}
      <tr>
        <td class="flag-{{time.flag}}">{{time.time}}</td>
        {% for row_week_data in all_week_data[loop.index0] %}
        <td>{{row_week_data}}</td>
        {% endfor %}
      </tr>
      {% endfor %}
    </table>
    -->
        """
        #----------------------------------------------------#
        """
        大丈夫なほう

        <table>
      <tr>
        <th>予定の合う時間</th>
      </tr>
      {% for time in scheduled_time %} {% if time.flag == 1 %}
      <tr>
        <td class="green">{{time.time}}</td>
      </tr>
      {% else %}
      <tr>
        <td class="yellow">{{time.time}}</td>
      </tr>
      {% endif %} {% endfor %}
    </table>
        """
        ##############################################


@app.route('/add_to_group/<string:group_name>', methods=['GET', 'POST'])
def add_to_group(group_name):
    if request.method == 'GET':
        return render_template("add_to_group.html")

    # POSTなら
    add_user = request.form['add_user']

    if db.session.query(UserList).filter_by(user_name=add_user).first() is None:
        flash('ユーザーが存在しません', category='alert alert-danger')
        return redirect(url_for('add_to_group', group_name=group_name))

    group = db.session.query(GroupList).filter_by(
        group_name=group_name).first()
    if (group.member1 or group.member1 or group.member1 or group.member1 or group.member1) == add_user:
        flash('{} は既にグループに加入しています'.format(add_user),
              category='alert alert-danger')
        return redirect(url_for('add_to_group', group_name=group_name))

    if group.member2 is None:
        group.member2 = add_user
    elif group.member3 is None:
        group.member3 = add_user
    elif group.member4 is None:
        group.member4 = add_user
    elif group.member5 is None:
        group.member5 = add_user
    elif group.member6 is None:
        group.member6 = add_user
    else:
        flash('これ以上メンバーを追加できません', category='alert alert-danger')
        return redirect(url_for('add_to_group', group_name=group_name))

    db.session.commit()
    flash('{} をグループに追加しました'.format(add_user), category='alert alert-success')

    return redirect(url_for('group', group_name=group_name))


@app.route('/remove_from_group/<string:group_name>', methods=['GET', 'POST'])
def remove_from_group(group_name):
    if request.method == 'GET':
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

        return render_template("remove_from_group.html", group_name=group_name, members=group_members)

    # POSTなら
    remove_user = request.form['remove_user']
    members = db.session.query(GroupList).filter_by(
        group_name=group_name).first()

    if members.member1 == remove_user:
        members.member1 = None
    elif members.member2 == remove_user:
        members.member2 = None
    elif members.member3 == remove_user:
        members.member3 = None
    elif members.member4 == remove_user:
        members.member4 = None
    elif members.member5 == remove_user:
        members.member5 = None
    elif members.member6 == remove_user:
        members.member6 = None
    db.session.commit()

    flash('{} をグループから削除しました'.format(remove_user),
          category='alert alert-success')
    return redirect(url_for('group', group_name=group_name))


@app.route('/change_name', methods=['GET', 'POST'])
def change_name():
    if request.method == 'GET':
        return render_template("change_name.html")

    # POSTなら
    user_name = request.cookies.get('user_name', None)
    if user_name is None:
        flash('ログインしてください', category='alert alert-danger')
        return redirect(url_for('index'))

    changed_name = request.form['changed_name']

    if db.session.query(UserList).filter_by(user_name=changed_name).first():
        error_message = 'ユーザー名 {} はすでに使用されています'.format(changed_name)
        flash(error_message, category='alert alert-danger')
        return redirect(url_for('change_name'))

    user = db.session.query(UserList).filter_by(user_name=user_name).first()
    user.user_name = changed_name
    db.session.add(user)
    db.session.commit()

    groups = db.session.query(GroupList).filter(or_(GroupList.member1 == user_name,
                                                    GroupList.member2 == user_name,
                                                    GroupList.member3 == user_name,
                                                    GroupList.member4 == user_name,
                                                    GroupList.member5 == user_name,
                                                    GroupList.member6 == user_name)).all()

    for g in groups:
        if g.member1 == user_name:
            g.member1 = changed_name
            db.session.add(g)
        elif g.member2 == user_name:
            g.member2 = changed_name
            db.session.add(g)
        elif g.member3 == user_name:
            g.member3 = changed_name
            db.session.add(g)
        elif g.member4 == user_name:
            g.member4 = changed_name
            db.session.add(g)
        elif g.member5 == user_name:
            g.member5 = changed_name
            db.session.add(g)
        else:
            g.member6 = changed_name
            db.session.add(g)

    db.session.commit()

    # make_responseでレスポンスオブジェクトを生成する
    response = make_response(redirect(url_for("index")))

    # Cookieの設定を行う
    max_age = 60 * 60 * 24  # 1日
    # max_age = 30  # テスト用
    expires = int(datetime.now().timestamp()) + max_age
    response.set_cookie('user_name', value=changed_name, max_age=max_age)
    #                   ,expires=expires, path='/', domain=domain, secure=None, httponly=False)

    flash('ユーザー名を {} に変更しました'.format(changed_name),
          category='alert alert-success')
    return response


if __name__ == "__main__":
    app.run()
