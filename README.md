# EPL bot
In order to start the bot - follow this simple steps:

1. Set in your virtual environment the following variables:
  - **SECRET_KEY**,
  - **BOT_TOKEN** (token gotten from bot_father),
  - **REDIS_URL** (for example - *'localhost:6379'*),
  - **DATABASE_URL** (for example - *'postgres://user:password@host:port/db_name'*)

2. Set webhook for telegram. (Because this bot is intended to be hosted on
heroku, there is no need in specifying a certificate for a webhook manually -
heroku will handle this by themselves.) Setting a webhook takes a bit more steps:

  * Change value of the setting variable **HOST_NAME** according to your
application host name (for example - *'application1.herokuapp.com'*)

  * Run command *'./manage.py set_webhook'*

  * (optional) Check the status of your just setted webhook by GET-request to
telegram api: `curl https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo`

3. Run command *'./manage.py migrate'* in order to create database and set it to
the proper state

4. Run command *'./manage.py parse_fixtures'* in order to fill up a DB with
EPL matches.