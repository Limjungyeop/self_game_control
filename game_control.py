# game_control.py

import os
import time
import signal
import psutil
import multiprocessing
import configparser
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QInputDialog
import game_info
import tray_icon

CONFIG_FILE = 'config.ini'
GAME_RUN_TIME_FILE = 'game_run_time.txt'
SAVE_TIME = 60  # 파일에 저장하는 간격(초)
SLEEP_TIME = 10  # Game 시간 체크 간격(초)
INIT_DATE = '9999-12-31T00:00:00.000000'  # Date 초기화 값

# 구성 파일 읽기
config = configparser.ConfigParser()
config.read(CONFIG_FILE)


# 전역 변수 정의
game_info_list = game_info.get_game_list()  # 체크 할 게임 리스트
max_program_run_time = int(config['ProgramSettings']['max_program_run_time'])  # 프로그램이 동작하는 시간
max_game_run_time = int(config['ControlSettings']['max_game_run_time'])  # 최대 게임 가능시간
control_start_date = datetime.fromisoformat((config['ControlSettings']['control_start_date']))  # control 시작 일시
game_run_time = multiprocessing.Value('i', 0)  # 게임 실행 시간
game_control_running = multiprocessing.Value('i', 0)


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

    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == app_name:
            try:
                p = psutil.Process(process.info['pid'])
                p.terminate()
                print(f"{app_name} Game이 종료되었습니다.")
            except psutil.NoSuchProcess:
                print(f"{app_name} Game을 찾을 수 없습니다.")


def get_control_time(start_date):
    current_date = datetime.now()
    return current_date - start_date


def save_max_game_run_time(max_time):
    # 설정 파일 업데이트
    config.read(CONFIG_FILE)
    config.set('ControlSettings', 'max_game_run_time', str(max_time))
    config.set('ControlSettings', 'control_start_date', datetime.now().isoformat())
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


# 게임 실행 시간 계산
def count_game_runtime(run_time, control_running):

    # 저장된 게임 실행 시간 로드
    run_time.value = load_game_run_time()
    print(f"이전 Game 실행 시간 : {run_time.value}초")
    # 실행 중으로 셋팅
    with control_running.get_lock():
        control_running.value = 1

    while True:
        if is_game_running():
            with run_time.get_lock():
                run_time.value += SLEEP_TIME

                # SAVE_TIME 마다 파일에 저장
                if run_time.value % SAVE_TIME == 0:
                    print(f'Game 실행 시간 저장')
                    save_game_run_time(run_time.value)

                # 게임 실행시간이 max_game_run_time보다 크거나 같으면 종료
                if run_time.value >= max_game_run_time:
                    for game in game_info_list:
                        terminate_application(game['name'])

        # 게임 실행시간이 max_game_run_time 보다 크면 종료
        if get_control_time(control_start_date) >= timedelta(seconds=max_program_run_time):
            break

        time.sleep(SLEEP_TIME)
        print(f'프로그램 실행 시간: {get_control_time(control_start_date)}초, 게임 실행 시간: {run_time.value}초')

    # 게임 실행 시간 초기화
    save_game_run_time(0)
    # 실행 종료로 셋팅
    with control_running.get_lock():
        control_running.value = 0
    print("서브 프로그램 종료")


def start_game_control():
    global max_game_run_time

    # 최초 값이거나 or control 시간이 종료되었으면 새로운값 입력
    if (control_start_date == datetime.fromisoformat(INIT_DATE) or
            get_control_time(control_start_date) >= timedelta(seconds=max_game_run_time)):
        window = None
        max_game_run_time_min = int(max_game_run_time / 60)  # 분으로 변경
        new_max_time, ok_pressed = QInputDialog.getInt(window,
                                                       "게임시간설정",
                                                       f"{max_program_run_time/3600}시간 동안 게임할 시간을 입력하세요.(분 단위)",
                                                       value=max_game_run_time_min)

        if ok_pressed:
            max_game_run_time = new_max_time * 60  # 분으로 변경
            save_max_game_run_time(max_game_run_time)

    # control process 수행
    game_control_process = multiprocessing.Process(target=count_game_runtime,
                                                   args=(game_run_time, game_control_running))
    game_control_process.daemon = False  # 백그라운드 프로세스 독립 - False
    print("Game Control 시작")
    game_control_process.start()
    print("Game Control 프로세스 종료")

    # 프로세스가 종료되었을 때를 대비하여 상태 업데이트
    # game_control_process.join()


# main
if __name__ == "__main__":
    # 종료 시그널 무시
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # tray icon 생성 -> 계속 실행됨
    tray_icon.create_tray_icon()

    print("메인 프로그램 종료")
