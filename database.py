# database.py
"""Access to the database"""

from datetime import datetime
import sqlite3
from typing import NamedTuple, Optional, Union

import discord

from resources import exceptions, logs, settings


ARCHMAGE_DB = sqlite3.connect(settings.DB_FILE, isolation_level=None)


INTERNAL_ERROR_SQLITE3 = 'Error executing SQL.\nError: {error}\nTable: {table}\nFunction: {function}\SQL: {sql}'
INTERNAL_ERROR_LOOKUP = 'Error assigning values.\nError: {error}\nTable: {table}\nFunction: {function}\Records: {record}'
INTERNAL_ERROR_NO_ARGUMENTS = 'You need to specify at least one keyword argument.\nTable: {table}\nFunction: {function}'


class User(NamedTuple):
    user_id: int
    target_enchant: int


async def log_error(error: Union[Exception, str], ctx: Optional[discord.ApplicationContext] = None):
    """Logs an error to the database and the logfile

    Arguments
    ---------
    error: Exception or a simple string.
    ctx: If context is available, the function will log the user input, the message timestamp
    and the user settings. If not, current time is used, settings and input are logged as "N/A".

    Raises
    ------
    sqlite3.Error when something goes wrong in the database. Also logs this error to the log file.
    """
    table = 'errors'
    function_name = 'log_error'
    sql = 'INSERT INTO errors VALUES (?, ?, ?, ?, ?)'
    if ctx is not None:
        timestamp = ctx.author.created_at
        command_name = f'{ctx.command.full_parent_name} {ctx.command.name}'.strip()
        command_data = str(ctx.interaction.data)
    else:
        timestamp = datetime.utcnow()
        command_name = 'N/A'
        command_data = 'N/A'
    try:
        user_settings = await get_user(ctx.author.id)
    except:
        user_settings = 'N/A'
    try:
        cur = ARCHMAGE_DB.cursor()
        cur.execute(sql, (timestamp, command_name, command_data, str(error), user_settings))
    except sqlite3.Error as error:
        logs.logger.error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql),
            ctx
        )
        raise


# --- Get Data ---
async def get_user(user_id: int) -> User:
    """Gets user settings.

    Returns
    -------
    User object

    Raises
    ------
    sqlite3.Error if something happened within the database.
    exceptions.NoDataFoundError if no user was found.
    LookupError if something goes wrong reading the dict.
    Also logs all errors to the database.
    """
    table = 'settings_user'
    function_name = 'get_user'
    sql = 'SELECT * FROM settings_user where user_id=?'
    try:
        cur = ARCHMAGE_DB.cursor()
        cur.row_factory = sqlite3.Row
        cur.execute(sql, (user_id,))
        record = cur.fetchone()
    except sqlite3.Error as error:
        await log_error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql)
        )
        raise
    if not record:
        raise exceptions.NoDataFoundError('User not in database')
    try:
        user_settings = User(
            user_id = record['user_id'],
            target_enchant = record['target_enchant'],
        )
    except Exception as error:
        await log_error(
            INTERNAL_ERROR_LOOKUP.format(error=error, table=table, function=function_name, record=record)
        )
        raise LookupError

    return user_settings


async def get_user_count(ctx: discord.ApplicationContext) -> int:
    """Gets the amount of users in the database.

    Returns
    -------
    Amound of users: int

    Raises
    ------
    sqlite3.Error if something happened within the database. Also logs this error to the log file.
    """
    table = 'settings_user'
    function_name = 'get_user_count'
    sql = 'SELECT COUNT(user_id) FROM settings_user'
    try:
        cur = ARCHMAGE_DB.cursor()
        cur.execute(sql)
        record = cur.fetchone()
    except sqlite3.Error as error:
        await log_error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql),
            ctx
        )
        raise
    (user_count,) = record
    return user_count


# --- Write Data ---
async def update_user(user_id: int, **kwargs) -> None:
    """Updates guild settings.

    Arguments
    ---------
    user_id: int
    kwargs (column=value):
        target_enchant: int

    Raises
    ------
    sqlite3.Error if something happened within the database.
    NoArgumentsError if not kwargs are passed (need to pass at least one)
    Also logs all error to the database.
    """
    table = 'settings_user'
    function_name = 'update_user'
    if not kwargs:
        await log_error(
            INTERNAL_ERROR_NO_ARGUMENTS.format(table=table, function=function_name)
        )
        raise exceptions.NoArgumentsError('You need to specify at least one keyword argument.')
    cur = ARCHMAGE_DB.cursor()
    try:
        await get_user(user_id)
    except exceptions.NoDataFoundError:
        sql = 'INSERT INTO settings_user (user_id, target_enchant) VALUES (?, ?)'
        try:
            cur.execute(sql, (user_id, settings.ENCHANTS.index('None')))
        except sqlite3.Error as error:
            await log_error(
                INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql)
            )
            raise
    try:
        sql = 'UPDATE settings_user SET'
        for kwarg in kwargs:
            sql = f'{sql} {kwarg} = :{kwarg},'
        sql = sql.strip(",")
        kwargs['user_id'] = user_id
        sql = f'{sql} WHERE user_id = :user_id'
        cur.execute(sql, kwargs)
    except sqlite3.Error as error:
        await log_error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql)
        )
        raise