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


@client.event
async def on_ready():
    await tree.sync(guild=guild_obj) if guild_obj else await tree.sync()
    print(f"Bot ready as {client.user}")

@tree.command(name="checkperms", description="Check if bot can send embeds & show a random uwu gif", guild=guild_obj)
async def checkperms(interaction: discord.Interaction):
    perms = interaction.channel.permissions_for(interaction.guild.me)
    if perms.embed_links:
        gif_url = random.choice(uwu_gifs)
        embed = Embed()
        embed.set_image(url=gif_url)
        await interaction.response.send_message(f"✅ I can send embeds! Here's a random uwu gif:", embed=embed)
    else:
        await interaction.response.send_message("❌ I don’t have permission to send embeds in this channel.", ephemeral=True)

client.run(TOKEN)
