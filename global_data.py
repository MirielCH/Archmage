# global_data.py

import os

# Get bot directory
bot_dir = os.path.dirname(__file__)

# Databases
dbfile = os.path.join(bot_dir, 'database/archmage_db.db')

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
log_dir = os.path.join(bot_dir, 'logs/')
logfile = os.path.join(log_dir, 'discord.log')