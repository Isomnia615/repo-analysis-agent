import json

from config.prompts import SYSTEM
from config.llm import client, MODEL
from tools.tool_schemas import TOOLS
from tools.registry import TOOL_HANDLERS
from tools.hooks import(
    ToolCallContext,
    trigger_hooks,
)
from tools.execute_tool import execute_tool


def agent_loop(messages: list, max_rounds: int = 8):
    """持续调用模型和工具，直到模型结束或达到轮数上限。"""

    rounds_since_todo = 0

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
            force = trigger_hooks("Stop", messages)
            if force:
                messages.append({
                    "role": "user",
                    "content": str(force),
                })
                continue

            print(
                assistant_message.content
                or "模型没有返回文本内容。"
            )
            return

        used_todo = False
        for call in assistant_message.tool_calls:
            name = call.function.name
            print(f"\n[调用工具] {name}")

            try:
                arguments = json.loads(call.function.arguments)
                if not isinstance(arguments, dict):
                    raise ValueError("工具参数必须是 JSON 对象")

                context = ToolCallContext(
                    call_id=call.id,
                    name=name,
                    input=arguments,
                )
                output = execute_tool(context, TOOL_HANDLERS)

                if name == "todo_write":
                    used_todo = True
            except Exception as exc:
                output = (
                    f"工具调用准备失败："
                    f"{type(exc).__name__}: {exc}"
                )

            print(str(output)[:300])
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(output),
            })

        rounds_since_todo = 0 if used_todo else rounds_since_todo + 1
        if rounds_since_todo >= 3:
            messages.append({
                "role": "user",
                "content": "提醒：请更新你的 todos。",
            })
            rounds_since_todo = 0

    print("达到最大工具调用轮数，请缩小任务范围后重试。")


if __name__ == "__main__":
    history = []

    while True:
        question = input("\nrepo-agent >> ").strip()

        if question.lower() in {"exit", "quit", "q"}:
            break

        if not question:
            continue

        trigger_hooks("UserPromptSubmit", question)
        history.append({
            "role": "user",
            "content": question,
        })

        agent_loop(history)