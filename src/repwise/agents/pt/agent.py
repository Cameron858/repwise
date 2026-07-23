from google.adk.agents.llm_agent import Agent

from repwise.tools.db import get_schema, sample_table_data

root_agent = Agent(
    name="pt_agent",
    model="gemini-3.1-flash-lite",
    description="A knowledgeable personal trainer assistant that tracks workout progress and provides lifting feedback.",
    instruction=(
        "You are an encouraging and technically precise Personal Trainer AI. "
        "When the user asks about past workouts, progress, or weights used, always "
        "use the available tools to retrieve factual workout data. "
        "Analyse their recent performance and give concise, actionable training advice."
    ),
    tools=[get_schema, sample_table_data],
)
