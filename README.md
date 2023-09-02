<!-- Steps to start the project -->

python3 -m venv venv
pip install -r requirements.txt

Postgres setup

<!-- Install psql globally -->
<!-- To enter psql terminal -->

psql ->

<!-- To create database and table in postgres -->

CREATE DATABASE <db_name>;
CREATE USER <db_username> WITH PASSWORD '<db_password>';
ALTER ROLE <db_username> SET client_encoding TO 'utf8';
ALTER ROLE <db_username> SET default_transaction_isolation TO 'read committed';
ALTER ROLE <db_username> SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE <db_name> TO <db_username>;

<!-- To exit from psql terminal -->

\q

<!-- To create superuser account for django admin -->
<!-- Inside venv -->

Superuser ->
python manage.py createsuperuser

<super_username>, <superuser_password>
