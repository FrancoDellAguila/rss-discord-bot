import os
import asyncio
import feedparser
from db import get_all_feeds, get_last_published, set_last_published
from typing import Any
import datetime

# número máximo de items a enviar por iteración (configurable vía env)
MAX_ITEMS = int(os.getenv("RSS_ITEMS_PER_POLL", "3"))

async def fetch_feed(loop, url: str) -> Any:
    # feedparser es sync; ejecútalo en thread pool
    return await loop.run_in_executor(None, feedparser.parse, url)

async def poll_and_notify(bot):
    loop = asyncio.get_event_loop()
    while True:
        try:
            feeds = get_all_feeds()  # [(url, [channel_id,...]), ...]
            for url, channels in feeds:
                parsed = await fetch_feed(loop, url)
                entries = parsed.entries
                if not entries:
                    continue

                # función auxiliar para obtener id único de un entry
                def entry_id(e):
                    return e.get("id") or e.get("link") or e.get("title") or ""

                last_seen = get_last_published(url)

                # determinar items no vistos (entries viene normalmente newest->oldest)
                if last_seen is None:
                    unseen = entries[:MAX_ITEMS]
                else:
                    ids = [entry_id(e) for e in entries]
                    try:
                        idx = ids.index(last_seen)
                        # entries antes de idx son más recientes que last_seen
                        unseen = entries[:idx]
                        unseen = unseen[:MAX_ITEMS]
                    except ValueError:
                        # last_seen no encontrado: tratar como todos nuevos (cap MAX_ITEMS)
                        unseen = entries[:MAX_ITEMS]

                if not unseen:
                    continue

                # enviar en orden cronológico (más antiguo primero dentro del lote)
                for entry in reversed(unseen):
                    text = f"Nueva noticia: {entry.get('title','(sin título)')}\n{entry.get('link','')}"
                    for ch in channels:
                        try:
                            channel = await bot.fetch_channel(int(ch))
                            await channel.send(text)
                        except Exception:
                            # no abortar todo por un error de canal
                            pass

                # actualizar last_seen al id del más reciente enviado (unseen[0] es el más nuevo)
                newest_id = entry_id(unseen[0])
                set_last_published(url, newest_id)
        except Exception:
            pass
        await asyncio.sleep(60)  # esperar 60s entre iteraciones