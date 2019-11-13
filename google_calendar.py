from datetime import date
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import *
from datetime import *
import locale

"""
date.today()  # 今日の日付
datetime.today()  # 時間まで

date.today().year  # 年
date.today().day  # 日

datetime.today().microsecond  # １秒以下も出る

date.today().isoformat()  # フォーマットの指定
datetime.today().strftime("%Y/%m/%d/%H/%M/%S")  # フォーマットの指定
### strftime('%A, %a, %B, %b') Monday, Mon, January, Jan ###
"""


def holiday():
    # 参考資料はこちら
    # https://developers.google.com/google-apps/calendar/quickstart/python

    # APIの認証を行う
    # API用の認証JSON
    json_file = 'K-ON schedule-9e8c5eec3ea8.json'
    # スコープ設定
    scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    # 認証情報作成
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_file, scopes=scopes)
    http_auth = credentials.authorize(Http())
    # API利用できる状態を作る
    service = discovery.build("calendar", "v3", http=http_auth)

    # 祝日を取得する
    # カレンダーIDには、日本の祝日カレンダーを指定
    calendar_id = "ja.japanese#holiday@group.v.calendar.google.com"
    """
    # 2016年の祝日を取得する例
    dtfrom = date(year=2016, month=1, day=1).isoformat() + "T00:00:00.000000Z"
    dtto = date(year=2016, month=12, day=31).isoformat() + "T00:00:00.000000Z"
    """

    if datetime.today().strftime('%a') == "Mon":
        start_day = (date.today() + timedelta(days=3))  # 木曜から
        end_day = (date.today() + timedelta(days=9))  # 水曜まで
    elif datetime.today().strftime('%a') == "Tue":
        start_day = (date.today() + timedelta(days=2))  # 木曜から
        end_day = (date.today() + timedelta(days=8))  # 水曜まで
    elif datetime.today().strftime('%a') == "Wed":
        start_day = (date.today() + timedelta(days=1))  # 木曜から
        end_day = (date.today() + timedelta(days=7))  # 水曜まで
    elif datetime.today().strftime('%a') == "Thu":
        start_day = (date.today() + timedelta(days=0))  # 木曜から
        end_day = (date.today() + timedelta(days=6))  # 水曜まで
    elif datetime.today().strftime('%a') == "Fri":
        start_day = (date.today() + timedelta(days=-1))  # 木曜から
        end_day = (date.today() + timedelta(days=5))  # 水曜まで
    elif datetime.today().strftime('%a') == "Sat":
        start_day = (date.today() + timedelta(days=-2))  # 木曜から
        end_day = (date.today() + timedelta(days=4))  # 水曜まで
    else:
        start_day = (date.today() + timedelta(days=-3))  # 木曜から
        end_day = (date.today() + timedelta(days=3))  # 水曜まで

    """
    dtfrom = date(year=date.today().year, month=1,
                  day=1).isoformat() + "T00:00:00.000000Z"
    dtto = date(year=date.today().year, month=12,
                day=31).isoformat() + "T00:00:00.000000Z"
    """

    dtfrom = str(start_day) + "T00:00:00.000000Z"
    dtto = str(end_day) + "T00:00:00.000000Z"

    # API実行
    events_results = service.events().list(
        calendarId=calendar_id,
        timeMin=dtfrom,
        timeMax=dtto,
        maxResults=50,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    # API結果から値を取り出す
    events = events_results.get('items', [])
    for event in events:
        print("%s\t%s" % (event["start"]["date"], event["summary"]))
    """
    2019-01-01      元日
    2019-01-14      成人の日
    2019-02-11      建国記念の日
    2019-03-21      春分の日
    2019-04-29      昭和の日
    2019-04-30      祝日
    2019-05-01      天皇の即位の日
    2019-05-02      祝日
    2019-05-03      憲法記念日
    2019-05-04      みどりの日
    2019-05-05      こどもの日
    2019-05-06      こどもの日 振替休日
    2019-07-15      海の日
    2019-08-11      山の日
    2019-08-12      山の日 振替休日
    2019-09-16      敬老の日
    2019-09-23      秋分の日
    2019-10-14      体育の日
    2019-10-22      即位礼正殿の儀の行われる日
    2019-11-03      文化の日
    2019-11-04      文化の日 振替休日
    2019-11-23      勤労感謝の日
    """

    # print(events)
    week_holidays = []
    if events:  # 配列は、要素が入っていればTrueを返す性質がある
        holidays = [x['start']['date'] for x in events]
        print(holidays)
        for i in range(7):

            if str(start_day + timedelta(days=i)) in holidays or (i == 2 or i == 3):
                week_holidays.append(1)
            else:
                week_holidays.append(0)
    else:
        week_holidays = [0, 0, 1, 1, 0, 0, 0]

    week_date = []
    day_data = ["木", "金", "土", "日", "月", "火", "水"]
    for i in range(7):
        temp_day = str(start_day + timedelta(days=i))
        ymd = temp_day.split("-")
        week_date.append("{}/{} ({})".format(ymd[1], ymd[2], day_data[i]))
        print(week_date[i])

    print(week_holidays)

    return week_holidays, week_date


if __name__ == "__main__":
    holiday()
