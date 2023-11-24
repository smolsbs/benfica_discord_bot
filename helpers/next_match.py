# imports
from datetime import datetime, timedelta

import os
import json
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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

DATA = '{"filters":{"Menu":"next","Modality":"{ECCFEB41-A0FD-4830-A3BB-7E57A0A15D00}","IsMaleTeam":true,"Rank":"16094ecf-9e78-4e3e-bcdf-28e4f765de9f","Tournaments":["sr:tournament:853","sr:tournament:7","sr:tournament:238","sr:tournament:345","sr:tournament:327","sr:tournament:336"],"Seasons":["2023/24"],"PageNumber":0}}'

DATA_WOMEN = '{"filters":{"Menu":"next","Modality":"{37A610A0-2CCD-4F89-A589-A1F995F8FCB5}","IsMaleTeam":false,"Rank":"16094ecf-9e78-4e3e-bcdf-28e4f765de9f","Tournaments":[],"Seasons":["2023/24"],"PageNumber":0}}'
# Functions

def make_event_helper(match):
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json") as file:
        config = json.load(file)

    nome_evento = f"{match['homeTeam']} Vs. {match['awayTeam']}"

    descricao = f"🏆 {match['competition']}\n🏟️ {match['stadium']}\n📺 {match['tv']}"
    nome_canal = f"#{utils.sanitize_str(match['homeTeam'])}_vs_{utils.sanitize_str(match['awayTeam'])}"
    inicio_jogo = datetime(year=int(match['year']),
                           month=int(match['month']),
                           day=int(match['day']),
                           hour=int(match['hour']),
                           minute=int(match['minute']),
                           tzinfo=ZoneInfo('Europe/Lisbon'))
    inicio_jogo = inicio_jogo.astimezone(tz=ZoneInfo(config['timezone']))
    fim_jogo = inicio_jogo + timedelta(hours=2)

    return [nome_evento, descricao, nome_canal, inicio_jogo, fim_jogo];

def req_get_next_match() -> str:
    games = req_get_next_match_helper(DATA)
    games += req_get_next_match_helper(DATA_WOMEN)

    games_dic = {idx: game for idx,game in enumerate(games)}

    ret = utils.write_config(games_dic)
    if ret:
        n_games = len(games_dic)
        games_list = ""
        for k,v in games_dic.items():
            games_list += f"\n{k}: {v['homeTeam']} - {v['awayTeam']} "

        return f"{n_games} novo(s) jogo(s) disponível(eis).{games_list}"
    return 'Nenhum jogo novo encontrado'


def req_get_next_match_helper(squad: str) -> list:
    s = requests.Session()
    conts = s.request('POST', URL, headers=H, data=squad)
    soup = BeautifulSoup(conts.content.decode(
        'utf-8', 'ignore'), 'html.parser')
    match_div = soup.find_all('div', {'class': 'calendar-item'})

    info_dic = []
    for i, match in enumerate(match_div):

        checker = match.find('div', {'class': 'calendar-match-hour'}).text
        if checker == 'A definir':
            continue

        s_date = match.find('div', {'class': 'startDateForCalendar'}).text
        match_date = datetime.strptime(s_date, r"%m/%d/%Y %I:%M:%S %p")
        try:
            squad_type = match.find('div', {'class': 'calendar-squad-type'}).text.lower()
        except AttributeError:
            squad_type = None

        loc = match.find(
            'div', {'class': 'calendar-match-location'}).text
        aux = match.find(
            'div', {'class': 'calendar-live-channels'})
        try:
            canal = aux.img['src'].split('/')[-1]
        except (AttributeError, TypeError):
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
            'homeTeam': f"{home}{' (F)' if squad_type == 'feminino' else ''}",
            'awayTeam': f"{away}{' (F)' if squad_type == 'feminino' else ''}",
            'year': str(match_date.year),
            'month': str(match_date.month),
            'day': str(match_date.day),
            'hour': str(match_date.hour),
            'minute': str(match_date.minute)
        }
        info_dic.append(info)

    return info_dic

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
