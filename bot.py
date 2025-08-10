import os, discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN env var. Set it in Railway > Your Service > Variables.")

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
    
print("TOKEN from env:", repr(TOKEN))

client.run(TOKEN)
