# Generated by Django 3.2.9 on 2021-12-05 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mood_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mood',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]