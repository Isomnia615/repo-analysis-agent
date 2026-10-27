import os
import json
import base64
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

API_ROOT = "https://api.github.com"


def github_get(path: str):
    """发送只读 GitHub API 请求。"""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-analysis-agent",
    }

    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        f"{API_ROOT}{path}",
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def get_repo_info(owner: str, repo: str) -> str:
    """查询仓库基本信息。"""
    owner = quote(owner, safe="")
    repo = quote(repo, safe="")

    data = github_get(f"/repos/{owner}/{repo}")

    info = {
        "name": data.get("full_name"),
        "description": data.get("description"),
        "language": data.get("language"),
        "default_branch": data.get("default_branch"),
        "stars": data.get("stargazers_count"),
        "url": data.get("html_url"),
    }

    return json.dumps(info, ensure_ascii=False)


def list_repo_files(
    owner: str,
    repo: str,
    path: str = "",
) -> str:
    """列出仓库根目录或指定目录下的文件。"""
    owner = quote(owner, safe="")
    repo = quote(repo, safe="")
    path = quote(path, safe="/")

    endpoint = f"/repos/{owner}/{repo}/contents"
    if path:
        endpoint += f"/{path}"

    data = github_get(endpoint)

    if not isinstance(data, list):
        return "该路径不是目录，请尝试读取文件。"

    files = [
        {
            "name": item.get("name"),
            "path": item.get("path"),
            "type": item.get("type"),
        }
        for item in data[:100]
    ]

    return json.dumps(files, ensure_ascii=False)


def read_repo_file(
    owner: str,
    repo: str,
    path: str,
) -> str:
    """读取公开仓库中的小型文本文件，不执行文件内容。"""
    owner = quote(owner, safe="")
    repo = quote(repo, safe="")
    path = quote(path, safe="/")

    data = github_get(
        f"/repos/{owner}/{repo}/contents/{path}"
    )

    if data.get("type") != "file":
        return "指定路径不是普通文件。"

    if data.get("size", 0) > 1_000_000:
        return "文件超过当前工具的读取大小限制。"

    if data.get("encoding") != "base64" or not data.get("content"):
        return "GitHub API 未返回可直接读取的文件内容。"

    raw = base64.b64decode(data["content"]).decode(
        "utf-8",
        errors="replace",
    )

    # 初期限制返回长度，避免一次占用过多模型上下文。
    if len(raw) > 12000:
        raw = raw[:12000] + "\n\n[文件内容已截断]"

    return raw