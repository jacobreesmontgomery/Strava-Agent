"""Pydantic models for tool inputs and outputs."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============================================================================
# Strava Tool Models
# ============================================================================


class AthleteProfile(BaseModel):
    """Output model for athlete profile information."""

    id: int
    username: str
    bio: Optional[str] = None
    firstname: str
    lastname: str
    city: Optional[str] = None
    country: Optional[str] = None

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": 12345,
                "username": "john_doe",
                "bio": "Marathon runner",
                "firstname": "John",
                "lastname": "Doe",
                "city": "San Francisco",
                "country": "USA",
            }
        }


# TODO: Update these models to align with the strava model type definitions.
# Errors occur right now when we try to initialize this model with the
# strava response data due to type mismatches.
class Activity(BaseModel):
    """Output model for a single activity in a list."""

    id: int
    name: str
    type: str
    distance: float = Field(description="Distance in meters")
    moving_time: int = Field(description="Moving time in seconds")
    elapsed_time: int = Field(description="Elapsed time in seconds")
    start_date: datetime

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": 9876543210,
                "name": "Morning Run",
                "type": "Run",
                "distance": 5000.0,
                "moving_time": 1800,
                "elapsed_time": 1920,
                "start_date": "2026-05-03T07:30:00Z",
            }
        }


class Split(BaseModel):
    """Model for activity split data."""

    distance: float = Field(description="Distance in meters")
    elapsed_time: int = Field(description="Elapsed time in seconds")
    moving_time: int = Field(description="Moving time in seconds")
    pace_zone: Optional[int] = None
    elevation_difference: Optional[float] = None
    average_heartrate: Optional[float] = None
    average_speed: Optional[float] = None
    average_grade_adjusted_speed: Optional[float] = None


class ActivityDetail(BaseModel):
    """Output model for detailed activity information."""

    id: int
    name: str
    type: str
    description: Optional[str] = None
    distance: float = Field(description="Distance in meters")
    moving_time: int = Field(description="Moving time in seconds")
    elapsed_time: int = Field(description="Elapsed time in seconds")
    start_date: datetime
    average_speed_m_s: Optional[float] = Field(None, description="Average speed in m/s")
    max_speed_m_s: Optional[float] = Field(None, description="Max speed in m/s")
    splits: list[Split] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": 9876543210,
                "name": "Morning Run",
                "type": "Run",
                "description": "Easy pace run",
                "distance": 5000.0,
                "moving_time": 1800,
                "elapsed_time": 1920,
                "start_date": "2026-05-03T07:30:00Z",
                "average_speed": 2.78,
                "max_speed": 4.5,
                "splits": [],
            }
        }


# ============================================================================
# Metrics Tool Models
# ============================================================================


class ActivityMetric(BaseModel):
    """Simplified activity model for metrics calculations."""

    id: int
    name: str
    type: str
    distance: float = Field(description="Distance in meters")
    moving_time: int = Field(description="Moving time in seconds")
    start_date: Optional[datetime] = None
    elevation_gain: Optional[float] = Field(
        None, description="Elevation gain in meters"
    )
    splits: list[Split] = Field(default_factory=list)


class PaceMetrics(BaseModel):
    """Output model for pace calculations."""

    average_pace_str: str = Field(description="Formatted pace (e.g., '6:30 min/km')")
    average_pace_seconds: float = Field(description="Pace in seconds per km/mi")
    total_distance: float = Field(description="Total distance in km/mi")
    distance_str: str = Field(description="Formatted distance string")
    total_moving_time: int = Field(description="Total moving time in seconds")
    total_moving_time_str: str = Field(description="Formatted time (HH:MM:SS)")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "average_pace_str": "6:30 min/km",
                "average_pace_seconds": 390.0,
                "total_distance": 10.5,
                "distance_str": "10.50 km",
                "total_moving_time": 4095,
                "total_moving_time_str": "1:08:15",
            }
        }


class SpeedMetrics(BaseModel):
    """Output model for speed calculations."""

    average_speed: float = Field(description="Average speed in km/h or mph")
    average_speed_str: str = Field(description="Formatted speed string")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "average_speed": 9.2,
                "average_speed_str": "9.20 km/h",
            }
        }


class ActivityTypeBreakdown(BaseModel):
    """Model for activity type breakdown in weekly summary."""

    count: int = Field(description="Number of activities of this type")
    distance_km: float = Field(description="Total distance in km")


class WeeklySummary(BaseModel):
    """Output model for weekly training summary."""

    total_activities: int
    total_distance_km: float
    total_moving_time_str: str = Field(description="Formatted time (Xh Xm)")
    total_moving_time_seconds: int
    breakdown_by_type: dict[str, ActivityTypeBreakdown] = Field(
        description="Breakdown of activities by type"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_activities": 5,
                "total_distance_km": 45.3,
                "total_moving_time_str": "3h 45m",
                "total_moving_time_seconds": 13500,
                "breakdown_by_type": {
                    "Run": {"count": 3, "distance_km": 25.5},
                    "Ride": {"count": 2, "distance_km": 19.8},
                },
            }
        }


class ElevationMetrics(BaseModel):
    """Output model for elevation calculations."""

    total_elevation_gain_m: float = Field(description="Total elevation gain in meters")
    total_elevation_loss_m: float = Field(description="Total elevation loss in meters")
    total_elevation_gain_ft: float = Field(description="Total elevation gain in feet")
    total_elevation_loss_ft: float = Field(description="Total elevation loss in feet")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_elevation_gain_m": 850.0,
                "total_elevation_loss_m": 850.0,
                "total_elevation_gain_ft": 2789.37,
                "total_elevation_loss_ft": 2789.37,
            }
        }
