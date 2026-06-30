from langchain_ollama import ChatOllama

ai_models = {
    "qwen2.5:7b_temp_0.3": ChatOllama(model="qwen2.5:7b", temperature=0.3),
    "qwen2.5:7b_temp_0": ChatOllama(model="qwen2.5:7b", temperature = 0)
}

expand_query_agent = ai_models["qwen2.5:7b_temp_0.3"]
email_agent = ai_models["qwen2.5:7b_temp_0"]
response_agent = ai_models["qwen2.5:7b_temp_0.3"]

