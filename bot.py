import os, discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    # Sync slash commands to all guilds the bot is in (first run may take a minute)
    try:
        await tree.sync()
        print(f"Synced slash commands. Logged in as {client.user} (id: {client.user.id})")
    except Exception as e:
        print("Slash command sync failed:", e)

@tree.command(name="ping", description="Replies with pong and latency.")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(client.latency*1000)}ms")

@tree.command(name="say", description="Make the bot say something.")
@app_commands.describe(text="What should I say?")
async def say_command(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)

@tree.command(name="uwu", description="React with a uwu gif.")
async def react_command(interaction: discord.Interaction):
    gif_url = "https://i.pinimg.com/originals/65/28/7a/65287a19692bfeac7a7fce6ad296cef4.gif"  
    await interaction.response.send_message(gif_url)

    
client.run(TOKEN)
