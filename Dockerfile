FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates unzip gnupg libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Stripe CLI (apt repo)
RUN curl -s https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public \
    | gpg --dearmor \
    | tee /usr/share/keyrings/stripe.gpg > /dev/null \
    && echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main" \
    | tee /etc/apt/sources.list.d/stripe.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends stripe \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/

ENV PATH="/root/.local/bin:$PATH"

RUN uv pip install --system --upgrade pip \
    && uv pip install --system .

COPY . /app/

EXPOSE 8000

RUN chmod +x /app/docker-entrypoint.sh

CMD ["/app/docker-entrypoint.sh"]
