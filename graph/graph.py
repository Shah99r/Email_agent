from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import(
    AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
)
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from tools.email import draft, send_email, update

load_dotenv()


# ─── Agent state ──────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ─── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are a helpful, concise email-drafting assistant.

Your workflow:
1. Greet the user warmly and ask if they would like to write an email.
2. Once they confirm, ask them to describe:
     - Who the email is for (recipient address)
     - What the email is about / any key points
3. Draft the email and call the `update` tool with recipient, subject, and body.
4. After every draft or edit, briefly describe the changes you made, then ask:
   "Are you happy with this, or would you like any changes?"
5. Apply any requested edits by calling `update` again with only the changed fields.
6. When the user says they're happy and want to send (e.g. "send it", "go ahead"),
   call `send_email`.

Rules:
- NEVER call any tool without the user's direction.
- NEVER call `send_email` unless the user explicitly asks you to send.
- Keep your prose replies short and clear.
- Do NOT repeat the full draft in your text; the tool result already shows it.
- If the user asks to quit or cancel, acknowledge politely and stop.

Current draft state is injected into every prompt automatically.

Output format:
    'query analysis': <>
"""

def build_system_message() -> SystemMessage:
    """Inject current draft state so the LLM is always up to date."""
    r = draft["recipient"] or "(not set)"
    s = draft["subject"]   or "(not set)"
    b = draft["body"]      or "(not set)"
    state_block = (
        f"\nCurrent in-memory draft:\n"
        f"  To      : {r}\n"
        f"  Subject : {s}\n"
        f"  Body    : {b}\n"
    )
    return SystemMessage(content=SYSTEM_PROMPT + state_block)


# ─── LLM + tools ──────────────────────────────────────────────────────────────
_tools     = [update, send_email]
_llm       = ChatOllama(model="llama3.2").bind_tools(_tools)
_tool_node = ToolNode(_tools)


# ─── Graph nodes ──────────────────────────────────────────────────────────────
def agent_node(state: AgentState) -> dict:
    """Call the LLM with the current conversation + fresh system prompt."""
    messages = [build_system_message()] + list(state["messages"])
    response = _llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Route: tools → agent loop, or END when the conversation is done."""
    last = state["messages"][-1]

    # A tool confirmed the email was sent → we're done
    if isinstance(last, ToolMessage) and last.content.startswith("✓ Email sent"):
        return "end"

    # LLM wants to call a tool
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"

    # LLM replied with plain text → hand back to the human
    return "end"


# ─── Build & compile ──────────────────────────────────────────────────────────
def build_graph():
    wf = StateGraph(AgentState)
    wf.add_node("agent", agent_node)
    wf.add_node("tools", _tool_node)

    wf.set_entry_point("agent")
    wf.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END},
    )
    wf.add_edge("tools", "agent")

    return wf.compile()


app = build_graph()