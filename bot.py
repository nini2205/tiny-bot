# bot.py
import os, io, random, asyncio
import discord, aiohttp
from discord import app_commands, Embed

# ---- Env ----
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN")

TENOR_KEY = os.getenv("TENOR_KEY")
if not TENOR_KEY:
    raise RuntimeError("Missing TENOR_KEY (add it in Railway > Service > Variables)")

GUILD_ID = os.getenv("GUILD_ID")  # optional: instant sync to your server
guild_obj = discord.Object(id=int(GUILD_ID)) if GUILD_ID else None

# ---- Discord client ----
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ---- Helpers ----
TENOR_BASE = "https://tenor.googleapis.com/v2"
UA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RioTheKittyButler/1.0)"
}

async def tenor_random_gif_url(query: str = "uwu") -> str | None:
    """
    Hit Tenor random endpoint and return a direct media URL.
    We prefer gif/tinygif/mp4 in that order.
    """
    params = {
        "key": TENOR_KEY,
        "q": query,
        "limit": 1,
        # client key is optional but recommended; it helps Tenor analytics. Use your app name.
        "client_key": "rio_kitty_butler",
        "media_filter": "minimal",  # faster; still includes gif/tinygif/mp4
        "random": "true",
    }
    timeout = aiohttp.ClientTimeout(total=8)

    async with aiohttp.ClientSession(headers=UA_HEADERS, timeout=timeout) as session:
        async with session.get(f"{TENOR_BASE}/search", params=params) as resp:
            if resp.status != 200:
                print(f"[tenor] HTTP {resp.status}")
                return None
            data = await resp.json()

    results = data.get("results", [])
    if not results:
        return None

    media = results[0].get("media_formats", {})
    # Prefer full gif, then tinygif, then mp4 (Discord can embed mp4 too)
    for key in ("gif", "tinygif", "mp4"):
        if key in media and "url" in media[key]:
            return media[key]["url"]
    return None

async def fetch_bytes(url: str) -> bytes | None:
    try:
        async with aiohttp.ClientSession(headers=UA_HEADERS) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                return await resp.read()
    except Exception as e:
        print(f"[fetch_bytes] error for {url}: {e}")
        return None

# ---- Commands (global) ----
@tree.command(name="ping", description="Replies with pong and latency.")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(client.latency*1000)}ms")

@tree.command(name="say", description="Make the bot say something.")
@app_commands.describe(text="What should I say?")
async def say_command(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)

@tree.command(name="gif", description="Send a random GIF from Tenor.")
@app_commands.describe(query="Search term (default: uwu)")
async def gif_command(interaction: discord.Interaction, query: str = "uwu"):
    await interaction.response.defer()  # give us a moment to fetch

    url = await tenor_random_gif_url(query)
    if not url:
        return await interaction.followup.send("No results from Tenor 😿")

    data = await fetch_bytes(url)
    if not data:
        return await interaction.followup.send("Couldn't fetch the GIF bytes 😢")

    # Upload so it always displays, then embed it
    file_ext = ".mp4" if url.endswith(".mp4") else ".gif"
    file = discord.File(io.BytesIO(data), filename=f"tenor{file_ext}")
    embed = Embed(title=f"🎞️ {query}")
    embed.set_image(url=f"attachment://tenor{file_ext}")

    perms = interaction.channel.permissions_for(interaction.guild.me)
    if perms.embed_links:
        await interaction.followup.send(embed=embed, file=file)
    else:
        await interaction.followup.send(content="(No Embed Links perm) here’s your GIF:", file=file)

# Backwards-compat alias: /uwu just calls /gif uwu
@tree.command(name="uwu", description="Send a random 'uwu' GIF from Tenor.")
async def uwu_command(interaction: discord.Interaction):
    await gif_command.callback(interaction, query="uwu")  # reuse logic

# ---- Sync on ready ----
@client.event
async def on_ready():
    try:
        if guild_obj:
            tree.copy_global_to(guild=guild_obj)
            synced = await tree.sync(guild=guild_obj)  # instant
            print(f"[READY] Synced {len(synced)} cmds to guild {GUILD_ID} as {client.user}")
        else:
            synced = await tree.sync()                 # global can take time
            print(f"[READY] Globally synced {len(synced)} cmds as {client.user}")
    except Exception as e:
        print("[ERROR] Slash command sync failed:", e)

client.run(TOKEN)
