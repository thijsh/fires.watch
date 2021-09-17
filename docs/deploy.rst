 .. deploy:

Deploy
======================================================================

Heroku
----------------------------------------------------------------------

**You can add a default Heroku app name to your environment with**:: 

    export HEROKU_APP=fires-watch-staging


**Regarding the commands below, note that**:

- You will have to change some values (name, region) below depending on your desired environment
- The AWS (and optional Mailgun) credentials need to be provided by you
- You will need the Heroku CLI tool locally installed for these commands to work (and log in with it)
- A 'dyno' is Heroku's version of a container

**You'll need the following commands at minimum**::

    # First, let's create a Heroku app with the first command.
    #
    # Note (and change if needed):
    # - The region flag
    # - The app name flag (-n)
    # Consider:
    # - Adding this newly created app to a pipeline (command not included here)
    heroku apps:create --region eu --buildpack heroku/python -n fires-watch-staging 

    # Create a postgres database, and set schedule backups
    heroku addons:create -a fires-watch-staging heroku-postgresql:hobby-dev

    # Heroku will now understand that DATABASE_URL refers to the newly created postgres db.

    # On Windows use double quotes for the time zone, e.g.
    # heroku pg:backups schedule --at "02:00 America/Los_Angeles" DATABASE_URL
    heroku pg:backups -a fires-watch-staging schedule --at '02:00 Europe/Amsterdam' DATABASE_URL
    heroku pg:promote -a fires-watch-staging DATABASE_URL

    # Create a Redis dyno
    heroku addons:create -a fires-watch-staging heroku-redis:hobby-dev

    # Set some default values
    heroku config:set -a fires-watch-staging PYTHONHASHSEED=random

    heroku config:set -a fires-watch-staging WEB_CONCURRENCY=4

    heroku config:set -a fires-watch-staging DJANGO_DEBUG=False
    heroku config:set -a fires-watch-staging DJANGO_SETTINGS_MODULE=config.settings.production
    heroku config:set -a fires-watch-staging DJANGO_SECRET_KEY="$(openssl rand -base64 64)"

    # Generating a 32 character-long random string without any of the visually similar characters "IOl01":
    heroku config:set -a fires-watch-staging DJANGO_ADMIN_URL="$(openssl rand -base64 4096 | tr -dc 'A-HJ-NP-Za-km-z2-9' | head -c 32)/"

    # Set this to your Heroku app url, e.g. 'bionic-beaver-28392.herokuapp.com'
    heroku config:set -a fires-watch-staging DJANGO_ALLOWED_HOSTS=fires-watch-staging.herokuapp.com,fires.watch

    # Assign with AWS_ACCESS_KEY_ID
    heroku config:set -a fires-watch-staging DJANGO_AWS_ACCESS_KEY_ID=XXXXXXXXXXXX

    # Assign with AWS_SECRET_ACCESS_KEY
    heroku config:set -a fires-watch-staging DJANGO_AWS_SECRET_ACCESS_KEY=YYYYYYYYYYYYY

    # Assign with AWS_STORAGE_BUCKET_NAME
    heroku config:set -a fires-watch-staging DJANGO_AWS_STORAGE_BUCKET_NAME=ZZZZZZZZZZZZZZ

    # Mailgun
    #
    # Option 1) Create a mailgun dyno (ignore next line if going for option 2)
    heroku addons:create mailgun:starter
    # Option 2) Use your own mailgun environment (uncomment following lines if going for option 2 here)
    #heroku config:set -a fires-watch-staging MAILGUN_API_KEY=replace-with-your-API-key
    #heroku config:set -a fires-watch-staging MAILGUN_API_URL=https://api.eu.mailgun.net/v3 # Note this points to the EU region, use https://api.mailgun.net/v3 for US
    #heroku config:set -a fires-watch-staging MAILGUN_DOMAIN=your.mailgun.domain
    #heroku config:set -a fires-watch-staging MAILGUN_PUBLIC_KEY=replace-with-your-mailgun-public-key
