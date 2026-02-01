from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def get_openai_client():
    if os.getenv("AZURE_OPENAI_API_KEY"):
        return AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    else:
        return OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/" if not os.getenv("OPENAI_API_KEY") else None
        )

client = get_openai_client()