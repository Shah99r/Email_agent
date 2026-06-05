import sys
import textwrap
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from graph.graph import app  


# ─── ANSI colour helpers ──────────────────────────────────────────────────────
_TTY = sys.stdout.isatty()

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _TTY else text

BOLD    = lambda t: _c("1",  t)
DIM     = lambda t: _c("2",  t)
CYAN    = lambda t: _c("96", t)
GREEN   = lambda t: _c("92", t)
YELLOW  = lambda t: _c("93", t)
MAGENTA = lambda t: _c("95", t)

W = 56  # layout width


# ─── UI primitives ────────────────────────────────────────────────────────────
def banner() -> None:
    print()
    print(CYAN("╔" + "═" * W + "╗"))
    print(CYAN("║") + BOLD(f"{'  AI Email Assistant':^{W}}") + CYAN("║"))
    print(CYAN("╚" + "═" * W + "╝"))
    print()


def divider(char: str = "─") -> None:
    print(DIM(char * (W + 2)))


def print_ai(text: str) -> None:
    """Word-wrapped assistant reply."""
    prefix = CYAN(BOLD("  Assistant › "))
    indent = " " * 14
    wrapped = textwrap.fill(text.strip(), width=W, subsequent_indent=indent)
    print(f"\n{prefix}{wrapped}\n")


def print_tool_call(name: str, args: dict) -> None:
    """Show the tool the agent is invoking and the arguments it chose."""
    print(YELLOW(f"\n  ⚙  Tool call  › {BOLD(name)}"))
    for k, v in args.items():
        val = str(v)
        print(YELLOW(f"     {k:12s}: {val}"))


def print_tool_result(content: str) -> None:
    """Show the value returned by a tool."""
    for line in content.strip().splitlines():
        print(MAGENTA(f"  │  {line}"))
    print()


def get_input() -> str:
    """Prompt the user and return their input, or 'quit' on Ctrl-C / EOF."""
    try:
        return input(GREEN("\n  You › ")).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "quit"


# ─── Response renderer ────────────────────────────────────────────────────────
def render_messages(messages: list[BaseMessage]) -> bool:
    """
    Render a list of new messages produced by one graph invocation.

    Handles three message types:
      AIMessage   — print the text reply; if it also carries tool_calls,
                    print each tool call header before the reply text.
      ToolMessage — print the tool's return value.

    Returns True if the email was successfully sent (session should end).
    """
    sent = False
    for msg in messages:
        if isinstance(msg, AIMessage):
            # Show tool calls attached to this AI turn
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    print_tool_call(tc["name"], tc.get("args", {}))
            # Show the text reply (may be empty when the LLM only called a tool)
            if msg.content:
                print_ai(msg.content)

        elif isinstance(msg, ToolMessage):
            print_tool_result(msg.content)
            if msg.content.startswith("✓ Email sent"):
                sent = True

    return sent


# ─── Conversation loop ────────────────────────────────────────────────────────
def run() -> None:
    banner()
    print(DIM("  Type 'quit' or press Ctrl+C at any time to exit.\n"))

    conversation: list[BaseMessage] = []

    # ── Opening greeting ──────────────────────────────────────────────────────
    # Invoke the graph with an empty history so the LLM introduces itself
    # and asks whether the user wants to write an email.
    result       = app.invoke({"messages": []})
    conversation = list(result["messages"])
    render_messages(conversation)

    # ── Main loop ─────────────────────────────────────────────────────────────
    while True:
        user_text = get_input()

        if not user_text:
            continue

        if user_text.lower() in {"quit", "exit", "bye", "cancel"}:
            print_ai("Alright, see you next time! 👋")
            break

        divider()
        conversation.append(HumanMessage(content=user_text))

        # Run one agent turn (may internally loop agent ↔ tools until the LLM
        # produces a plain-text reply or the email is sent)
        result       = app.invoke({"messages": conversation})
        new_messages = result["messages"][len(conversation):]
        conversation = list(result["messages"])

        sent = render_messages(new_messages)

        if sent:
            divider("═")
            print(GREEN(BOLD("\n  ✓  Email sent! Session complete.\n")))
            break


if __name__ == "__main__":
    run()