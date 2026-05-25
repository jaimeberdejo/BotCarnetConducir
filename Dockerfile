FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY data_B.json ./data_B.json
# Las imagenes no se empaquetan: se sirven desde GitHub raw (BOT_IMAGE_BASE_URL)
# y Telegram las cachea por file_id tras el primer envio.

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

CMD ["python", "-m", "botcarnet"]
