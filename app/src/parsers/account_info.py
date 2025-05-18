"""Parsing info about account"""

import logging
from typing import Optional, Dict

import aiohttp
from fluentogram import TranslatorRunner
from bs4 import BeautifulSoup


async def get_info_about_profile(account_id: int) -> Optional[Dict]:
    """Возвращает JSON с данными о профиле игрока."""

    url = f"https://api.opendota.com/api/players/{account_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
        return data
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при запросе профиля: {e}")
        return None
    except Exception as e:
        logging.error(f"Неизвестная ошибка при запросе профиля: {e}")
        return None
    
async def get_info_about_peers(account_id: int):
    """Возвращает отсортированный список с данными о друзьях пользователя из доты."""

    url = f"https://api.opendota.com/api/players/{account_id}/peers"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
        if not data:
            return None
        
        players = []
        for i in data:
            players.append({'name': i['personaname'], 'account_id': i['account_id'], 'games': int(i["games"])})

        sorted_players = sorted(players, key=lambda item: item['games'], reverse=True)  # Сортировка по количеству игр
        return sorted_players
    except aiohttp.ClientError as e:
        logging.error("Ошибка клиента в get_info_about_peers: %s", e, exc_info=True)
        return None
    except Exception as e:
        logging.error("Неизвестная ошибка при запросе профиля: %s", e, exc_info=True)
        return None


async def get_info_about_heroes(account_id: int) -> Optional[Dict]:
    """Возвращает JSON с данными о героях игрока."""

    url = f"https://api.opendota.com/api/players/{account_id}/wardmap"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
        return data
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при запросе героев: {e}")
        return None
    except Exception as e:
        logging.error(f"Неизвестная ошибка при запросе героев: {e}")
        return None


async def get_info_about_wl(account_id: int) -> Optional[Dict]:
    """Возвращает JSON с данными о кол-ве побед и поражений игрока."""

    wl_url = f"https://api.opendota.com/api/players/{account_id}/wl"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(wl_url) as response:
                response.raise_for_status()
                data = await response.json()
        return data
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при запросе WL: {e}")
        return None
    except Exception as e:
        logging.error(f"Неизвестная ошибка при запросе WL: {e}")
        return None


async def get_winrate_last_twenty_matches(account_id: int) -> Optional[Dict]:
    """Возвращает JSON с данными о проценте побед игрока за 20 игр."""

    url = f"https://api.opendota.com/api/players/{account_id}/wl"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"limit": 20}) as response:
                response.raise_for_status()
                data = await response.json()
        return data
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при запросе winrate (20): {e}")
        return None
    except Exception as e:
        logging.error(f"Неизвестная ошибка при запросе winrate (20): {e}")
        return None


async def get_rank_account(account_id: int, locale: TranslatorRunner) -> str:
    """Возвращает строчку с рангом игрока из DotaBuff"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0"
    }
    url = f"https://{locale.language()}.dotabuff.com/players/{account_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    rank_element = (soup.find("div", class_="rank-tier-wrapper")["title"].split(":")[1].strip())
                    if rank_element:
                        return rank_element
                    else:
                        return locale.unknown()
                else:
                    logging.error(f"Ошибка: {response.status}")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


async def search_account_by_nickname(name: str) -> Optional[Dict]:
    """Возвращает информацию о найденных аккаунтах по заданному никнейму."""
    url = "https://api.opendota.com/api/search"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"q": name}) as response:
                response.raise_for_status()
                data = await response.json()
        return data
    except aiohttp.ClientError as e:
        logging.error("Ошибка при запросе (search_account_by_nickname): %e", e, exc_info=True)
        return None
    except Exception as e:
        logging.error("Неизвестная ошибка при запросе (search_account_by_nickname): %e", e, exc_info=True)
        return None
