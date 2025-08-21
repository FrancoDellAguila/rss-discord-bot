# RSS Discord Bot
Bot de Discord que permite suscribirse a feeds RSS desde canales.

## Estructura principal
- bot.py — bot de Discord
- db.py — acceso a SQLite y utilidades de suscripción
- poller.py — tarea que consulta feeds y notifica canales
- requirements.txt — dependencias

## Requisitos
- Python 3.8+
- Token de bot de Discord

## Instalación (Windows, PowerShell)
1. Abrir PowerShell
2. Crear y activar entorno virtual:
   - python -m venv .venv
   - .\.venv\Scripts\Activate
3. Instalar dependencias:
   - pip install -r requirements.txt
4. Exportar token (temporal en la sesión actual):
   - $env:DISCORD_TOKEN="TU_TOKEN_AQUI"
   - O permanentemente: setx DISCORD_TOKEN "TU_TOKEN_AQUI" (requiere reiniciar terminal)

## Ejecutar

- Ejecutar el bot (incluye poller que notificará a los canales suscritos):
  - .\.venv\Scripts\python bot.py

## Uso

Bot (en cualquier canal del servidor donde el bot tenga permisos):
- `!subscribe <feed_url>` — suscribe el canal al feed.
- `!unsubscribe <feed_url>` — quita la suscripción del canal.
- `!list` — lista los feeds suscritos en el canal.
- `!recent <feed_url> <cantidad de noticias>`


## Notas
- La DB `subscriptions.db` se crea automáticamente en el mismo directorio.
- El poller guarda un identificador del último ítem visto para evitar duplicados; por simplicidad solo envía el ítem más reciente por iteración.
- Ajusta el intervalo y la lógica del poller en `poller.py` si necesitas enviar varios ítems o cambiar la frecuencia.

## Problemas comunes
- Error por token: asegúrate de tener `DISCORD_TOKEN` en el entorno y que el bot esté invitado al servidor con permisos para enviar mensajes.
- Permisos de canal: el bot necesita permiso `Send Messages` para postear en el canal.


## Docker

1. Construir imagen y levantar servicios (API + bot):
   - docker compose up --build -d

2. Variables de entorno:
   - Colocar `DISCORD_TOKEN=...` y otras variables necesarias en `.env` en el mismo directorio.
   - IMPORTANTE: no subir `.env` al repositorio; rota el token si estuvo expuesto.

3. Servicios:
   - API disponible en http://localhost:8000
   - Bot se conecta con el token y usa la misma base `subscriptions.db` (persistida en el host).

4. Logs:
   - Ver logs del bot: docker compose logs -f bot
   - Ver logs del API: docker compose logs -f api

5. Detener:
   - docker compose down

Notas:
- El contenedor comparte `subscriptions.db` como volumen con el host; si prefieres usar un volumen Docker, cambia el `volumes:` en docker-compose.
- Si necesitas ajustar N items por poll o puerto, establece variables de entorno y modifica `docker-compose.yml` según sea necesario.
