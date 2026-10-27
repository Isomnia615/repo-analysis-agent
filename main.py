import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from config.prompts import SYSTEM
from tools.tool_schemas import TOOLS
from tools.registry import TOOL_HANDLERS
from tools.hooks import(
    ToolCallContext,
    trigger_hooks,
)
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


def agent_loop(messages: list, max_rounds: int = 8):
    """持续调用模型和工具，直到模型结束或达到轮数上限。"""

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                *messages,
            ],
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=3000,
        )

        assistant_message = response.choices[0].message

        # 保存模型本轮响应，包括可能存在的 tool_calls
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        # 没有工具调用时，显示最终回答并结束
        if not assistant_message.tool_calls:
            print(
                assistant_message.content
                or "模型没有返回文本内容。"
            )
            return

        # 执行模型请求的工具
        for call in assistant_message.tool_calls:
            name = call.function.name
            print(f"\n[调用工具] {name}")

            handler = TOOL_HANDLERS.get(name)

            if handler is None:
                output = f"错误：未知工具 {name}"
            else:
                try:
                    arguments = json.loads(
                        call.function.arguments
                    )

                    if not isinstance(arguments, dict):
                        raise ValueError("工具参数必须是 JSON 对象")

                    context = ToolCallContext(
                        call_id=call.id,
                        name=name,
                        input=arguments,
                    )

                    blocked=trigger_hooks(
                        "PreToolUse",
                        context,
                    )

                    if blocked is not None:
                        output = f"权限拒绝：{blocked}"

                    else:

                        try:
                            output = handler(**arguments)
                        except Exception as exc:
                            output = (
                                f"工具执行失败："
                                f"{type(exc).__name__}: {exc}"
                            )

                        try:
                           trigger_hooks(
                               "PostToolUse",
                                context,
                                output,
                            )
                        except Exception as hook_exc:
                            # Hook 本身出错，不覆盖原始工具结果
                            print(f"[HOOK] 执行后回调失败：{hook_exc}")

                except Exception as exc:
                    output = (
                        f"工具调用准备失败："
                        f"{type(exc).__name__}: {exc}"
                    )

            print(str(output)[:300])

            # 将工具结果交还给模型
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(output),
            })

    print("达到最大工具调用轮数，请缩小任务范围后重试。")


if __name__ == "__main__":
    history = []

    while True:
        question = input("\nrepo-agent >> ").strip()

        if question.lower() in {"exit", "quit", "q"}:
            break

        if not question:
            continue

        history.append({
            "role": "user",
            "content": question,
        })

        agent_loop(history)