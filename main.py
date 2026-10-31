import json
from config.prompts import ENVIRONMENT_PROMPT, WORK_PROMPT
from tools.skill_tools import SKILL_LOADER
from config.llm import client, MODEL
from tools.tool_schemas import TOOLS
from tools.skill_tools import WORKDIR
from tools.registry import TOOL_HANDLERS
from tools.hooks import(
    ToolCallContext,
    trigger_hooks,
)
from tools.execute_tool import execute_tool

def build_system_prompt() -> str:
    return (
        f"你是一个运行在 {WORKDIR} 目录下的编程智能体。当前环境信息：{ENVIRONMENT_PROMPT}。"
        "请使用可用工具完成用户交代的编程任务。"
        f"任务执行规则：{WORK_PROMPT}"
        "优先采取实际行动，而不是仅仅解释解决方案。"
        "在任务完成后，简要说明执行结果。\n\n"
        f"当前可用的skill列表：\n{SKILL_LOADER.catalog()}\n\n"
        "当某项skill适用于当前任务时，必须使用 load_skill 工具读取该skill的完整说明，并按照skill说明执行任务。"
    )


SYSTEM = build_system_prompt()


def agent_loop(messages: list, max_rounds: int = 30):
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
    print("Repo Analysis Agent: Skill Loading")
    print("Enter a question, press Enter to send. Type q to quit.\n")

    history = []

    while True:
        try:
            question = input("\033[36mrepo-agent >> \033[0m").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue

        if question.lower() in {"q", "exit", "quit"}:
            break

        trigger_hooks("UserPromptSubmit", question)
        history.append({
            "role": "user",
            "content": question,
        })

        agent_loop(history)