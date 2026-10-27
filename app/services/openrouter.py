
from pathlib import Path

from flask import json


PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "running_coach.md"
)

instructions = PROMPT_PATH.read_text(encoding="utf-8")

def generate_training_plan(context_data):
    context = (
        PROMPT_PATH / "running_coach.md"
    ).read_text(encoding="utf-8")

    daily_prompt = (
        PROMPT_PATH / "daily_training_day.md"
    ).read_text(encoding="utf-8")

    messages = [
        {
            "role": "system",
            "content": context,
        },
        {
            "role": "user",
            "content": (
                daily_prompt + "\n\nDonnées pour cette génération :\n" + json.dumps(context_data, ensure_ascii=False)
            ),
        },
    ]

    # Envoyer messages à l'API OpenRouter
    # Retourner le programme
    