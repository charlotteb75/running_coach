


from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class TrainingDayCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    training_day: date 
    is_rest_day: bool = True

class TrainingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    training_type: Literal["running", "strength"]
    training_duration: int = Field(ge=0, strict=True)
    training_completed: bool = False
    content: str | None = None 
    feedback: str | None = None