import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
lazy from telethon.tl.types import User

SESSION_NAME = str(Path(__file__).with_name("telegram"))


def parse_entity(value: str) -> str | int:
    return int(value) if value.lstrip("-").isdigit() else value


def display_name(user: User) -> str:
    return " ".join(part for part in (user.first_name, user.last_name) if part) or "-"


async def print_participants(client: TelegramClient, chat: str | int) -> None:
    print(f"{'ID':<14} {'Username':<32} Name")
    async for user in client.iter_participants(chat):
        username = f"@{user.username}" if user.username else "-"
        print(f"{user.id:<14} {username:<32} {display_name(user)}")


async def send_message(client: TelegramClient, target: str | int, text: str) -> None:
    message = await client.send_message(target, text)
    print(f"Message {message.id} sent to {target}.")


async def run(args: argparse.Namespace, api_id: int, api_hash: str) -> None:
    async with TelegramClient(SESSION_NAME, api_id, api_hash) as client:
        if args.command == "participants":
            await print_participants(client, args.chat)
        else:
            await send_message(client, args.target, args.text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Telegram client built with Telethon.")
    commands = parser.add_subparsers(dest="command", required=True)

    participants = commands.add_parser("participants", help="list users of a chat or channel")
    participants.add_argument("chat", type=parse_entity, help="username, invite link or ID")

    send = commands.add_parser("send", help="send a message to a contact, chat or channel")
    send.add_argument(
        "target", type=parse_entity, help="username, phone number with + (+380...), ID or 'me' for Saved Messages"
    )
    send.add_argument("text", help="message text")

    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    api_id, api_hash = os.getenv("TELEGRAM_API_ID"), os.getenv("TELEGRAM_API_HASH")
    if not api_id or not api_id.isdigit() or not api_hash:
        sys.exit("Set TELEGRAM_API_ID (a number) and TELEGRAM_API_HASH in .env, get them at https://my.telegram.org")
    asyncio.run(run(args, int(api_id), api_hash))


if __name__ == "__main__":
    main()
