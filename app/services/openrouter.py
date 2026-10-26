
from pathlib import Path


PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "running_coach.md"
)

instructions = PROMPT_PATH.read_text(encoding="utf-8")

def generate_training_plan()
    