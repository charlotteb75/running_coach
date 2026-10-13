


from datetime import date
from typing import Literal, Self
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TrainingDayCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    training_day_date: date 
    is_rest_day: bool = True

class TrainingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_training_day: int = Field(ge=0, strict=True)
    training_type: Literal["running", "strength"]
    training_duration: int = Field(ge=0, strict=True)
    training_completed: bool = False
    content: str | None = Field(min_length=10)
    feedback: str | None = None

class TrainingDayUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_rest_day: bool | None = Field(strict=True)
    
class TrainingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_training_day: int| None = Field(default=None, strict=True)
    training_type: str | None = Field(default=None, strict=True)
    training_duration: int | None = Field(ge=0, default=None, strict=True)
    content: str| None = Field(default=None, strict=True)
    training_completed: bool | None = Field(default=None, strict=True)
    feedback: str | None = Field(default=None, strict=True)

    @model_validator(mode="after")
    def require_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be present")
        return self