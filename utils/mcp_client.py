from langchain_mcp_adapters.client import MultiServerMCPClient  
import os
from dotenv import load_dotenv
load_dotenv()   
mcp_client = MultiServerMCPClient({
        "gmail": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-google-gmail@latest"],
            "env": {
                "GMAIL_CREDENTIALS_PATH": os.getenv("GMAIL_CREDENTIAL_PATH", ""),
                "GMAIL_TOKEN_PATH": os.getenv("GMAIL_TOKEN_PATH", "")
            }
        }
    }
)
