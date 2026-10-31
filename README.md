# Repo Analysis Agent

A Python-based GitHub repository analysis agent that uses LLM tool calling to inspect repository metadata, browse file structures, and read source code.

**This project is inspired by the agent-building concepts and implementation patterns demonstrated in [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code), particularly tool execution workflows and Hooks. These ideas are adapted to the GitHub repository analysis scenario.**

## Features

- **Repository Inspection** — Retrieve repository information and browse file structures.
- **Source Code Reading** — Read repository files to support evidence-based analysis.
- **LLM Tool Calling** — Select and execute tools according to user requests.
- **Hook Mechanism** — Implement pre-tool checks, execution logging, and post-tool processing.
- **Permission Control** — Restrict tool access through a whitelist and sensitive-file checks.

## Tech Stack

- Python
- LLM API
- GitHub API
- Function / Tool Calling
- Hooks

## Getting Started

1. Clone the repository:

   ```bash
   git clone <https://github.com/Isomnia615/repo-analysis-agent>
   cd repo-analysis-agent
   ```

2. Configure the required API credentials using `.env.example` as a reference.
3. Install the project dependencies.
4. Run the agent:

   ```bash
   python main.py
   ```

## Future Improvements

This project is under active development. I will continue improving the agent's planning and tool selection, permission control, error handling, and analysis quality.

## Reference

- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) — Reference for agent-building concepts, tool execution workflows, and Hooks.

---

# Repo Analysis Agent（中文）

一个基于 Python 的 GitHub 开源仓库分析智能体，通过大模型工具调用获取仓库信息、浏览文件目录和读取源码。

**本项目参考了 [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) 中的智能体构建思路与实现模式，重点借鉴工具调用流程和 Hooks 机制，并结合 GitHub 仓库分析场景进行了适配与改造。**

## 项目功能

- **仓库信息查询**：获取 GitHub 仓库的基本信息。
- **目录浏览**：查看仓库中的文件与目录结构。
- **源码读取**：读取指定文件，为项目分析提供事实依据。
- **大模型工具调用**：根据用户需求选择并执行相应工具。
- **Hook 机制**：在工具调用前后执行日志记录、权限检查等操作。
- **权限控制**：通过工具白名单和敏感文件路径检查限制工具访问。

## 技术栈

- Python
- 大语言模型 API
- GitHub API
- Function / Tool Calling
- Hooks

## 快速开始

1. 克隆项目：

   ```bash
   git clone <https://github.com/Isomnia615/repo-analysis-agent>
   cd repo-analysis-agent
   ```

2. 参考 `.env.example` 配置所需的 API 凭证。
3. 安装项目所需依赖。
4. 启动 Agent：

   ```bash
   python main.py
   ```

## 后续计划

本项目仍在持续开发中。后续将继续完善智能体的任务规划与工具选择能力、权限控制机制、异常处理流程和仓库分析质量，逐步提升其稳定性与实用性。

## 参考项目

- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)：参考其智能体构建思路、工具调用流程与 Hooks 机制。

