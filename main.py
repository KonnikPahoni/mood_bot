import datetime

import django

from mood_bot.constants import MOOD_QUESTION_TEXT

django.setup()

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

from mood_bot.services import (
    setup_user_service,
    set_ask_time_service,
    save_mood_service,
)
from mood_bot.settings import TELEGRAM_TOKEN


def get_button(_mood):
    return telegram.InlineKeyboardButton(text=str(_mood), callback_data=_mood)


ASK_TIME = 1
remove_keyboard_markup = telegram.ReplyKeyboardRemove(remove_keyboard=True)
moods_markup = telegram.InlineKeyboardMarkup(
    [
        [get_button(1), get_button(2), get_button(3), get_button(4), get_button(5)],
        [get_button(6), get_button(7), get_button(8), get_button(9), get_button(10)],
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


def mood(update: Update, context: CallbackContext):
    update.message.reply_text(
        MOOD_QUESTION_TEXT,
        reply_markup=moods_markup,
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
    save_mood_service(update.callback_query.message.chat.id, update.callback_query.data)

    today_str = datetime.datetime.now().strftime("%d %B")

    context.bot.edit_message_text(
        chat_id=callback_message.chat_id,
        message_id=callback_message.message_id,
        text=f"☺ Thank you! Your mood ({update.callback_query.data}) is saved to the database ({today_str}).",
        reply_markup=None,
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
    button_handler = CallbackQueryHandler(callback)

    dispatcher.add_handler(setup_handler)
    dispatcher.add_handler(mood_handler)
    dispatcher.add_handler(button_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
