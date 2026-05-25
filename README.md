# Nerd Gym Bros

![CI](https://github.com/RavKov/nerd-gym-bros/actions/workflows/ci.yml/badge.svg)

Backend and staff/admin panel for the **Integrated Gym Training Management System** engineering thesis project. This repository contains the Django backend, REST API, reporting layer, and internal admin workflows used by the companion mobile app.

## Tech Stack

- Django 5 + Django REST Framework
- PostgreSQL
- SimpleJWT authentication
- Stripe subscriptions
- Docker Compose for local development
- `uv`, `ruff`, `pytest`, `pre-commit`

## Project Structure

- `gymProj/gymApp/` - core domain models and template-based staff/admin workflows
- `gymProj/gymApi/` - mobile-facing REST API
- `gymProj/gymReports/` - report generation (PDF, DOCX, XLSX)
- `docs/ARCHITECTURE.md` - high-level architecture and request flows

## Local Setup

1. Create local environment variables: `cp .env.example .env`
2. Start the application stack: `docker compose up --build`
3. Load migrations and seed data: `docker compose exec web bash -lc "/app/refresh_db.sh"`
4. Open the staff/admin interface at [http://127.0.0.1:8000](http://127.0.0.1:8000)

Development-only default admin credentials:

- Login: `admin`
- Password: `admin`

## Environment Configuration

The main environment variables are:

| Variable | Description |
| --- | --- |
| `DJANGO_ENV` | `development` (default) or `production` |
| `DJANGO_SECRET_KEY` | Django secret key; required in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames; required in production |
| `CORS_ALLOWED_ORIGINS` | Allowed mobile/web origins; required in production |
| `STRIPE_API_KEY` | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |

See `.env.example` for the full list, including database and security-related settings.

## API Documentation

The repository exposes generated OpenAPI docs:

- Schema: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
- Swagger UI: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

## Quality Checks

- Run tests: `uv run pytest`
- Run lint: `uv run ruff check .`
- Check formatting: `uv run ruff format --check .`
- Install hooks: `uv run pre-commit install`

## Architecture Notes

The backend currently follows a modular Django monolith approach:

- shared domain models in `gymApp`
- domain-split API views in `gymApi/views/`
- exports and reporting in `gymReports`
- JWT auth, throttling, and scoped access helpers for the mobile API

More detail is available in `docs/ARCHITECTURE.md`.

## Demo

Project walkthrough video:

[https://www.youtube.com/watch?v=a2BepgsEpck](https://www.youtube.com/watch?v=a2BepgsEpck)
