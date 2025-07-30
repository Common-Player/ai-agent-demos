# LangGraph 多功能 AI Agent 项目集合

集合包含了使用 LangGraph 框架构建的多个智能代理示例，其中 **langGrap-info-create** 是主要项目。

## 🌟 核心项目：langGrap-info-create


### 🛠️ 技术架构
- **前端**: 纯 HTML + CSS + JavaScript
- **后端**: Flask + LangGraph + LangChain 
- **AI 模型**: Google Gemini 2.5 Pro
- **工具集成**: Tavily Search + Tavily Extract
- **会话管理**: 基于 LangGraph 的内存管理

### 🚀 快速开始

```bash
cd langGrap-info-create
pip install -r requirements.txt

# 配置环境变量（创建.env文件）
# GOOGLE_API_KEY=your_google_api_key_here
# TAVILY_API_KEY=your_tavily_api_key_here

# 启动Web界面
python run_web.py
```

然后在浏览器中访问：http://localhost:8080

### 📖 详细文档
查看 `langGrap-info-create/README.md` 获取完整的使用指南和功能介绍。