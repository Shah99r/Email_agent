from langfuse.langchain import CallbackHandler
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()

lfuse = Langfuse()
langfuse_handler = CallbackHandler()

