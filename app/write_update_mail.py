from controller.query_expand import QueryExpand
from controller.agent_state import AgentState
from app.prompt import get_write_email_sys_prompt, get_update_email_sys_prompt
from app.models import email_agent
from langgraph.types import Command

llm = email_agent
structured_llm = llm.with_structured_output(QueryExpand)

# Write and update email node
def write_update_email_node(state: AgentState) -> Command:
    """Call the LLM with the current body draft and use the update tool to make changes"""
    draft = state['draft']
    recipient_val = (draft.recipient if hasattr(draft, "recipient") else draft.get("recipient", "")).lower()
    subject_val = draft.subject if hasattr(draft, "subject") else draft.get("subject", "")
    body_val = draft.body if hasattr(draft, "body") else draft.get("body", "")
    
    if state['email_status'] == "requires_update":
        update_sys_prompt = get_update_email_sys_prompt()
        chain = update_sys_prompt | structured_llm
        response = chain.invoke({
            "recipient": recipient_val,
            "subject": subject_val,
            "body_draft": body_val,
            "user_feedback": state['feedback']
        })
    else:
        write_sys_prompt = get_write_email_sys_prompt()
        chain = write_sys_prompt | structured_llm
        response = chain.invoke({
            "recipient": recipient_val,
            "subject": subject_val,
            "body_draft": body_val
        })
    
    return Command(
        update={
            "draft": response, 
            "email_status": "drafted" 
        },
        goto="response_synth_node"
    )




