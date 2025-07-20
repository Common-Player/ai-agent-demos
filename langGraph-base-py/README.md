# LangGraph Base 天气问答 Agent (Python 版)

## 项目简介

本项目基于 LangGraph、LangChain 和大模型 API，构建了一个支持天气问答的命令行智能 Agent。

## 主要功能
- 支持命令行交互，询问任意城市天气
- 可选择流式或非流式输出大模型回复
- 支持多种大模型后端（如 Anthropic Claude、DeepSeek 等）
- 集成 TavilySearch 用于检索实时天气相关信息

## 功能实现方法
- 集成 TavilySearch 工具，Agent 在需要外部信息时会自动调用 Tavily 进行实时天气等相关内容检索，提升回答的准确性和时效性。
- 通过 LangChain 的 Agent 框架集成多种大模型和工具完成搭建
- 用户选择流式输出时，调用大模型的 `astream` 并处理返回数据，边生成边输出内容，实现实时反馈。

## 使用方法
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的 API Keys
   ```
3. 运行 agent：
   ```bash
   python agent.py
   ```
4. 按提示输入想查询天气的地点和是否流式输出

## 环境变量配置
需要在 `.env` 文件中配置以下 API Keys：
- `ANTHROPIC_API_KEY`: Anthropic Claude API 密钥
- `TAVILY_API_KEY`: Tavily 搜索 API 密钥