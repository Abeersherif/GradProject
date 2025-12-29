import sys
import os

print(f"Python executable: {sys.executable}")
print("sys.path:")
for p in sys.path:
    print(f"  {p}")

try:
    import pydantic
    print(f"Pydantic version: {pydantic.VERSION}")
    print(f"Pydantic file: {pydantic.__file__}")
except ImportError:
    print("Pydantic not found")

try:
    import openai
    print(f"OpenAI version: {openai.__version__}")
    print(f"OpenAI file: {openai.__file__}")
except ImportError:
    print("OpenAI not found")

try:
    import langchain
    print(f"LangChain version: {langchain.__version__}")
except ImportError:
    print("LangChain not found")
