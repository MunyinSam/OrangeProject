from datetime import datetime, timezone
from bson import ObjectId
from mongoengine import Document, fields, connect, StringField, IntField, FloatField, ListField, EmbeddedDocument, EmbeddedDocumentListField

import discord
from discord import app_commands
from discord.ext import commands
import random
import pprint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to MongoDB --------------------------------------------

connect('Chapokit1', host=str(os.getenv("MONGODB_URI")))

# maindb--------------------------------

class Player(Document):
    discord_id = fields.StringField(required=True)
    name = fields.StringField(required=True)
    level = fields.IntField(default=1)
    xp = fields.IntField(default=0)
    evade = fields.IntField()
    attack = fields.IntField()
    defense = fields.IntField()  
    current_health = fields.IntField()
    default_health = fields.IntField()
    speed = fields.IntField()
    norma = fields.IntField(default=1)
    stars = fields.IntField(default=0)
    cards = fields.ListField()  # List of references to Card documents
    deck = fields.ListField()
    position = fields.IntField(default=0)  # Position on the game board
    current_character = fields.StringField()
    money = fields.IntField()
    win_condition = fields.StringField()
    current_position = fields.IntField(default=0)  # Stores the index of the tile the player is currently on
    game_board = fields.ReferenceField('Board')
    coins=fields.IntField()

    def apply_character(self, character):
        self.attack = character.attack
        self.defense = character.defense
        self.evade = character.evade
        self.speed = character.speed
        self.current_character = character.name
        self.save()  # Assuming this saves the document

class CharacterTemplate(Document):
    name = fields.StringField(required=True)
    level = fields.IntField(default=1)
    description = fields.StringField()
    default_health = fields.IntField()
    attack = fields.IntField()
    defense = fields.IntField()
    evade = fields.IntField()
    speed = fields.IntField()
    character_image_url = fields.StringField()  # URL to an image of the character for UI elements

class Room(Document):
    roomID = fields.StringField(required=True)
    players = fields.ListField(fields.ReferenceField('Player'))  # Supports more than two players
    current_turn = fields.ReferenceField('Player')
    game_board = fields.ReferenceField('Board')  # Reference to the game board used
    game_status = fields.StringField(default="waiting", choices=["waiting", "active", "finished"])
    turn_number = fields.IntField(default=0)

class Card(Document):
    card_name = fields.StringField(required=True)
    card_type = fields.StringField(choices=["trap", "boost", "event","battle"])
    card_effect = fields.StringField()  # Description of what the card does
    level = fields.IntField()
    rarity = fields.StringField(required=True)
    cost = fields.IntField(default=0)  # Cost to use the card
    attack = fields.IntField()
    defense = fields.IntField()
    evade = fields.IntField()
    hp = fields.IntField()
    card_image_url = fields.StringField(required=True)
    

class Tile(EmbeddedDocument):
    type = StringField(choices=["bonus", "drop", "warp", "draw", "encounter", "home"])
    occupied_by = ListField(StringField())  # List of player IDs who are currently on this tile

class Board(Document):
    board_name = StringField()
    tiles = EmbeddedDocumentListField(Tile)
    players = ListField()
    # turn = StringField()
    # game_status = fields.StringField(default="waiting", choices=["waiting", "active", "finished"])

