import os, random, discord
from discord import app_commands, Embed

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN env var")

GUILD_ID = os.getenv("GUILD_ID")  # set this in Railway for instant sync (server ID)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# --- commands defined as GLOBAL ---
@tree.command(name="ping", description="Replies with pong and latency.")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(client.latency*1000)}ms")

@tree.command(name="say", description="Make the bot say something.")
@app_commands.describe(text="What should I say?")
async def say_command(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)

uwu_gifs = [
    "https://media.tenor.com/1dX9o0mR5eMAAAAC/uwu-cat.gif",
    "https://media.tenor.com/7b4o1J8c5oQAAAAd/uwu-anime.gif",
    "https://media.tenor.com/q0s4bQzvYHcAAAAd/kitty-uwu.gif",
    "https://media1.tenor.com/m/HUO-YsiBS9MAAAAC/kjslave.gif",
]

@tree.command(name="uwu", description="React with a random uwu gif.")
async def uwu_command(interaction: discord.Interaction):
    url = random.choice(uwu_gifs)
    embed = Embed()
    embed.set_image(url=url)
    await interaction.response.send_message(embed=embed)

@client.event
async def on_ready():
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            tree.copy_global_to(guild=guild)   # copy all globals to your guild
            await tree.sync(guild=guild)       # instant in that server
            print(f"Synced to guild {GUILD_ID} as {client.user}")
        else:
            await tree.sync()                   # global rollout (can take up to ~1 hour)
            print(f"Globally synced as {client.user}")
    except Exception as e:
        print("Slash command sync failed:", e)

client.run(TOKEN)
