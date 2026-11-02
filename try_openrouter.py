import argparse
import json
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from app import create_app
from app.jobs.generate_trainings import build_training_context
from app.services.openrouter import generate_training_plan
from app.jobs.save_training_plan import save_training_plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and validate a plan with OpenRouter")
    parser.add_argument("--save", action="store_true", help="Save the validated plan to the configured database")
    args = parser.parse_args()
    app = create_app()
    target_date = date.today() + timedelta(days=1)

    with app.app_context():
        context = build_training_context(target_date)

        print("Context sent :")
        print(json.dumps(context, ensure_ascii=False, indent=2))

        print("\nSending to OpenRouter...")
        result = generate_training_plan(context)

        print("\nAnswer from the model :")
        print(result.model_dump_json(indent=2))

        if args.save:
            save_training_plan(result, target_date)
            print("\nPlan saved to the database.")
        else:
            print("\nValidation successful. Nothing saved (use --save to persist).")
