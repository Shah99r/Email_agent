from langgraph.types import Command
from controller.agent_state import AgentState
from app.tools import send_email 
import re

def response_synth_node(state: AgentState) -> Command:
    draft = state.get('draft') or {"recipient": "", "subject": "", "body": ""}

    recipient = draft.get("recipient", "").strip()
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', recipient)
    

    if match:
        # .group(0) grabs the actual text string matched by the regex pattern
        recipient = match.group(0).lower().strip() 
    else:
        # Fallback just in case no email structure was detected
        recipient = recipient.replace("[", "").replace("]", "").strip()
    
    body = draft.get("body", "").strip()

    # 1. Show the user the current state of the draft
    print("\n" + "="*50)
    print("           CURRENT EMAIL DRAFT FOR REVIEW          ")
    print("="*50)
    print(f"To:      {recipient if recipient else '[MISSING - REQUIRED]'}")
    print(f"Subject: {draft.get('subject', '(No Subject Line)')}")
    print("-"*50)
    print("Body:")
    print(body if body else "[MISSING - REQUIRED]")
    print("="*50 + "\n")

    # 2. Grab the user's intent
    print("Options: Type 'send' to approve, or type your modification requests.")
    user_input = input("Your input: ").strip()

    # 3. INTERCEPT AND CHECK VALIDS BEFORE SENDING
    if user_input.lower() == 'send':
        missing_fields = []
        if not recipient:
            missing_fields.append("Recipient Email")
        if not body:
            missing_fields.append("Email Body")

        # If crucial data is missing, BLOCK the helper function call
        if missing_fields:
            print(f"\n❌ ERROR: Cannot send. Missing: {', '.join(missing_fields)}.")
            print("Please provide the missing details first.")
            
            # Loop back to the exact same node to ask again
            return Command(
                update={"email_status": "drafted"}, 
                goto="response_synth_node"
            )
        
        # If everything passes structural check, execute the helper safely!
        print("\n🚀 All checks passed. Sending email...")
        tool_result = send_email(
            recipient=recipient,
            subject=draft.get('subject', ''),
            body=body
        )
        print(f"[Tool Output]: {tool_result}")
        
        return Command(update={"email_status": "sent"}, goto="__end__")

    # 4. Handle standard text updates/modifications
    else:
        return Command(
            update={
                "email_status": "requires_update",
                "feedback": user_input
            },
            goto="write_update_email_node"
        )