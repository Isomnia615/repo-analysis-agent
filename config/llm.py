import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "").strip()
MODEL = os.getenv("LLM_MODEL")

if not API_KEY or not MODEL:
    raise RuntimeError("请先正确配置 .env")

client_args = {"api_key": API_KEY}
if BASE_URL:
    client_args["base_url"] = BASE_URL

client = OpenAI(**client_args)
