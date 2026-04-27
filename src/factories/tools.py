"""Factory for creating Strava tools."""

from typing import Any
from langchain.tools import tool, BaseTool

from stravalib.client import Client
from stravalib.model import DetailedActivity, DetailedAthlete


def create_strava_tools(client: Client) -> list[BaseTool]:
    """Creates tool instances bound to a Strava client.

    Args:
        client: The Strava client instance

    Returns:
        list[BaseTool]: List of tool instances
    """

    @tool
    def get_athlete_profile() -> dict[str, Any]:
        """
        Fetches the athlete's profile information from Strava.

        Returns:
            dict: A dictionary containing athlete profile details.
        """
        athlete: DetailedAthlete = client.get_athlete()
        return {
            "id": athlete.id,
            "username": athlete.username,
            "bio": athlete.description,
            "firstname": athlete.firstname,
            "lastname": athlete.lastname,
            "city": athlete.city,
            "country": athlete.country,
        }

    @tool
    def get_activities(
        before: str | None = None,
        after: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetches the athlete's activities from Strava.

        Args:
            before (str | None): ISO 8601 formatted date string to filter activities before this date.
            after (str | None): ISO 8601 formatted date string to filter activities after this date.
            limit (int | None): Maximum number of activities to fetch.

        Returns:
            list[dict]: A list of dictionaries containing activity details.
        """
        activities = client.get_activities(before=before, after=after, limit=limit)
        return [
            {
                "id": activity.id,
                "name": activity.name,
                "type": activity.type,
                "distance": activity.distance,
                "moving_time": activity.moving_time,
                "elapsed_time": activity.elapsed_time,
                "start_date": activity.start_date,
            }
            for activity in activities
        ]

    @tool
    def get_activity_details(
        activity_id: int, include_all_efforts: bool = False
    ) -> dict[str, Any]:
        """Fetches detailed information about a specific activity.

        Args:
            activity_id (int): The ID of the activity to fetch details for.
            include_all_efforts (bool): Whether to include all efforts in the response.

        Returns:
            dict: A dictionary containing detailed information about the activity.
        """
        activity: DetailedActivity = client.get_activity(
            activity_id=activity_id, include_all_efforts=include_all_efforts
        )
        return {
            "id": activity.id,
            "name": activity.name,
            "type": activity.type,
            "description": activity.description,
            "distance": activity.distance,
            "moving_time": activity.moving_time,
            "elapsed_time": activity.elapsed_time,
            "start_date": activity.start_date,
            "average_speed": activity.average_speed,
            "max_speed": activity.max_speed,
            "splits": (
                [
                    {
                        "distance": split.distance,
                        "elapsed_time": split.elapsed_time,
                        "moving_time": split.moving_time,
                        "pace_zone": split.pace_zone,
                        "elevation_difference": split.elevation_difference,
                        "average_heartrate": split.average_heartrate,
                        "average_speed": split.average_speed,
                        "average_grade_adjusted_speed": split.average_grade_adjusted_speed,
                    }
                    for split in activity.splits_metric
                ]
                if activity.splits_metric
                else []
            ),
        }

    return [get_athlete_profile, get_activities, get_activity_details]
