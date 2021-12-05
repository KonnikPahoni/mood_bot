import datetime
import logging
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from mood_bot.models import TgUser, Mood


def setup_user_service(user):
    try:
        tg_user = TgUser.objects.get(id=user.id)
        tg_user.first_name = user.first_name
        tg_user.language_code = user.language_code
        tg_user.last_name = user.last_name
        tg_user.username = user.username

        tg_user.save()
    except TgUser.DoesNotExist:
        logging.info(f"Creating new user with id={user['id']}")

        TgUser.objects.create(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
        )


def set_ask_time_service(user_id, ask_time):
    tg_user = TgUser.objects.get(id=user_id)
    time_object = datetime.datetime.strptime(ask_time, "%H:%M").time()
    tg_user.ask_time = time_object
    tg_user.save()

    cron = CrontabSchedule(hour=time_object.hour, minute=time_object.minute)
    cron.save()

    try:
        task = PeriodicTask.objects.get(name=str(tg_user.id))
        task.crontab = cron
    except PeriodicTask.DoesNotExist:
        task = PeriodicTask(
            name=str(tg_user.id),
            task="mood_bot.celery.ask_about_mood",
            args=f"[{str(tg_user.id)}]",
            crontab=cron,
        )

    task.save()


def save_mood_service(user_id, mood):
    logging.info(f"Saving mood for user {user_id}")
    Mood.objects.create(tg_user_id=user_id, value=mood)
