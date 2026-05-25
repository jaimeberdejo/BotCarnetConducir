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

## Fuente de contenido

- Dataset base: `donmerendolo/anki-carnet-conducir`
- Las imagenes locales deben vivir en `Imagenes/` o en la ruta indicada por `BOT_IMAGES_DIR`

## Notas

- Las preguntas propuestas por usuarios se guardan separadas del banco importado.
- Practica y examenes solo usan preguntas importadas activas.
