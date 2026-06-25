import os
import smtplib
from typing import Optional
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()



# ─── Tool: send_email ─────────────────────────────────────────────────────────
def send_email(
    recipient: Optional[str] = None,
    subject:   Optional[str] = None,
    body:      Optional[str] = None,
) -> str:
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

    return f"✓ Email sent successfully to {recipient}."