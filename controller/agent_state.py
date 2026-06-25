from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from controller.query_expand import QueryExpand
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    draft: QueryExpand | None
    email_status: Literal["drafted", "requires_update", "approved_to_send", "sent"]
    feedback: str

