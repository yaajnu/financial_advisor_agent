from langgraph.graph import StateGraph, START, END
from typing import Literal

# from .utils import call_model, call_tool, AgentState, should_continue
from financial_advisor_agent.agents.utils import tools
from financial_advisor_agent.prompts.system_prompts import market_sentiment_agent_prompt
from financial_advisor_agent.tools.get_stock_info import (
    get_stock_info,
    State,
    # create_get_stock_info_tool,
)
from langchain_core.agents import AgentFinish
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from functools import partial
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnableConfig

from langchain_groq import ChatGroq
from financial_advisor_agent.constants import GROQ_API_KEY

llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=GROQ_API_KEY,
)


def create_tool_agent(system_prompt: str = market_sentiment_agent_prompt):
    """Helper function to create agents with custom tools and system prompt
    Args:
        llm (ChatVertexAI): LLM for the agent
        tools (list): list of tools the agent will use
        system_prompt (str): text describing specific agent purpose

    Returns:
        executor (AgentExecutor): Runnable for the agent created.
    """

    system_prompt_template = PromptTemplate(
        template=system_prompt
        + """
                ONLY respond to the part of query relevant to your purpose.
                IGNORE tasks you can't complete. 
                """
    )
    tools.append(get_stock_info)
    # define system message
    system_message_prompt = SystemMessagePromptTemplate(prompt=system_prompt_template)

    prompt = ChatPromptTemplate.from_messages(
        [
            system_message_prompt,
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    agent = create_react_agent(llm, tools, prompt=prompt, state_schema=State)

    return agent


import operator
from typing import Annotated, Sequence, TypedDict
import functools
from langchain_core.messages import BaseMessage

from langgraph.graph import StateGraph, END


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    kite: object
    # The 'next' field indicates where to route to next
    # indicator_data: dict


from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command

agent = create_tool_agent()


# For agents in the crew
def market_sentiment_nodes(
    state: AgentState,
) -> Command[Literal["strategy_selector_agent", END]]:
    result = agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "strategy_selector_agent")
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    # result["messages"][-1] = HumanMessage(
    #     content=result["messages"][-1].content, name="market_sentiment_agent"
    # )
    return Command(
        update={
            # share internal message history of research agent with other agents
            "messages": result["messages"],
        },
        goto=goto,
    )


from .strategy_selector_agent import create_strategy_agent

strat_agent = create_strategy_agent()


# For agents in the crew
def strategy_selector_nodes(
    state: AgentState,
) -> Command[Literal["market_sentiment_agent", END]]:
    result = strat_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "market_sentiment_agent")
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="strategy_selector_agent"
    )
    return Command(
        update={
            # share internal message history of chart agent with other agents
            "messages": result["messages"],
        },
        goto=goto,
    )


def get_next_node(last_message: BaseMessage, goto: str):
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    # if "MARKET SENTIMENT" in last_message.content:
    #     return "strategy_selector_agent"
    return goto


def routing(state):
    if "FINAL ANSWER" in state["messages"][-1].content:
        return END
    if "MARKET SENTIMENT" in state["messages"][-1].content:
        return "strategy_selector_agent"
    return "strategy_selector_agent"


def create_market_sentiment_agent():
    """
    Create a market sentiment agent with the given model.

    Args:
        model: The model to use for generating responses.

    Returns:
        A StateGraph representing the market sentiment agent.
    """
    # Define a new graph with our state
    workflow = StateGraph(AgentState)

    # 1. Add our nodes
    workflow.add_node("market_sentiment_agent", market_sentiment_nodes)
    workflow.add_node("strategy_selector_agent", strategy_selector_nodes)
    # workflow.add_node("tools", call_tool)
    # 2. Set the entrypoint as `agent`, this is the first node called
    # workflow.set_entry_point("llm")
    # # 3. Add a conditional edge after the `llm` node is called.
    # workflow.add_conditional_edges(
    #     # Edge is used after the `llm` node is called.
    #     "llm",
    #     # The function that will determine which node is called next.
    #     should_continue,
    #     # Mapping for where to go next, keys are strings from the function return, and the values are other nodes.
    #     # END is a special node marking that the graph is finish.
    #     {
    #         # If `tools`, then we call the tool node.
    #         "continue": "tools",
    #         # Otherwise we finish.
    #         "end": END,
    #     },
    # )
    # 4. Add a normal edge after `tools` is called, `llm` node is called next.
    workflow.add_edge(START, "market_sentiment_agent")
    workflow.add_conditional_edges(
        "market_sentiment_agent",
        routing,
        {
            "strategy_selector_agent": "strategy_selector_agent",
            "market_sentiment_agent": "market_sentiment_agent",
        },
    )
    # workflow.add_edge("llm", END)

    # Now we can compile and visualize our graph
    graph = workflow.compile()
    graph.get_graph().draw_mermaid_png(
        output_file_path="market_sentiment_agent_graph.png"
    )

    return graph
