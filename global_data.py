# global_data.py

import os

# Get bot directory
bot_dir = os.path.dirname(__file__)

# Databases
dbfile = os.path.join(bot_dir, 'database/erg_db.db')
default_dbfile = os.path.join(bot_dir, 'database/erg_db_default.db')

# Prefix
default_prefix = '-'

# All enchants
enchants_list = ('normie','good','great','mega','epic','hyper','ultimate','perfect','edgy','ultra-edgy','omega','ultra-omega','godly',)
enchants_aliases = {
    'ed': 'edgy',
    'ultraedgy': 'ultra-edgy',
    'ue': 'ultra-edgy',
    'ultraomega': 'ultra-omega',
    'uo': 'ultra-omega'
}

# Embed color
color = 0xDD9624

# Set default footer
async def default_footer(prefix):
    footer = f'You look simply enchanting today.'
    
    return footer

# Error log file
logfile = os.path.join(bot_dir, 'logs/discord.log')