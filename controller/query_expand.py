from typing import TypedDict
from pydantic import Field

class QueryExpand(TypedDict):
    #request analysis description = analyse user req based on pre msg
    recipient: str = Field(description="Email address of the recipient")
    subject: str = Field(description="Small and concise subject of the email")
    body: str = Field(description="Body of the email")

