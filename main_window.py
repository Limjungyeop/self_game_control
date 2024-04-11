import sys
import time
import game_control
import configparser
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QInputDialog

CONFIG_FILE = 'config.ini'
GAME_RUN_TIME_FILE = 'game_run_time.txt'    

first_window = None  # 첫 번째 윈도우를 전역 변수로 미리 정의
second_window = None  # 두 번째 윈도우를 전역 변수로 미리 정의
tirdh_window = None  # 두 번째 윈도우를 전역 변수로 미리 정의

def window(get_game_run_time, shared_value):
    app = QApplication(sys.argv)
    widget = QWidget()

    label = QLabel("", widget)
    label.setGeometry(10, 10, 200, 30)

    button = QPushButton("오늘 게임한 시간 확인", widget)
    button.setGeometry(10, 50, 300, 360)
    button.setStyleSheet("background-color: orange; color: black; font-size: 16px;")
    button.clicked.connect(lambda: open_first_window(get_game_run_time, shared_value))

    button = QPushButton("오늘 잔여 게임시간 확인", widget)
    button.setGeometry(350, 50, 300, 360)
    button.setStyleSheet("background-color: green; color: black; font-size: 16px;")
    button.clicked.connect(lambda: open_second_window(get_game_run_time, shared_value))

    button = QPushButton("게임 시간 설정", widget)
    button.setGeometry(690, 50, 300, 360)
    button.setStyleSheet("background-color: gold; color: black; font-size: 16px;")
    button.clicked.connect(change_max_game_run_time)

    widget.setGeometry(500, 300, 1000, 600)
    widget.setWindowTitle("자기주도게임제한")
    widget.show()
    app.exec_()


def open_first_window(get_game_run_time, shared_value):
    global first_window
    first_window = QWidget()
    first_window.setGeometry(700, 400, 500, 300)
    first_window.setWindowTitle("오늘 게임한 시간")
   
    label = QLabel("", first_window)
    label.setStyleSheet("color: black; font-size: 21px;")
    label.setGeometry(10, 80, 480, 30)
    
    current_run_time = get_game_run_time(shared_value)
    hours, minutes, seconds = seconds_to_hours_minutes(current_run_time)
    label.setText(f"오늘 게임을 {hours} 시간 {minutes} 분 {seconds}초 플레이했습니다.")

    first_window.show()

def open_second_window(get_game_run_time, shared_value):
    global second_window

    second_window = QWidget()
    second_window.setGeometry(700, 400, 500, 300)
    second_window.setWindowTitle("잔여시간")

    label = QLabel("", second_window)
    label.setStyleSheet("color: black; font-size: 21px;")
    label.setGeometry(10, 80, 480, 30)

    print(game_control.max_game_run_time)
    
    current_run_time = get_game_run_time(shared_value)
    remain_run_time = game_control.max_game_run_time - current_run_time

    hours, minutes, seconds = seconds_to_hours_minutes(remain_run_time)

    label.setText(f"오늘 게임 잔여 시간은 {hours} 시간 {minutes} 분 {seconds}초 입니다.")

    second_window.show()

def change_max_game_run_time():
    global tirdh_window
    new_max_time, ok_pressed = QInputDialog.getInt(tirdh_window, "게임 시간 설정", "게임 시간 제한 (초단위):", value=game_control.max_game_run_time)

    if ok_pressed:
        save_max_game_run_time(new_max_time)

def seconds_to_hours_minutes(seconds):
    hours, remainder = divmod(seconds, 3600)  # 1 시간 = 3600 초
    minutes, seconds = divmod(remainder, 60)  # 1 분 = 60 초

    return hours, minutes, seconds

        
def save_max_game_run_time(new_max_time):
    # 설정 파일 업데이트
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    config.set('GameSettings', 'max_game_run_time', str(new_max_time))

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
