import asyncio
import re
from langgraph.types import Command
from controller.agent_state import AgentState
from utils.mcp_client import mcp_client

async def response_synth_node(state: AgentState) -> Command:
    draft = state.get('draft') or {"recipient": "", "subject": "", "body": ""}

    # 1. Clean the recipient text using the regex pattern
    recipient = draft.get("recipient", "").strip()
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', recipient)
    
    if match:
        recipient = match.group(0).lower().strip() 
    else:
        recipient = recipient.replace("[", "").replace("]", "").strip()
    
    body = draft.get("body", "").strip()
    subject = draft.get('subject', '(No Subject Line)')

    # Update draft snapshot with the regex-cleaned email address
    if isinstance(draft, dict):
        draft["recipient"] = recipient
    else:
        draft.recipient = recipient

    # 2. Render current draft snapshot details
    print("\n" + "="*50)
    print("           CURRENT EMAIL DRAFT FOR REVIEW          ")
    print("="*50)
    print(f"To:      {recipient if recipient else '[MISSING - REQUIRED]'}")
    print(f"Subject: {subject}")
    print("-"*50)
    print("Body:")
    print(body if body else "[MISSING - REQUIRED]")
    print("="*50 + "\n")

    # 3. Grab user input safely in async thread
    print("Options: Type 'send' to approve execution, or describe changes.")
    user_input = await asyncio.to_thread(input, "Your input: ")
    user_input = user_input.strip()

    # 4. HARD SEND ROUTE (Deterministic Tool Invocation)
    if user_input.lower() == 'send':
        # Block if critical structures are missing
        if not recipient or not body:
            print("\nERROR: Cannot proceed. Critical data structures are missing.")
            return Command(
                update={"email_status": "drafted"}, 
                goto="response_synth_node"
            )
            
        print("\nApproving dispatch. Fetching Gmail MCP tools...")
        mcp_tools = await mcp_client.get_tools()
        tool_map = {tool.name: tool for tool in mcp_tools}
        
        target_tool = "gmail_send_message"
        if target_tool in tool_map:
            # Construct the clean payload
            tool_args = {
                "to": recipient,
                "subject": subject,
                "body": body
            }
            
            # Defensive Check: Explicitly guard against any rogue nil/empty keys
            for field in ['attachment_paths', 'cc', 'bcc']:
                if field in tool_args and tool_args[field] in ['', '<nil>', 'none', 'null', None]:
                    del tool_args[field]

            print(f"Directly calling MCP Tool: {target_tool}...")
            tool_result = await tool_map[target_tool].ainvoke(tool_args)
            print(f"[Tool Execution Output]: {tool_result}")
            
            return Command(update={"email_status": "sent"}, goto="__end__")
        else:
            print(f"❌ Error: {target_tool} tool not exposed by MCP server.")
            return Command(update={"email_status": "drafted"}, goto="response_synth_node")

    # 5. HARD REVISION ROUTE (Bypasses LLM entirely)
    else:
        print("\n📝 Routing back to update loop with feedback...")
        return Command(
            update={
                "email_status": "requires_update",
                "feedback": user_input
            },
            goto="write_update_email_node"
        )