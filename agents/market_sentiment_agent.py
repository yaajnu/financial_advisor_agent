from langgraph.graph import StateGraph, END
from .utils import call_model, call_tool, AgentState, should_continue


def create_market_sentiment_agent(model):
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
    workflow.add_node("llm", call_model(model))
    workflow.add_node("tools", call_tool)
    # 2. Set the entrypoint as `agent`, this is the first node called
    workflow.set_entry_point("llm")
    # 3. Add a conditional edge after the `llm` node is called.
    workflow.add_conditional_edges(
        # Edge is used after the `llm` node is called.
        "llm",
        # The function that will determine which node is called next.
        should_continue,
        # Mapping for where to go next, keys are strings from the function return, and the values are other nodes.
        # END is a special node marking that the graph is finish.
        {
            # If `tools`, then we call the tool node.
            "continue": "tools",
            # Otherwise we finish.
            "end": END,
        },
    )
    # 4. Add a normal edge after `tools` is called, `llm` node is called next.
    workflow.add_edge("tools", "llm")

    # Now we can compile and visualize our graph
    graph = workflow.compile()
    return graph
