import sys
import os
import subprocess
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.abspath(__file__))

# Add to Python path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    __package__ = ""

load_dotenv()
print("Running startup initialization...")

# Install private repos
github_token = os.getenv("GITHUB_TOKEN")
print("BONDAAAAAA")
commands = [
    {
        "name": "Update package list",
        "cmd": [
            "apt-get",
            "update",
        ],
        "timeout": 120,
    },
    {
        "name": "Download tools",
        "cmd": [
            "apt-get",
            "install",
            "build-essential",
            # "wget",
        ],
        "timeout": 120,
    },
    {
        "name": "Download TA-Lib source",
        "cmd": [
            "wget",
            "https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz",
        ],
        "timeout": 120,
    },
    {
        "name": "Extract archive",
        "cmd": ["tar", "-xzf", "ta-lib-0.6.4-src.tar.gz"],
        "timeout": 30,
    },
    {
        "name": "Configure build",
        "cmd": ["./configure", "--prefix=/usr"],
        "cwd": "ta-lib-0.6.4",
        "timeout": 60,
    },
    {"name": "Compile source", "cmd": ["make"], "cwd": "ta-lib-0.6.4", "timeout": 300},
    {
        "name": "Install TA-Lib",
        "cmd": ["make", "install"],
        "cwd": "ta-lib-0.6.4",
        "timeout": 60,
    },
]
print(os.listdir("."))
for step in commands:
    try:
        print(f"🔧 {step['name']}...")
        cwd = step.get("cwd", ".")
        timeout = step.get("timeout", 60)

        result = subprocess.run(
            step["cmd"], cwd=cwd, timeout=timeout, capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"✅ {step['name']} completed")
        else:
            print(f"❌ {step['name']} failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error in {step['name']}: {e}")
print(os.listdir("."))
print(os.getcwd())
# os.chdir("ta-lib")
subprocess.check_call([sys.executable, "-m", "pip", "install", "ta-lib"])
os.chdir("..")
if github_token:
    subprocess.run(
        [
            "git",
            "config",
            "--global",
            f"url.https://x-access-token:{github_token}@github.com/.insteadOf",
            "https://github.com/",
        ],
        check=False,
    )

    # Clone the repository directly
    repo_dir = "./financial_advisor_agent"
    if not os.path.exists(repo_dir):
        try:
            subprocess.check_call(
                [
                    "git",
                    "clone",
                    f"https://x-access-token:{github_token}@github.com/yaajnu/financial_advisor_agent.git",
                    repo_dir,
                ]
            )
            print("✅ Repository cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone repository: {e}")
import os

print(os.listdir("."))

# Any other initialization
print("Startup initialization complete!")
import os
import traceback
import gradio as gr
from dotenv import load_dotenv
from kiteconnect import KiteConnect
from financial_advisor_agent.constants import key_secret
import webbrowser
from financial_advisor_agent.agents.market_sentiment_agent import (
    create_market_sentiment_agent,
    create_tool_agent,
    market_sentiment_nodes,
)
from functools import partial

# Assuming your agent messages are from LangChain
from langchain_core.messages import AIMessage, ToolMessage

# Load environment variables if you are using a .env file
load_dotenv()


# The redirect URL you have configured in your Kite Connect app settings.
REDIRECT_URL = "http://127.0.0.1:7860/redirect"


def create_initial_state():
    """Initializes the application state."""
    return {"kite": KiteConnect(api_key=key_secret[0]), "access_token": None}


def generate_login_link(auth_state):
    """Generates the Kite Connect login URL and presents it to the user."""
    kite = auth_state["kite"]
    login_url = kite.login_url()
    webbrowser.open(login_url)
    return gr.Markdown(
        f"✅ Login URL Generated! \n\nIf your browser didn't open automatically, [click here to log in]({login_url}).",
        visible=True,
    )


def generate_session(request_token, auth_state):
    """Takes the request_token, generates a session, and stores the access_token."""
    if not request_token or not request_token.strip():
        return auth_state, gr.Markdown(
            "❌ **Error:** Request Token cannot be empty.", visible=True
        )
    kite = auth_state["kite"]
    try:
        data = kite.generate_session(request_token, api_secret=key_secret[1])
        access_token = data["access_token"]
        print(f"Access Token: {access_token}")  # For debugging purposes
        os.environ["KITE_ACCESS_TOKEN"] = access_token if access_token else ""
        auth_state["access_token"] = access_token
        kite.set_access_token(access_token)
        auth_state["kite"] = kite  # Update the kite instance with the new access token
        feedback = gr.Markdown(
            "✅ **Success!** Session generated and access token is now active.",
            visible=True,
        )
    except Exception as e:
        feedback = gr.Markdown(f"❌ **Error generating session:** {e}", visible=True)
    return auth_state, feedback


# --- NEW: Helper function to format intermediate steps ---
def format_rationale_messages(messages):
    """
    Formats the intermediate messages from the agent into a readable Markdown string.
    """
    if not messages:
        return ""

    # Skip the first message, which is the user's input
    intermediate_steps = messages[1:]
    if not intermediate_steps:
        return "No intermediate steps to display."

    formatted_string = "### Agent Rationale\n\n"
    for msg in intermediate_steps:
        print(f"Processing message: {msg}")
        if isinstance(msg, AIMessage) and msg.tool_calls:
            formatted_string += "**🤖 Thought & Tool Call:**\n"
            if msg.content:
                formatted_string += f"{msg.content}\n"
            for tool_call in msg.tool_calls:
                formatted_string += f"- Calling tool: `{tool_call['name']}` with arguments: `{tool_call['args']}`\n"
        elif isinstance(msg, ToolMessage):
            formatted_string += f"\n**🛠️ Tool Output for `{msg.name}`:**\n"
            formatted_string += f"```\n{msg.content}\n```\n\n"
        elif isinstance(msg, AIMessage):
            # This is the final answer, we can omit it or show it as 'Final Thought'
            pass  # Omit from rationale as it's in the main chat

    return formatted_string


# --- MODIFIED: chat_response now yields to two components ---
def chat_response(user_message, history, auth_state):
    """
    The chatbot logic, now yielding updates for both the chat and the rationale.
    """
    history.append([user_message, ""])
    rationale_string = "Agent is thinking..."
    # Initial yield to show the user's message immediately
    yield history, rationale_string

    access_token = auth_state.get("access_token")

    if not access_token:
        history[-1][1] = "I am not authenticated. Please complete the login flow first."
        yield history, "Authentication check failed."
        return

    try:
        kite = auth_state["kite"]
        top_agent = create_tool_agent(kite=kite)
        top_agent_node = partial(market_sentiment_nodes, agent=top_agent, name="llm")
        agent = create_market_sentiment_agent(top_agent_node)
        inputs = {
            "messages": [("user", user_message)],
            "agent_scratchpad": [],
            "kite": kite,
        }

        full_response = ""
        for state in top_agent.stream(inputs, stream_mode="values"):
            # for state in top_agent.invoke(inputs, stream_mode="values"):
            all_messages = state["messages"]
            print(f"Current messages: {all_messages}")
            # The final user-facing response is always the content of the last AIMessage
            final_message_obj = next(
                (m for m in reversed(all_messages) if isinstance(m, AIMessage)), None
            )

            if final_message_obj and final_message_obj.content:
                full_response = final_message_obj.content

            history[-1][1] = full_response
            rationale_string = format_rationale_messages(all_messages)

            # Yield a tuple to update both components
            # history = top_agent.invoke(inputs)
            print(f"Agent response: {history}")
            print("-------------")
            yield history, rationale_string

    except Exception as e:
        print(traceback.format_exc(e))
        history[-1][1] = f"An error occurred: {e}"
        yield history, f"An error occurred during generation: {e}"


# --- MODIFIED: Gradio UI Layout with Accordion ---
with gr.Blocks(theme=gr.themes.Soft(), title="Financial Advisor Chatbot") as demo:
    auth_state = gr.State(value=create_initial_state)

    gr.Markdown("# Financial Advisor with Kite Connect")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Authentication Flow")
            with gr.Accordion("Step 1: Generate Login Link", open=True):
                login_button = gr.Button("Click to Login with Kite", variant="primary")
                login_link_output = gr.Markdown(visible=False)
            with gr.Accordion("Step 2: Generate Session", open=True):
                gr.Markdown(
                    "After logging in, you will be redirected. **Copy the `request_token` value from the new page's URL** and paste it below."
                )
                request_token_input = gr.Textbox(
                    label="Paste Request Token Here", type="password"
                )
                session_button = gr.Button("Generate Session")
                session_status_output = gr.Markdown(visible=False)
        with gr.Column(scale=2):
            gr.Markdown("### Chat Interface")
            chatbot_window = gr.Chatbot(
                label="Conversation", height=400, bubble_full_width=False
            )

            # --- NEW: Accordion for showing the rationale ---
            with gr.Accordion("Show Rationale", open=False):
                rationale_output = gr.Markdown(
                    "The agent's thought process will appear here live."
                )

            message_textbox = gr.Textbox(
                placeholder="Once authenticated, ask me anything about the market...",
                show_label=False,
            )

    # --- Event Listeners ---
    login_button.click(
        fn=generate_login_link, inputs=[auth_state], outputs=[login_link_output]
    )
    session_button.click(
        fn=generate_session,
        inputs=[request_token_input, auth_state],
        outputs=[auth_state, session_status_output],
    )

    # --- MODIFIED: submit event now updates two outputs ---
    message_textbox.submit(
        fn=chat_response,
        inputs=[message_textbox, chatbot_window, auth_state],
        # The generator will now stream to both components
        outputs=[chatbot_window, rationale_output],
    )


# --- Launch the App ---
if __name__ == "__main__":
    demo.launch()


# demo.launch()
# print("BONDS")
