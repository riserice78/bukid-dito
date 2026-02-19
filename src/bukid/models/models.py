from pydantic import BaseModel, Field
from typing import List

class VegetableMarketPrice(BaseModel):
    low: float = Field(description="Lowest market price per kg")
    high: float = Field(description="Highest market price per kg")

class VegetableSchedule(BaseModel):
    """Schema for a single vegetable's planting and harvesting schedule"""
    vegetable: str = Field(description="Name of the vegetable")
    vegetable_price: VegetableMarketPrice
    vegetable_price_currency: str = Field(description="Currency of the vegetable price")
    plant_start_month: int = Field(description="Month to start planting (1-12)", ge=1, le=12)
    plant_end_month: int = Field(description="Month to end planting (1-12)", ge=1, le=12)
    harvest_start_month: int = Field(description="Month to start harvesting (1-12)", ge=1, le=12)
    harvest_end_month: int = Field(description="Month to end harvesting (1-12)", ge=1, le=12)
    companion_plant: str = Field(description="Name of the companion plant with reason")
    reason: str = Field(description="Why the vegetable would thrive in the location")

class VegetableScheduleOutput(BaseModel):
    """Complete output schema for all vegetables"""
    vegetable_schedule: List[VegetableSchedule]
