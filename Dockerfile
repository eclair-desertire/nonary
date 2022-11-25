FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y libpq-dev \
  && apt-get install -y libzbar-dev \
  && apt-get install -y apt-utils \
  && apt-get install -y gettext \
  && apt-get install -y python3-dev \
  && apt-get install -y libwebp-dev \
  && apt-get install -y cron \
  && apt-get install -y nano

# Updating pip to latest version
RUN pip install --upgrade pip

RUN pip install poetry

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN ls /app/

# Requirements are installed here to ensure they will be cached.
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY ./start.django.sh /start-django
COPY ./start.gunicorn.sh /start-gunicorn
RUN sed -i 's/\r$//g' /start-django && chmod +x /start-django
RUN sed -i 's/\r$//g' /start-gunicorn && chmod +x /start-gunicorn

ADD . /app/

# Add the cron job
RUN crontab -l | { cat; echo "0 0 * * * python /app/close_shift.py"; } | crontab -

# Run the command on container startup
CMD cron
