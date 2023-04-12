# imports
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from helpers import utils

# Global vars
URL = 'https://www.slbenfica.pt/api/sitecore/Calendar/CalendarEvents'
TZ = 'Europe/Lisbon'
WEEKDAY = {
    1: 'Segunda-feira',
    2: 'Terça-feira',
    3: 'Quarta-feira',
    4: 'Quinta-feira',
    5: 'Sexta-feira',
    6: 'Sábado',
    7: 'Domingo'
}

H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0",
     'Accept-Encoding': 'gzip, deflate, br',
     'Referer': 'https://www.slbenfica.pt/pt-pt/futebol/calendario',
     'Content-Type': 'application/json'}

DATA = "{\"filters\":{\"Menu\":\"next\",\"Modality\":\"{ECCFEB41-A0FD-4830-A3BB-7E57A0A15D00}\",\"IsMaleTeam\":true,\"Rank\":\"16094ecf-9e78-4e3e-bcdf-28e4f765de9f\",\"Tournaments\":[\"dp:tournament:50d243c9-fee7-4b34-bdcc-22bf446935eb\",\"sr:tournament:853\",\"sr:tournament:7\",\"sr:tournament:238\",\"sr:tournament:327\",\"sr:tournament:336\"],\"Seasons\":[\"2022/23\"],\"PageNumber\":0}}"

# Functions


def req_get_next_match() -> datetime:
    s = requests.Session()

    conts = s.request('POST', URL, headers=H, data=DATA)

    soup = BeautifulSoup(conts.content, 'html.parser')

    match_div = soup.find('div', {'class': 'calendar-item'})

    loc = match_div.find(
        'div', {'class': 'calendar-match-location'}).text
    canal = match_div.find(
        'div', {'class': 'calendar-live-channels'}).text.strip()
    comp = match_div.find(
        'div', {'class': 'calendar-competition'}).text

    s_date = match_div.find('div', {'class': 'startDateForCalendar'}).text
    match_date = datetime.strptime(s_date, r"%m/%d/%Y %I:%M:%S %p")

    home = match_div.find(
        'div', {'class': 'home-team'}).text.strip()
    away = match_div.find(
        'div', {'class': 'away-team'}).text.strip()


    if canal == "":
        canal = 'N/A'

    info = {'next_match': {
        'tv': canal,
        'competition': comp,
        'stadium': loc,
        'homeTeam': home,
        'awayTeam': away,
        'year': str(match_date.year),
        'month': str(match_date.month),
        'day': str(match_date.day),
        'hour': str(match_date.hour),
        'minute': str(match_date.minute)
    }
    }

    return utils.write_config(info)


def fetch_config_next_match() -> datetime:
    cfg = utils.read_conf('next_match')

    next_match = datetime(
        year=int(cfg['year']),
        month=int(cfg['month']),
        day=int(cfg['day']),
        hour=int(cfg['hour']),
        minute=int(cfg['minute']))

    return next_match


def how_long_until() -> str:
    match_date = fetch_config_next_match()
    local_time = datetime.now()

    if local_time > match_date:
        if match_date + timedelta(hours=2) > local_time:

            sentence = '<:slb:240116451782950914> Já começou há '
            sentence += utils.create_date_sentence(local_time-match_date)
            sentence += ' <:slb:240116451782950914>'
            return sentence
        return ""

    time_to_match = match_date - local_time

    if time_to_match.days != 0:
        sentence = '<:slb:240116451782950914> Falta(m) '
        sentence += utils.create_date_sentence(time_to_match)

    else:
        sentence = '<:slb:240116451782950914> É hoje! Já só falta(m)'
        sentence += utils.create_date_sentence(time_to_match)

    sentence += ' para ver o Glorioso de novo! <:slb:240116451782950914>'
    return sentence


