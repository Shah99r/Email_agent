from langgraph.graph import StateGraph, START, END
from controller.agent_state import AgentState

from app.query_expander import expand_query_node
from app.write_update_mail import write_update_email_node            
from app.response_synth_node import response_synth_node   
# from IPython.display import Image, display


def route_after_synthesis(state: AgentState) -> str:
    """
    Analyzes the email_status in the state to dynamically route the graph execution path.
    """
    status = state.get("email_status")
    
    if status == "sent":
        return END # Gracefully exit the graph execution loop
        
    elif status == "requires_update":
        return "write_update_email_node" # Route back to LLM to process feedback
        
    else:
        # Default fallback if the validation gate intercepted a 'send' command 
        # because fields were missing (status resets to 'drafted').
        return "response_synth_node" # Self-loop to ask for input again

workflow = StateGraph(AgentState)

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
        "response_synth_node": "response_synth_node" # The self-correcting fallback loop
    }
)

app = workflow.compile()

# Generate png of Graph


# try:
#     png_data = app.get_graph().draw_mermaid_png()
#     with open("graph_flow.png", "wb") as f:
#         f.write(png_data)
#     print("\n[Success]: Graph saved! Open 'graph_flow.png' in your project root to see it.")
# except Exception as e:
#     print(f"\n[Error rendering PNG]: {e}")
#     print("Falling back to Mermaid Markdown code block instead:\n")
#     print(app.get_graph().draw_mermaid())