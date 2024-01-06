import datetime
import logging
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import matplotlib.pyplot as plt
import io
from mood_bot.exceptions import CrontabNotDefined
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

    tg_user.crontab = cron
    tg_user.task = task
    tg_user.save()


def save_mood_service(user_id, callback_data):
    logging.info(f"Saving mood for user {user_id}")

    value, date_string = callback_data.split("_")
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")

    Mood.objects.create(tg_user_id=user_id, value=value, date=date)

    return value, date


def off_messages_service(user_id):
    tg_user = TgUser.objects.get(id=user_id)

    if tg_user.task is not None:
        tg_user.crontab = tg_user.task.crontab
        tg_user.task.delete()
        tg_user.task = None
        tg_user.save()


def on_messages_service(user_id):
    tg_user = TgUser.objects.get(id=user_id)

    try:
        task = PeriodicTask.objects.get(name=str(tg_user.id))

        if tg_user.crontab is None:
            tg_user.crontab = task.crontab

    except PeriodicTask.DoesNotExist:
        if tg_user.crontab is None:
            raise CrontabNotDefined

        task = PeriodicTask(
            name=str(tg_user.id),
            task="mood_bot.celery.ask_about_mood",
            args=f"[{str(tg_user.id)}]",
            crontab=tg_user.crontab,
        )
        task.save()

    tg_user.task = task
    tg_user.save()


def plot_service(user_id, date_start=None, date_end=None):
    tg_user = TgUser.objects.get(id=user_id)

    mood_records_filterset = Mood.objects.filter(tg_user=tg_user)

    if date_start is not None:
        mood_records_filterset = mood_records_filterset.filter(date__gte=date_start)

    if date_end is not None:
        mood_records_filterset = mood_records_filterset.filter(date__lte=date_end)

    mood_records = list(mood_records_filterset.values_list("date", "value"))

    dates = list(map(lambda elem: elem[0], mood_records))
    moods = list(map(lambda elem: elem[1], mood_records))

    plt.clf()

    plt.plot(dates, moods)

    plt.xlabel("Time")
    plt.ylabel("Mood")

    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)

    return buf
