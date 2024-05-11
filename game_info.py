import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import configparser

CONFIG_FILE = 'config.ini'

# 구성 파일 읽기
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# 구성 파일 초기화
key_file_name = str(config['ProgramSettings']['key_file_name'])
database_url = str(config['ProgramSettings']['database_url'])

# Firebase 인증 및 초기화
cred = credentials.Certificate(key_file_name)
firebase_admin.initialize_app(cred, {'databaseURL': database_url})

def get_game_list():

    # Firebase Database에서 데이터 읽기
    ref = db.reference('/game_list')
    game_list = ref.get()

    print(game_list)

    return game_list
