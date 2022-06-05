# Mood bot (v1.1)

This bot is created to help monitor your mood. Lean and mean.

## Deployment

### Install Docker and Docker Compose

### Populate .env file

```
cp .env.dist .env
```

### Build and run containers

```
docker-compose build && docker-compose up -d
```

## App updating

### Connect to the docker container

```
docker container exec -it mood_bot.app /bin/bash
```

### To apply migrations:

```
python3 manage.py migrate
```

### To purge the queue:

```
docker container exec -it mood_bot.celery celery -A celery purge -f
```

## Telegram bot commands

start - Set the time me when I should ask you about your mood daily
mood - Report your mood during the day additionally
off - Turn off crontab
on - Turn on crontab
plot - Plot mood for the last 180 days
plot_all - Plot mood for all records