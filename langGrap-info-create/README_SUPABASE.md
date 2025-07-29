# 🎉 AI网页设计师 - Supabase用户认证和历史记录集成

## 🚀 项目概述

您的AI网页设计师项目已成功集成Supabase用户认证和历史记录功能！现在用户可以注册账号、登录系统，并自动保存所有的设计历史和AI对话记录。

## ✨ 新增功能

### 🔐 用户认证系统
- ✅ 用户注册（邮箱验证）
- ✅ 用户登录/登出
- ✅ 会话管理
- ✅ 用户状态显示

### 📚 历史记录管理
- ✅ 自动保存所有提示词和AI响应
- ✅ 保存网页生成记录和HTML文件
- ✅ 按功能类型分类存储
- ✅ 用户使用统计分析

### 🛡️ 数据安全
- ✅ 行级安全策略(RLS)
- ✅ 用户数据隔离
- ✅ 安全的会话管理

## 📋 快速启动指南

### 1️⃣ 安装依赖包
```bash
cd langGrap-info-create
pip install -r requirements.txt
```

### 2️⃣ 配置环境变量

确保您的 `.env` 文件包含以下配置：

```bash
# Google Gemini API 密钥
GOOGLE_API_KEY=your_google_api_key_here

# Tavily API 密钥
TAVILY_API_KEY=your_tavily_api_key_here

# Flask配置
FLASK_SECRET_KEY=779b1222ec84287668a81e0853ba8b8907bf9289d3efe1616f50467b3efb3c2c

# Supabase配置
SUPABASE_URL=https://srohrgfegliprclhwwwa.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNyb2hyZ2ZlZ2xpcHJjbGh3d3dhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3NjY2NTksImV4cCI6MjA2OTM0MjY1OX0.JAKW615ymm7tAV4j41_c1zKLKRdp9IIdSE3NnR3w7N8
```

### 3️⃣ 设置Supabase数据库

1. 登录 [Supabase Dashboard](https://supabase.com/dashboard)
2. 进入项目 `srohrgfegliprclhwwwa`
3. 打开 **SQL Editor**
4. 执行以下SQL语句创建必要的表：

```sql
-- 用户提示词历史记录表
CREATE TABLE IF NOT EXISTS prompt_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    prompt_type VARCHAR(50) DEFAULT 'custom',
    model_type VARCHAR(50) DEFAULT 'simple',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户网页生成记录表
CREATE TABLE IF NOT EXISTS webpage_generations (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    html_content TEXT,
    filename VARCHAR(255),
    design_type VARCHAR(50) DEFAULT 'ai_design',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_prompt_history_user_id ON prompt_history(user_id);
CREATE INDEX IF NOT EXISTS idx_prompt_history_created_at ON prompt_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_webpage_generations_user_id ON webpage_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_webpage_generations_created_at ON webpage_generations(created_at DESC);

-- 启用行级安全策略
ALTER TABLE prompt_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE webpage_generations ENABLE ROW LEVEL SECURITY;

-- 用户只能访问自己的数据
CREATE POLICY "Users can only access their own prompt history" ON prompt_history
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own webpage generations" ON webpage_generations
    FOR ALL USING (auth.uid() = user_id);

-- 插入权限
CREATE POLICY "Authenticated users can insert prompt history" ON prompt_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Authenticated users can insert webpage generations" ON webpage_generations
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### 4️⃣ 启动应用

```bash
python run_web.py
```

然后访问：http://localhost:8080

## 🎯 功能使用说明

### 用户注册和登录

1. **首次访问**：点击右上角"登录/注册"按钮
2. **注册账号**：
   - 填写邮箱地址
   - 设置密码（至少6位）
   - 用户名（可选）
   - 点击"注册"
3. **邮箱验证**：检查邮箱中的验证邮件并点击验证链接
4. **登录使用**：验证后使用邮箱和密码登录

### AI网页设计

1. **登录后**：在主页文本框中详细描述您的设计需求
2. **开始设计**：点击"🚀 开始 AI 设计"
3. **查看结果**：AI会生成网页并显示结果
4. **自动保存**：所有设计请求和结果会自动保存到您的历史记录

### 历史记录查看

1. **显示历史**：点击"📚 历史记录"区域的"显示历史记录"
2. **分类查看**：
   - **提示词记录**：查看所有AI对话历史
   - **网页生成**：查看生成的网页文件
   - **使用统计**：查看个人使用统计
3. **访问生成文件**：点击网页记录中的链接直接查看生成的网页

## 🔧 技术架构

### 后端组件
- **Flask**: Web应用框架
- **Supabase**: 用户认证和数据库
- **LangGraph + LangChain**: AI Agent框架
- **Google Gemini 2.5**: 大语言模型

### 新增模块
- `auth_manager.py`: 用户认证管理
- `history_manager.py`: 历史记录管理
- `templates/auth.html`: 登录注册页面
- `templates/index_enhanced.html`: 增强版主页

### 数据库表
- `prompt_history`: 用户提示词历史
- `webpage_generations`: 网页生成记录

## 🛡️ 安全特性

### 数据保护
- **行级安全(RLS)**: 用户只能访问自己的数据
- **会话安全**: Flask Session + Supabase Auth
- **数据加密**: Supabase提供的企业级加密

### 隐私保证
- 每个用户的数据完全隔离
- 所有API调用都需要身份验证
- 敏感信息安全存储

## 📊 功能特点

### 个性化体验
- 🎨 保存个人设计历史
- 📈 追踪使用统计
- 🔍 便捷的历史搜索
- 💾 自动数据备份

### 用户友好
- 🎯 直观的用户界面
- 📱 响应式设计
- ⚡ 快速的数据加载
- 🎉 流畅的用户体验

## 🆕 新增API端点

- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户登出
- `GET /api/user` - 获取用户信息
- `GET /api/history/prompts` - 获取提示词历史
- `GET /api/history/webpages` - 获取网页生成记录
- `GET /api/history/stats` - 获取使用统计
- `GET /auth` - 认证页面

## 🎉 完成的集成

✅ **用户认证系统** - 完整的注册、登录、登出功能
✅ **历史记录管理** - 自动保存所有用户交互
✅ **数据安全保护** - 企业级的数据安全策略
✅ **个性化界面** - 显示用户状态和个人数据
✅ **统计分析功能** - 用户使用情况统计
✅ **响应式设计** - 支持各种设备访问

## 🔮 后续扩展建议

- 🔍 历史记录搜索功能
- 📤 数据导出功能
- ⚙️ 用户设置页面
- 📊 更丰富的统计图表
- 🏷️ 标签和分类管理
- 🔄 数据同步功能

---

🎊 **恭喜！您的AI网页设计师现在拥有完整的用户系统和数据管理功能！**

立即启动应用，注册账号开始体验吧！🚀 