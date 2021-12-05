from django.db import models


class TgUser(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    language_code = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    ask_time = models.TimeField(null=True, blank=True)


class Mood(models.Model):
    id = models.AutoField(primary_key=True)
    tg_user = models.ForeignKey("TgUser", on_delete=models.CASCADE)
    value = models.SmallIntegerField()
    added = models.DateTimeField(auto_now_add=True)
