from io import BytesIO

import django

django.setup()

import datetime
from mood_bot.constants import MOOD_QUESTION_TEXT
from mood_bot.exceptions import CrontabNotDefined
import telegram
import logging
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from PIL import Image
from mood_bot.services import (
    setup_user_service,
    set_ask_time_service,
    save_mood_service,
    off_messages_service,
    on_messages_service,
    plot_service,
)
from mood_bot.settings import TELEGRAM_TOKEN


def get_button(_mood):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    callback_data = f"{_mood}_{today_str}"

    return telegram.InlineKeyboardButton(text=str(_mood), callback_data=callback_data)


ASK_TIME = 1
remove_keyboard_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)


def get_moods_markup():
    return telegram.InlineKeyboardMarkup(
        [
            [
                get_button(0.5),
                get_button(1),
                get_button(1.5),
                get_button(2),
                get_button(2.5),
            ],
            [
                get_button(3),
                get_button(3.5),
                get_button(4),
                get_button(4.5),
                get_button(5),
            ],
            [
                get_button(5.5),
                get_button(6),
                get_button(6.5),
                get_button(7),
                get_button(7.5),
            ],
            [
                get_button(8),
                get_button(8.5),
                get_button(9),
                get_button(9.5),
                get_button(10),
            ],
        ]
    )


def start(update: Update, context: CallbackContext) -> int:
    setup_user_service(update.message.from_user)

    update.message.reply_text(
        "Hi! Please, send me the time you want me to ask you about your mood. We use UTC timezone. Example: 21:30",
        reply_markup=remove_keyboard_markup,
        reply_to_message_id=update.message.message_id,
    )

    return ASK_TIME


def off(update: Update, context: CallbackContext):
    off_messages_service(update.message.from_user.id)

    update.message.reply_text(
        "😳 No problem. I will not send you a single message, man.",
        reply_markup=remove_keyboard_markup,
        reply_to_message_id=update.message.message_id,
    )


def on(update: Update, context: CallbackContext):
    try:
        on_messages_service(update.message.from_user.id)
    except CrontabNotDefined:
        update.message.reply_text(
            "Crontab is not defined. Please, use /start command to define your crontab.",
            reply_markup=remove_keyboard_markup,
            reply_to_message_id=update.message.message_id,
        )

        return

    update.message.reply_text(
        "😃 Yeah! Talk to you soon!",
        reply_markup=remove_keyboard_markup,
        reply_to_message_id=update.message.message_id,
    )


def mood(update: Update, context: CallbackContext):
    update.message.reply_text(
        MOOD_QUESTION_TEXT,
        reply_markup=get_moods_markup(),
        reply_to_message_id=update.message.message_id,
    )


def set_ask_time(update: Update, context: CallbackContext) -> int:
    ask_time = update.message.text

    try:
        set_ask_time_service(update.message.from_user.id, ask_time)
    except ValueError:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Invalid format. Please, try again. Example: 21:30.",
            reply_markup=remove_keyboard_markup,
            reply_to_message_id=update.message.message_id,
        )

        return ASK_TIME

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"👍🏼 Accepted. You will be receiving messages at {ask_time} every day (UTC time).",
        reply_markup=remove_keyboard_markup,
        reply_to_message_id=update.message.message_id,
    )

    return ConversationHandler.END


def callback(update: Update, context: CallbackContext):
    callback_message = update.callback_query.message
    logging.info(update)
    value, date = save_mood_service(
        update.callback_query.message.chat.id, update.callback_query.data
    )

    date_str = date.strftime("%-d %B")

    context.bot.edit_message_text(
        chat_id=callback_message.chat_id,
        message_id=callback_message.message_id,
        text=f"☺ Thank you! Your mood ({value}) is saved to the database ({date_str}).",
        reply_markup=None,
    )


def plot(update: Update, context: CallbackContext):
    date_start = datetime.datetime.now() - datetime.timedelta(days=180)
    _plot = plot_service(update.message.from_user.id, date_start, None)

    context.bot.send_photo(
        update.effective_chat.id,
        _plot,
        reply_markup=remove_keyboard_markup,
        reply_to_message_id=update.message.message_id,
        caption="Here is your graph! Only mood records for the last 180 days are shown. Use the /plot_all command to see all records.",
    )


def plot_all(update: Update, context: CallbackContext):
    _plot = plot_service(update.message.from_user.id)

    context.bot.send_photo(
        update.effective_chat.id,
        _plot,
        reply_markup=remove_keyboard_markup,
        reply_to_message_id=update.message.message_id,
        caption="Here is your graph! It includes all your mood records in the database. Use /plot command to see only records for the last 180 days.",
    )


updater = Updater(TELEGRAM_TOKEN)
dispatcher = updater.dispatcher


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    setup_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_TIME: [
                MessageHandler(Filters.text, set_ask_time),
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    mood_handler = CommandHandler("mood", mood)
    on_handler = CommandHandler("on", on)
    off_handler = CommandHandler("off", off)
    button_handler = CallbackQueryHandler(callback)
    plot_handler = CommandHandler("plot", plot)
    plot_all_handler = CommandHandler("plot_all", plot_all)

    dispatcher.add_handler(setup_handler)
    dispatcher.add_handler(mood_handler)
    dispatcher.add_handler(on_handler)
    dispatcher.add_handler(off_handler)
    dispatcher.add_handler(button_handler)
    dispatcher.add_handler(plot_handler)
    dispatcher.add_handler(plot_all_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
