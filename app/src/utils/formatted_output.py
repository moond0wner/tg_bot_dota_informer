from typing import Dict, List

from fluentogram import TranslatorRunner

from ..parsers.info import AccountInfo

GAME_MODE = {
    0: "Unknown",
    1: "All Pick",
    2: "Captains Mode",
    3: "Random Draft",
    4: "Single Draft",
    5: "All Random",
    13: "Limited Heroes",
    15: "Custom Game",
    16: "Captains Draft",
    18: "Ability Draft",
    20: "All Random Death Match",
    21: "1 vs 1 Mid",
    22: "All Draft",
    23: "Turbo",   
}


LOBBY_TYPE = {
    1: "Tournament",
    5: "Team Ranked Matchmaking",
    6: "Solo Ranked Matchmaking",
    7: "Ranked",
    8: "1 vs 1 Mid",
    9: "Battle Cup",
    0: "Normal"
}

def format_player_info_in_match(
    players: List[Dict[str, any]], player_index: int, locale: TranslatorRunner
) -> str:

    if player_index < 0 or player_index >= len(players):
        return locale.player_was_not_found()

    player = players[player_index]
    answer = (
        f"{locale.name()} `{player['name']}`\n"
        f"{locale.hero()} `{player['hero']}`\n"
        f"{locale.account_id()} `{player['account_id']}`\n"
        f"{locale.team()} `{player['team']}`\n"
        f"{locale.rank()} `{player['rank']}`\n"
        f"{locale.kda()} `{player['kda']}`\n"
        f"{locale.lvl()} `{player['lvl']}`\n"
        f"{locale.aghanim_scepter()} {locale.yes_emoji() if player['aghanim_scepter'] > 0 else locale.no_emoji()}\n"
        f"{locale.aghanim_shard()} {locale.yes_emoji() if player['aghanim_shard'] > 0 else locale.no_emoji()}\n"
        f"{locale.networth()} `{player['networth']}`\n"
        f"{locale.gold_per_min()} `{player['gold_per_min']:.0f}`\n"
        f"{locale.enemy_damage()} `{player['hero_damage']:.0f}`\n"
        f"{locale.enemy_damage_per_min()} `{player['hero_damage_per_min']:.0f}`\n"
        f"{locale.last_hits_per_min()} `{player['last_hits_per_min']:.0f}`\n"
        f"{locale.hero_healing_per_min()} `{player['hero_healing_per_min']:.0f}`\n"
        f"{locale.tower_damage()} `{player['tower_damage']}`"
    )

    if answer.count("None") > 0:
        answer += f"\n\n{locale.probably_account_hidden()}"

    return answer


def format_button_result(result: str):
    answer = dict()
    for player in result:
        answer[f'account_id: {player["account_id"]}'] = (
            f'{player["personaname"]} — {player["account_id"]}'
        )

    return answer


# nick - 123456789


def format_account_info(account: AccountInfo, locale: TranslatorRunner):
    result = (
        f"*{account.name}* \\| `{locale.wr(winrate=account.total_winrate)}%`\n\n"
        f"{locale.rank()} `{account.rank}`\n"
        f"{locale.number_matches()} `{account.total_matches}` \\| 🔺`{account.wins} `🔻`{account.losses}`\n"
        f"{locale.wr_last_20_matches()} `{account.winrate_last_20_matches}%`\n"
        f"{locale.has_dplus_now()} {locale.yes_emoji() if account.has_dplus_now else locale.no_emoji()}\n"
        f"{locale.country()} `{account.location}`\n"
        f"{locale.account_id()} `{account.account_id}`\n"
        f"{locale.steam_id()} `{account.steam_id}`\n\n"
        f"{locale.last_match()} {account.last_match}\n"
        f"{locale.friends()}\n{account.peers}\n"    
    )
    
    if result.count("None") > 0:
        result += f"\n{locale.probably_account_hidden()}"

    return result


def format_general_match_info(match: Dict, locale: TranslatorRunner):
    result = (
        f'{locale.game_mode()} `{GAME_MODE.get(match["game_mode"], locale.unknown())}`\n'
        f'{locale.lobby_type()} `{LOBBY_TYPE.get(match["lobby_type"], locale.unknown())}`\n'
        f'{locale.win()} `{match["win"]}`\n'
        f'{locale.number_players()} `{match["quantity_players"]}`\n'
        f'{locale.abandoned()} `{match["abandoned"]}`\n'
        f'{locale.match_id()} `{match["id_match"]}`\n'
    )
    return result
