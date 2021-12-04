# Mood bot

This bot is created to help monitor individual mood. Lean and mean

## Deployment

### Install Docker and Docker Compose

### Populate .env file

```
cp .env.dist .env
```

### Build and run containers

```
docker-compose build && docker-compose up
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