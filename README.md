<p align="center">
      <img src="https://i.ibb.co/wZBkph7k/418030aec1eab430b66c42040b6e2234.jpg" alt="Project Logo Url" width="300">
</p>

<p align="center">
   <img src="https://img.shields.io/badge/python-_3.13-red" alt="Python Version">
   <img src="https://img.shields.io/badge/Version-_v1.0%20(Alpha)-blue"alt="Project Version">
   <img src="https://img.shields.io/badge/License-_MIT-green" alt="License">
</p>

## About

A Telegram bot that uses the OpenDota API to provide information about Dota 2. The functions of viewing accounts, match details, player statistics in matches, and searching for accounts by nickname are implemented.

## Documentation

### 1. Account Information

*   **Description:** Getting information about a Dota 2 account.
*   **How to get an Account ID:** In a Dota 2 player's profile (in the Dota 2 profile). Example: `123456789`.
*   **Interaction:**
    1.  Click the "Account Information by ID" button.
    2.  The bot will request the account ID.
    3.  Enter the account ID and send it to the bot.
    4.  The bot will provide: Name, link to Steam profile, rank, and other statistics.
    5.  If the account is hidden from OpenDota, the bot will inform you.
*   **Errors:** The bot will notify you if the account is not found or the ID is entered incorrectly.

### 2. Account Search by Nickname

*   **Description:** Search for a Dota 2 account by nickname.
*   **Interaction:**
    1.  Click the "Account search by nickname" button.
    2.  The bot will request a nickname.
    3.  Enter a nickname and send it to the bot.
    4.  The bot will provide: A list of accounts in the form of inline buttons found by nickname (account names and IDs).
    5.  Click on any player you find to view their information.
*   **Errors:** The bot will notify you if no accounts are found or the nickname contains invalid characters.

### 3. Match Information

*   **Description:** Getting detailed information about a Dota 2 match.
*   **How to get the Match ID:** In the history of Dota 2 matches. Example: `7123456789`.
*   **Interaction:**
    1.  Click the "Match Information" button.
    2.  The bot will request the match ID.
    3.  Enter the match ID and send it to the bot.
    4.  The bot will provide: Information about the participants, results, duration, and other statistics of the match.
*   **Errors:** The bot will notify you if the match is not found or the ID is entered incorrectly.

### 4. Language

*   **Description:** Changes the language spoken by the bot.
*   **Interaction:**
    1.  Click the "Language" button.
    2.  The bot will prompt you to choose the language Russian or English.
    3.  Select the suggested language and return to the main menu.
    

## Developers

- [moond0wner](https://github.com/moond0wner)

## License
Project tg_bot_dota_informer is distributed under the [MIT license](https://opensource.org/license/MIT).