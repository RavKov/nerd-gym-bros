#!/usr/bin/env bash
set -euo pipefail

cd /app/gymProj

python manage.py migrate --noinput

if [[ "${DJANGO_COLLECTSTATIC:-true}" == "true" ]]; then
  python manage.py collectstatic --noinput
fi

if [[ "${DJANGO_ENV:-development}" == "production" ]]; then
  exec gunicorn gymProj.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-3}" \
    --threads "${GUNICORN_THREADS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-60}"
fi

python manage.py runserver 0.0.0.0:${PORT:-8000} &

if [[ -n "${STRIPE_API_KEY:-}" && "${DJANGO_ENV:-development}" != "production" ]]; then
  if [[ -x "/root/.stripe/bin/stripe" ]]; then
    /root/.stripe/bin/stripe listen --api-key "$STRIPE_API_KEY" --forward-to "http://127.0.0.1:${PORT:-8000}/api/stripe_webhook/" &
  elif command -v stripe >/dev/null 2>&1; then
    stripe listen --api-key "$STRIPE_API_KEY" --forward-to "http://127.0.0.1:${PORT:-8000}/api/stripe_webhook/" &
  elif [[ -x "/root/.local/bin/stripe" ]]; then
    /root/.local/bin/stripe listen --api-key "$STRIPE_API_KEY" --forward-to "http://127.0.0.1:${PORT:-8000}/api/stripe_webhook/" &
  else
    echo "Stripe CLI not found at /root/.stripe/bin/stripe; stripe listen will not start."
  fi
elif [[ -z "${STRIPE_API_KEY:-}" ]]; then
  echo "STRIPE_API_KEY not set; stripe listen will not start."
else
  echo "Production mode detected; stripe listen will not start."
fi

wait -n
