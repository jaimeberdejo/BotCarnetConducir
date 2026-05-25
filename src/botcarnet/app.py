from __future__ import annotations

import logging
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .db import (
    add_user_submission,
    answer_exam_question,
    clear_exam_session,
    connect,
    count_imported_questions,
    create_exam_session,
    get_exam_question,
    get_question_by_id,
    get_random_imported_question,
    get_user_stats,
    init_db,
    log_answer,
    pick_exam_question_ids,
    set_bank_question,
    set_practice_question,
)
from .importer import import_questions
from .models import QuestionDraft
from .render import (
    feedback_text,
    format_question,
    main_menu_keyboard,
    question_image_path,
    question_keyboard,
)
from .settings import Settings, get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
LOGGER = logging.getLogger(__name__)

SUBMIT_PROMPT, SUBMIT_A, SUBMIT_B, SUBMIT_C, SUBMIT_CORRECT, SUBMIT_EXPLANATION = range(6)


def get_conn(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["conn"]


def get_settings_from_context(context: ContextTypes.DEFAULT_TYPE) -> Settings:
    return context.application.bot_data["settings"]


async def send_main_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str = "Elige una opcion:"
) -> None:
    target = update.effective_message
    if target is None:
        return
    await target.reply_text(text, reply_markup=main_menu_keyboard())


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
    keyboard = question_keyboard(callback_prefix, question.id)
    target = update.effective_message
    if target is None:
        return
    if image_path:
        with image_path.open("rb") as image_file:
            await target.reply_photo(photo=image_file, caption=message, reply_markup=keyboard)
    else:
        await target.reply_text(message, reply_markup=keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_main_menu(
        update,
        context,
        "Bienvenido a BotCarnetConducir.\nPuedes practicar, hacer examen, ver preguntas, anadir nuevas y revisar tus estadisticas.",
    )


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
        footer=f"Pregunta {current_index + 1}/{total} · Fallos actuales: {mistakes}",
    )


async def show_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = get_conn(context)
    question = get_random_imported_question(conn)
    if question is None:
        await update.effective_message.reply_text("No hay preguntas en el banco.")
        return
    set_bank_question(conn, update.effective_user.id, question.id)
    title = f"Banco de preguntas · ID {question.id}"
    image_path = question_image_path(get_settings_from_context(context).images_dir, question)
    text = format_question(question, title, show_explanation=True)
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Otra pregunta", callback_data="menu:bank")]]
    )
    if image_path:
        with image_path.open("rb") as image_file:
            await update.effective_message.reply_photo(photo=image_file, caption=text, reply_markup=keyboard)
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
    ]
    recent_errors = stats["recent_errors"]
    if recent_errors:
        lines.extend(["", "Preguntas que mas fallas:"])
        for prompt, misses in recent_errors:
            lines.append(f"- ({misses}) {prompt[:90]}")
    await update.effective_message.reply_text("\n".join(lines), reply_markup=main_menu_keyboard())


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
    question = result["question"]
    await query.message.reply_text(
        feedback_text(question, bool(result["is_correct"]), int(selected_raw))
    )
    if result["finished"]:
        clear_exam_session(get_conn(context), update.effective_user.id)
        mistakes = int(result["mistakes"])
        total = int(result["total"])
        correct_count = int(result["correct_count"])
        passed = mistakes <= get_settings_from_context(context).exam_fail_threshold
        verdict = "APROBADO" if passed else "SUSPENSO"
        await query.message.reply_text(
            "\n".join(
                [
                    "Examen terminado",
                    f"Resultado: {verdict}",
                    f"Aciertos: {correct_count}",
                    f"Fallos: {mistakes}",
                    f"Total: {total}",
                ]
            ),
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
        footer=f"Pregunta {current_index + 1}/{total} · Fallos actuales: {mistakes}",
    )


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query = update.callback_query
    await query.answer()
    action = query.data.split(":", 1)[1]
    if action == "practice":
        await start_practice(update, context)
    elif action == "exam":
        await start_exam(update, context)
    elif action == "bank":
        await show_bank(update, context)
    elif action == "stats":
        await show_stats(update, context)
    elif action == "submit":
        await query.message.reply_text("Escribe el enunciado de la nueva pregunta.")
        return SUBMIT_PROMPT
    elif action == "home":
        await send_main_menu(update, context)
    return None


async def cancel_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("submission", None)
    await update.effective_message.reply_text("Alta cancelada.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END


async def submit_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["submission"] = {"prompt": update.effective_message.text.strip()}
    await update.effective_message.reply_text("Respuesta A:")
    return SUBMIT_A


async def submit_a(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["submission"]["option_a"] = update.effective_message.text.strip()
    await update.effective_message.reply_text("Respuesta B:")
    return SUBMIT_B


async def submit_b(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["submission"]["option_b"] = update.effective_message.text.strip()
    await update.effective_message.reply_text("Respuesta C:")
    return SUBMIT_C


async def submit_c(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["submission"]["option_c"] = update.effective_message.text.strip()
    await update.effective_message.reply_text("Opcion correcta: responde A, B o C.")
    return SUBMIT_CORRECT


async def submit_correct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.effective_message.text.strip().upper()
    mapping = {"A": 0, "B": 1, "C": 2}
    if answer not in mapping:
        await update.effective_message.reply_text("Respuesta no valida. Usa A, B o C.")
        return SUBMIT_CORRECT
    context.user_data["submission"]["correct_index"] = mapping[answer]
    await update.effective_message.reply_text("Explicacion opcional. Si no quieres, escribe SKIP.")
    return SUBMIT_EXPLANATION


async def submit_explanation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    explanation = update.effective_message.text.strip()
    if explanation.upper() == "SKIP":
        explanation = ""
    data = context.user_data.pop("submission")
    draft = QuestionDraft(
        prompt=data["prompt"],
        option_a=data["option_a"],
        option_b=data["option_b"],
        option_c=data["option_c"],
        correct_index=data["correct_index"],
        explanation=explanation,
        image_name=None,
        source_type="user",
        source_id=None,
        status="pending",
        submitted_by=update.effective_user.id,
    )
    add_user_submission(get_conn(context), draft)
    await update.effective_message.reply_text(
        "Pregunta guardada como propuesta pendiente de revision.",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


def build_application(settings: Settings) -> Application:
    conn = connect(settings.db_path)
    init_db(conn)
    imported = import_questions(conn, settings.dataset_json, settings.dataset_url, settings.images_dir)
    LOGGER.info("Preguntas importadas en este arranque: %s", imported)
    LOGGER.info("Total preguntas importadas: %s", count_imported_questions(conn))

    application = Application.builder().token(settings.bot_token).build()
    application.bot_data["conn"] = conn
    application.bot_data["settings"] = settings

    submission_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu_router, pattern=r"^menu:submit$")],
        states={
            SUBMIT_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_prompt)],
            SUBMIT_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_a)],
            SUBMIT_B: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_b)],
            SUBMIT_C: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_c)],
            SUBMIT_CORRECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_correct)],
            SUBMIT_EXPLANATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, submit_explanation)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_submission)],
        per_message=False,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", start))
    application.add_handler(submission_handler)
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
