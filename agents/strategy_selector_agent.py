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

    system_prompt_template = PromptTemplate(
        template=system_prompt
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
    agent = create_react_agent(llm, tools=[], prompt=prompt)

    return agent
