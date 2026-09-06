# BotCarnetConducir

Bot de Telegram para preparar el examen teórico del permiso de conducir B en España.

Práctica infinita, exámenes tipo DGT de 30 preguntas con suspenso a los 4 fallos, banco de preguntas navegable y estadísticas personales. Todo dentro de un chat de Telegram, sin app web ni Anki.

Este repositorio es **autocontenido**: incluye el código del bot, el dataset de preguntas (`data_B.json`) y las 2.776 imágenes del banco (`Imagenes/`). No necesitas ningún otro repo ni servicio externo.

---

## Índice

- [Qué hace](#qué-hace)
- [Requisitos](#requisitos)
- [Tutorial 1 — Crear tu propio bot de Telegram](#tutorial-1--crear-tu-propio-bot-de-telegram)
- [Tutorial 2 — Montarlo en local](#tutorial-2--montarlo-en-local)
- [Variables de entorno](#variables-de-entorno)
- [Cómo funcionan las imágenes](#cómo-funcionan-las-imágenes)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Tests](#tests)
- [Problemas frecuentes](#problemas-frecuentes)
- [Licencia y atribución](#licencia-y-atribución)

---

## Qué hace

| Comando | Qué hace |
|---|---|
| `/start`, `/menu` | Menú principal con botones y estado del banco de preguntas |
| `/practica` | Práctica infinita: pregunta aleatoria, respondes A/B/C y ves si has acertado con la explicación |
| `/examen` | Examen de 30 preguntas al estilo DGT. Se suspende con más de 3 fallos |
| `/estadisticas` | Aciertos, fallos y precisión, separados entre práctica y examen. Se pueden reiniciar |
| `/banco` | Navegar y consultar el banco completo de preguntas con su explicación |
| `/ayuda` | Ayuda y lista de comandos |

Detalles de implementación que conviene conocer:

- **Sin servidor de estado**: todo vive en un SQLite local (`botcarnet.db`). Las estadísticas son por `user_id` de Telegram.
- **Las imágenes se cachean solas**: la primera vez que una pregunta con foto se envía, Telegram devuelve un `file_id` que se guarda en la base de datos. A partir de ahí no se vuelve a subir el fichero, se reenvía el `file_id`. Es mucho más rápido y no consume ancho de banda.
- **El banco es una copia propia**: el dataset se importa una vez a SQLite. Puedes editar preguntas sin depender del repositorio original.

---

## Requisitos

- Python 3.11 o superior
- Una cuenta de Telegram
- Git

No hace falta base de datos, Docker ni cuenta en ningún proveedor cloud para usarlo en local.

---

## Tutorial 1 — Crear tu propio bot de Telegram

Cada persona necesita **su propio bot** con su propio token. El token es una credencial: quien lo tenga controla el bot, así que no lo compartas ni lo subas a GitHub.

### Paso 1. Habla con @BotFather

@BotFather es el bot oficial de Telegram para crear bots.

1. Abre Telegram y busca **@BotFather** (el que tiene la marca de verificación azul).
2. Pulsa **Iniciar** / envía `/start`.

### Paso 2. Crea el bot

1. Envía `/newbot`.
2. BotFather te pide un **nombre visible**. Es el que verá la gente en el chat. Ejemplo: `Test Carnet B`.
3. Después te pide un **username**. Tiene que ser único en todo Telegram y **terminar en `bot`**. Ejemplo: `mi_test_carnetb_bot`.
   - Si te dice `Sorry, this username is already taken`, prueba otro.
4. BotFather responde con un mensaje que contiene el token, con esta pinta:

   ```
   Use this token to access the HTTP API:
   123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
   ```

   **Copia ese token**, lo necesitas en el Tutorial 2.

### Paso 3. (Opcional) Ajustes del bot

Con BotFather puedes personalizarlo:

- `/setuserpic` — foto de perfil del bot.
- `/setdescription` — texto que se ve antes de pulsar «Iniciar».
- `/setabouttext` — descripción corta del perfil.
- `/setprivacy` — no hace falta tocarlo: este bot funciona en chats privados.

No necesitas configurar los comandos a mano: **el propio bot registra su menú de comandos, su descripción y su descripción corta al arrancar**, así que aparecerán solos la primera vez que lo ejecutes.

### Paso 4. Si pierdes el token

Vuelve a @BotFather → `/mybots` → elige tu bot → **API Token**. Si crees que se ha filtrado, ahí mismo puedes usar **Revoke current token** para invalidarlo y generar uno nuevo.

---

## Tutorial 2 — Montarlo en local

### Paso 1. Clona el repositorio

```bash
git clone https://github.com/jaimeberdejo/BotCarnetConducir.git
cd BotCarnetConducir
```

> El repo pesa unos 150 MB porque incluye las imágenes de las preguntas. Si solo quieres el código y prefieres que las imágenes se descarguen bajo demanda desde GitHub, clona sin historial y borra la carpeta:
> ```bash
> git clone --depth 1 https://github.com/jaimeberdejo/BotCarnetConducir.git
> cd BotCarnetConducir && rm -rf Imagenes
> ```
> El bot detecta que no hay imágenes locales y las baja de la URL pública. Ver [Cómo funcionan las imágenes](#cómo-funcionan-las-imágenes).

### Paso 2. Entorno virtual e instalación

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

Esto instala la única dependencia real: `python-telegram-bot` (v21).

### Paso 3. Configura tu token

Copia la plantilla y pega el token que te dio BotFather:

```bash
cp .env.example .env
```

Edita `.env`:

```env
BOT_TOKEN=123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```

`.env` está en `.gitignore`, así que no se sube al repositorio. Alternativamente puedes exportar la variable en tu shell (`export BOT_TOKEN=...`) en lugar de usar el fichero.

### Paso 4. Arranca el bot

```bash
python -m botcarnet
```

En el **primer arranque** el bot:

1. Crea `botcarnet.db` (SQLite).
2. Importa las 2.947 preguntas de `data_B.json`.
3. Registra el menú de comandos y la descripción en Telegram.
4. Se queda escuchando (`polling`).

Verás algo así en la consola:

```
2026-01-01 12:00:00 INFO botcarnet.app :: Preguntas importadas en este arranque: 2947
2026-01-01 12:00:00 INFO botcarnet.app :: Total preguntas importadas: 2947
```

Los arranques siguientes son instantáneos: la base ya está poblada y la importación es idempotente (hace *upsert*, no duplica).

### Paso 5. Pruébalo

Abre Telegram, busca tu bot por el username que elegiste (`@mi_test_carnetb_bot`), pulsa **Iniciar** y envía `/practica`.

Para pararlo, `Ctrl+C` en la terminal. El bot solo responde mientras el proceso esté corriendo: si cierras la terminal o apagas el ordenador, deja de responder. Para tenerlo activo de forma permanente hay que ejecutarlo en una máquina que no se apague; el `Dockerfile` incluido sirve para desplegarlo en cualquier plataforma que corra contenedores.

---

## Variables de entorno

Todas son opcionales salvo `BOT_TOKEN`.

| Variable | Por defecto | Para qué sirve |
|---|---|---|
| `BOT_TOKEN` | *(obligatoria)* | Token del bot que te da @BotFather. Sin ella el arranque falla con `BOT_TOKEN no configurado.` |
| `BOT_DB_PATH` | `botcarnet.db` | Ruta del SQLite. En despliegues, apúntala a un volumen persistente |
| `BOT_IMAGES_DIR` | `Imagenes` | Carpeta de imágenes locales. Si no existe, se usa la URL remota |
| `BOT_DATASET_JSON` | `data_B.json` | Copia local del dataset. Si no existe, se descarga de `BOT_DATASET_URL` |
| `BOT_DATASET_URL` | Dataset de `donmerendolo/anki-carnet-conducir` | De dónde bajar el JSON si no hay copia local |
| `BOT_IMAGE_BASE_URL` | `.../BotCarnetConducir/master/Imagenes/` | Base para servir imágenes por HTTP cuando no hay copia local |

Dos constantes de examen viven en el código (`src/botcarnet/settings.py`) por si quieres ajustarlas: `exam_question_count` (30) y `exam_fail_threshold` (3).

---

## Cómo funcionan las imágenes

El bot resuelve la foto de cada pregunta en tres niveles, en este orden:

1. **`telegram_file_id` guardado en la base de datos** — si la pregunta ya se envió antes, se reenvía el identificador de Telegram. Instantáneo, sin tráfico.
2. **Fichero local en `BOT_IMAGES_DIR`** — si tienes la carpeta `Imagenes/` clonada. Se sube el fichero y se guarda el `file_id` resultante para la próxima vez.
3. **Descarga desde `BOT_IMAGE_BASE_URL`** — se baja de `raw.githubusercontent.com` y se envía, guardando también el `file_id`.

Si los tres fallan, la pregunta se manda como texto: nunca se rompe el flujo por una imagen.

Esto significa que **puedes desplegar sin las imágenes** para que el contenedor pese poco (es justo lo que hace el `Dockerfile`, que no las copia): se sirven desde GitHub la primera vez y a partir de ahí van por `file_id`.

Si haces fork del repo, acuérdate de apuntar `BOT_IMAGE_BASE_URL` a **tu** fork, y de que el repo sea público — `raw.githubusercontent.com` no sirve ficheros de repositorios privados.

---

## Estructura del proyecto

```
BotCarnetConducir/
├── src/botcarnet/
│   ├── __main__.py     # Punto de entrada: python -m botcarnet
│   ├── app.py          # Handlers de Telegram, menús y flujos de práctica/examen
│   ├── db.py           # Esquema SQLite y todas las consultas
│   ├── importer.py     # Carga data_B.json al banco (upsert idempotente)
│   ├── models.py       # Question / QuestionDraft
│   ├── render.py       # Formato de mensajes y teclados inline
│   └── settings.py     # Configuración por entorno + carga de .env
├── tests/              # Tests del importador
├── Imagenes/           # 2.776 imágenes del banco de preguntas
├── data_B.json         # Dataset de preguntas del permiso B
├── Dockerfile          # Imagen para despliegue (sin Imagenes/)
└── pyproject.toml
```

---

## Tests

```bash
pip install pytest
pytest
```

Cubren la normalización del dataset y la resolución de nombres de imagen del importador (el dataset original mezcla extensiones `.jpg` y `.JPG`).

---

## Problemas frecuentes

**`RuntimeError: BOT_TOKEN no configurado.`**
No hay `.env` en el directorio desde el que lanzas el comando, o la variable está vacía. Ojo: `.env` se busca en el **directorio de trabajo actual**, no en el del paquete. Ejecuta `python -m botcarnet` desde la raíz del repo.

**`telegram.error.InvalidToken`**
El token está mal copiado (suele faltar un trozo, o sobra un espacio). Recupéralo con `/mybots` en @BotFather.

**`Conflict: terminated by other getUpdates request`**
Tienes dos instancias del mismo bot corriendo a la vez — por ejemplo, una en local y otra en un servidor. Telegram solo permite un consumidor de updates por token. Para una de las dos.

**El bot no responde y no hay error en consola**
Comprueba que estás escribiendo al bot correcto (el username exacto que creaste) y que pulsaste **Iniciar**.

**Las preguntas llegan sin foto**
Se está usando la ruta remota y la descarga falla. Verifica que `BOT_IMAGE_BASE_URL` apunta a un repositorio **público** y que la URL termina en `/`. Prueba a abrir en el navegador `https://raw.githubusercontent.com/jaimeberdejo/BotCarnetConducir/master/Imagenes/B_32.jpg`.

**Quiero empezar de cero**
Borra `botcarnet.db` y vuelve a arrancar. Se reimporta el banco y se pierden todas las estadísticas.

---

## Licencia y atribución

Este proyecto se distribuye bajo **GPL-3.0** (ver [`LICENSE`](LICENSE)).

El banco de preguntas (`data_B.json`) y las imágenes (`Imagenes/`) proceden de [**donmerendolo/anki-carnet-conducir**](https://github.com/donmerendolo/anki-carnet-conducir), publicado bajo GPL-3.0. Se redistribuyen aquí bajo la misma licencia, con atribución al proyecto original.

Es material de estudio no oficial: no está avalado por la DGT ni sustituye a los tests oficiales.
