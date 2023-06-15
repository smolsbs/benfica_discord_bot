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


def req_get_next_match() -> str:
    s = requests.Session()
    conts = s.request('POST', URL, headers=H, data=DATA)
    soup = BeautifulSoup(conts.content.decode(
        'utf-8', 'ignore'), 'html.parser')
    match_div = soup.find_all('div', {'class': 'calendar-item'})

    info_dic = {}
    for i, match in enumerate(match_div):

        checker = match.find('div', {'class': 'calendar-match-hour'}).text
        if checker == 'A definir':
            continue

        s_date = match.find('div', {'class': 'startDateForCalendar'}).text
        match_date = datetime.strptime(s_date, r"%m/%d/%Y %I:%M:%S %p")

        loc = match.find(
            'div', {'class': 'calendar-match-location'}).text
        aux = match.find(
            'div', {'class': 'calendar-live-channels'})
        try:
            canal = aux.img['src'].split('/')[-1]
        except AttributeError:
            canal = 'N/A'

        comp = match.find(
            'div', {'class': 'calendar-competition'}).text
        home = match.find(
            'div', {'class': 'home-team'}).text.strip()
        away = match.find(
            'div', {'class': 'away-team'}).text.strip()

        info = {
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
        info_dic[i] = info

    print(info_dic)
    ret = utils.write_config(info_dic)
    if ret:
        jogos = len(info_dic)

        return f"{jogos} novo(s) jogo(s) adicionado(s)"
    return ret


def fetch_config_next_match() -> datetime:
    cfg = utils.read_conf('next_match')

    next_match = datetime(
        year=int(cfg['year']),
        month=int(cfg['month']),
        day=int(cfg['day']),
        hour=int(cfg['hour']),
        minute=int(cfg['minute']))

    return next_match


if __name__ == "__main__":
    req_get_next_match()
