import configparser
import datetime

from os import getcwd
from selenium import webdriver

CONFIG_PATH = f"{getcwd()}/discord.conf"
CONFIG = configparser.ConfigParser()

def read_conf(section=None) -> dict:
    config = CONFIG.read(CONFIG_PATH)
    if section:
        try:
            return config[section]
        except KeyError:
            print('No key found, returning full config instead')
    return config

def write_conf(data: dict) -> None:
    for section, sub_section in data.items():
        if not CONFIG.has_section(section):
            CONFIG.add_section(section)
        
        for k, v in sub_section.items():
            CONFIG.set(section, str(k), str(v))

    with open(CONFIG_PATH, 'w', encoding='utf-8') as fp:
        CONFIG.write(fp)


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
