token = "your_token_here" # your bot token
cogs = [
    "cogs.list",
    "cogs.of",
    "cogs.cogs" 
]
BOT_LANGUAGE = "english"

DEBUG = True # Set to False for production

# CommandTree will by synced is these guilds on every startup
# if DEBUG is True
TEST_GUILDS = [] # Enter guild ids here

BABEL_DOMAIN = "messages"
BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_TIMEZONE = "UTC"

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
