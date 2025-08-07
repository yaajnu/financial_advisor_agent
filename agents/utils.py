import datetime
from typing import Annotated, Any, Dict, Sequence, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages

from financial_advisor_agent.constants import GOOGLE_SEARCH_API_KEY
from financial_advisor_agent.tools.get_indicator_data import get_indicator_data

# from financial_advisor_agent.tools.get_stock_info import get_stock_info
from financial_advisor_agent.tools.get_news_headlines import get_news_headlines

# from financial_advisor_agent.tools.utils import market_sentiment_tools
from financial_advisor_agent.prompts.system_prompts import market_sentiment_agent_prompt


tools = [
    get_indicator_data,
    get_news_headlines,
]

market_sentiment_tools = {tool.name: tool for tool in tools}


class AgentState(TypedDict):
    """The state of the agent."""

    auth_keys: dict[str, Any]
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
    state: AgentState,
    config: RunnableConfig,
):
    # Invoke the model with the system prompt and the messages
    messages_with_system = [market_sentiment_agent_prompt] + state["messages"]
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
