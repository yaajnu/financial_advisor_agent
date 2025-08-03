import datetime
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import (
    add_messages,
)  # helper function to add messages to the state
from langchain_core.messages import SystemMessage
from ..constants import google_search_api_key

from ..tools.utils import market_sentiment_tools

system_prompt = SystemMessage(
    content="You are an expert financial assistant."
    "Use tools to find accurate information about the historical and indicator data and give the market sentiment. But dont use the tools to get data for more than 45 days in the past from the current date"
    f"The current date is {datetime.now().strftime('%Y-%m-%d')}\
           The google search api key is {google_search_api_key}."
)


class AgentState(TypedDict):
    """The state of the agent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    number_of_steps: int


# Define our tool node
def call_tool(state: AgentState):
    outputs = []

    # Iterate over the tool calls in the last message
    for tool_call in state["messages"][-1].tool_calls:
        # Get the tool by name
        tool_result = market_sentiment_tools[tool_call["name"]].invoke(
            tool_call["args"]
        )
        outputs.append(
            ToolMessage(
                content=tool_result,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}


def call_model(
    model,
    state: AgentState,
    config: RunnableConfig,
):
    # Invoke the model with the system prompt and the messages
    messages_with_system = [system_prompt] + state["messages"]
    response = model.invoke(messages_with_system, config)
    # We return a list, because this will get added to the existing messages state using the add_messages reducer
    return {"messages": [response]}


# Define the conditional edge that determines whether to continue or not
def should_continue(state: AgentState):
    messages = state["messages"]
    # If the last message is not a tool call, then we finish
    if not messages[-1].tool_calls:
        return "end"
    # default to continue
    return "continue"
