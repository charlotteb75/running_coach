


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
    training_duration: int = Field(gt=0, strict=True)
    training_completed: bool = False
    content: str | None = Field(min_length=10)
    feedback: str | None = None

class TrainingDayUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_rest_day: bool | None = Field(strict=True)
    
class TrainingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_training_day: int | None = Field(default=None, strict=True)
    training_type: str | None = Field(default=None, strict=True)
    training_duration: int | None = Field(gt=0, default=None, strict=True)
    content: str| None = Field(default=None, strict=True)
    training_completed: bool | None = Field(default=None, strict=True)
    feedback: str | None = Field(default=None, strict=True)

    @model_validator(mode="after")
    def require_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be present")
        return self
    
class MilestoneCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    achieved: bool = Field(default=False, strict=True)
    date_achieved: date | None = Field(default=None)
    date_estimated: date
    milestone_distance: float | None = Field(gt=0, default=None, strict=True)
    milestone_speed: float | None = Field(gt=0, default=None, strict=True)
    milestone_type: Literal["distance", "pace", "pace on distance"]

    @model_validator(mode="after")
    def require_speed_or_distance(self) -> Self:
        if self.milestone_type == "distance":
            if self.milestone_distance is None:
                raise ValueError("Distance must be set for this milestone type")
            if self.milestone_speed is not None:
                raise ValueError("Speed must be null for this milestone type")
            
        elif self.milestone_type == "speed":
            if self.milestone_speed is None:
                raise ValueError("Speed must be set for this milestone type")
            if self.milestone_distance is not None:
                raise ValueError("Distance must be null for this milestone type")
            
        elif self.milestone_type == "speed on distance":
            if self.milestone_speed is None | self.milestone_distance is None:
                raise ValueError("Speed and distance must be specified for this milestone type")

        return self
    
class MilestoneUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    achieved: bool = Field(strict=True)
    date_achieved: date

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)