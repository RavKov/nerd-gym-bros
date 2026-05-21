cd gymProj

rm db.sqlite3
# rm gymApp/migrations/0*.py
# rm gymReports/migrations/0*.py

# python3 manage.py makemigrations
# cd ..
# cp ./0002_db_objects.py ./gymProj/gymApp/migrations/0002_db_objects.py
# cd gymProj
python3 manage.py migrate 
python3 manage.py loaddata dictionaries.json
python3 manage.py loaddata exercises.json
python3 manage.py loaddata workout_plans.json
python3 manage.py loaddata subscription_plans.json
python3 manage.py loaddata users.json
python3 manage.py loaddata client_profiles.json
python3 manage.py loaddata gyms_and_addresses.json
python3 manage.py loaddata gym_reviews.json
python3 manage.py loaddata subscriptions.json
python3 manage.py loaddata subscription_payments.json
python3 manage.py loaddata workout_plan_runs.json
python3 manage.py loaddata workout_day_logs.json
python3 manage.py loaddata workout_item_logs.json
python3 manage.py loaddata workout_set_logs.json
python3 manage.py loaddata bug_reports.json
python3 manage.py loaddata feature_requests.json
python3 manage.py loaddata mobile_text_content.json

python3 manage.py createsuperuser --username admin --noinput --email admin@example.com
# Ustawianie hasła dla użytkownika admin, bo createsuperuser nie ma --password
python3 manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); u=U.objects.get(username='admin'); u.set_password('admin'); u.save()"

cd ..