import logging
import os

import telegram
from celery import Celery
from mood_bot.constants import MOOD_QUESTION_TEXT

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mood_bot.settings")
# set the default Django settings module for the 'celery' program.
from main import updater, moods_markup

celery = Celery("mood_bot")


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    pass


@celery.task
def ask_about_mood(user_id):
    try:
        updater.bot.send_message(
            chat_id=user_id, text=MOOD_QUESTION_TEXT, reply_markup=moods_markup
        )
    except (telegram.error.Unauthorized, telegram.error.BadRequest) as e:
        logging.error(f"Error sending daily task to {str(user_id)}: {str(e)}")


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
celery.autodiscover_tasks()
