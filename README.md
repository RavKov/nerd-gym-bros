# Nerd Gym Bros

![CI](https://github.com/RavKov/nerd-gym-bros/actions/workflows/ci.yml/badge.svg)

Backend oraz panel administracyjny do mojego projektu inżynierskiego, którym jest **Zintegrowany system zarządzania treningiem**.

Projekt stworzony z użyciem frameworka webowego Django.


## Konfiguracja środowiska

1. Skopiuj plik szablonu: `cp .env.example .env`
2. Uzupełnij wartości w `.env` (szczególnie klucze Stripe, jeśli testujesz płatności).
3. Domyślnie działa tryb **development** (`DJANGO_ENV=development`) — bez dodatkowej konfiguracji wystarczy do lokalnego Dockera.

| Zmienna | Opis |
|---------|------|
| `DJANGO_ENV` | `development` (domyślnie) lub `production` |
| `DJANGO_SECRET_KEY` | Klucz Django; **wymagany** w production |
| `DJANGO_ALLOWED_HOSTS` | Dozwolone hosty (po przecinku); **wymagane** w production |
| `CORS_ALLOWED_ORIGINS` | Originy dla aplikacji mobilnej; **wymagane** w production |
| `STRIPE_API_KEY` | Sekret Stripe (mapowany na `STRIPE_SECRET_KEY` w aplikacji) |
| `STRIPE_WEBHOOK_SECRET` | Sekret webhooka Stripe |

Więcej zmiennych (baza, HSTS, CSRF) — w pliku [.env.example](.env.example).


## Prezentacja wideo
Dla jasnego zrozumienia całości systemu, proszę zapoznać się z poniższą prezentacją:

https://www.youtube.com/watch?v=a2BepgsEpck


## Uruchomienie Zintegrowanego systemu zarządzania treningiem

### Uruchomienie nerd-gym-bros (Backendu i panelu administracyjnego)
 1. (Opcjonalnie) `cp .env.example .env` i uzupełnij Stripe — patrz sekcja [Konfiguracja środowiska](#konfiguracja-środowiska)
 2. Uruchom `docker compose up --build`
 3. Po pomyślnym uruchomieniu serwera Django oraz bazy PostgreSQL uruchom: `docker compose exec web bash -lc "/app/refresh_db.sh"` - migracje i wczytywanie danych z fixtures
 4. Dostęp do panelu administracyjnego w przeglądarce na adresie `127.0.0.1:8000`
 5. Domyślne dane logowania admina (tylko środowisko dev): Login: `admin` | Hasło: `admin`

### Uruchomienie nerd-gym-bros-mobile (aplikacji mobilnej)
 1. Wymagany emulator z Android Studio - ja użyłem Medium_Phone_API_36 (emulator version: 36.3.10-14472402)
 2. Eksport zmiennych (wybierz swoją lokalizację sdk):
 2.1. `export ANDROID_HOME=$HOME/Library/Android/sdk`
 2.2. `export PATH=$PATH:$ANDROID_HOME/emulator`
 2.3. `export PATH=$PATH:$ANDROID_HOME/platform-tools`
 3. Urucom `npm install`
 4. Uruchom `npx expo run:android`
 5. W razie problemów: https://docs.expo.dev/workflow/android-studio-emulator/
 6. Po pomyślnym uruchomieniu aplikacji należy zarejestrować się. Kod do weryfikacji utworzonego usera pojawi się w logach serwera django po pomyślnym utworzeniu konta.
 7. UWAGA! Na githubie nie dołączyłem .env z tokenami, więc proszę o kontakt w razie niedziałającej integracji z Stripe.
