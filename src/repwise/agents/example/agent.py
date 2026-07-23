from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model="gemini-3.1-flash-lite",
    name="root_agent",
    description="You are an example agent made using Google ADK 2.0",
    instruction="Provide general, friendly chat to the user.",
)
