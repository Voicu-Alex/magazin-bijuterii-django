# Magazin de Bijuterii

Proiect Django - Tehnici Web / Django, FMI, Universitatea din București, grupa 244.

## Rulare

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd magazinbijuterii
python manage.py migrate
python manage.py populeaza
python manage.py runserver
```

Baza de date: PostgreSQL (`django_bijuterii`, schema `django`). Userul se creează cu `documentatie/creare_user.sql`.
