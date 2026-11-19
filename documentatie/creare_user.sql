-- Comenzi rulate in psql ca superuser postgres, dupa CREATE DATABASE django_bijuterii;
CREATE SCHEMA django;
CREATE USER alexandru WITH ENCRYPTED PASSWORD 'alexandru';
GRANT ALL ON DATABASE django_bijuterii TO alexandru;
ALTER ROLE alexandru SET search_path = django, public;
GRANT ALL ON SCHEMA django TO alexandru;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA django TO alexandru;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA django TO alexandru;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA django TO alexandru;
