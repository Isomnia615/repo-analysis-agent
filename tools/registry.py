from tools.github_tools import (
    get_repo_info,
    list_repo_files,
    read_repo_file,
)

TOOL_HANDLERS = {
    "get_repo_info": get_repo_info,
    "list_repo_files": list_repo_files,
    "read_repo_file": read_repo_file,
}