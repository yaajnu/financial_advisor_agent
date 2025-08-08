from langgraph.graph import StateGraph, END

# from .utils import call_model, call_tool, AgentState, should_continue
from financial_advisor_agent.agents.utils import tools
from financial_advisor_agent.prompts.system_prompts import market_sentiment_agent_prompt
from financial_advisor_agent.tools.get_stock_info import (
    get_stock_info,
    State,
    # create_get_stock_info_tool,
)
from langchain.agents import AgentExecutor, create_tool_calling_agent
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


def create_tool_agent(system_prompt: str = market_sentiment_agent_prompt, kite=None):
    """Helper function to create agents with custom tools and system prompt
    Args:
        llm (ChatVertexAI): LLM for the agent
        tools (list): list of tools the agent will use
        system_prompt (str): text describing specific agent purpose

    Returns:
        executor (AgentExecutor): Runnable for the agent created.
    """

    # Each worker node will be given a name and some tools.

    system_prompt_template = PromptTemplate(
        template=system_prompt
        + """
                ONLY respond to the part of query relevant to your purpose.
                IGNORE tasks you can't complete. 
                """
    )
    # get_stock_info_tool = partial(get_stock_info, kite=kite)
    # tools.append(
    #     Tool(
    #         name="get_stock_info",
    #         func=get_stock_info_tool,
    #         description="Get historical information about a stock including historical data",
    #         args_schema=StockInfoInput,
    #     )
    # )
    # get_stock_info_tool = get_stock_info
    tools.append(get_stock_info)
    # define system message
    system_message_prompt = SystemMessagePromptTemplate(prompt=system_prompt_template)

    prompt = ChatPromptTemplate.from_messages(
        [
            system_message_prompt,
            MessagesPlaceholder(variable_name="messages"),
            # MessagesPlaceholder(variable_name="agent_scratchpad"),
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
    # The 'next' field indicates where to route to next
    next: str

    agent_history: Annotated[Sequence[BaseMessage], operator.add]


from langchain_core.messages import AIMessage


# For agents in the crew
def market_sentiment_nodes(state, agent, name):

    input = {
        "messages": [state["messages"][-1]],
        "agent_history": state["agent_history"],
    }
    result = agent.invoke(input)

    return {
        "agent_history": [
            AIMessage(
                content=result["output"],
                additional_kwargs={"intermediate_steps": result["intermediate_steps"]},
                name=name,
            )
        ]
    }


def create_market_sentiment_agent(node):
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
    workflow.add_node("llm", node)
    # workflow.add_node("tools", call_tool)
    # 2. Set the entrypoint as `agent`, this is the first node called
    workflow.set_entry_point("llm")
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
    workflow.add_edge("llm", END)

    # Now we can compile and visualize our graph
    graph = workflow.compile()
    return graph
