"""Parsing info about account"""

import aiohttp
import logging
from dataclasses import dataclass

from typing import Optional, Dict

from fluentogram import TranslatorRunner

from ..parsers.match_info import get_last_match_info

@dataclass
class AccountInfo:
    account_id: Optional[int] = None
    steam_id: Optional[str] = None
    name: Optional[str] = None
    rank: Optional[str] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    total_matches: Optional[int] = None
    total_winrate: Optional[int] = None
    winrate_last_20_matches: Optional[int] = None
    last_match: Optional[str] = None
    avatar: Optional[str] = None
    profile_url: Optional[str] = None
    location: Optional[str] = None
    has_dplus_now: Optional[bool] = None


async def get_info_about_profile(account_id: int) -> Optional[Dict]:
    """Возвращает JSON с данными о профиле игрока."""

    url = f'https://api.opendota.com/api/players/{account_id}'
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


async def get_info_about_heroes(account_id: int) -> Optional[Dict]:
    """Возвращает JSON с данными о героях игрока."""

    url = f'https://api.opendota.com/api/players/{account_id}/wardmap'
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

    wl_url = f'https://api.opendota.com/api/players/{account_id}/wl'
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

    url = f'https://api.opendota.com/api/players/{account_id}/wl'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'limit': 20}) as response:
                response.raise_for_status()
                data = await response.json()
        return data
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при запросе winrate (20): {e}")
        return None
    except Exception as e:
        logging.error(f"Неизвестная ошибка при запросе winrate (20): {e}")
        return None

async def get_info_about_account(account_id: int,
                                 locale: TranslatorRunner) -> AccountInfo:
    """Возвращает полную информацию о профиле игрока."""

    try:
        player_data = await get_info_about_profile(account_id)
        wl_data = await get_info_about_wl(account_id)
        last_wl_data= await get_winrate_last_twenty_matches(account_id)
        last_match_info = await get_last_match_info(account_id, locale)

        if player_data is None or wl_data is None:
            return None

        try:
            total_winrate = wl_data['win'] / (wl_data['win'] + wl_data['lose']) * 100
        except:
            total_winrate = 0

        try:
            winrate_last_20_matches = last_wl_data['win'] / (last_wl_data['win'] + last_wl_data['lose']) * 100
        except:
            winrate_last_20_matches = 0

        total_matches = wl_data['win'] + wl_data['lose']
        if last_match_info:
            last_match = (f'\n{locale.kda()}`{last_match_info[1]["kills"]}` \\| '
                          f'`{last_match_info[1]["deaths"]}` \\| '
                          f'`{last_match_info[1]["assists"]}`\n'
                          f'{locale.win()} `{last_match_info[-1]}`\n'
                          f'{locale.match_id()} `{last_match_info[0]}`\n')
        else:
            last_match = locale.unknown()

        account_info = AccountInfo()

        profile = player_data.get('profile', {})

        account_info.name = profile.get('personaname')
        account_info.rank = player_data.get('rank_tier')
        account_info.wins = wl_data.get('win')
        account_info.losses = wl_data.get('lose')
        account_info.total_matches = total_matches
        account_info.total_winrate = f'{total_winrate:.2f}'
        account_info.winrate_last_20_matches = f'{winrate_last_20_matches:.2f}'
        account_info.last_match = last_match
        account_info.avatar = profile.get('avatarfull')
        account_info.profile_url = profile.get('profileurl')
        account_info.account_id = account_id
        account_info.steam_id = profile.get('steamid')
        account_info.location = profile.get('loccountrycode')
        account_info.has_dplus_now = profile.get('is_subscriber')
        return account_info
    except Exception as e:
        logging.error(f'Возникла ошибка: {e}')
        return None


async def search_account_by_nickname(name: str) -> Optional[Dict]:
    """Возвращает информацию о найденных аккаунтах по заданному никнейму"""
    url = f'https://api.opendota.com/api/search'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'q': name}) as response:
                response.raise_for_status()
                data = await response.json()
        return data
    except aiohttp.ClientError as e:
        logging.error(f"Ошибка при запросе: {e}")
        return None
    except Exception as e:
        logging.error(f"Неизвестная ошибка при запросе: {e}")
        return None