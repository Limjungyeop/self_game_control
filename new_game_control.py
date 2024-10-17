# game_control.py
import os
import signal
import psutil
import configparser
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QInputDialog
import game_info
import new_tray_icon
import random

CONFIG_FILE = 'config.ini'
GAME_RUN_TIME_FILE = 'game_run_time.txt'
INIT_DATE = '9999-12-31T00:00:00.000000'  # Date 초기화 값

# 구성 파일 읽기
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# 환경변수
max_program_run_time = int(config['ProgramSettings']['max_program_run_time'])  # 프로그램이 동작하는 시간
sleep_time = int(config['ProgramSettings']['sleep_time'])  # Game 시간 체크 간격(초)
save_time = int(config['ProgramSettings']['save_time'])  # 파일에 저장하는 간격(초)
# sleep_time,save_time = (int(config['ProgramSettings']['sleep_time']),int(config['ProgramSettings']['save_time']))

max_game_run_time = int(config['ControlSettings']['max_game_run_time'])  # 최대 게임 가능시간
control_start_date = datetime.fromisoformat((config['ControlSettings']['control_start_date']))  # control 시작 일시

# 전역 변수 정의
game_info_list = game_info.get_game_list()  # 체크 할 게임 리스트
game_run_time = 0  # multiprocessing.Value('i', 0)  # 게임 실행 시간
is_game_control_running = 0   # multiprocessing.Value('i', 0) # 게임실행체크가 시작되면 1 안되면 0


# 게임 실행 여부 확인
def is_game_running():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        for game in game_info_list:
            if process.info['name'] == game['name']:
                # print(f"실행 Game -> {process.info['name']}")
                return True
    return False


# 게임 종료
def terminate_application(app_name):
    for process in psutil.process_iter(attrs=['name']):  # 프로세스에서 앱이름과 pid가져오기
        if process.info['name'] == app_name:
            try:
                process.terminate()
                print(f"{app_name} Game이 종료되었습니다.")
            except psutil.NoSuchProcess:
                print(f"{app_name} Game을 찾을 수 없습니다.")


def get_control_time(start_date):
    current_date = datetime.now()
    return current_date - start_date  # 현재 시간에서 프로그램 시작 시간을 뺀다.


def save_max_game_run_time(max_time):
    # 설정 파일 업데이트
    config.read(CONFIG_FILE)
    config.set('ControlSettings', 'max_game_run_time', str(max_time))  # 입력받은 최대게임시간을 config에 저장
    config.set('ControlSettings', 'control_start_date', datetime.now().isoformat())  # 게임제어가 시작된 시간을 현재시간으로 저장
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


# 게임 실행시간 저장
def save_game_run_time(run_time):
    with open(GAME_RUN_TIME_FILE, 'w') as f:
        f.write(str(run_time))


# 저장된 게임 실행시간 가져오기
def load_game_run_time():
    if os.path.exists(GAME_RUN_TIME_FILE):
        with open(GAME_RUN_TIME_FILE, 'r') as f:
            return int(f.read())


def start_game_control():
    global max_game_run_time
    global is_game_control_running
    global game_run_time
    # 최초 값이거나 24시간이 지나면 새로운 max_game_run_time을 입력받음
    if (control_start_date == datetime.fromisoformat(INIT_DATE) or  # 처음으로 프로그램을 시작한 경우(이전에 시작한 경우가 없음)
            get_control_time(control_start_date) >= timedelta(seconds=max_program_run_time)):  # 24시간이 지났는지 확인하는 문구()

        window = None
        max_game_run_time_min = int(max_game_run_time / 60)  # 분으로 변경
        new_max_time, ok_pressed = QInputDialog.getInt(window,
                                                       "게임시간설정",
                                                       f"{max_program_run_time/3600}시간 동안 게임할 시간을 입력하세요.(분 단위)",
                                                       value=max_game_run_time_min)

        if ok_pressed:
            max_game_run_time = new_max_time * 60  # 초로 변경
            save_max_game_run_time(max_game_run_time)
    game_run_time = load_game_run_time()
    is_game_control_running = 1


def check_game_run_time():
    global game_run_time
    global is_game_control_running
    if is_game_control_running == 1:
        if is_game_running():
            game_run_time += int(new_tray_icon.REFRESH_TIME/1000)
            # SAVE_TIME 마다 파일에 저장
            if game_run_time % save_time == 0:
                print(f'Game 실행 시간 저장')
                save_game_run_time(game_run_time)

            # 게임 실행시간이 max_game_run_time보다 크거나 같으면 종료
            if game_run_time >= max_game_run_time:
                for game in game_info_list:
                    terminate_application(game['name'])

        if get_control_time(control_start_date) >= timedelta(seconds=max_program_run_time):
            save_game_run_time(0)
            is_game_control_running = 0
        print(f'프로그램 실행 시간: {get_control_time(control_start_date)}초, 게임 실행 시간: {game_run_time}초')


# main
if __name__ == "__main__":
    # 종료 시그널 무시
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # tray icon 생성 -> 계속 실행됨
    new_tray_icon.create_tray_icon()

    print("메인 프로그램 종료")
