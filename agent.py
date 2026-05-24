from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

from tools.race_results import get_race_results
from tools.driver_compare import Head_to_Head
from tools.strategy import analyze_strategy
from tools.weather import get_weather

load_dotenv(".env.local")

# --- Tool wrappers ---
# Claude reads the docstring to decide when to call each tool

@tool
def race_results_tool(year: int, race_name: str) -> str:
    """Fetch race results for a given year and Grand Prix name. Returns finishing positions, grid positions, time gaps, fastest lap, and retirement status."""
    return get_race_results(year, race_name)

@tool
def driver_compare_tool(year: int, driver1: str, driver2: str, race_name: str, session_type: str) -> str:
    """Compare two drivers head-to-head at a specific race weekend and session. Session type can be 'R' for race, 'Q' for qualifying, 'FP1'/'FP2'/'FP3' for practice."""
    return Head_to_Head(year, driver1, driver2, race_name, session_type)

@tool
def strategy_tool(year: int, race_name: str) -> str:
    """Analyze tire strategy for a given year and Grand Prix. Returns pit stop data, tire compounds used, and stint lengths."""
    return analyze_strategy(year, race_name)

@tool
def weather_tool(circuit_name: str) -> str:
    """Get current weather and forecast for a Formula 1 circuit location. Use this for questions about weather conditions at a race venue."""
    return get_weather(circuit_name)


# --- State ---
# LangGraph passes this dict between nodes — messages accumulate as the agent loops

class State(TypedDict):
    messages: Annotated[list, add_messages]


# --- Model ---

tools = [race_results_tool, driver_compare_tool, strategy_tool, weather_tool]
llm = ChatAnthropic(model="claude-sonnet-4-6")
llm_with_tools = llm.bind_tools(tools)


# --- Nodes ---
# call_model: Claude thinks and decides what to do next
# call_tools: executes whichever tool Claude picked

def call_model(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# --- Graph ---
# Conditional edge: if Claude called a tool, go to call_tools; otherwise stop

graph_builder = StateGraph(State)

graph_builder.add_node("call_model", call_model)
graph_builder.add_node("call_tools", ToolNode(tools))

graph_builder.add_edge(START, "call_model")
graph_builder.add_conditional_edges("call_model", tools_condition)
graph_builder.add_edge("call_tools", "call_model")

agent = graph_builder.compile()


# --- Entry point ---
# app.py calls this with the user's message and gets back a string response

def run_agent(user_message: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return result["messages"][-1].content
