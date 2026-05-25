from __future__ import annotations

from pathlib import Path

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
            [InlineKeyboardButton("Ver banco", callback_data="menu:bank")],
            [InlineKeyboardButton("Anadir pregunta", callback_data="menu:submit")],
            [InlineKeyboardButton("Estadisticas", callback_data="menu:stats")],
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
