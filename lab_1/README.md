# Tasks for Lab 1

Working with the HTTP protocol, requests and public APIs.

## Task 1.
Get the exchange rates from the NBU website for the previous week using Postman. API usage example: https://bank.gov.ua/admin_uploads/article/Instr_API_KURS_VAL_data.pdf

## Task 2.
Get the exchange rates from the NBU website for the previous week using the Python `requests` library.

## Task 3.
Plot the exchange rate changes using the `matplotlib` library.

## Task 4.
Using Python and the `telethon` library (https://docs.telethon.dev/en/stable/index.html), perform the following actions in Telegram:
- get the list of users of any chat or channel;
- send a message to a contact directly or publish a message in a chat or channel.

## Task 5.
Based on the Telegram Bot API and the example (https://gitlab.com/Athamaxy/telegram-bot-tutorial/-/blob/main/TutorialBot.py), create a bot that supports the `menu`, `whisper` and `scream` commands.

## Solutions

| Task | File                                                       | What it does                                          |
|------|------------------------------------------------------------|-------------------------------------------------------|
| 1    | [nbu.postman_collection.json](nbu.postman_collection.json) | Postman request for NBU rates over the last 7 days    |
| 2    | [rates.py](rates.py)                                       | Prints NBU rates for the last 7 days                  |
| 3    | [chart.py](chart.py)                                       | Plots the rates, one chart per currency               |
| 4    | [telegram_client.py](telegram_client.py)                   | Lists chat members and sends messages as your account |
| 5    | [bot.py](bot.py)                                           | Telegram bot with `/menu`, `/scream` and `/whisper`   |

## How to run

Run every command from the repository root. Install the dependencies once and create `.env` from the template:

```bash
uv sync
cp .env.example .env
```

### Task 1 — Postman
Import `lab_1/nbu.postman_collection.json` in Postman (**Import** → choose the file) and press **Send**. A pre-request script fills in the last 7 days. Change the `currency` collection variable (for example to `eur`) to get another currency.

### Task 2 — rates with `requests`
```bash
uv run python -m lab_1.rates
uv run python -m lab_1.rates USD EUR GBP
```

### Task 3 — chart
```bash
uv run python -m lab_1.chart
uv run python -m lab_1.chart USD EUR GBP
```

### Task 4 — Telethon client
Needs `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` in `.env`. Get them at https://my.telegram.org → **API development tools**. The first run asks for your phone number and login code and saves the session to `lab_1/telegram.session`.

```bash
uv run python -m lab_1.telegram_client participants @group_username
uv run python -m lab_1.telegram_client send @username "Hello from Telethon"
uv run python -m lab_1.telegram_client send me "Saved for later"
```

Members of a channel are visible only to its admins; members of a group are visible to everyone in it.

### Task 5 — bot
My running instance is [@network_labs_bot](https://t.me/network_labs_bot); it answers while `bot.py` is running.

To run your own bot, create one with [@BotFather](https://t.me/BotFather) (`/newbot`) and put the token it sends into `.env` as `TELEGRAM_BOT_TOKEN`.

```bash
uv run python -m lab_1.bot
```

The bot answers only while this command runs; it prints `Application started` and logs every message it gets. Stop it with Ctrl+C. Open the bot in Telegram (`t.me/<bot username>`) and press **Start**.

To get the **Menu** button with the commands next to the message field, send `/setcommands` to BotFather once, pick the bot and paste:

```text
start - Start the bot
help - Show the available commands
menu - Show a menu with inline buttons
scream - Repeat your messages in upper case
whisper - Repeat your messages unchanged
stop - Stop repeating your messages until /start
```

| Command    | Action                                                            |
|------------|-------------------------------------------------------------------|
| `/start`   | Lists the commands and resumes repeating after `/stop`.           |
| `/help`    | Lists the commands.                                               |
| `/menu`    | Sends a two-page menu: **Next** and **Back** switch the pages.    |
| `/scream`  | Repeats every text message in upper case (only in this chat).     |
| `/whisper` | Repeats messages unchanged again.                                 |
| `/stop`    | Stops repeating messages in this chat until `/start`.             |
| any text   | Repeated back to you.                                             |
