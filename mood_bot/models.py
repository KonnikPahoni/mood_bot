from django.db import models


class TgUser(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    language_code = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    ask_time = models.TimeField(null=True, blank=True)
    task = models.ForeignKey(
        "django_celery_beat.PeriodicTask",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user",
    )
    crontab = models.ForeignKey(
        "django_celery_beat.CrontabSchedule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user",
    )


class Mood(models.Model):
    id = models.AutoField(primary_key=True)
    tg_user = models.ForeignKey("TgUser", on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=3, decimal_places=1)
    date = models.DateField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
