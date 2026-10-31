from tools.base_handlers import BASE_HANDLERS
from tools.skill_tools import SKILL_LOADER
from tools.subagent_tools import run_subagent

TOOL_HANDLERS = {
    **BASE_HANDLERS,
    "task": run_subagent,
    "load_skill": SKILL_LOADER.load,
}

SUB_HANDLERS = dict(BASE_HANDLERS)