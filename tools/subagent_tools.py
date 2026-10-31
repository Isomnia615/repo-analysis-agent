import json

from tools.hooks import ToolCallContext, trigger_hooks
from config.prompts import SUB_SYSTEM
from tools.tool_schemas import SUB_TOOLS
from tools.base_handlers import BASE_HANDLERS
from config.llm import client, MODEL
from tools.execute_tool import execute_tool


def run_subagent(prompt: str) -> str:
    print("\n\033[35m[Subagent started]\033[0m")
    messages = [{"role": "user", "content": prompt}]

    for _ in range(30):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SUB_SYSTEM},
                *messages,
            ],
            tools=SUB_TOOLS,
            tool_choice="auto",
            max_tokens=8000,
        )
        assistant_message = response.choices[0].message
        messages.append(assistant_message.model_dump(exclude_none=True))

        if not assistant_message.tool_calls:
            force = trigger_hooks("Stop", messages)
            if force:
                messages.append({"role": "user", "content": str(force)})
                continue
            print("\033[35m[Subagent done]\033[0m")
            return assistant_message.content or "(no summary)"

        for call in assistant_message.tool_calls:
            name = call.function.name
            print(f"  \033[90m[sub] 调用工具: {name}\033[0m")

            try:
                arguments = json.loads(call.function.arguments)
                if not isinstance(arguments, dict):
                    raise ValueError("工具参数必须是 JSON 对象")

                context = ToolCallContext(
                    call_id=call.id,
                    name=name,
                    input=arguments,
                )
                output = execute_tool(context, BASE_HANDLERS)
            except Exception as exc:
                output = (
                    f"工具调用准备失败："
                    f"{type(exc).__name__}: {exc}"
                )

            print(f"  \033[90m[sub] {str(output)[:100]}\033[0m")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(output),
            })

    print("\033[35m[Subagent stopped]\033[0m")
    return "Subagent stopped after 30 turns without a final answer."