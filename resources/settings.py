# settings.py

import os

from dotenv import load_dotenv


# Read the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEBUG_MODE = os.getenv('DEBUG_MODE')

BOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BOT_DIR, 'database/archmage_db.db')
LOG_FILE = os.path.join(BOT_DIR, 'logs/discord.log')

DEV_GUILDS = [730115558766411857,] # Change to your own dev guild id(s)
OWNER_ID = 619879176316649482 # Change to your own user id

EPIC_RPG_ID = 555955826880413696

EMBED_COLOR = 0xDD9624

DEFAULT_FOOTER = 'You look simply enchanting today.'

ENCHANTS = (
    'Normie',
    'Good',
    'Great',
    'Mega',
    'Epic',
    'Hyper',
    'Ultimate',
    'Perfect',
    'EDGY',
    'ULTRA-EDGY',
    'OMEGA',
    'ULTRA-OMEGA',
    'GODLY',
    'VOID',
    'None',
)