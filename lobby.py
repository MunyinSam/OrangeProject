from gameclass import * 
from commands import *

#----------------------------------------------------------------------

import discord
from discord.ui import Button, View
from discord import app_commands
from discord import File
from discord.ext import tasks, commands
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

#----------------------------------------------------------------------
load_dotenv()
print("Current Working Directory:", os.getcwd())

uri = str(os.getenv("MONGODB_URI"))
client = MongoClient(uri, server_api=ServerApi('1'))

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

#----------------------------------------------------------------------



#----------------------------------------------------------------------

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# Munyin's Bot
bot.run(os.getenv("BOT_KEY"))


