from dataclasses import dataclass
from pathlib import Path
from typing import Any

WORKDIR = Path.cwd()
HOOKS = {"UserPromptSubmit": [], "PreToolUse": [], "PostToolUse": [], "Stop": []}

@dataclass
class ToolCallContext:
    name: str
    input: dict[str, Any]
    call_id: str

def register_hook(event: str, callback):
    if event not in HOOKS:
        raise ValueError(f"未知 Hook 事件：{event}")
    
    HOOKS[event].append(callback)

def trigger_hooks(event: str, *args):
    if event not in HOOKS:
        raise ValueError(f"未知 Hook 事件：{event}")
    
    for callback in HOOKS[event]:
        result = callback(*args)

        if result is not None:  # A hook result blocks this tool call.
            return result
    return None

READ_ONLY_TOOLS = {
    "get_repo_info",
    "list_repo_files",
    "read_repo_file",
    "todo_write",
    "task",
    "load_skill",
}

DENIED_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
}

def log_hook(context: ToolCallContext) -> None:
    """记录每一次工具调用尝试。"""
    print(f"\n[HOOK] 准备调用工具：{context.name}")

def permission_hook(context: ToolCallContext) -> str | None:
    """检查工具白名单和敏感路径。"""

    # 1. 只允许白名单中的工具
    if context.name not in READ_ONLY_TOOLS:
        return f"工具不在只读白名单中：{context.name}"

    # 2. 检查可能表示文件路径的参数
    path_keys = ("path", "file_path", "filepath", "filename")

    for key in path_keys:
        path = context.input.get(key, "")

        if not path:
            continue

        if not isinstance(path, str):
            return f"文件路径参数格式错误：{key}"

        parts = path.replace("\\", "/").split("/")

        for part in parts:
            if part.lower() in DENIED_FILENAMES:
                return f"禁止读取敏感文件：{part}"

    # None 表示允许继续执行
    return None

def large_output_hook(
    context: ToolCallContext,
    output: Any,
) -> None:
    """工具返回内容过大时给出提醒。"""
    if len(str(output)) > 100_000:
        print(
            f"[HOOK] 警告：工具 {context.name} "
            "返回内容超过 100000 个字符"
        )

TOOL_CALL_COUNTS={}
def count_tool_hook(context,output):
    name = context.name

    TOOL_CALL_COUNTS[name] = (
        TOOL_CALL_COUNTS.get(name, 0) + 1
    )

    print(
        f"[HOOK] {name} "
        f"累计调用 {TOOL_CALL_COUNTS[name]} 次"
    )

def context_inject_hook(query: str):
    print(f"\033[90m[HOOK] UserPromptSubmit: working in {WORKDIR}\033[0m")
    return None

def summary_hook(messages: list):
    tool_count = sum(1 for m in messages
                     if m.get("role") == "tool")
    print(f"\033[90m[HOOK] Stop: session used {tool_count} tool calls\033[0m")
    return None

# 注册执行前 Hook
register_hook("PreToolUse", log_hook)
register_hook("PreToolUse", permission_hook)
register_hook("UserPromptSubmit", context_inject_hook)

# 注册执行后 Hook
register_hook("PostToolUse", large_output_hook)
register_hook("PostToolUse", count_tool_hook)
register_hook("Stop", summary_hook)
