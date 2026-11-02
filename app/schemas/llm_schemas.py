"""Validation of generated plans before any database write."""

from datetime import date
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GeneratedTraining(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id_training: int | None = Field(default=None, gt=0, strict=True)
    training_type: Literal["running", "strength"]
    title: str = Field(min_length=1)
    training_duration: int = Field(gt=0, strict=True)
    training_distance: float | None = Field(default=None, gt=0, allow_inf_nan=False, strict=True)
    description: str = Field(min_length=1)

    @model_validator(mode="after")
    def check_distance(self) -> Self:
        if self.training_type == "running" and self.training_distance is None:
            raise ValueError("Running trainings must include training_distance in km")
        if self.training_type == "strength" and self.training_distance is not None:
            raise ValueError("Strength trainings cannot include a distance")
        return self


class GeneratedTrainingDay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    training_day_date: date
    trainings: list[GeneratedTraining] = Field(max_length=2)

    @model_validator(mode="after")
    def unique_types(self) -> Self:
        types = [training.training_type for training in self.trainings]
        if len(types) != len(set(types)):
            raise ValueError("Only one training of each type is allowed per day")
        return self


class GeneratedMilestone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_milestone: int = Field(gt=0, strict=True)
    date_estimated: date
    milestone_type: Literal["distance", "pace", "pace on distance"]
    milestone_distance: float | None = Field(default=None, gt=0, allow_inf_nan=False, strict=True)
    milestone_speed: float | None = Field(default=None, gt=0, allow_inf_nan=False, strict=True)

    @model_validator(mode="after")
    def check_target(self) -> Self:
        if self.milestone_type in ("distance", "pace on distance") and self.milestone_distance is None:
            raise ValueError("This milestone requires a distance")
        if self.milestone_type in ("pace", "pace on distance") and self.milestone_speed is None:
            raise ValueError("This milestone requires a pace")
        if self.milestone_type == "distance" and self.milestone_speed is not None:
            raise ValueError("A distance milestone cannot include a pace")
        if self.milestone_type == "pace" and self.milestone_distance is not None:
            raise ValueError("A pace milestone cannot include a distance")
        return self


class GeneratedPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    updated_training_days: list[GeneratedTrainingDay]
    updated_milestones: list[GeneratedMilestone]

    @model_validator(mode="after")
    def unique_entries(self) -> Self:
        dates = [day.training_day_date for day in self.updated_training_days]
        training_ids = [
            training.id_training
            for day in self.updated_training_days
            for training in day.trainings
            if training.id_training is not None
        ]
        milestone_ids = [milestone.id_milestone for milestone in self.updated_milestones]
        for values in (dates, training_ids, milestone_ids):
            if len(values) != len(set(values)):
                raise ValueError("Dates and identifiers must not appear more than once")
        return self


def validate_training_plan(content: str, target_date: date) -> GeneratedPlan:
    plan = GeneratedPlan.model_validate_json(content)
    if any(day.training_day_date < target_date for day in plan.updated_training_days):
        raise ValueError("The plan cannot modify days before target_date")
    if any(m.date_estimated < target_date for m in plan.updated_milestones):
        raise ValueError("Milestone estimates cannot precede target_date")
    return plan
