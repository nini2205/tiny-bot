import os, random, discord
from discord import app_commands, Embed

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN env var")

# Optional: set this in Railway > Variables for instant guild sync
GUILD_ID = os.getenv("GUILD_ID")
guild_obj = discord.Object(id=int(GUILD_ID)) if GUILD_ID else None

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

uwu_gifs = [
    "https://media.tenor.com/1dX9o0mR5eMAAAAC/uwu-cat.gif",
    "https://media.tenor.com/7b4o1J8c5oQAAAAd/uwu-anime.gif",
    "https://media.tenor.com/q0s4bQzvYHcAAAAd/kitty-uwu.gif",
    "https://media1.tenor.com/m/HUO-YsiBS9MAAAAC/kjslave.gif",
]

# ---- Commands (global definitions) ----
@tree.command(name="ping", description="Replies with pong and latency.")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(client.latency*1000)}ms")

@tree.command(name="say", description="Make the bot say something.")
@app_commands.describe(text="What should I say?")
async def say_command(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)

@tree.command(name="uwu", description="Send a random uwu GIF.")
async def uwu_command(interaction: discord.Interaction):
    url = random.choice(uwu_gifs)
    embed = Embed()
    embed.set_image(url=url)
    await interaction.response.send_message(embed=embed)

@tree.command(name="checkperms", description="Check if bot can send embeds here.")
async def checkperms(interaction: discord.Interaction):
    perms = interaction.channel.permissions_for(interaction.guild.me)
    if perms.embed_links:
        await interaction.response.send_message("✅ I can send embeds in this channel.")
    else:
        await interaction.response.send_message("❌ I don’t have **Embed Links** permission here.", ephemeral=True)

# ---- Sync on ready ----
@client.event
async def on_ready():
    try:
        if guild_obj:
            tree.copy_global_to(guild=guild_obj)
            await tree.sync(guild=guild_obj)   # instant in your server
            print(f"Synced to guild {GUILD_ID} as {client.user}")
        else:
            await tree.sync()                   # global (may take up to ~1 hour)
            print(f"Globally synced as {client.user}")
    except Exception as e:
        print("Slash command sync failed:", e)

client.run(TOKEN)
