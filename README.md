# BotCarnetConducir

Bot de Telegram para practicar el examen teorico del carnet B en Espana.

## Requisitos

- Python 3.11+
- Token de bot de Telegram en `BOT_TOKEN`

## Configuracion

Variables soportadas:

- `BOT_TOKEN`: token del bot de Telegram
- `BOT_DB_PATH`: ruta de la base de datos SQLite. Por defecto `botcarnet.db`
- `BOT_IMAGES_DIR`: carpeta de imagenes. Por defecto `Imagenes`
- `BOT_DATASET_JSON`: copia local opcional de `data_B.json`
- `BOT_DATASET_URL`: URL alternativa del dataset JSON

Puedes usar un `.env` sencillo:

```env
BOT_TOKEN=tu_token
```

## Arranque

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m botcarnet
```

En el primer arranque el bot inicializa la base de datos e importa preguntas del carnet B. Si no encuentra `BOT_DATASET_JSON`, descarga `data_B.json` desde el repositorio fuente.

## Despliegue 24/7

Si tu ordenador esta apagado, el bot solo puede seguir activo si corre en un servicio externo.

### Opcion recomendada: Railway

Este repo ya incluye `Dockerfile`, asi que Railway puede desplegarlo como servicio persistente.

Configura estas variables:

- `BOT_TOKEN`: token del bot
- `BOT_DB_PATH=/app/data/botcarnet.db`
- `BOT_IMAGES_DIR=/app/Imagenes`
- `BOT_DATASET_JSON=/app/data_B.json`

Adjunta un volumen persistente y montalo en:

- `/app/data`

Pasos:

1. Sube este repo a GitHub.
2. En Railway, crea un proyecto nuevo desde el repo.
3. Railway detectara el `Dockerfile` y arrancara el bot con `python -m botcarnet`.
4. En el servicio, anade las variables anteriores.
5. Crea un volumen y montalo en `/app/data`.
6. Despliega.

Notas:

- `data_B.json` e `Imagenes/` van dentro de la imagen del contenedor.
- La base SQLite se guarda en el volumen, asi no se pierde entre reinicios.
- Si mas adelante quieres escalar o simplificar backups, convendra mover SQLite a Postgres.

Referencias oficiales:

- Railway Build & Deploy: https://docs.railway.com/build-deploy
- Railway Volumes: https://docs.railway.com/volumes

## Fuente de contenido

- Dataset base: `donmerendolo/anki-carnet-conducir`
- Las imagenes locales deben vivir en `Imagenes/` o en la ruta indicada por `BOT_IMAGES_DIR`

## Notas

- Las preguntas propuestas por usuarios se guardan separadas del banco importado.
- Practica y examenes solo usan preguntas importadas activas.
