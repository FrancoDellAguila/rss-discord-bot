FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# dependencias del sistema (si hacen falta para alguna librería)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# copiar archivos de requerimientos primero para aprovechar layer cache
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copiar el resto
COPY . .

# runtime por defecto (override en docker-compose)
CMD ["python", "bot.py"]