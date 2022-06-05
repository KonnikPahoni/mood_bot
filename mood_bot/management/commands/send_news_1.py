import logging

from django.core.management.base import BaseCommand
from main import updater, remove_keyboard_markup
from mood_bot.models import TgUser
from mood_bot.services import plot_service


class Command(BaseCommand):
    help = "Send graph updates."

    UPDATE_TEXT_1 = (
        "Привет! Мной никто, кроме @KonnikPahoni, не пользуется, но я все равно решил разослать это сообщение "
        "той паре человек, которая меня попробовала. \n\nВо-первых, спасибо тебе! Во-вторых, держи свой "
        "график настроения."
    )

    UPDATE_TEXT_2 = (
        "Я полезен не только тем, что сохраняю эту информацию. Я также полезен тем, кто заставляю тебя "
        "рефлексировать о своем состоянии каждый день. Ведь как ты знаешь, в осознанности — сила 🕉. \n\n"
        "Чиллового воскресенья, друг. "
    )

    def handle(self, *args, **options):

        for tg_user in TgUser.objects.all():
            try:
                updater.bot.send_message(
                    chat_id=tg_user.id,
                    text=self.UPDATE_TEXT_1,
                    reply_markup=remove_keyboard_markup,
                )

                _plot = plot_service(tg_user.id)
                updater.bot.send_photo(
                    tg_user.id,
                    _plot,
                    reply_markup=remove_keyboard_markup,
                    caption="This one includes all your mood records in the database. Use /plot command to "
                    "see only records for the last 180 days.",
                )

                updater.bot.send_message(
                    chat_id=tg_user.id,
                    text=self.UPDATE_TEXT_2,
                    reply_markup=remove_keyboard_markup,
                )
            except Exception as e:
                logging.error(
                    f"Could not send a message for user {tg_user.id}: {str(e)}"
                )

        self.stdout.write("Update sent out.")
