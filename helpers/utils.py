import datetime
import json
import os

from selenium import webdriver

DB_FILE = f"{os.path.realpath(os.path.dirname(__file__))}/../match.json"


def read_config() -> dict:
    try:
        fp = open(DB_FILE, 'r', encoding='utf-8')
    except FileNotFoundError:
        return None

    cfg = json.load(fp)
    fp.close()
    return cfg

def write_config(data: dict) -> bool:
    with open(DB_FILE, 'w', encoding='utf-8') as fp:
        serial_json = json.dumps(data)
        fp.write(serial_json)

    return True


def sanitize_str(_str: str) -> str:
    aux = _str.lower()
    aux = aux.replace(' ', '_').replace('.', '')

    return aux


def spawn_driver() -> webdriver.Firefox:
    ff_opts = webdriver.FirefoxOptions()
    ff_opts.add_argument('--headless')

    driver = webdriver.Firefox(options=ff_opts)

    return driver


def create_date_sentence(_time: datetime.timedelta) -> list[str]:
    final_str = []

    days = _time.days
    hours = _time.seconds // 3600
    minutes = _time.seconds % 60
    seconds = _time.seconds - minutes - (hours * 60 * 60)


    if days > 0:
        final_str.append(f"{days} dia{'s' if days > 1 else ''}")
    if hours > 0:
        final_str.append(f"{hours} hora{'s' if hours > 1 else ''}")
    if minutes > 0:
        final_str.append(f"{minutes} minuto{'s' if minutes > 1 else ''}")
    if seconds > 0:
        final_str.append(f"{seconds} segundo{'s' if seconds > 1 else ''}")

    return final_str
