import os, random, discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN env var")

# Optional: set this to your server ID for instant slash commands
GUILD_ID = os.getenv("GUILD_ID")  # put this in Railway Variables if you want fast sync
guild_obj = discord.Object(id=int(GUILD_ID)) if GUILD_ID else None

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    try:
        if guild_obj:
            # fast: only your server
            await tree.sync(guild=guild_obj)
            print(f"Synced to guild {GUILD_ID}. Logged in as {client.user} ({client.user.id})")
        else:
            # slow: global (can take up to ~1 hour)
            await tree.sync()
            print(f"Globally synced. Logged in as {client.user} ({client.user.id})")
    except Exception as e:
        print("Slash command sync failed:", e)

@tree.command(name="ping", description="Replies with pong and latency.", guild=guild_obj)
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(client.latency*1000)}ms")

@tree.command(name="say", description="Make the bot say something.", guild=guild_obj)
@app_commands.describe(text="What should I say?")
async def say_command(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)

# Use direct media URLs (Tenor 'media.tenor.com' or 'c.tenor.com' links)
uwu_gifs = [
    "https://media.tenor.com/1dX9o0mR5eMAAAAC/uwu-cat.gif",
    "https://media.tenor.com/7b4o1J8c5oQAAAAd/uwu-anime.gif",
    "https://media.tenor.com/q0s4bQzvYHcAAAAd/kitty-uwu.gif",
]

@tree.command(name="uwu", description="React with a random uwu gif.", guild=guild_obj)
async def uwu_command(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(uwu_gifs))

client.run(TOKEN)
