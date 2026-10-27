import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
print("程序开始运行", flush=True)


api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL", "").strip()
model = os.getenv("LLM_MODEL")

print("API Key 已配置：", bool(api_key), flush=True)
print("模型名称：", model, flush=True)
print("Base URL：", base_url, flush=True)

if not api_key or not model:
    raise RuntimeError(
        "请检查 .env，确认已配置 LLM_API_KEY 和 LLM_MODEL"
    )

client_args = {"api_key": api_key}

if base_url:
    client_args["base_url"] = base_url

client = OpenAI(**client_args)

print("正在请求大模型，请稍候...", flush=True)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "你是一个擅长分析 Python 项目的助手。",
        },
        {
            "role": "user",
            "content": "请用一句话解释什么是 AI Agent。",
        },
    ],
    max_tokens=200,
)

print(response.choices[0].message.content)