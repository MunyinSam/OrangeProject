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

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.add_view(MainMenuView())

#---------------------------------------------------------------------------------------------------
# Deck Builder
#---------------------------------------------------------------------------------------------------




#---------------------------------------------------------------------------------------------------

game_sessions = {}

# 2 Buttons
class MainMenuView(discord.ui.View):
    def __init__(self, ctx, room_id, player_id):
        super().__init__(timeout=None)  # Set timeout=None if you want the buttons to be always active
        self.ctx = ctx
        self.room_id = room_id
        self.player_id = player_id

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green, custom_id="start_game")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        room = Room.objects(id=self.room_id).first()
        room.game_status = "active"
        room.save()
        channel_name = room.roomID

        player_list = []
        player_permissions = []
        guild = self.ctx.guild
        
        if len(room.players) > 1:
        
            for i, player in enumerate(room.players, start=1):

                member_id = int(player.discord_id)  # Convert the Discord ID to an integer
                member = guild.get_member(member_id)
                
                if member:
                    player_list.append(f"{player.name}")
                    player_permissions.append(member)
                else:
                    player_list.append(f"{player.name} (not found)")

            playerlist_str = "\n".join(player_list)

            existing_channel = discord.utils.get(guild.channels, name=channel_name)
            if not existing_channel:
                # Set the channel permissions
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                for member in player_permissions:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

                new_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
                # board = generate_initial_board()
                # message = await new_channel.send(board_to_string(board))
                # start_message = "Room Created"
                # game_sessions[new_channel.id] = message.id
                embed = discord.Embed(title=f'Channel {channel_name} created successfully!', description=f"Player List: \n {playerlist_str}", color=0x00ff00)
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                await interaction.response.send_message(f'A channel named "{channel_name}" already exists.', ephemeral=False)
        
        else:
            await interaction.response.send_message(f'You need at least 2 Players to start the game.', ephemeral=False)
    
    @discord.ui.button(label="Join", style=discord.ButtonStyle.blurple, custom_id="join_game")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        room = Room.objects(id=self.room_id).first()
        
        if room and room.game_status == "waiting":
            player = Player.objects(discord_id=str(interaction.user.id)).first()
            if player:
                if player.id not in [p.id for p in room.players]:
                    room.players.append(player)
                    room.save()
                    await interaction.response.send_message(f'{interaction.user.display_name} has joined the game.', ephemeral=False)
                else:
                    await interaction.response.send_message(f'You are already in the game.', ephemeral=True)
            else:
                await interaction.response.send_message("You are not registered as a player in this game.", ephemeral=True)
        else:
            await interaction.response.send_message("The room is not available or the game has already started.", ephemeral=True)


                

#---------------------------------------------------------------------------------------------------

@bot.command(name="menu")
async def send_menu(ctx):
    player = Player.objects(discord_id=str(ctx.author.id)).first()
    board = Board().save()
    
    lobby = Room(
        roomID=f"100% Orange Juice",
        players=[],  
        current_turn=player,
        game_board=board,
        game_status="waiting",
        turn_number=0
    )
    lobby.save()
    print("Lobby Created")

    file_path = r'C:\Users\Munyin\Munyin Repository\Orange\OrangeProject\picture\Lobby.png'  # Full path to the file

    # Set the filename as "Lobby.png" to match with the attachment URL in the embed
    file = discord.File(file_path, filename="Lobby.png")

    embed = discord.Embed(title="Lobby", description="Select an option to proceed:", color=0x00ff00)

    # Make sure the URL in set_image matches the filename given to discord.File
    embed.set_image(url="attachment://Lobby.png")
    
    await ctx.send(embed=embed, file=file, view=MainMenuView(ctx, lobby.id, player.id))

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


