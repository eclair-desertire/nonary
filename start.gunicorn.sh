#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

mkdir -p static
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

echo "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(phone_number='${DJANGO_SUPERUSER_EMAIL}').exists():
    user = User.objects.create_superuser(
        '${DJANGO_SUPERUSER_EMAIL}',
        '${DJANGO_SUPERUSER_PASSWORD}'
    )
" | python manage.py shell || /bin/true

gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS}
