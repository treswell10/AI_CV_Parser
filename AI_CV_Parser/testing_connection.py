from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

TEMPERATURE = 0.2
MAX_TOKENS = 4096

MODEL = os.environ.get("MODEL")

client = AzureOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://guardian.sars.gov.za/guardian"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01"),
)

print("AzureOpenAI is configured successfully !!!!!!!!!!!!")

