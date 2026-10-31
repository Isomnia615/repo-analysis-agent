from tools.base_handlers import BASE_HANDLERS
from tools.subagent_tools import run_subagent

TOOL_HANDLERS = {
    **BASE_HANDLERS,
    "task": run_subagent,
}

SUB_HANDLERS = dict(BASE_HANDLERS)