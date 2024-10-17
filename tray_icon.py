# tray_icon.py

import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
import game_control
import random

REFRESH_TIME = 10 * 1000  # Tray에 게임시간 표시 주기(밀리초 단위)

# 전역 변수 정의
window = None  # 윈도우를 전역 변수로 미리 정의
app = QApplication(sys.argv)
menu = QMenu()


def create_tray_icon():

    # 트레이 아이콘 생성
    tray_icon = QSystemTrayIcon(QIcon("game_stop.png"), app)
    tray_icon.setToolTip("Game Control")

    # 메뉴 항목 추가
    view_action = menu.addAction("게임 실행 정보")
    view_action.triggered.connect(lambda: view_game_info())

    restart_action = menu.addAction("다시실행")
    restart_action.triggered.connect(lambda: game_control.start_game_control())
    restart_action.setEnabled(not get_value(game_control.is_game_control_running))  # 초기 상태 설정

    # 메뉴를 트레이 아이콘에 설정
    tray_icon.setContextMenu(menu)
    # 10초에 한번씩 update_game_time을(REFRESH_TIME)호출하여 툴팁을 변경한다
    update_timer = QtCore.QTimer()
    update_timer.timeout.connect(lambda: update_game_time(tray_icon, restart_action))
    update_timer.start(REFRESH_TIME)
    # 게임 제어시작
    game_control.start_game_control()

    tray_icon.show()

    print("Tray Icon 생성")
    sys.exit(app.exec_())

# 툴팁에있는 게임시간과 남은 시간 업데이트
def update_game_time(tray_icon, restart_action):

    game_time = get_game_time()
    remain_game_time = get_remain_game_time()
    msg = f"{game_time}\n{remain_game_time}"

    tray_icon.setToolTip(msg)
    # 게임시간을 업데이트할때마다 '다시실행'메뉴를 활성화해야하는지 체크
    restart_action.setEnabled(not get_value(game_control.is_game_control_running))


def get_game_time():

    hours, minutes, seconds = seconds_to_hours_minutes(get_value(game_control.game_run_time))

    return f"게임시간 : {hours} 시간 {minutes} 분 {seconds}초"


def get_remain_game_time():

    current_game_run_time = get_value(game_control.game_run_time)

    remain_game_run_time = game_control.max_game_run_time - current_game_run_time
    # 음수 값이 나올땐 0을 반환, 10초마다 체크하기에 현재게임시간이 맥스게임 런타임보다 더 커질 수 있음
    remain_game_run_time = remain_game_run_time if remain_game_run_time > 0 else 0

    hours, minutes, seconds = seconds_to_hours_minutes(remain_game_run_time)

    return f"남은시간 : {hours} 시간 {minutes} 분 {seconds}초"


def view_game_info():

    global window

    window = QWidget()
    window.setGeometry(700, 400, 400, 200)
    window.setWindowTitle("게임 실행 정보")

    label = QLabel("", window)
    label.setStyleSheet("color: black; font-size: 21px;")
    label.setGeometry(70, 50, 350, 100)

    game_time = get_game_time()
    remain_game_time = get_remain_game_time()
    msg = f"{game_time}\n\n{remain_game_time}"

    label.setText(msg)

    window.show()


def seconds_to_hours_minutes(seconds):

    hours, remainder = divmod(seconds, 3600)  # 1 시간 = 3600 초
    minutes, seconds = divmod(remainder, 60)  # 1 분 = 60 초

    return hours, minutes, seconds


def get_value(shared_value):
    with shared_value.get_lock():
        return shared_value.value
