from langgraph.graph import StateGraph, START, END
from controller.agent_state import AgentState

from app.query_expander import expand_query_node
from app.write_update_mail import write_update_email_node            
from app.response_synth_node import response_synth_node 

def route_after_synthesis(state: AgentState) -> str:
    """
    Analyzes the email_status in the state to dynamically route the graph execution path.
    """
    status = state.get("email_status")
    
    if status == "sent":
        return END 
        
    elif status == "requires_update":
        return "write_update_email_node" 
        
    else:
        return "response_synth_node" 

workflow = StateGraph(AgentState)

# Add your workflow structure nodes natively
workflow.add_node("query_expander_node", expand_query_node)
workflow.add_node("write_update_email_node", write_update_email_node)
workflow.add_node("response_synth_node", response_synth_node)

workflow.add_edge(START, "query_expander_node")
workflow.add_edge("query_expander_node", "write_update_email_node")
workflow.add_edge("write_update_email_node", "response_synth_node")

workflow.add_conditional_edges(
    "response_synth_node",
    route_after_synthesis,
    {
        END: END,
        "write_update_email_node": "write_update_email_node",
        "response_synth_node": "response_synth_node" 
    }
)

app = workflow.compile()

# # Generate visual architecture diagram map for verification tracking safely
# try:
#     png_data = app.get_graph().draw_mermaid_png()
#     with open("graph_flow.png", "wb") as f:
#         f.write(png_data)
#     print("\n[Success]: Graph saved! Open 'graph_flow.png' in your project root to see it.")
# except Exception as e:
#     print(f"\n[Error rendering PNG]: {e}")