import json
import requests

H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0",
     'Content-Type': 'application/json'}

PLAYER_STATS_URL = "https://api.sofascore.com/api/v1/player/_PLAYER_ID_/unique-tournament/238/season/42655/statistics/overall"


def populate_players() -> bool:
    req = requests.get('https://api.sofascore.com/api/v1/team/3006/players', 
                        headers=H, timeout=5)
    try:
        req.raise_for_status()
    except requests.HTTPError as e:
        print(e)

    data = json.loads(req.text)
    
    players = {"players": []}
    for i in data['players']:
        p_name = i['player']['name']
        try:
            p_jersey = i['player']['jerseyNumber']
        except KeyError:
            p_jersey = "0"
        p_id = i['player']['id']
        p_pos = i['player']['position']
        p_photo = f"https://api.sofascore.app/api/v1/player/{p_id}/image"

        players['players'].append({
            "name": p_name,
            "jersey": p_jersey,
            "id": p_id,
            "position": p_pos,
            "photo": p_photo
        })

    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players, f)


def add_player(data:dict)-> bool:
    pass
    
def bulk_add_players(data:dict)-> bool:
    pass

def delete_player(player_id: str)-> bool:
    pass

def fetch_player_stats(jerseynum: int)-> dict:
    with open('players.json', 'r', encoding='utf-8') as f:
        players = json.load(f)

    for i in players['players']:
        if i['jersey'] == str(jerseynum):
            _name = i['name']
            _position = i['position']
            _id = i['id']
            _photo = i['photo']
            break
        return 'Jogador não encontrado'

    url = PLAYER_STATS_URL.replace('_PLAYER_ID_', str(_id))
    req = requests.get(url, headers=H, timeout=5)
    data = json.loads(req.text)

    return parse_player_stats(data['statistics'], _name, _position)


def parse_player_stats(data: dict, name: str, position: str)-> str:
    stats = f"{name}\n\n\
Jogos: {data['appearances']}\n\
Rating: {round(data['rating'], 2)}\n\
Amarelos: {data['yellowCards']}\n\
Vermelhos: {data['redCards']}\n"

    if position == "G":
        conc_jogo = round(data['goalsConceded']/data['appearances'], 2)
        stats += f"Defesas: {data['saves']}\n\
Golos concedidos: {data['goalsConceded']}\n\
Golos concedidos/jogo: {conc_jogo}\n\
Penaltis confrontados: {data['penaltyFaced']}\n\
Penaltis defendidos: {data['penaltySave']}"
    else:
        goal_percent = round(data['goals']/data['totalShots']*100, 1)
        stats += f"Golos: {data['goals']}\n\
Assistencias: {data['goalsAssistsSum']}\n\
Remates: {data['totalShots']}\n\
Golos/Remate: {goal_percent}%\n\
Eficácia de passes: {round(data['accuratePassesPercentage'],2)}%"

    return stats

def fetch_match_stats(match_id: str)-> dict:
    pass



if __name__ == "__main__":
    print(fetch_player_stats(99))
    print('====================')
    print(fetch_player_stats(88))
