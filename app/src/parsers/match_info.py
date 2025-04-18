"""Parsing info about match"""
import logging
import json
from dataclasses import dataclass, asdict

import aiohttp
from typing import Dict, List, Optional, Union

from fluentogram import TranslatorRunner

@dataclass
class PlayerMatchInfo:
    account_id: Optional[int] = None
    name: Optional[str] = None
    team: Optional[str] = None
    rank: Optional[str] = None
    lvl: Optional[str] = None
    networth: Optional[str] = None
    kda: Optional[str] = None
    aghanim_scepter: Optional[int] = None
    aghanim_shard: Optional[int] = None
    hero_damage: Optional[int] = None
    gold_per_min: Optional[int] = None
    hero_damage_per_min: Optional[int] = None
    hero_healing_per_min: Optional[int] = None
    kills_per_min: Optional[int] = None
    last_hits_per_min: Optional[int] = None
    tower_damage: Optional[int] = None


async def get_general_info_about_match(match_id: int,
                                       locale: TranslatorRunner) -> Dict[str, str]:
    """Возвращает общую информацию о матче."""

    url =  f'https://api.opendota.com/api/matches/{match_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()


    radiant_win = data.get('radiant_win', False)
    human_players = data.get('human_players', 0)
    match_id_value = data.get('match_id', 'N/A')
    players = data.get('players', [])
    abandoned_count = sum(player.get('abandons', 0) for player in players)

    win_text = locale.radiant() if radiant_win else locale.dire()
    quantity_players_text = human_players
    abandoned_text = abandoned_count
    id_match_text = match_id_value

    return {
        'win': win_text,
        'quantity_players': quantity_players_text,
        'abandoned': abandoned_text,
        'id_match': id_match_text,
        'num_players': human_players
    }


async def get_info_about_players_of_match(match_id: int,
                                          locale: TranslatorRunner) -> str:
    """Возвращает информацию о каждом игроке из заданного матча."""

    url = f'https://api.opendota.com/api/matches/{match_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    player_info_list = []
    players = data.get('players', [])


    for player in players:
        player_info = PlayerMatchInfo(
        account_id=player.get('account_id'),
        name=player.get('personaname'),
        team=locale.radiant() if player.get('IsRadiant', False) else locale.dire(),
        rank = player.get('rank_tier'),
        lvl = player.get('level', 'N/A'),
        networth = player.get('net_worth'),
        kda=f"{player.get('kills', 0)} | {player.get('deaths', 0)} | {player.get('assists', 0)}",
        aghanim_scepter=player.get('aghanims_scepter', 0),
        aghanim_shard=player.get('aghanims_shard', 0),
        hero_damage=player.get('hero_damage')
        )

        benchmarks = player.get('benchmarks')

        if benchmarks:
            player_info.gold_per_min = benchmarks.get('gold_per_min', {}).get('raw')
            player_info.hero_damage_per_min = benchmarks.get('hero_damage_per_min', {}).get('raw')
            player_info.hero_healing_per_min = benchmarks.get('hero_healing_per_min', {}).get('raw')
            player_info.kills_per_min = benchmarks.get('kills_per_min', {}).get('raw')
            player_info.last_hits_per_min = benchmarks.get('last_hits_per_min', {}).get('raw')
            player_info.tower_damage = benchmarks.get('tower_damage', {}).get('raw')
        else:
            player_info.gold_per_min = None
            player_info.hero_damage_per_min = None
            player_info.hero_healing_per_min = None
            player_info.kills_per_min = None
            player_info.last_hits_per_min = None
            player_info.tower_damage = None


        player_info_list.append(player_info)

    return json.dumps([asdict(player) for player in player_info_list], indent=4)



async def get_last_match_info(account_id: int,
                              locale: TranslatorRunner) -> List[Union[Optional[str], Dict[str, str]]]:
    """Возвращает информацию об игроке в последнем его матче."""

    url = f'https://api.opendota.com/api/players/{account_id}/matches'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'limit': 1}) as response:
                response.raise_for_status()
                data = await response.json()

        if not data:
            return []

        match_data = data[0]
        return [
            str(match_data['match_id']),
            {
                 'kills': str(match_data['kills']),
                 'deaths': str(match_data['deaths']),
                 'assists': str(match_data['assists'])
            },
            locale.radiant() if match_data['radiant_win'] else locale.dire()
        ]
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при запросе к API: {e}")
        return []
    except (KeyError, TypeError) as e:
        logging.error(f"Ошибка при обработке данных: {e}")
        return []
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {e}")
        return []