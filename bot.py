# bot.py
import os
import io
import random
import discord
import aiohttp
from discord import app_commands, Embed

# ---- Config ----
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN env var")

# Optional for instant slash-command availability in YOUR server:
# In Railway > Service > Variables, set GUILD_ID=<your_server_id>
GUILD_ID = os.getenv("GUILD_ID")
guild_obj = discord.Object(id=int(GUILD_ID)) if GUILD_ID else None

# ---- Client / Command Tree ----
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ---- Data ----
UWU_GIFS = [
    # Use direct media links where possible (Tenor media)
    "https://media.tenor.com/1dX9o0mR5eMAAAAC/uwu-cat.gif",
    "https://media.tenor.com/7b4o1J8c5oQAAAAd/uwu-anime.gif",
    "https://media.tenor.com/q0s4bQzvYHcAAAAd/kitty-uwu.gif",
    "https://media.tenor.com/HUO-YsiBS9MAAAAd/kjslave.gif",
]

# ---- Commands (define as GLOBAL; we'll copy to guild on_ready) ----
@tree.command(name="ping", description="Replies with pong and latency.")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(client.latency * 1000)}ms")

@tree.command(name="say", description="Make the bot say something.")
@app_commands.describe(text="What should I say?")
async def say_command(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)

@tree.command(name="uwu", description="Send a random uwu GIF.")
async def uwu_command(interaction: discord.Interaction):
    """Fetch a GIF server-side and upload it so it always displays."""
    url = random.choice(UWU_GIFS)

    # Fetch the GIF bytes
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await interaction.response.send_message("Couldn't fetch a GIF 😢")
            data = await resp.read()

    # Upload as attachment; embed references the attachment URL
    file = discord.File(io.BytesIO(data), filename="uwu.gif")
    embed = Embed()
    embed.set_image(url="attachment://uwu.gif")

    # If bot lacks Embed Links, still send the file without the embed
    perms = interaction.channel.permissions_for(interaction.guild.me)
    if perms.embed_links:
        await interaction.response.send_message(embed=embed, file=file)
    else:
        await interaction.response.send_message(content="(No Embed Links perm) uwu gif:", file=file)

@tree.command(name="checkperms", description="Check if the bot can send embeds here.")
async def checkperms_command(interaction: discord.Interaction):
    perms = interaction.channel.permissions_for(interaction.guild.me)
    msg = []
    msg.append(f"Embed Links: {'✅' if perms.embed_links else '❌'}")
    msg.append(f"Send Messages: {'✅' if perms.send_messages else '❌'}")
    msg.append(f"Attach Files: {'✅' if perms.attach_files else '❌'}")
    await interaction.response.send_message("\n".join(msg), ephemeral=not perms.embed_links)

# ---- Sync on Ready ----
@client.event
async def on_ready():
    try:
        if guild_obj:
            # Copy all global commands to your guild for instant usage
            tree.copy_global_to(guild=guild_obj)
            synced = await tree.sync(guild=guild_obj)
            print(f"[READY] Synced {len(synced)} commands to guild {GUILD_ID} as {client.user}")
        else:
            # Global sync (may take up to ~1 hour to appear)
            synced = await tree.sync()
            print(f"[READY] Globally synced {len(synced)} commands as {client.user}")
    except Exception as e:
        print("[ERROR] Slash command sync failed:", e)

# ---- Run ----
client.run(TOKEN)
