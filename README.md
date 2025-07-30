# LangGraph 多功能 AI Agent 项目集合

集合包含了使用 LangGraph 框架构建的多个智能代理示例，其中 **langGrap-info-create** 是主要项目。

## 🌟 核心项目：langGrap-info-create

### 🛠️ 技术架构
- **前端**: 纯 HTML + CSS + JavaScript，无框架依赖
- **后端**: Flask + LangGraph + LangChain 
- **数据库**: Supabase (PostgreSQL) + 行级安全策略
- **认证系统**: Supabase Auth + Flask Session
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
# SUPABASE_URL=your_supabase_project_url
# SUPABASE_ANON_KEY=your_supabase_anon_key

# 设置数据库（首次使用）
# 1. 在Supabase Dashboard中执行 database_schema.sql
# 2. 可选：运行测试脚本检查连接
python debug_test.py

# 启动Web界面
python run_web.py
```

然后在浏览器中访问：http://localhost:8080

### 📊 数据库配置

1. **创建Supabase项目**: 访问 [Supabase](https://supabase.com/) 创建新项目
2. **执行数据库架构**: 在Supabase Dashboard的SQL编辑器中执行 `database_schema.sql`
3. **配置环境变量**: 从项目设置页面获取URL和API密钥
4. **测试连接**: 运行 `python debug_test.py` 验证配置

### 📖 详细文档
查看 `langGrap-info-create/README.md` 获取完整的使用指南和功能介绍。

---

## 🔑 API密钥获取指南

### Google Gemini API
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 登录Google账号
3. 创建新的API密钥
4. 复制密钥到`.env`文件中的`GOOGLE_API_KEY`

### Tavily Search API
1. 访问 [Tavily](https://tavily.com/)
2. 注册账号并登录
3. 在Dashboard中获取API密钥
4. 复制密钥到`.env`文件中的`TAVILY_API_KEY`

### Supabase配置
1. 访问 [Supabase](https://supabase.com/) 并创建新项目
2. 在项目设置中找到API配置
3. 复制`Project URL`到`SUPABASE_URL`
4. 复制`anon public`密钥到`SUPABASE_ANON_KEY`

## 🎯 推荐使用

从 **langGrap-info-create** 项目开始提供了：
- AI Agent功能
- 完整的用户管理系统
- 持久化数据存储
- 现代化的Web界面

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Pull Request 和 Issue！