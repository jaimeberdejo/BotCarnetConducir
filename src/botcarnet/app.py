from __future__ import annotations

import io
import logging
import urllib.request
from pathlib import Path

from telegram.error import BadRequest
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from .db import (
    answer_exam_question,
    clear_exam_session,
    connect,
    count_active_imported_questions,
    count_imported_questions,
    create_exam_session,
    get_exam_question,
    get_exam_review,
    get_metadata,
    get_question_by_id,
    get_random_imported_question,
    get_user_stats,
    init_db,
    list_imported_questions,
    log_answer,
    pick_exam_question_ids,
    record_exam_result,
    reset_user_stats,
    set_bank_question,
    set_question_telegram_file_id,
    set_practice_question,
)
from .importer import import_questions
from .render import (
    bank_detail_keyboard,
    bank_list_keyboard,
    feedback_text,
    format_question,
    main_menu_keyboard,
    question_image_path,
    question_image_url,
    question_keyboard,
    shorten_prompt,
    stats_keyboard,
    stats_reset_keyboard,
)
from .settings import Settings, get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
LOGGER = logging.getLogger(__name__)

OPTION_LABELS = ["A", "B", "C"]
BANK_PAGE_SIZE = 8

BOT_COMMANDS: list[tuple[str, str]] = [
    ("start", "Iniciar y mostrar el menu"),
    ("menu", "Mostrar el menu principal"),
    ("practica", "Practica infinita de preguntas"),
    ("examen", "Hacer un examen tipo test"),
    ("estadisticas", "Ver tus estadisticas"),
    ("banco", "Explorar el banco de preguntas"),
    ("ayuda", "Ver la ayuda y los comandos"),
]

BOT_DESCRIPTION = (
    "Prepara el examen teorico del carnet de conducir (permiso B).\n\n"
    "Comandos disponibles:\n"
    "/practica - Practica infinita de preguntas\n"
    "/examen - Examen tipo test (30 preguntas)\n"
    "/estadisticas - Tus aciertos, fallos y precision\n"
    "/banco - Explorar el banco de preguntas\n"
    "/menu - Menu principal\n"
    "/ayuda - Ayuda"
)

BOT_SHORT_DESCRIPTION = (
    "Test del permiso B: /practica, /examen, /estadisticas y /banco de preguntas."
)


def get_conn(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["conn"]


def get_settings_from_context(context: ContextTypes.DEFAULT_TYPE) -> Settings:
    return context.application.bot_data["settings"]


def download_remote_image(image_url: str) -> io.BytesIO:
    with urllib.request.urlopen(image_url, timeout=30) as response:
        payload = response.read()
    buffer = io.BytesIO(payload)
    buffer.name = Path(image_url).name or "question-image.jpg"
    buffer.seek(0)
    return buffer


async def send_main_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str = "Elige una opcion:"
) -> None:
    target = update.effective_message
    if target is None:
        return
    conn = get_conn(context)
    question_total = count_active_imported_questions(conn)
    synced_at = get_metadata(conn, "dataset_synced_at") or "sin registrar"
    summary = (
        f"Banco actual: {question_total} preguntas\n"
        f"Ultima actualizacion: {synced_at}"
    )
    await target.reply_text(
        f"{text}\n\n{summary}",
        reply_markup=main_menu_keyboard(),
    )


async def send_question(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    question,
    title: str,
    callback_prefix: str,
    footer: str | None = None,
    show_explanation: bool = False,
) -> None:
    message = format_question(question, title, footer=footer, show_explanation=show_explanation)
    image_path = question_image_path(get_settings_from_context(context).images_dir, question)
    image_url = question_image_url(get_settings_from_context(context).image_base_url, question)
    keyboard = question_keyboard(callback_prefix, question.id)
    target = update.effective_message
    if target is None:
        return
    if question.telegram_file_id:
        try:
            await target.reply_photo(
                photo=question.telegram_file_id,
                caption=message,
                reply_markup=keyboard,
            )
            return
        except BadRequest:
            LOGGER.warning("Fallo usando telegram_file_id para la pregunta %s", question.id)
    elif image_path:
        with image_path.open("rb") as image_file:
            sent = await target.reply_photo(
                photo=image_file,
                caption=message,
                reply_markup=keyboard,
            )
            if sent.photo:
                set_question_telegram_file_id(
                    get_conn(context), question.id, sent.photo[-1].file_id
                )
            return
    if image_url:
        try:
            remote_image = download_remote_image(image_url)
            sent = await target.reply_photo(
                photo=remote_image,
                caption=message,
                reply_markup=keyboard,
            )
            if sent.photo:
                set_question_telegram_file_id(
                    get_conn(context), question.id, sent.photo[-1].file_id
                )
            return
        except BadRequest:
            LOGGER.warning(
                "Telegram no pudo descargar la imagen remota de la pregunta %s: %s",
                question.id,
                image_url,
            )
        except Exception:
            LOGGER.warning(
                "No se pudo descargar la imagen remota de la pregunta %s: %s",
                question.id,
                image_url,
                exc_info=True,
            )
    await target.reply_text(message, reply_markup=keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_main_menu(
        update,
        context,
        "Bienvenido a BotCarnetConducir.\nPuedes practicar, hacer examen y revisar tus estadisticas.",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    target = update.effective_message
    if target is None:
        return
    await target.reply_text(BOT_DESCRIPTION, reply_markup=main_menu_keyboard())


async def start_practice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = get_conn(context)
    question = get_random_imported_question(conn)
    if question is None:
        await update.effective_message.reply_text("No hay preguntas importadas todavia.")
        return
    set_practice_question(conn, update.effective_user.id, question.id)
    await send_question(
        update,
        context,
        question,
        "Modo practica",
        "practice",
        footer="Responde y te dire la solucion al instante.",
    )


async def start_exam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = get_conn(context)
    settings = get_settings_from_context(context)
    question_ids = pick_exam_question_ids(conn, settings.exam_question_count)
    if not question_ids:
        await update.effective_message.reply_text("No hay preguntas suficientes para arrancar un examen.")
        return
    create_exam_session(conn, update.effective_user.id, question_ids)
    question, current_index, total, mistakes = get_exam_question(conn, update.effective_user.id)
    if question is None:
        await update.effective_message.reply_text("No se pudo iniciar el examen.")
        return
    await send_question(
        update,
        context,
        question,
        "Examen carnet B",
        "exam",
        footer=f"Pregunta {current_index + 1}/{total}",
    )


async def show_bank(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0) -> None:
    conn = get_conn(context)
    total = count_active_imported_questions(conn)
    if total == 0:
        await update.effective_message.reply_text("No hay preguntas en el banco.")
        return
    total_pages = max((total + BANK_PAGE_SIZE - 1) // BANK_PAGE_SIZE, 1)
    safe_page = min(max(page, 0), total_pages - 1)
    questions = list_imported_questions(conn, safe_page * BANK_PAGE_SIZE, BANK_PAGE_SIZE)
    lines = [
        "Banco de preguntas",
        f"Pagina {safe_page + 1} de {total_pages}",
        "",
        "Selecciona el numero de una pregunta para verla completa:",
        "",
    ]
    for index, question in enumerate(questions, start=1):
        image_marker = " [img]" if question.image_name else ""
        lines.append(
            f"{index}. #{question.id}{image_marker} · {shorten_prompt(question.prompt, limit=110)}"
        )
    keyboard = bank_list_keyboard(questions, safe_page, total_pages)
    message = update.effective_message
    if message is None:
        return
    await message.reply_text("\n".join(lines), reply_markup=keyboard)


async def show_bank_detail(
    update: Update, context: ContextTypes.DEFAULT_TYPE, question_id: int, page: int
) -> None:
    conn = get_conn(context)
    question = get_question_by_id(conn, question_id)
    if question is None:
        await update.effective_message.reply_text("Pregunta no encontrada.")
        return
    set_bank_question(conn, update.effective_user.id, question.id)
    title = f"Banco de preguntas · ID {question.id}"
    image_path = question_image_path(get_settings_from_context(context).images_dir, question)
    image_url = question_image_url(get_settings_from_context(context).image_base_url, question)
    text = format_question(question, title, show_explanation=True)
    keyboard = bank_detail_keyboard(page)
    if image_path:
        with image_path.open("rb") as image_file:
            await update.effective_message.reply_photo(
                photo=image_file, caption=text, reply_markup=keyboard
            )
    elif image_url:
        try:
            remote_image = download_remote_image(image_url)
            await update.effective_message.reply_photo(
                photo=remote_image,
                caption=text,
                reply_markup=keyboard,
            )
        except Exception:
            LOGGER.warning(
                "No se pudo descargar la imagen remota de banco para la pregunta %s: %s",
                question.id,
                image_url,
            )
            await update.effective_message.reply_text(text, reply_markup=keyboard)
    else:
        await update.effective_message.reply_text(text, reply_markup=keyboard)


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = get_conn(context)
    stats = get_user_stats(conn, update.effective_user.id)
    practice_total = stats["practice_correct"] + stats["practice_incorrect"]
    exam_total = stats["exam_correct"] + stats["exam_incorrect"]
    practice_accuracy = (
        (stats["practice_correct"] * 100 / practice_total) if practice_total else 0.0
    )
    exam_accuracy = (stats["exam_correct"] * 100 / exam_total) if exam_total else 0.0
    lines = [
        "Tus estadisticas",
        "",
        f"Practica: {stats['practice_correct']} aciertos / {stats['practice_incorrect']} fallos",
        f"Precision practica: {practice_accuracy:.1f}%",
        "",
        f"Examen: {stats['exam_correct']} aciertos / {stats['exam_incorrect']} fallos",
        f"Precision examen: {exam_accuracy:.1f}%",
        f"Examenes aprobados: {stats['exams_passed']}",
        f"Examenes suspendidos: {stats['exams_failed']}",
    ]
    recent_errors = stats["recent_errors"]
    if recent_errors:
        lines.extend(["", "Preguntas que mas fallas:"])
        for prompt, misses in recent_errors:
            lines.append(f"- ({misses}) {prompt[:90]}")
    await update.effective_message.reply_text("\n".join(lines), reply_markup=stats_keyboard())


async def practice_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, question_id_raw, selected_raw = query.data.split(":")
    question = get_question_by_id(get_conn(context), int(question_id_raw))
    if question is None:
        await query.message.reply_text("Pregunta no encontrada.")
        return
    selected_index = int(selected_raw)
    is_correct = selected_index == question.correct_index
    log_answer(get_conn(context), update.effective_user.id, question.id, "practice", is_correct)
    await query.message.reply_text(
        feedback_text(question, is_correct, selected_index),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Siguiente", callback_data="menu:practice")],
                [InlineKeyboardButton("Menu", callback_data="menu:home")],
            ]
        ),
    )


async def exam_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, _, selected_raw = query.data.split(":")
    result = answer_exam_question(get_conn(context), update.effective_user.id, int(selected_raw))
    if not result.get("exists"):
        await query.message.reply_text("No hay un examen activo.", reply_markup=main_menu_keyboard())
        return
    if result["finished"]:
        review_items = get_exam_review(get_conn(context), update.effective_user.id)
        clear_exam_session(get_conn(context), update.effective_user.id)
        mistakes = int(result["mistakes"])
        total = int(result["total"])
        correct_count = int(result["correct_count"])
        passed = mistakes <= get_settings_from_context(context).exam_fail_threshold
        verdict = "APROBADO" if passed else "SUSPENSO"
        record_exam_result(
            get_conn(context),
            update.effective_user.id,
            total,
            correct_count,
            mistakes,
            passed,
        )
        summary_lines = [
            "Examen terminado",
            f"Resultado: {verdict}",
            f"Aciertos: {correct_count}",
            f"Fallos: {mistakes}",
            f"Total: {total}",
        ]
        wrong_items = [item for item in review_items if not item["is_correct"]]
        if wrong_items:
            summary_lines.extend(["", "Resumen de fallos:"])
            for index, item in enumerate(wrong_items, start=1):
                question = item["question"]
                selected_label = OPTION_LABELS[item["selected_index"]]
                correct_label = OPTION_LABELS[item["correct_index"]]
                summary_lines.extend(
                    [
                        "",
                        f"{index}. {question.prompt}",
                        f"Tu respuesta: {selected_label}",
                        f"Correcta: {correct_label}",
                    ]
                )
                if question.explanation:
                    summary_lines.append(f"Explicacion: {question.explanation}")
        else:
            summary_lines.extend(["", "No has tenido fallos en este examen."])
        await send_long_text(
            query.message,
            "\n".join(summary_lines),
            reply_markup=main_menu_keyboard(),
        )
        return
    next_question, current_index, total, mistakes = get_exam_question(
        get_conn(context), update.effective_user.id
    )
    if next_question is None:
        await query.message.reply_text("No se pudo continuar el examen.", reply_markup=main_menu_keyboard())
        return
    await send_question(
        update,
        context,
        next_question,
        "Examen carnet B",
        "exam",
        footer=f"Pregunta {current_index + 1}/{total}",
    )


async def send_long_text(message, text: str, reply_markup=None) -> None:
    limit = 3500
    chunks = [text[i : i + limit] for i in range(0, len(text), limit)] or [text]
    for index, chunk in enumerate(chunks):
        await message.reply_text(
            chunk,
            reply_markup=reply_markup if index == len(chunks) - 1 else None,
        )


async def bank_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    action = parts[1]
    if action == "noop":
        return
    if action == "list":
        await show_bank(update, context, int(parts[2]))
        return
    if action == "view":
        await show_bank_detail(update, context, int(parts[2]), int(parts[3]))
        return


async def stats_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action = query.data.split(":")[2]
    if action == "confirm":
        await query.message.reply_text(
            "Esto borrara tus estadisticas personales de practica y examen. No afecta al banco de preguntas. Confirmas?",
            reply_markup=stats_reset_keyboard(),
        )
        return
    if action == "cancel":
        await query.message.reply_text("Operacion cancelada.", reply_markup=stats_keyboard())
        return
    if action == "apply":
        reset_user_stats(get_conn(context), update.effective_user.id)
        await query.message.reply_text(
            "Tus estadisticas se han reiniciado.",
            reply_markup=main_menu_keyboard(),
        )
        return


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query = update.callback_query
    await query.answer()
    action = query.data.split(":", 1)[1]
    if action == "practice":
        await start_practice(update, context)
    elif action == "exam":
        await start_exam(update, context)
    elif action == "stats":
        await show_stats(update, context)
    elif action == "home":
        await send_main_menu(update, context)
    return None


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [BotCommand(command, description) for command, description in BOT_COMMANDS]
    )
    await application.bot.set_my_description(BOT_DESCRIPTION)
    await application.bot.set_my_short_description(BOT_SHORT_DESCRIPTION)


def build_application(settings: Settings) -> Application:
    conn = connect(settings.db_path)
    init_db(conn)
    imported = 0
    if count_imported_questions(conn) == 0:
        imported = import_questions(conn, settings.dataset_json, settings.dataset_url, settings.images_dir)
    LOGGER.info("Preguntas importadas en este arranque: %s", imported)
    LOGGER.info("Total preguntas importadas: %s", count_imported_questions(conn))

    application = (
        Application.builder().token(settings.bot_token).post_init(post_init).build()
    )
    application.bot_data["conn"] = conn
    application.bot_data["settings"] = settings

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", start))
    application.add_handler(CommandHandler("practica", start_practice))
    application.add_handler(CommandHandler("examen", start_exam))
    application.add_handler(CommandHandler("estadisticas", show_stats))
    application.add_handler(CommandHandler("banco", show_bank))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CallbackQueryHandler(stats_router, pattern=r"^stats:"))
    application.add_handler(CallbackQueryHandler(practice_answer, pattern=r"^practice:\d+:[012]$"))
    application.add_handler(CallbackQueryHandler(exam_answer, pattern=r"^exam:\d+:[012]$"))
    application.add_handler(CallbackQueryHandler(menu_router, pattern=r"^menu:"))
    return application


def main() -> None:
    settings = get_settings()
    if not settings.images_dir.exists():
        LOGGER.warning("La carpeta de imagenes no existe: %s", settings.images_dir)
    application = build_application(settings)
    application.run_polling()
