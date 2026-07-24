from datetime import UTC, date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class Weekday(StrEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class MealOfDay(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"


class Unit(StrEnum):
    GRAM = "g"
    MILLILITRE = "ml"
    TSP = "tsp"
    TBSP = "tbsp"
    UNIT = "unit"


class Ingredient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)

    quantity: float | None = Field(default=..., gt=0)
    unit: Unit | None = None
    to_taste: bool = False

    @field_validator("name")
    @classmethod
    def canonicalise_name(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("ingredient name must not be blank")
        return v

    @model_validator(mode="after")
    def amount_matches_to_taste(self):
        has_quantity = self.quantity is not None
        has_unit = self.unit is not None
        if self.to_taste:
            if has_quantity or has_unit:
                raise ValueError(
                    "to_taste ingredient must not carry a quantity or unit"
                )
        else:
            if not (has_quantity and has_unit):
                raise ValueError(
                    "quantified ingredient requires both quantity and unit"
                )
        return self


class Meal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meal_of_day: MealOfDay
    name: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=200)
    ingredients: list[Ingredient] = Field(min_length=1)
    steps: list[str] = Field(min_length=1)


class Day(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: Weekday
    meals: list[Meal] = Field(min_length=1)


class PlanContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    days: list[Day] = Field(min_length=7, max_length=7)

    @model_validator(mode="after")
    def all_weekdays_present(self):
        seen = {d.day for d in self.days}
        missing = set(Weekday) - seen
        if missing:
            raise ValueError(f"plan missing weekdays: {sorted(m.value for m in missing)}")
        return self

class Plan(PlanContent):
    account_id: int                      
    week_beginning: date                 
    model_name: str                      
    prompt_version: str                  
    schema_version: str = "1.0"          
    plan_id: UUID = Field(default_factory=uuid4)
    generated_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("week_beginning")
    @classmethod
    def must_be_monday(cls, v: date) -> date:
        if v.weekday() != 0:
            raise ValueError("week_beginning must be a Monday")
        return v
    



    



