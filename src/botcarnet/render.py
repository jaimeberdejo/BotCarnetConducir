from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .models import Question


OPTION_LABELS = ["A", "B", "C"]


def question_keyboard(prefix: str, question_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("A", callback_data=f"{prefix}:{question_id}:0"),
                InlineKeyboardButton("B", callback_data=f"{prefix}:{question_id}:1"),
                InlineKeyboardButton("C", callback_data=f"{prefix}:{question_id}:2"),
            ]
        ]
    )


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Practica infinita", callback_data="menu:practice")],
            [InlineKeyboardButton("Hacer examen", callback_data="menu:exam")],
            [InlineKeyboardButton("Estadisticas", callback_data="menu:stats")],
        ]
    )


def bank_list_keyboard(items: list[Question], page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    current_row: list[InlineKeyboardButton] = []
    for index, question in enumerate(items, start=1):
        current_row.append(
            InlineKeyboardButton(
                str(index),
                callback_data=f"bank:view:{question.id}:{page}",
            )
        )
        if len(current_row) == 4:
            rows.append(current_row)
            current_row = []
    if current_row:
        rows.append(current_row)
    nav_row_top: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row_top.append(InlineKeyboardButton("<< 1", callback_data="bank:list:0"))
    if page >= 10:
        nav_row_top.append(
            InlineKeyboardButton(f"< 10", callback_data=f"bank:list:{max(page - 10, 0)}")
        )
    if page > 0:
        nav_row_top.append(
            InlineKeyboardButton("Anterior", callback_data=f"bank:list:{page - 1}")
        )
    if nav_row_top:
        rows.append(nav_row_top)

    if page > 0:
        pass
    nav_row_bottom: list[InlineKeyboardButton] = [
        InlineKeyboardButton(f"{page + 1}/{max(total_pages, 1)}", callback_data="bank:noop")
    ]
    if page + 1 < total_pages:
        nav_row_bottom.append(
            InlineKeyboardButton("Siguiente", callback_data=f"bank:list:{page + 1}")
        )
    if page + 10 < total_pages:
        nav_row_bottom.append(
            InlineKeyboardButton(
                "10 >", callback_data=f"bank:list:{min(page + 10, total_pages - 1)}"
            )
        )
    if page + 1 < total_pages:
        nav_row_bottom.append(
            InlineKeyboardButton(
                f"{total_pages} >>", callback_data=f"bank:list:{total_pages - 1}"
            )
        )
    rows.append(nav_row_bottom)
    rows.append([InlineKeyboardButton("Menu", callback_data="menu:home")])
    return InlineKeyboardMarkup(rows)


def bank_detail_keyboard(page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Volver a la lista", callback_data=f"bank:list:{page}")],
            [InlineKeyboardButton("Menu", callback_data="menu:home")],
        ]
    )


def stats_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Reiniciar estadisticas", callback_data="stats:reset:confirm")],
            [InlineKeyboardButton("Menu", callback_data="menu:home")],
        ]
    )


def stats_reset_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Si, reiniciar", callback_data="stats:reset:apply"),
                InlineKeyboardButton("Cancelar", callback_data="stats:reset:cancel"),
            ]
        ]
    )


def format_question(
    question: Question,
    title: str,
    footer: str | None = None,
    show_explanation: bool = False,
) -> str:
    lines = [
        title,
        "",
        question.prompt,
        "",
        f"A. {question.option_a}",
        f"B. {question.option_b}",
        f"C. {question.option_c}",
    ]
    if show_explanation and question.explanation:
        lines.extend(["", f"Explicacion: {question.explanation}"])
    if footer:
        lines.extend(["", footer])
    return "\n".join(lines)


def feedback_text(question: Question, is_correct: bool, selected_index: int) -> str:
    result = "Correcta" if is_correct else "Incorrecta"
    selected_label = OPTION_LABELS[selected_index]
    correct_label = OPTION_LABELS[question.correct_index]
    lines = [
        f"{result}.",
        f"Tu respuesta: {selected_label}",
        f"Respuesta correcta: {correct_label}",
    ]
    if question.explanation:
        lines.append(f"Explicacion: {question.explanation}")
    return "\n".join(lines)


def question_image_path(images_dir: Path, question: Question) -> Path | None:
    if not question.image_name:
        return None
    path = images_dir / question.image_name
    return path if path.exists() else None


def question_image_url(base_url: str, question: Question) -> str | None:
    if not question.image_name:
        return None
    return f"{base_url.rstrip('/')}/{quote(question.image_name)}"


def shorten_prompt(text: str, limit: int = 90) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."
