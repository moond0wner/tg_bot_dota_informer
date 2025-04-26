import json
import logging

from dataclasses import asdict, dataclass
from typing import Optional

import aiohttp

from fluentogram import TranslatorRunner

from ..parsers.account_info import (
    get_rank_account,
    get_info_about_profile,
    get_info_about_wl,
    get_winrate_last_twenty_matches,
)
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


async def get_info_about_players_of_match(
    match_id: int, locale: TranslatorRunner
) -> str:
    """Возвращает информацию о каждом игроке из заданного матча."""

    url = f"https://api.opendota.com/api/matches/{match_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    player_info_list = []
    players = data.get("players", [])

    for player in players:
        player_info = PlayerMatchInfo(
            account_id=player.get("account_id"),
            name=player.get("personaname"),
            team=locale.radiant() if player.get("IsRadiant", False) else locale.dire(),
            rank=await get_rank_account(
                account_id=player.get("account_id"), locale=locale
            ),
            lvl=player.get("level", "N/A"),
            networth=player.get("net_worth"),
            kda=f"{player.get('kills', 0)} | {player.get('deaths', 0)} | {player.get('assists', 0)}",
            aghanim_scepter=player.get("aghanims_scepter", 0),
            aghanim_shard=player.get("aghanims_shard", 0),
            hero_damage=player.get("hero_damage"),
        )

        benchmarks = player.get("benchmarks")

        if benchmarks:
            player_info.gold_per_min = benchmarks.get("gold_per_min", {}).get("raw")
            player_info.hero_damage_per_min = benchmarks.get(
                "hero_damage_per_min", {}
            ).get("raw")
            player_info.hero_healing_per_min = benchmarks.get(
                "hero_healing_per_min", {}
            ).get("raw")
            player_info.kills_per_min = benchmarks.get("kills_per_min", {}).get("raw")
            player_info.last_hits_per_min = benchmarks.get("last_hits_per_min", {}).get(
                "raw"
            )
            player_info.tower_damage = benchmarks.get("tower_damage", {}).get("raw")
        else:
            player_info.gold_per_min = None
            player_info.hero_damage_per_min = None
            player_info.hero_healing_per_min = None
            player_info.kills_per_min = None
            player_info.last_hits_per_min = None
            player_info.tower_damage = None

        player_info_list.append(player_info)

    return json.dumps([asdict(player) for player in player_info_list], indent=4)


async def get_info_about_account(
    account_id: int, locale: TranslatorRunner
) -> AccountInfo:
    """Возвращает полную информацию о профиле игрока."""

    try:
        player_data = await get_info_about_profile(account_id)
        wl_data = await get_info_about_wl(account_id)
        last_wl_data = await get_winrate_last_twenty_matches(account_id)
        last_match_info = await get_last_match_info(account_id, locale)
        rank = await get_rank_account(account_id, locale)

        if player_data is None or wl_data is None:
            return None

        try:
            total_winrate = round(
                wl_data["win"] / (wl_data["win"] + wl_data["lose"]) * 100, 2
            )
        except ZeroDivisionError:
            total_winrate = 0

        try:
            winrate_last_20_matches = round(
                last_wl_data["win"]
                / (last_wl_data["win"] + last_wl_data["lose"])
                * 100,
                2,
            )
        except ZeroDivisionError:
            winrate_last_20_matches = 0

        total_matches = wl_data["win"] + wl_data["lose"]
        if last_match_info:
            last_match = (
                f'\n{locale.kda()} `{last_match_info[1]["kills"]}` \\| '
                f'`{last_match_info[1]["deaths"]}` \\| '
                f'`{last_match_info[1]["assists"]}`\n'
                f"{locale.win()} `{last_match_info[-1]}`\n"
                f"{locale.match_id()} `{last_match_info[0]}`\n"
            )
        else:
            last_match = locale.unknown()

        account_info = AccountInfo()

        profile = player_data.get("profile", {})

        account_info.name = profile.get("personaname")
        account_info.rank = rank
        account_info.wins = wl_data.get("win")
        account_info.losses = wl_data.get("lose")
        account_info.total_matches = total_matches
        account_info.total_winrate = f"{total_winrate:.2f}"
        account_info.winrate_last_20_matches = f"{winrate_last_20_matches:.2f}"
        account_info.last_match = last_match
        account_info.avatar = profile.get("avatarfull")
        account_info.profile_url = profile.get("profileurl")
        account_info.account_id = account_id
        account_info.steam_id = profile.get("steamid")
        account_info.location = profile.get("loccountrycode")
        account_info.has_dplus_now = profile.get("is_subscriber")
        return account_info
    except Exception as e:
        logging.error(f"Возникла ошибка: {e}")
        return None
