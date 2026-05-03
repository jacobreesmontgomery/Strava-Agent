"""Factory for creating Strava tools."""

from logging import getLogger
from langchain.tools import tool, BaseTool

from stravalib.client import Client
from stravalib.model import DetailedActivity, DetailedAthlete

from models.tools import (
    AthleteProfile,
    Activity,
    ActivityDetail,
    Split,
)

logger = getLogger(__name__)


def create_strava_tools(client: Client) -> list[BaseTool]:
    """Creates tool instances bound to a Strava client.

    Args:
        client: The Strava client instance

    Returns:
        list[BaseTool]: List of tool instances
    """

    @tool
    def get_athlete_profile() -> AthleteProfile:
        """
        Fetches the athlete's profile information from Strava.

        Returns:
            AthleteProfile: Athlete profile details.
        """
        try:
            athlete: DetailedAthlete = client.get_athlete()
            profile = AthleteProfile(
                id=athlete.id or 0,
                username=athlete.username or "",
                bio=athlete.description,
                firstname=athlete.firstname or "",
                lastname=athlete.lastname or "",
                city=athlete.city,
                country=athlete.country,
            )
            logger.info(f"Successfully fetched athlete profile for {athlete.username}")
            return profile
        except Exception as e:
            logger.error(f"Error fetching athlete profile: {e}")
            raise

    # NOTE: Consider doing some arithmetic on the acquired activities to return more insightful metrics (e.g. total distance, average pace, etc.)
    # to reduce agent reasoning load and improve response quality. Doing this may remove
    # the need for the additional metrics tools.
    # TODO: Add unit support (km vs mi).
    @tool
    def get_activities(
        before: str | None = None,
        after: str | None = None,
        limit: int | None = None,
    ) -> list[Activity]:
        """Fetches the athlete's activities from Strava.

        Args:
            before (str | None): ISO 8601 formatted date string to filter activities before this date.
            after (str | None): ISO 8601 formatted date string to filter activities after this date.
            limit (int | None): Maximum number of activities to fetch.

        Returns:
            list[Activity]: A list of activity objects.
        """
        try:
            activities_raw = client.get_activities(
                before=before,
                after=after,
                limit=limit,
            )

            # TODO: Add avg_pace as an additional parameter.
            # TODO: Fix type mismatch errors for the relevant fields (type, distance, etc.).
            activities = [
                Activity(
                    id=activity.id or 0,
                    name=activity.name or "",
                    type=activity.type,  # type: ignore
                    distance=activity.distance or 0.0,
                    moving_time=activity.moving_time or 0,
                    elapsed_time=activity.elapsed_time or 0,
                    start_date=activity.start_date,  # type: ignore
                )
                for activity in activities_raw
            ]

            logger.info(
                f"Successfully fetched {len(activities)} activities (limit: {limit})"
            )
            return activities
        except Exception as e:
            logger.error(f"Error fetching activities: {e}")
            raise

    # TODO: Add unit support (km vs mi).
    @tool
    def get_activity_details(
        activity_id: int, include_all_efforts: bool = False
    ) -> ActivityDetail:
        """Fetches detailed information about a specific activity.

        Args:
            activity_id (int): The ID of the activity to fetch details for.
            include_all_efforts (bool): Whether to include all efforts in the response.

        Returns:
            ActivityDetail: Detailed activity information.
        """
        try:
            activity: DetailedActivity = client.get_activity(
                activity_id=activity_id,
                include_all_efforts=include_all_efforts,
            )

            splits = []
            if activity.splits_metric:
                splits = [
                    Split(
                        distance=split.distance or 0.0,
                        elapsed_time=split.elapsed_time or 0,
                        moving_time=split.moving_time or 0,
                        pace_zone=split.pace_zone,
                        elevation_difference=split.elevation_difference,
                        average_heartrate=split.average_heartrate,
                        average_speed=split.average_speed,
                        average_grade_adjusted_speed=split.average_grade_adjusted_speed,
                    )
                    for split in activity.splits_metric
                ]

            # TODO: Add avg_pace as an additional parameter.
            activity_detail = ActivityDetail(
                id=activity.id or 0,
                name=activity.name or "",
                type=activity.type,  # type: ignore
                description=activity.description,
                distance=activity.distance or 0.0,
                moving_time=activity.moving_time or 0,
                elapsed_time=activity.elapsed_time or 0,
                start_date=activity.start_date,  # type: ignore
                average_speed_m_s=activity.average_speed,
                max_speed_m_s=activity.max_speed,
                splits=splits,
            )

            logger.info(f"Successfully fetched details for activity {activity_id}")
            return activity_detail
        except Exception as e:
            logger.error(f"Error fetching activity details for {activity_id}: {e}")
            raise

    return [get_athlete_profile, get_activities, get_activity_details]
