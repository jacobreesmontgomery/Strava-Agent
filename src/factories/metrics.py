"""Factory for creating training metrics calculation tools."""

from logging import getLogger
from datetime import datetime
from langchain.tools import tool, BaseTool

from models.tools import (
    PaceMetrics,
    SpeedMetrics,
    WeeklySummary,
    ActivityTypeBreakdown,
    ElevationMetrics,
    ActivityMetric,
)

logger = getLogger(__name__)


# NOTE: These tools may not be needed if we expand the original set of
# strava tools to provide more comprehensive, aggregated metrics. TBD
# based on ~vibes~ and testing.
def create_metrics_tools() -> list[BaseTool]:
    """Creates tool instances for calculating training metrics.

    Returns:
        list[BaseTool]: List of metric calculation tool instances
    """

    @tool
    def calculate_average_pace(
        activities: list[ActivityMetric], unit: str = "mi"
    ) -> PaceMetrics:
        """Calculate average pace across multiple activities.

        Args:
            activities (list[ActivityMetric]): List of activity objects with distance and moving_time.
                Distance in meters, moving_time in seconds.
            unit (str): Distance unit for output - "km" or "mi". Defaults to "mi".

        Returns:
            PaceMetrics: Pace metrics including formatted pace and time strings.
        """
        try:
            total_distance_m = sum(a.distance for a in activities)
            total_moving_time_s = sum(a.moving_time for a in activities)

            if total_distance_m == 0 or total_moving_time_s == 0:
                raise ValueError(
                    "Invalid activity data: distance or moving time is zero"
                )

            # Convert to km or miles
            if unit.lower() == "mi":
                total_distance = total_distance_m / 1609.34
                distance_str = f"{total_distance:.2f} mi"
            else:
                total_distance = total_distance_m / 1000
                distance_str = f"{total_distance:.2f} km"

            # Calculate pace in seconds per km/mi
            pace_seconds = total_moving_time_s / total_distance

            # Convert to mm:ss format
            minutes = int(pace_seconds // 60)
            seconds = int(pace_seconds % 60)
            pace_str = f"{minutes}:{seconds:02d} min/{unit}"

            # Convert total moving time to hours:minutes:seconds
            hours = int(total_moving_time_s // 3600)
            remaining_seconds = total_moving_time_s % 3600
            minutes_total = int(remaining_seconds // 60)
            seconds_total = int(remaining_seconds % 60)
            time_str = f"{hours}:{minutes_total:02d}:{seconds_total:02d}"

            result = PaceMetrics(
                average_pace_str=pace_str,
                average_pace_seconds=round(pace_seconds, 2),
                total_distance=round(total_distance, 2),
                distance_str=distance_str,
                total_moving_time=total_moving_time_s,
                total_moving_time_str=time_str,
            )

            logger.info(
                f"Calculated average pace: {result.average_pace_str} "
                f"over {result.distance_str}"
            )
            return result
        except Exception as e:
            logger.error(f"Error calculating average pace: {e}")
            raise

    @tool
    def calculate_average_speed(
        activities: list[ActivityMetric], unit: str = "mph"
    ) -> SpeedMetrics:
        """Calculate average speed across multiple activities.

        Args:
            activities (list[ActivityMetric]): List of activity objects with distance and moving_time.
            unit (str): Speed unit for output - "kmh" or "mph". Defaults to "mph".

        Returns:
            SpeedMetrics: Speed metrics with formatted speed string.
        """
        try:
            total_distance_m = sum(a.distance for a in activities)
            total_moving_time_s = sum(a.moving_time for a in activities)

            if total_distance_m == 0 or total_moving_time_s == 0:
                raise ValueError(
                    "Invalid activity data: distance or moving time is zero"
                )

            # Convert to km and hours
            total_distance_km = total_distance_m / 1000
            total_hours = total_moving_time_s / 3600

            if unit.lower() == "mph":
                # Convert km to miles
                total_distance_km = total_distance_km * 0.621371
                speed = total_distance_km / total_hours if total_hours > 0 else 0
                speed_str = f"{speed:.2f} mph"
            else:
                speed = total_distance_km / total_hours if total_hours > 0 else 0
                speed_str = f"{speed:.2f} km/h"

            result = SpeedMetrics(
                average_speed=round(speed, 2),
                average_speed_str=speed_str,
            )

            logger.info(f"Calculated average speed: {result.average_speed_str}")
            return result
        except Exception as e:
            logger.error(f"Error calculating average speed: {e}")
            raise

    @tool
    def summarize_weekly_training(activities: list[ActivityMetric]) -> WeeklySummary:
        """Summarize weekly training metrics from activities.

        Args:
            activities (list[ActivityMetric]): List of activity objects with metric data.

        Returns:
            WeeklySummary: Weekly training summary with breakdowns.
        """
        try:
            # Group by activity type
            by_type: dict[str, list[ActivityMetric]] = {}
            for activity in activities:
                activity_type = activity.type or ""
                if activity_type not in by_type:
                    by_type[activity_type] = []
                by_type[activity_type].append(activity)

            # Calculate totals
            total_distance_m = sum(a.distance for a in activities)
            total_moving_time_s = sum(a.moving_time for a in activities)
            total_distance_km = total_distance_m / 1000

            # Format time
            hours = int(total_moving_time_s // 3600)
            remaining = total_moving_time_s % 3600
            minutes = int(remaining // 60)
            time_str = f"{hours}h {minutes}m"

            # Build breakdown by activity type
            breakdown = {}
            for activity_type, type_activities in by_type.items():
                type_distance = sum(a.distance for a in type_activities) / 1000
                breakdown[activity_type] = ActivityTypeBreakdown(
                    count=len(type_activities),
                    distance_km=round(type_distance, 2),
                )

            result = WeeklySummary(
                total_activities=len(activities),
                total_distance_km=round(total_distance_km, 2),
                total_moving_time_str=time_str,
                total_moving_time_seconds=total_moving_time_s,
                breakdown_by_type=breakdown,
            )

            logger.info(
                f"Weekly summary: {result.total_activities} activities, "
                f"{result.total_distance_km} km, {result.total_moving_time_str}"
            )
            return result
        except Exception as e:
            logger.error(f"Error summarizing weekly training: {e}")
            raise

    @tool
    def filter_activities_by_date_range(
        activities: list[ActivityMetric],
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[ActivityMetric]:
        """Filter activities within a date range.

        Args:
            activities (list[ActivityMetric]): List of activity objects to filter.
            start_date (str): ISO format start date (inclusive). If None, no lower bound.
            end_date (str): ISO format end date (inclusive). If None, no upper bound.

        Returns:
            list[ActivityMetric]: Filtered activities within the date range.
        """
        try:
            filtered = activities
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                    filtered = [
                        a for a in filtered if a.start_date and a.start_date >= start_dt
                    ]
                except (ValueError, AttributeError):
                    logger.warning(
                        f"Invalid start_date format, ignoring filter: {start_date}"
                    )

            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                    # Include entire end day
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                    filtered = [
                        a for a in filtered if a.start_date and a.start_date <= end_dt
                    ]
                except (ValueError, AttributeError):
                    logger.warning(
                        f"Invalid end_date format, ignoring filter: {end_date}"
                    )

            result = filtered

            logger.info(
                f"Filtered activities by date range: {len(result)} activities from "
                f"{start_date or 'beginning'} to {end_date or 'end'}"
            )
            return result
        except Exception as e:
            logger.error(f"Error filtering activities by date range: {e}")
            raise

    @tool
    def calculate_elevation_metrics(
        activities: list[ActivityMetric],
    ) -> ElevationMetrics:
        """Calculate elevation statistics across activities.

        Args:
            activities (list[ActivityMetric]): List of activities with elevation data.

        Returns:
            ElevationMetrics: Elevation gain/loss in meters and feet.
        """
        try:
            total_gain = 0
            total_loss = 0

            for activity in activities:
                # Try direct elevation fields
                total_gain += activity.elevation_gain or 0
                total_loss += 0  # elevation_loss not in ActivityMetric model

                # Try splits data
                splits = activity.splits
                for split in splits:
                    total_gain += split.elevation_difference or 0

            result = ElevationMetrics(
                total_elevation_gain_m=round(total_gain, 2),
                total_elevation_loss_m=round(total_loss, 2),
                total_elevation_gain_ft=round(total_gain * 3.28084, 2),
                total_elevation_loss_ft=round(total_loss * 3.28084, 2),
            )

            logger.info(
                f"Calculated elevation metrics: {result.total_elevation_gain_m}m gain, "
                f"{result.total_elevation_loss_m}m loss"
            )
            return result
        except Exception as e:
            logger.error(f"Error calculating elevation metrics: {e}")
            raise

    return [
        calculate_average_pace,
        calculate_average_speed,
        summarize_weekly_training,
        filter_activities_by_date_range,
        calculate_elevation_metrics,
    ]
