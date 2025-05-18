"""Parsing info about match"""

import logging
from typing import Dict, List, Optional, Union

import aiohttp
from fluentogram import TranslatorRunner


async def get_general_info_about_match(
    match_id: int, locale: TranslatorRunner
) -> Dict[str, str]:
    """Возвращает общую информацию о матче."""

    url = f"https://api.opendota.com/api/matches/{match_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    radiant_win = data.get("radiant_win", False)
    human_players = data.get("human_players", 0)
    match_id_value = data.get("match_id", locale.unknown())
    players = data.get("players", [])
    game_mode = data.get("game_mode", locale.unknown())
    lobby_type = data.get("lobby_type", locale.unknown())
    abandoned_count = sum(player.get("abandons", 0) for player in players)

    win_text = locale.radiant() if radiant_win else locale.dire()
    quantity_players_text = human_players
    abandoned_text = abandoned_count
    id_match_text = match_id_value

    print(
        {
            "win": win_text,
            "quantity_players": quantity_players_text,
            "abandoned": abandoned_text,
            "id_match": id_match_text,
            "num_players": human_players,
            "game_mode": game_mode,
            "lobby_type": lobby_type
        }
    )
    return {
        "win": win_text,
        "quantity_players": quantity_players_text,
        "abandoned": abandoned_text,
        "id_match": id_match_text,
        "num_players": human_players,
        "game_mode": game_mode,
        "lobby_type": lobby_type
    }
    


async def get_last_match_info(
    account_id: int, locale: TranslatorRunner
) -> List[Union[Optional[str], Dict[str, str]]]:
    """Возвращает информацию об игроке в последнем его матче."""

    url = f"https://api.opendota.com/api/players/{account_id}/matches"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"limit": 1}) as response:
                response.raise_for_status()
                data = await response.json()

        if not data:
            return []

        match_data = data[0]
        hero = await get_name_hero_from_match(match_data['hero_id'], locale)
        return [
            str(match_data["match_id"]),
            {
                "hero_name": hero,
                "kills": str(match_data["kills"]),
                "deaths": str(match_data["deaths"]),
                "assists": str(match_data["assists"]),
            },
            locale.radiant() if match_data["radiant_win"] else locale.dire(),
        ]
    except aiohttp.ClientError as e:
        logging.error(
            "Ошибка при запросе к API (get_last_match_info): %e", e, exc_info=True
        )
        return []
    except (KeyError, TypeError) as e:
        logging.error(
            "Ошибка при обработке данных (get_last_match_info): %e", e, exc_info=True
        )
        return []
    except Exception as e:
        logging.error("Неизвестная ошибка (get_last_match_info): %e", e, exc_info=True)
        return []


async def get_name_hero_from_match(hero_id: int, locale: TranslatorRunner) -> str:
    """Возвращает имя героя по его ID"""

    url = f"https://api.opendota.com/api/heroes"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

        if not data:
            return locale.unknown()

        return data[hero_id - 2]['localized_name'] # Чтобы найти нужный id нужно отнять -2 у hero_id (p.s. ох уж это api opendota...)
    except aiohttp.ClientError as e:
        logging.error(
            "Ошибка при запросе к API (get_name_hero_from_match): %e", e, exc_info=True
        )
        return []
    except (KeyError, TypeError) as e:
        logging.error("Ошибка при обработке данных (get_name_hero_from_match): %e", e, exc_info=True)
        return []
    except Exception as e:
        logging.error("Неизвестная ошибка (get_name_hero_from_match): %e", e, exc_info=True)
        return []
