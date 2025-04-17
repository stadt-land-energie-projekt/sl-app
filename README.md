# Stadt-Land-Energie Webapp

The (django) webapp for the scenario-explorer of the "Stadt-Land-Energie" project.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

License: GPLv3

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd slapp
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd slapp
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd slapp
celery -A config.celery_app worker -B -l info
```

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

### Load data into application

First you have to set up all tables in the database by runnning:

```
python manage.py migrate
```

Afterwards you have to load in data.

For ZIB data:
Copy folders `base`, `cost` and `robust` into folder `slapp/data/zib/`.

>**Only for server**
>
>If you want to do this on server, you have to upload data to server first.
This can be done by using `scp` and copy data to you home folder on server.
Form there, you must move data to data folder in the app (probably inside a docker volume).
Last step is to give access rights to app data.
As docker runs with its own user django, which is unknown to the server system, you first have to find out related system user ID.
You can do so, by entering docker container and run `ls -ln` - this will show you files and owners (in numeric format).
Outside the docker container use the numeric ID to change owner of app data to this user, via `chown -R <user_id>:<user_id> <data_folder>`.
Now, you can enter container again and check if data belongs to docker user.

To simplify data commands a _Makefile_ has been
added, which can be used by command `make`.
You can load all data by running (or you can run them one-by-one):

```
make load_regions load_data load_zib_data
```

And you can empty all data by running:

```
make empty_data
```

## Deployment
This application is ready to be deployed via Caprover. Make sure to define the following Environmental Variables:

REDIS_URL=
DATABASE_URL=postgis://
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=
DJANGO_ADMIN_URL=
DJANGO_ALLOWED_HOSTS=
DJANGO_ACCOUNT_ALLOW_REGISTRATION=True
SENTRY_DSN=
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
STARTUP_COMMAND=/start
CELERY_BROKER_URL=redis://
MAP_ENGINE_TILING_SERVICE_TOKEN=
MAP_ENGINE_TILING_SERVICE_STYLE_ID=
MAP_ENGINE_USE_DISTILLED_MVTS=

### To upload new data, its is probably the easiest to make them work locally, create a backup and use that backup on the target postgres/gis:

* create a backup of the local DB: pg_dump -Fc db_name > db_name.tar
* restore DB to remote server: pg_restore -h server_url -p server_url -d remote_db_name -U remote_db_name -c db_name.tar

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
