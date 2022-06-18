token = "your_token_here" # your bot token
cogs = [
    "cogs.list",
    "cogs.of",
    "cogs.cogs" 
]
BOT_LANGUAGE = "english"

BABEL_DOMAIN = "messages"
BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_TIMEZONE = "UTC"
BABEL_TRANSLATION_DIRECTORIES = "translations"

# The DB has to be hosted by PostgreSQL
DB_USERNAME = ""
DB_PASSWORD = ""
DB_HOST = ""
DB_PORT = 5432
DB_NAME = ""
DB_SCHEMA = ""

# If you want to create a SSH tunnel to connect to the DB
# Only for local development
USE_SSH_TUNNEL = False
SSH_HOST = "0.0.0.0"
SSH_PORT = 22 # By default, this is the SSH port
SSH_USERNAME = ""
SSH_PASSWORD = ""
SSH_REMOTE_HOST = "127.0.0.1"
SSH_REMOTE_PORT = 5432 # By default, this is the PostgreSQL port
