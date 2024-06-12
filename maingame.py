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
import random

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

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.add_view(MainGameView())
#----------------------------------------------------------------------

class MainGame(discord.ui.View):
    def __init__(self, ctx, boardID):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.boardID = boardID
    
    @discord.ui.button(label="Roll", style=discord.ButtonStyle.green, custom_id="rolldice")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)

        # Roll the dice
        roll_result = random.randint(1, 6)
        
        # current_player_tile = find_player_tile(self.boardID, user_id)
        if current_player_tile is None:
            current_player_tile = 0  # Default to start if not found
        
        # Calculate the new tile index
        tile_index = (current_player_tile + roll_result) % 25  # Ensure it wraps around if it exceeds the board size
        print(tile_index)
        # Update the player's position on the board
        # add_player_to_tile(self.boardID, tile_index, user_id)
        
        # Retrieve the occupied_by list of the new tile
        board = Board.objects(board_name=str(self.boardID)).first()
        if board:
            new_tile = board.tiles[tile_index]
            occupied_by = new_tile.occupied_by

            await interaction.response.send_message(
                f"Roll clicked. You rolled a {roll_result}. You moved to tile {tile_index}. Current occupants: {occupied_by}",
                ephemeral=False
            )
        else:
            await interaction.response.send_message(
                f"Board not found",
                ephemeral=False
            )

class MainGameView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)  # Set timeout=None if you want the buttons to be always active
        self.ctx = ctx
        
    @discord.ui.button(label="Start", style=discord.ButtonStyle.green, custom_id="start_game")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        # board = generate_initial_board()
        # message = board_to_string(board)

        
        embed = discord.Embed(title="Game Start!", color=0x00ff00)
        
        view = MainGame(self.ctx, "Standard Game Board")
        # await interaction.response.send_message(message, ephemeral=False)
        await interaction.channel.send(embed=embed, view=view)

    @discord.ui.button(label="Select Character", style=discord.ButtonStyle.blurple, custom_id="select_char")
    async def select_character_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Character Selection", description="Select a character for your player.", color=0x00ff00)
        
        all_characters = CharacterTemplate.objects()  # Fetch all characters
        view = CharacterView(all_characters, interaction.user)
        
        await interaction.response.send_message('Character Selection', ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)

class CharacterDropdown(discord.ui.Select):
    def __init__(self, all_characters, user):
        self.user = user
        # Create a dictionary to map character IDs to character objects
        self.character_id_to_object = {str(character.id): character for character in all_characters}
        
        options = [
            discord.SelectOption(label=character.name, description=f"Level: {character.level}, Attack: {character.attack}, Defense: {character.defense}, Evade: {character.evade}, Speed: {character.speed}", value=str(character.id))
            for character in all_characters
        ]

        # Ensure there are options to add, handle cases where there are no characters
        if not options:
            options = [discord.SelectOption(label="No characters available", description="No characters to select", value="no_characters")]

        super().__init__(placeholder="Choose a character...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        character_id = self.values[0]
        character = self.character_id_to_object[character_id]

        # Call the function to apply the character to the user's player profile
        player = Player.objects(discord_id=str(self.user.id)).first()
        if player:
            player.apply_character(character)
        
        # Send a message with the character name
        await interaction.response.send_message(f"Character selected: {character.name}", ephemeral=True)

class CharacterView(discord.ui.View):
    def __init__(self, all_characters, user):
        super().__init__()
        self.add_item(CharacterDropdown(all_characters, user))

@bot.command(name="game")
async def start_game(ctx):
    view = MainGameView(ctx)
    await ctx.send("Click a button to start.", view=view)






#----------------------------------------------------------------------

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# Munyin's Bot
bot.run(os.getenv("BOT_KEY"))