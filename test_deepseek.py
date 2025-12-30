import os
from langchain_openai import ChatOpenAI

api_key = "sk-9281fc022631d4fb483c45a4bf4e9e4e7"
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com",
    temperature=0.3,
    max_tokens=2000,
    timeout=10
)

try:
    print("Testing DeepSeek connection...")
    res = llm.invoke("Hi, please return 'success'")
    print(f"Result: {res.content}")
except Exception as e:
    print(f"DeepSeek connection FAILED: {e}")
