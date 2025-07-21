# LangGraph Base 天气问答 Agent (Python 版)

## 项目简介

本项目基于 LangGraph、LangChain 和大模型 API，构建了一个支持天气问答的命令行智能 Agent。

## 主要功能
- 支持命令行交互，询问任意城市天气
- 使用 Google Gemini 2.5 Pro 大语言模型
- 可选择流式或非流式输出大模型回复
- 集成 TavilySearch 用于检索实时天气相关信息
- 实时显示 Tavily 搜索工具的调用状态

## 功能实现方法
- 集成 TavilySearch 工具，Agent 在需要外部信息时会自动调用 Tavily 进行实时天气等相关内容检索，提升回答的准确性和时效性。
- 通过 LangChain 的 Agent 框架集成 Gemini 2.5 Pro 大模型和搜索工具完成搭建
- 实时显示工具调用状态，让用户清楚了解搜索过程
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
5. 观察程序显示的 Tavily 搜索工具调用状态

## 环境变量配置
创建 `.env` 文件并配置以下 API Keys：

```bash
# Google AI Studio API 配置（必需）
GOOGLE_API_KEY=your_google_api_key_here

# Tavily 搜索 API 配置（必需）
TAVILY_API_KEY=your_tavily_api_key_here
```

### API 密钥获取方式：
- **Google API Key**: 访问 [Google AI Studio](https://aistudio.google.com/app/apikey) 创建 API 密钥
- **Tavily API Key**: 访问 [Tavily](https://tavily.com/) 注册并获取 API 密钥

## 使用的模型
- **Gemini 2.5 Pro**: Google 最新的高性能多模态大语言模型

## 新功能特色
- ✅ **实时工具调用反馈**: 当 Agent 调用 Tavily 搜索工具时会显示：
  - 🔍 正在搜索的查询内容
  - ✅ 搜索完成确认
  - 📋 **Tavily 原始搜索结果输出**（完整显示搜索到的数据）
  - ❌ 搜索失败提示（如有）