# config.py
# Все конфиденциальные данные и пути хранятся здесь

# Папки для картинок и видео
IMAGES_FOLDER = 'Desktop\\pictures'  
VIDEOS_FOLDER = 'Desktop\\videos'    

# Кабинеты и токены Ozon 
ACCOUNTS = [
    ("ACCOUNT_ID_1", "API_KEY_1", "store1"),  # токены кабинетов
    ("ACCOUNT_ID_2", "API_KEY_2", "store2"),
    ("ACCOUNT_ID_3", "API_KEY_3", "store3")
]

# Выбираем активный кабинет (индекс 1 для примера)
ACTIVE_ACCOUNT_INDEX = 1

# Yandex.Disk
YANDEX_DISK_FOLDER = "/all_m"  # папка для видео на Яндекс.Диске
YANDEX_DISK_TOKEN = "YANDEX_TOKEN_1"  # токен Яндекс.Диска 
FOLDER_LINK = "https://disk.yandex.ru/d/FAKE_FOLDER_LINK"  # публичная ссылка на папку для видео

# Названия видео
VIDEO_PREFIX = "VIDEO_PREFIX_"  
# имена видео, загружаемых на ЯД, будут начинаться на этот набор символов

# Таблицы
TABLE_PATH = 'Desktop\\backup.xlsx'  # выгружаемая таблица с ссылками на видео на Яндекс.Диске
TABLE_SHEET_NAME = 'sheet_name_demo' # sheet_name в table
GUIDS_FILE = 'Desktop\\articles_demo.xlsx'  # таблица с GUID-ами товаров, для которых нужны видео
GUIDS_SHEET_NAME = 'Sheet1'
