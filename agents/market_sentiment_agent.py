from langgraph.graph import StateGraph, END

# from .utils import call_model, call_tool, AgentState, should_continue
from financial_advisor_agent.agents.utils import tools
from financial_advisor_agent.prompts.system_prompts import (
    market_sentiment_agent_prompt,
    strategy_selector_agent_prompt,
)
from financial_advisor_agent.tools.get_stock_info import (
    get_stock_info,
    State,
    # create_get_stock_info_tool,
)
from langgraph.prebuilt.chat_agent_executor import AgentState

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

import operator
from typing import Annotated, Literal, Sequence, TypedDict
import functools
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.types import Command

from langgraph.graph import StateGraph, START, END


# The agent state is the input to each node in the graph
# class AgentState(TypedDict):
class MyAgentState(AgentState):

    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

    agent_history: Annotated[Sequence[BaseMessage], operator.add]
    kite: object


from langchain_core.messages import AIMessage


def create_tool_agent(
    system_prompt: str = market_sentiment_agent_prompt, kite=None, state=State
):
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
    agent = create_react_agent(llm, tools, prompt=prompt, state_schema=state)

    return agent


agent = create_tool_agent(state=MyAgentState)


# For agents in the crew
def market_sentiment_nodes(state) -> Command[Literal["strategy_agent"]]:

    input = {
        "messages": [state["messages"][-1]],
        "agent_history": state["agent_history"],
        "kite": state["kite"],
    }
    result = agent.invoke(input)

    return Command(update={"messages": [result["messages"]]}, goto="strategy_agent")


from .strategy_selector_agent import create_strategy_agent

strat_agent = create_strategy_agent()
import pickle


def create_strat_node(state) -> Command[Literal[END]]:
    system_prompt_template = PromptTemplate(
        template=strategy_selector_agent_prompt
        + """
                ONLY respond to the part of query relevant to your purpose.
                IGNORE tasks you can't complete. 
                """
    )
    # tools.append(get_stock_info)
    # define system message
    system_message_prompt = SystemMessagePromptTemplate(prompt=system_prompt_template)

    prompt = ChatPromptTemplate.from_messages(
        [
            system_message_prompt,
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    input = {
        "messages": state["messages"][-1][:-1]
        + [HumanMessage(state["messages"][-1][-1].content)],
        # "agent_history": state["agent_history"],
    }
    pickle.dump(input, open("input.pkl", "wb"))
    formatted_prompt = prompt.invoke(input)
    result = strat_agent.invoke(formatted_prompt)

    return Command(update={"messages": [result]}, goto=END)


def create_market_sentiment_agent():
    """
    Create a market sentiment agent with the given model.

    Args:
        model: The model to use for generating responses.

    Returns:
        A StateGraph representing the market sentiment agent.
    """
    # Define a new graph with our state
    workflow = StateGraph(MyAgentState)

    # 1. Add our nodes
    workflow.add_node("market_sentiment_agent", market_sentiment_nodes)
    workflow.add_node("strategy_agent", create_strat_node)
    # workflow.add_node("tools", call_tool)
    # 2. Set the entrypoint as `agent`, this is the first node called
    workflow.add_edge(START, "market_sentiment_agent")
    # # 3. Add a conditional edge after the `market_sentiment_agent` node is called.
    # workflow.add_conditional_edges(
    #     # Edge is used after the `market_sentiment_agent` node is called.
    #     "market_sentiment_agent",
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
    # workflow.add_edge("llm", "strategy_agent")
    # workflow.add_edge("strategy_agent", END)

    # Now we can compile and visualize our graph
    graph = workflow.compile()
    graph.get_graph().draw_mermaid_png(
        output_file_path="market_sentiment_agent_graph.png"
    )

    return graph
