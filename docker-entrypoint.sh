#!/usr/bin/env bash
set -euo pipefail

cd /app/gymProj

python manage.py migrate --noinput

python manage.py runserver 0.0.0.0:8000 &

if [[ -n "${STRIPE_API_KEY:-}" ]]; then
  if [[ -x "/root/.stripe/bin/stripe" ]]; then
    /root/.stripe/bin/stripe listen --api-key "$STRIPE_API_KEY" --forward-to http://127.0.0.1:8000/api/stripe_webhook/ &
  elif command -v stripe >/dev/null 2>&1; then
    stripe listen --api-key "$STRIPE_API_KEY" --forward-to http://127.0.0.1:8000/api/stripe_webhook/ &
  elif [[ -x "/root/.local/bin/stripe" ]]; then
    /root/.local/bin/stripe listen --api-key "$STRIPE_API_KEY" --forward-to http://127.0.0.1:8000/api/stripe_webhook/ &
  else
    echo "Stripe CLI not found at /root/.stripe/bin/stripe; stripe listen will not start."
  fi
else
  echo "STRIPE_API_KEY not set; stripe listen will not start."
fi

wait -n
