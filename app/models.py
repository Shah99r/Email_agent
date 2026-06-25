from langchain_ollama import ChatOllama

ai_models = {
    "llama3.2_temp_0.3": ChatOllama(model="llama3.2", temperature=0.3),
    "llama3.2_temp_0": ChatOllama(model="llama3.2", temperature = 0)
}

expand_query_agent = ai_models["llama3.2_temp_0.3"]
email_agent = ai_models["llama3.2_temp_0"]
response_agent = ai_models["llama3.2_temp_0.3"]

