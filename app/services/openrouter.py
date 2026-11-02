
import os
from datetime import date
from pathlib import Path

import json
from pydantic import ValidationError
from openai import OpenAI
from app.schemas.llm_schemas import GeneratedPlan, validate_training_plan


PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts"

def generate_training_plan(context_data):
    context = (
        PROMPT_PATH / "running_coach.md"
    ).read_text(encoding="utf-8")

    daily_prompt = (
        PROMPT_PATH / "daily_training_day.md"
    ).read_text(encoding="utf-8")
    daily_prompt += (
        "\nRetourne uniquement un objet JSON conforme à ce schéma, sans commentaire :\n"
        + json.dumps(GeneratedPlan.model_json_schema(), ensure_ascii=False)
    )

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

    target_date = date.fromisoformat(context_data["target_date"])

    with OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_KEY"],
        timeout=120.0
    ) as client:
        # One initial generation, then two corrections maximum.
        for attempt in range(3):
            response = client.chat.completions.create(
                model=os.environ["OPENROUTER_MODEL"],
                messages=messages,
            )

            if not response.choices:
                raise RuntimeError("OpenRouter did not return a response")
            choice = response.choices[0]
            if choice.finish_reason != "stop":
                raise RuntimeError(
                    f"Generation did not end normally : {choice.finish_reason}"
                )
            content = choice.message.content
            if not content:
                raise RuntimeError("OpenRouter returned an empty content")

            try:
                return validate_training_plan(content, target_date)
            except ValueError as error:
                if attempt == 2:
                    raise

                if isinstance(error, ValidationError):
                    errors = [
                        {
                            "field": ".".join(str(part) for part in item["loc"]),
                            "message": item["msg"],
                        }
                        for item in error.errors()
                    ]
                else:
                    errors = [{"field": "plan", "message": str(error)}]

                messages = messages + [
                    {"role": "assistant", "content": content},
                    {
                        "role": "user",
                        "content": (
                            "La réponse a échoué à la validation :\n"
                            + json.dumps(errors, ensure_ascii=False)
                            + "\nCorrige les erreurs et retourne le JSON complet, sans "
                            "balises Markdown ni commentaire. Respecte le schéma et "
                            "target_date. Conserve les éléments valides du programme. "
                            "Pour créer un training, utilise id_training=null. Pour "
                            "une modification, utilise un identifiant entier fourni "
                            "dans le contexte. N'invente aucun identifiant. Les "
                            "milestones retournées doivent déjà exister dans le contexte."
                        ),
                    },
                ]
