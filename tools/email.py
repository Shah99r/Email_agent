import os
import smtplib
from typing import Optional
from email.message import EmailMessage
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

# ─── Shared draft state ───────────────────────────────────────────────────────
# A single dict acts as the "clipboard" between agent turns.
# The agent never needs to re-state the full email; it just patches fields.
draft: dict[str, str] = {
    "recipient": "",
    "subject":   "",
    "body":      "",
}


def draft_summary() -> str:
    """Return a human-readable snapshot of the current draft."""
    r = draft["recipient"] or "(not set)"
    s = draft["subject"]   or "(not set)"
    b = draft["body"]      or "(not set)"
    return (
        "┌─ Current Draft ──────────────────────────────\n"
        f"│  To      : {r}\n"
        f"│  Subject : {s}\n"
        f"│  Body    :\n"
        + "\n".join(f"│    {line}" for line in b.splitlines())
        + "\n└──────────────────────────────────────────────"
    )


# ─── Tool: update ─────────────────────────────────────────────────────────────
@tool
def update(
    recipient: Optional[str] = None,
    subject:   Optional[str] = None,
    body:      Optional[str] = None,
) -> str:
    """
    Creates or updates the email draft stored in memory.

    Call this tool whenever the user wants to:
      - Draft a new email
      - Change the recipient, subject, or body
      - Apply any edit or revision to the current draft

    Only pass the fields that need to change; omitted fields stay as-is.

    Args:
        recipient: Email address of the recipient.
        subject:   Subject line of the email.
        body:      Full body text of the email.

    Returns:
        A confirmation string showing the updated draft.
    """
    if recipient is not None:
        draft["recipient"] = recipient.strip()
    if subject is not None:
        draft["subject"] = subject.strip()
    if body is not None:
        draft["body"] = body.strip()

    return f"Draft updated.\n\n{draft_summary()}"


# ─── Tool: send_email ─────────────────────────────────────────────────────────
@tool
def send_email() -> str:
    """
    Sends the current email draft to the recipient via SMTP.

    Call this tool ONLY when the user explicitly confirms they want to
    send the email (e.g. "send it", "go ahead and send", "yes, send").

    Reads credentials from environment variables:
        SENDER_EMAIL     – the Gmail (or other) address to send from
        SENDER_PASSWORD  – the app password for that address
        SMTP_SERVER      – optional, defaults to smtp.gmail.com
        SMTP_PORT        – optional, defaults to 587

    Returns:
        A success or error message string.
    """
    sender    = os.getenv("SENDER_EMAIL", "").strip()
    password  = os.getenv("SENDER_PASSWORD", "").strip()
    smtp_host = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    # ── Credential check ──────────────────────────────────────────────────────
    if not sender or not password:
        return (
            "Error: SENDER_EMAIL and SENDER_PASSWORD must be set in your "
            ".env file before sending."
        )

    # ── Draft validation ──────────────────────────────────────────────────────
    recipient = draft["recipient"]
    subject   = draft["subject"]
    body      = draft["body"]

    missing = [f for f, v in [("recipient", recipient), ("subject", subject), ("body", body)] if not v]
    if missing:
        return f"Error: Cannot send – the following fields are empty: {', '.join(missing)}."

    # ── Build message ─────────────────────────────────────────────────────────
    msg            = EmailMessage()
    msg["From"]    = sender
    msg["To"]      = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    # ── Send ──────────────────────────────────────────────────────────────────
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        return (
            "Error: SMTP authentication failed. "
            "Check that SENDER_EMAIL and SENDER_PASSWORD are correct, "
            "and that 'less secure app access' or an App Password is enabled."
        )
    except Exception as exc:
        return f"Error: Failed to send email – {exc}"

    # Clear draft after a successful send so a fresh session starts clean
    draft.update({"recipient": "", "subject": "", "body": ""})

    return f"✓ Email sent successfully to {recipient}."