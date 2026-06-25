from app.langfuse import lfuse
from langchain_core.prompts import ChatPromptTemplate

def get_write_email_sys_prompt():
    prompt = lfuse.get_prompt("write_email_sys_prompt")
    template_string = prompt.get_langchain_prompt()
    return ChatPromptTemplate.from_template(template_string)

def get_update_email_sys_prompt():
    prompt = lfuse.get_prompt("update_email_sys_prompt")
    template_string = prompt.get_langchain_prompt()
    return ChatPromptTemplate.from_template(template_string)

def get_query_expander_sys_prompt():
    prompt = lfuse.get_prompt("expand_query_prompt")
    template_string = prompt.get_langchain_prompt()
    return ChatPromptTemplate.from_template(template_string)

def get_response_synthesizer_prompt():
    prompt = lfuse.get_prompt("response_synth")
    template_string = prompt.get_langchain_prompt()
    return ChatPromptTemplate.from_template(template_string)