from app.graph import app
from app.langfuse import langfuse_handler
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import traceback
import asyncio

load_dotenv()

async def run_email_agent():
    print("=" * 60)
    print("🚀 EMAIL GENERATION & REFINEMENT AGENT CORE BOOTED")
    print("=" * 60)
    
    # Prompt user for their core objective
    initial_prompt = input("What email task would you like to perform today?\n👉 ").strip()
    if not initial_prompt:
        print("❌ Action canceled. An initial instruction is required to begin.")
        return

    # Initialize a clean global state dictionary matching AgentState schemas

    
    initial_state = {
        "messages": [HumanMessage(content=initial_prompt)],
        "email_status": "drafting",
        "draft": {
            "recipient": "",
            "subject": "",
            "body": ""
        },
        "feedback": ""
    }

    print("\n[Processing]: Expanding intent data blueprints and crafting initial draft...")
    
    # 3. INTERACTIVE AGENT GRAPH EXECUTION LOOP
    # Since human verification uses terminal inputs, we invoke the graph session
    # and wait for it to cleanly complete or exit at the END node.
    try:
        # Pass the Langfuse configuration handler in standard config to log agent pipelines
        final_output = await app.ainvoke(
            initial_state, 
            config={"callbacks": [langfuse_handler]}
        )
        
        print("\n" + "=" * 60)
        print("🎉 PROCESS COMPLETION REPORT")
        print("=" * 60)
        print(f"Final Action Lifecycle Status: {final_output.get('email_status', 'Completed')}")
        print("System safely powered down.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Core Runtime Crash Intercepted: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_email_agent())