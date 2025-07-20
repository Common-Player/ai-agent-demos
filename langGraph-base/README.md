# LangGraph Base 天气问答 Agent

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
- 用户选择流式输出时，调用大模型的 `stream` 并处理返回数据，边生成边输出内容，实现实时反馈。

## 使用方法
1. 安装依赖：
   ```bash
   npm install
   ```
2. 配置环境变量（如需 API Key 等，可参考 .env 示例）
3. 运行 agent：
   ```bash
   node agent.js
   ```
4. 按提示输入想查询天气的地点和是否流式输出