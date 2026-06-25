from controller.query_expand import QueryExpand
from controller.agent_state import AgentState
from app.prompt import get_query_expander_sys_prompt
from app.models import expand_query_agent
from langgraph.types import Command
import re


llm = expand_query_agent
# node
# expand query and then parse it into the state
def expand_query_node(state: AgentState) -> Command:
    """Parse the user prompt into a structured output"""
    structured_llm = llm.with_structured_output(QueryExpand)
    sys_prompt = get_query_expander_sys_prompt()
    chain = sys_prompt | structured_llm
    latest_message = state["messages"][-1].content if state["messages"] else ""
    parsed_output = chain.invoke({"message": latest_message})

    # --- AUTO-CORRECT GUARDRAIL ---
    # 1. Use regex to find any valid email directly in the raw user message
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', latest_message)
    
    if email_match:
        exact_email = email_match.group(0).lower()
        # 2. Force the exact string onto your parsed_output object
        if hasattr(parsed_output, "recipient"):
            parsed_output.recipient = exact_email
        elif isinstance(parsed_output, dict):
            parsed_output["recipient"] = exact_email

    print(parsed_output)
    return Command(
        update={"draft": parsed_output, "email_status": "drafted"},
        goto="write_update_email_node"
    )
    