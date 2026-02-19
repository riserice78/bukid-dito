from pydantic import BaseModel, Field
from typing import List

##class VegetableMarketPrice(BaseModel):
#    low: float = Field(description="Lowest market price per kg")
#    high: float = Field(description="Highest market price per kg")

class VegetableSchedule(BaseModel):
    """Schema for a single vegetable's planting and harvesting schedule"""
    vegetable: str = Field(description="Name of the vegetable")
    plant_start_month: int = Field(description="Month to start planting (1-12)", ge=1, le=12)
    plant_end_month: int = Field(description="Month to end planting (1-12)", ge=1, le=12)
    harvest_start_month: int = Field(description="Month to start harvesting (1-12)", ge=1, le=12)
    harvest_end_month: int = Field(description="Month to end harvesting (1-12)", ge=1, le=12)
    companion_plant: str = Field(description="Name of the companion plant with reason")
#    reason: str = Field(description="Why the vegetable would thrive in the location")

class VegetableScheduleOutput(BaseModel):
    """Complete output schema for all vegetables"""
    vegetable_schedule: List[VegetableSchedule]


class VegetablePreparationItem(BaseModel):
    vegetable: str = Field(..., description="Name of the vegetable")
    can_grow_from_scraps: bool = Field(..., description="Whether it can be grown from food scraps")
    scraps_how: str = Field(..., description="How to grow from food scraps, or 'N/A' if not applicable")
    prep_lead_time: str = Field(..., description="Best time to start preparation before planting, e.g. '2–3 weeks before planting'")
    special_tips: str = Field(..., description="Special tips for the user's planting medium")

class VegetablePreparationOutput(BaseModel):
    vegetable_preparation: List[VegetablePreparationItem]
    notes: str = Field(default="", description="Any general preparation notes")


class VegetableRecommendation(BaseModel):
    vegetable: str = Field(..., description="Name of the vegetable")
    reason: str = Field(..., description="Why it suits the location, season, and planting medium")
    pot_size: str = Field(default="", description="Recommended pot size if planting in pots, else empty")

class VegetableResearchOutput(BaseModel):
    vegetable_recommendations: List[VegetableRecommendation]
    summary: str = Field(default="", description="General summary or intro note")