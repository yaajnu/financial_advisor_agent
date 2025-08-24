from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage

# from .utils import call_model, call_tool, AgentState, should_continue
from financial_advisor_agent.prompts.system_prompts import (
    strategy_selector_agent_prompt,
)
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_groq import ChatGroq
from financial_advisor_agent.constants import GROQ_API_KEY
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=GROQ_API_KEY,
)


def create_strategy_agent(system_prompt: str = strategy_selector_agent_prompt):
    """Helper function to create agents with custom tools and system prompt
    Args:
        llm (ChatVertexAI): LLM for the agent
        tools (list): list of tools the agent will use
        system_prompt (str): text describing specific agent purpose

    Returns:
        executor (AgentExecutor): Runnable for the agent created.
    """

    agent = llm

    return agent
