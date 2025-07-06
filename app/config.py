import os
from dotenv import load_dotenv
load_dotenv()

# For llm
llm_api_key = os.getenv("GOOGLE_API_KEY", "")
model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
temperature = os.getenv("TEMPERATURE", "1.0")

# For tools
tavily_api_key = os.getenv("TAVILY_API_KEY", "")
