import os
import asyncio
from discord.ext import commands
import db
from poller import poll_and_notify
from dotenv import load_dotenv
import feedparser

# carga variables desde .env si existe
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("Error: define DISCORD_TOKEN en variables de entorno o en .env")
    raise SystemExit(1)

intents = None
try:
    from discord import Intents
    intents = Intents.default()
    intents.message_content = True
except Exception:
    intents = None

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot listo: {bot.user}")
    # arrancar poller si no está corriendo
    asyncio.create_task(poller_task())

async def poller_task():
    await bot.wait_until_ready()
    await poll_and_notify(bot)

@bot.command(name="subscribe")
async def subscribe(ctx, feed_url: str):
    channel_id = str(ctx.channel.id)
    db.add_subscription(channel_id, feed_url)
    await ctx.send(f"Suscrito a {feed_url} en este canal.")

@bot.command(name="unsubscribe")
async def unsubscribe(ctx, feed_url: str):
    channel_id = str(ctx.channel.id)
    deleted = db.remove_subscription(channel_id, feed_url)
    if deleted:
        await ctx.send(f"Cancelada suscripción a {feed_url}")
    else:
        await ctx.send("No se encontró esa suscripción en este canal.")

@bot.command(name="list")
async def list_cmd(ctx):
    channel_id = str(ctx.channel.id)
    feeds = db.list_subscriptions_for_channel(channel_id)
    if not feeds:
        await ctx.send("No hay suscripciones en este canal.")
        return
    await ctx.send("Suscripciones:\n" + "\n".join(feeds))

@bot.command(name="recent")
async def recent(ctx, feed_url: str, count: int = 1):
    """!recent <feed_url> <count> — envía los últimos `count` ítems del feed al canal."""
    try:
        n = int(count)
    except Exception:
        await ctx.send("Count inválido. Usa un número entero. Ej: `!recent https://ejemplo.com/rss 3`")
        return
    if n <= 0:
        await ctx.send("El número debe ser mayor que 0.")
        return

    MAX_PER_REQUEST = 5
    if n > MAX_PER_REQUEST:
        await ctx.send(f"Máximo permitido: {MAX_PER_REQUEST}. Enviando {MAX_PER_REQUEST} ítems.")
        n = MAX_PER_REQUEST

    # intentar usar el "typing" context manager compatible con varias versiones
    typing_cm = None
    if hasattr(ctx, "typing"):
        typing_cm = ctx.typing()
    elif getattr(ctx, "channel", None) and hasattr(ctx.channel, "typing"):
        typing_cm = ctx.channel.typing()

    async def fetch_and_send():
        loop = asyncio.get_event_loop()
        parsed = await loop.run_in_executor(None, feedparser.parse, feed_url)
        entries = parsed.entries
        if not entries:
            await ctx.send("No se encontraron entradas en ese feed o la URL es inválida.")
            return

        to_send = entries[:n]  # feedparser suele devolver newest->oldest
        for entry in reversed(to_send):  # enviar más antiguo primero dentro del lote
            title = entry.get("title", "(sin título)")
            link = entry.get("link", "")
            published = entry.get("published", "")
            text = f"**{title}**\n{published}\n{link}"
            try:
                await ctx.send(text)
            except Exception:
                pass

    if typing_cm:
        try:
            async with typing_cm:
                await fetch_and_send()
        except Exception:
            # en caso de fallo dentro del typing, intentar enviar sin typing
            await fetch_and_send()
    else:
        await fetch_and_send()

if __name__ == "__main__":
    bot.run(TOKEN)