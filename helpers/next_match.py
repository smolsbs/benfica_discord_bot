# imports
from datetime import datetime, timedelta
from pprint import pprint
import pendulum

from selenium.webdriver.common.by import By

from helpers import utils

# Global vars
URL = 'https://www.slbenfica.pt/pt-pt/futebol/calendario'
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

# Functions
def get_next_match() -> datetime:
    browser = utils.spawn_driver()
    browser.get(URL)
    browser.implicitly_wait(2.5)    # wait for browser to load all elements

    main_div = browser.find_element(By.CLASS_NAME, 'calendar-item')

    # tv channel and competition
    tv_div = main_div.find_element(By.CLASS_NAME, 'calendar-live-channels')
    tv_channel = tv_div.find_element(
        By.TAG_NAME, 'img').get_attribute('src').split('/')[-1]

    competition = main_div.find_element(
        By.CLASS_NAME, 'calendar-competition').get_attribute("textContent")

    # teams 
    home_div = main_div.find_element(By.CLASS_NAME, 'home-team')
    home_team = home_div.find_element(
        By.CLASS_NAME, 'calendar-item-team-name').get_attribute("textContent")
    
    away_div = main_div.find_element(By.CLASS_NAME, 'away-team')
    away_team = away_div.find_element(
        By.CLASS_NAME, 'calendar-item-team-name').get_attribute("textContent")

    # date and stadium info
    next_match_div = main_div.find_element(
        By.CLASS_NAME, 'calendar-match-info')
    next_match_date = next_match_div.find_element(
        By.CLASS_NAME, 'startDateForCalendar').get_attribute("textContent")
    stadium = next_match_div.find_element(
        By.CLASS_NAME, 'locationForCalendar').get_attribute("textContent")

    match_date = datetime.strptime(next_match_date, r"%m/%d/%Y %I:%M:%S %p")


    info = {'next_match': {
        'tv': tv_channel,
        'competition': competition,
        'stadium': stadium,
        'homeTeam': home_team,
        'awayTeam': away_team,
        'year': str(match_date.year),
        'month': str(match_date.month),
        'day': str(match_date.day),
        'hour': str(match_date.hour),
        'minute': str(match_date.minute)
        }
    }
    pprint(info)

    browser.quit()

    return


    utils.write_conf(info)

get_next_match()

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
    tz_diff = (pendulum.today() - pendulum.today(TZ)).total_hours()
    local_time = datetime.now() + timedelta(hours=int(tz_diff))

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
