import time
import psutil
import multiprocessing
import main_window
import configparser

CONFIG_FILE = 'config.ini'
GAME_RUN_TIME_FILE = 'game_run_time.txt'

# 구성 파일 읽기
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# 전역 변수 정의
game_run_time = multiprocessing.Value('i', 0)
game_name_list = ["notepad.exe", "StarCraft.exe","RobloxPlayerBeta.exe","LeagueofLegends.exe"]

# 구성 파일에서 max_game_run_time 초기화
max_game_run_time = int(config['GameSettings']['max_game_run_time'])

# 게임 실행 여부 확인
def is_game_running():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] in game_name_list:
            print(process.info['name'])
            return True
    return False

# 게임 종료
def terminate_application(app_name):
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == app_name:
            try:
                p = psutil.Process(process.info['pid'])
                p.terminate()
                print(f"{app_name} 프로세스가 종료되었습니다.")
            except psutil.NoSuchProcess:
                print(f"{app_name} 프로세스를 찾을 수 없습니다.")

# 게임 실행 시간 계산
def count_game_runtime(game_run_time):
    while True:
        if is_game_running():
            with game_run_time.get_lock():
                game_run_time.value += 1

                # if shared_value.value % 10 == 0:
                #     print(f'save')
                #     # 60의 배수마다 파일에 저장
                #     save_game_run_time(shared_value.value)

                if game_run_time.value >= max_game_run_time:
                    for game_name in game_name_list:
                        terminate_application(game_name)

        time.sleep(1)
        print(f'게임 실행 시간: {game_run_time.value} 초')

def get_game_run_time(shared_value):
    with shared_value.get_lock():
        return shared_value.value
# def save_game_run_time(run_time):
#     with open(GAME_RUN_TIME_FILE, 'w') as f:
#         f.write(str(run_time))

# def load_game_run_time():
#     if os.path.exists(GAME_RUN_TIME_FILE):
#         with open(GAME_RUN_TIME_FILE, 'r') as f:
#             game_run_time.value = int(f.read())

if __name__ == "__main__":
    # load_game_run_time()  # 저장된 게임 실행 시간 로드

    shared_game_run_time = multiprocessing.Value('i', game_run_time.value)

    game_process = multiprocessing.Process(target=count_game_runtime, args=(shared_game_run_time,))
    game_process.daemon = True  # 백그라운드 프로세스
    game_process.start()

    try:
        main_window.window(get_game_run_time, shared_game_run_time)
    except KeyboardInterrupt:
        # 프로그램 종료 시 정리
        pass

    # 프로그램이 종료될 때 게임 실행 시간을 저장
    # save_game_run_time(shared_game_run_time)

