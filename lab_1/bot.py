import logging
import os
import sys

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)

HELP = (
    "Send me any message and I will repeat it.\n\n"
    "/start - Start the bot\n"
    "/help - Show the available commands\n"
    "/menu - Show a menu with inline buttons\n"
    "/scream - Repeat your messages in upper case\n"
    "/whisper - Repeat your messages unchanged\n"
    "/stop - Stop repeating your messages until /start"
)
FIRST_MENU = "<b>Menu 1</b>\n\nA beautiful menu with a shiny inline button."
SECOND_MENU = "<b>Menu 2</b>\n\nA better menu with even more shiny inline buttons."

NEXT_BUTTON = "Next"
BACK_BUTTON = "Back"
TUTORIAL_BUTTON = "Tutorial"

FIRST_MENU_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton(NEXT_BUTTON, callback_data=NEXT_BUTTON)]])
SECOND_MENU_MARKUP = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
        [InlineKeyboardButton(TUTORIAL_BUTTON, url="https://core.telegram.org/bots/api")],
    ]
)
MENUS = {
    NEXT_BUTTON: (SECOND_MENU, SECOND_MENU_MARKUP),
    BACK_BUTTON: (FIRST_MENU, FIRST_MENU_MARKUP),
}


class EchoBot:
    def __init__(self) -> None:
        self.screaming_chats: set[int] = set()
        self.stopped_chats: set[int] = set()

    def build_application(self, token: str) -> Application:
        application = Application.builder().token(token).build()
        application.add_handlers(
            [
                CommandHandler("start", self.start),
                CommandHandler("help", self.show_help),
                CommandHandler("menu", self.menu),
                CommandHandler("scream", self.scream),
                CommandHandler("whisper", self.whisper),
                CommandHandler("stop", self.stop),
                CallbackQueryHandler(self.button_tap),
                MessageHandler(~filters.COMMAND, self.echo),
            ]
        )
        return application

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.message
        if message is None or message.chat_id in self.stopped_chats:
            return
        sender = message.from_user.first_name if message.from_user else "Unknown"
        logger.info("%s wrote %s", sender, message.text)

        if message.chat_id in self.screaming_chats and message.text:
            text = message.text.upper()
            # Formatting offsets only stay valid when upper case keeps the length (not for "ß" -> "SS").
            entities = message.entities if len(text) == len(message.text) else ()
            await context.bot.send_message(message.chat_id, text, entities=entities)
        else:
            await message.copy(message.chat_id)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat:
            self.stopped_chats.discard(update.effective_chat.id)
        await self.show_help(update, context)

    async def show_help(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message:
            await update.message.reply_text(HELP)

    async def scream(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat and update.message:
            self.screaming_chats.add(update.effective_chat.id)
            await update.message.reply_text("SCREAM MODE ON. SEND ME SOMETHING!")

    async def whisper(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat and update.message:
            self.screaming_chats.discard(update.effective_chat.id)
            await update.message.reply_text("whisper mode on, I will repeat messages as they are")

    async def stop(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat and update.message:
            self.stopped_chats.add(update.effective_chat.id)
            await update.message.reply_text("Stopped. I will not repeat your messages until you send /start.")

    async def menu(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message:
            await update.message.reply_text(FIRST_MENU, parse_mode=ParseMode.HTML, reply_markup=FIRST_MENU_MARKUP)

    async def button_tap(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if query is None or query.data is None:
            return
        text, markup = MENUS[query.data]
        await query.answer()
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)


def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        sys.exit("Set TELEGRAM_BOT_TOKEN in .env, get it from https://t.me/BotFather")

    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    EchoBot().build_application(token).run_polling()


if __name__ == "__main__":
    main()
