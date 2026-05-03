from os import getenv
from dotenv import load_dotenv
from typing import Any, AsyncGenerator
from logging import getLogger

from langchain.agents import create_agent

# from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph

from stravalib.client import Client
from stravalib.protocol import AccessInfo

from factories.tools import create_strava_tools
from factories.metrics import create_metrics_tools

logger = getLogger(__name__)

load_dotenv()

STRAVA_CLIENT_ID = int(getenv("STRAVA_CLIENT_ID", 0))
STRAVA_CLIENT_SECRET = getenv("STRAVA_CLIENT_SECRET", "")
MY_REFRESH_TOKEN = getenv("MY_REFRESH_TOKEN", "")

if (
    not all([STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, MY_REFRESH_TOKEN])
    and STRAVA_CLIENT_ID != 0
):
    logger.error(
        "Missing required environment variables. Please ensure STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, and MY_REFRESH_TOKEN are set in the .env file."
    )
    raise ValueError(
        "Missing required environment variables. Please ensure STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, and MY_REFRESH_TOKEN are set in the .env file."
    )


class CoachingAgent:

    def __init__(self) -> None:
        """Initializes the CoachingAgent with the provided Strava access token.

        Args:
            access_token (str): The Strava API access token for authentication.
        """
        self._init_client()
        self.chat_model = ChatOpenAI(
            model="gpt-5.4-mini",
            temperature=0.7,
            timeout=None,
            max_retries=3,
            use_responses_api=True,
        )
        self.agent = self.create_agent()

    def _refresh_access_token(self) -> AccessInfo:
        """Refreshes the Strava API access token using the refresh token.

        Returns:
            AccessInfo: The updated access information.
        """
        client = Client()
        response: AccessInfo = client.refresh_access_token(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            refresh_token=MY_REFRESH_TOKEN,
        )
        return response

    def _init_client(self) -> None:
        """Initializes the Strava API client using the access token."""
        auth_data: AccessInfo = self._refresh_access_token()
        self.client = Client(
            access_token=auth_data["access_token"],
            refresh_token=auth_data["refresh_token"],
            token_expires=auth_data["expires_at"],
        )

    def create_agent(self) -> CompiledStateGraph:
        """Creates a LangChain agent with the defined tools.

        Returns:
            CompiledStateGraph: The created LangChain agent.
        """
        strava_tools = create_strava_tools(client=self.client)
        metrics_tools = create_metrics_tools()
        tools = strava_tools + metrics_tools

        # TODO: Add domain context to the prompt (topics/metrics the agent should focus on, types of insights to provide, etc.)
        return create_agent(
            model=self.chat_model,
            tools=tools,
            system_prompt="""
            You are an assistant running coach that helps athletes analyze their Strava data and 
            answer any questions they may have about their training, performance, and progress.
            
            ## **Available Tools**:
            
            ### Strava Data Retrieval:
            - `get_athlete_profile`: Fetches the athlete's profile information from Strava.
            - `get_activities`: Fetches the athlete's activities from Strava, with optional filters.
            - `get_activity_details`: Fetches detailed information about a specific activity, including 
                splits and performance metrics.

            ### Metrics Calculation (Use these for ALL arithmetic with training data):
            - `calculate_average_pace`: Calculates average pace across activities. Input the activities list.
            - `calculate_average_speed`: Calculates average speed across activities.
            - `summarize_weekly_training`: Provides weekly training summary (total distance, time, breakdown by type).
            - `filter_activities_by_date_range`: Filters activities within a date range before analysis.
            - `calculate_elevation_metrics`: Calculates total elevation gain/loss across activities.

            ## **IMPORTANT - Math and Calculations**:
            ALWAYS use the metric calculation tools for ANY arithmetic involving training data. 
            Do NOT attempt to perform manual calculations. The metric tools handle:
            - Pace calculations (min/km, min/mi)
            - Speed calculations (km/h, mph)
            - Distance/time aggregations
            - Unit conversions (meters to km/mi, seconds to formatted time)
            - Weekly/date-range filtering and summarization
            
            When a user asks about summaries, averages, or totals, use the appropriate metric tool.

            When a user asks for details about specific activities, you must first use the `get_activities` 
            tool to acquire the activity ID, and then use the `get_activity_details` tool to fetch the 
            detailed information about that activity.

            ## Response Guidelines
            - Be concise, informative, and professional in your responses.
            - Your response must only be grounded in information directly obtained from the tools. 
                If requested information isn't available via these tools, indicate that you do
                not have access to that information.
            - Utilize markdown-formatted lists, tables, or other structured formats when presenting 
                data to enhance readability and clarity.
            - When creating markdown tables, ensure each row (including the header separator) is on 
                its own line. Format:
                ```
                | Header 1 | Header 2 |
                |---|---|
                | Value 1 | Value 2 |
                ```
            - Responses should begin with a direct answer to the user's query, followed by any 
                supporting information or insights derived from the data. Avoid unnecessary 
                preambles or introductions.

            # Caveats
            - Strava's first day of the week is Monday, so when users ask for weekly summaries or 
                comparisons, ensure that you align with this convention.
            - Assume your users are from the United States, unless specified otherwise, meaning you 
                should use the imperial system (miles, feet, etc.) for the relevant metrics in your responses.
            """,
        )

    # TODO: Implement streaming and deprecate non-streaming.
    async def astream(self, query: str) -> AsyncGenerator[dict[str, Any], None]:
        """Streams the agent's response to a user's query.

        Args:
            query (str): The user's query or request.

        Returns:
            AsyncGenerator[dict[str, Any], None]: An asynchronous generator yielding chunks of the agent's response.
        """
        async for chunk in self.agent.astream(
            {"messages": [{"role": "user", "content": query}]}
        ):
            yield chunk

    async def ainvoke(self, query: str) -> dict[str, Any]:
        """Invokes the agent with a user's query and returns the complete response.

        Args:
            query (str): The user's query or request.

        Returns:
            dict[str, Any]: The complete response from the agent.
        """
        response: dict[str, Any] = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        return response
