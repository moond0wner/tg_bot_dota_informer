"""Parsing info about match"""

import logging
import json
from dataclasses import dataclass, asdict

import aiohttp
from typing import Dict, List, Optional, Union

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
    match_id_value = data.get("match_id", "N/A")
    players = data.get("players", [])
    abandoned_count = sum(player.get("abandons", 0) for player in players)

    win_text = locale.radiant() if radiant_win else locale.dire()
    quantity_players_text = human_players
    abandoned_text = abandoned_count
    id_match_text = match_id_value

    return {
        "win": win_text,
        "quantity_players": quantity_players_text,
        "abandoned": abandoned_text,
        "id_match": id_match_text,
        "num_players": human_players,
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
        return [
            str(match_data["match_id"]),
            {
                "kills": str(match_data["kills"]),
                "deaths": str(match_data["deaths"]),
                "assists": str(match_data["assists"]),
            },
            locale.radiant() if match_data["radiant_win"] else locale.dire(),
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
