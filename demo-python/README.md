# 🤖 增强型AI Agent (Python版本)

参考 JavaScript 版本改进的增强型 AI Agent 演示程序，基于LangChain和DeepSeek构建。

## 🔧 系统要求

- **Python**: 3.8+ 
- **pip**: 包管理器
- **操作系统**: macOS, Linux, Windows

## ✨ 主要功能

### 🚀 核心功能
- 🔍 **网络搜索** - 使用 TavilySearch 获取最新信息
- 🧮 **数学计算** - 安全的数学表达式计算
- ⏰ **时间查询** - 获取当前日期和时间
- 📁 **文件操作** - 读取、写入和列出文件
- 🌤️ **天气查询** - 获取城市天气信息（模拟数据）
- 💻 **系统信息** - 获取操作系统和硬件信息
- 🧠 **对话记忆** - 保持对话上下文

### 🛠️ 高级特性
- 📊 **配置管理** - 详细的配置文件支持
- 🔒 **安全控制** - 文件访问安全检查
- 🎨 **交互式界面** - 美观的命令行界面
- 🔄 **错误处理** - 完善的错误处理机制
- 📝 **日志记录** - 可配置的日志系统

## 🚀 快速开始

### 方法一：使用自动安装脚本（推荐）

```bash
python setup.py
```

这会自动完成依赖项安装和环境文件创建。

### 方法二：手动安装

#### 1. 安装依赖项

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

创建`.env`文件（复制`env-example.txt`并重命名）：

```env
# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Tavily Search API Key
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. 获取API密钥

1. **DeepSeek API密钥**：
   - 访问 [DeepSeek官网](https://platform.deepseek.com/)
   - 注册账户并获取API密钥

2. **Tavily API密钥**：
   - 访问 [Tavily官网](https://tavily.com/)
   - 注册账户并获取API密钥

### 4. 编辑.env文件

将获取的API密钥填入`.env`文件中相应位置。

### 5. 运行程序

```bash
# 运行演示程序
python agent.py

# 运行交互式界面
python interactive_agent.py
```

## 🎮 使用方法

### 交互式命令
- `/help` - 显示帮助信息
- `/clear` - 清除屏幕
- `/config` - 显示当前配置
- `/history` - 显示对话历史
- `/reset` - 重置对话历史
- `/exit` - 退出程序

### 使用示例

#### 基本查询
```
现在几点了？
帮我计算 123 + 456 * 789
搜索最新的AI技术发展
```

#### 文件操作
```
{"action": "read", "path": "README.md"}
{"action": "write", "path": "test.txt", "content": "Hello World"}
{"action": "list", "path": "./"}
```

#### 天气查询
```
北京今天天气怎么样？
上海的天气如何？
```

#### 系统信息
```
获取系统信息
显示内存使用情况
```

## ⚙️ 配置说明

### 配置文件结构
配置文件 `agent_config.py` 包含以下主要部分：

- **LLM配置** - 模型参数设置
- **搜索配置** - 搜索相关设置
- **文件操作配置** - 文件访问控制
- **安全配置** - 安全限制设置
- **工具配置** - 各个工具的启用状态

### 环境变量
- `ENVIRONMENT` - 环境类型（development/production）
- `DEEPSEEK_API_KEY` - DeepSeek API密钥
- `TAVILY_API_KEY` - Tavily搜索API密钥

## 📁 项目结构

```
demo-python/
├── agent.py                 # 主程序文件
├── interactive_agent.py     # 交互式界面
├── agent_config.py          # 配置管理
├── requirements.txt         # 依赖清单
├── setup.py                 # 安装脚本
├── env-example.txt          # 环境变量示例
└── README.md               # 说明文档
```

## 🛠️ 技术栈

- **LangChain**: 核心框架
- **DeepSeek**: 大语言模型
- **Tavily**: 网络搜索工具
- **PSUtil**: 系统信息获取
- **Colorama**: 终端颜色支持
- **Python**: 运行环境

## 📊 主要改进

相比原版本，新版本添加了：

1. **多工具支持** - 集成了6个实用工具
2. **配置管理** - 完整的配置文件系统
3. **交互式界面** - 美观的命令行界面
4. **错误处理** - 完善的错误处理机制
5. **安全控制** - 文件访问安全检查
6. **记忆功能** - 改进的对话历史记录

## 🔧 依赖说明

- `langchain` - 核心框架
- `langchain-deepseek` - DeepSeek LLM支持
- `langchain-community` - 社区工具集
- `tavily-python` - 搜索工具
- `colorama` - 终端颜色支持
- `psutil` - 系统信息获取
- `python-dotenv` - 环境变量管理

## 🔒 注意事项

- 确保API密钥配置正确
- 网络连接正常（用于搜索功能）
- 首次运行可能需要下载模型依赖项
- 如果遇到导入错误，请先运行 `pip install langchain-deepseek`

## 🔧 故障排除

### 常见问题

1. **API密钥未配置** - 请检查 `.env` 文件中的API密钥
2. **依赖缺失** - 运行 `pip install -r requirements.txt`
3. **权限问题** - 检查文件访问权限
4. **网络问题** - 确保网络连接正常

### 调试模式
设置环境变量启用调试模式：
```bash
export ENVIRONMENT=development
python agent.py
```

### 具体解决方案

#### 1. 导入错误
如果遇到 `ImportError: cannot import name 'ChatDeepSeek'` 错误，请确保：
- 运行了 `pip install langchain-deepseek`
- 使用正确的导入语句：`from langchain_deepseek import ChatDeepSeek`

#### 2. API密钥错误
请确保在 `.env` 文件中正确配置了：
- `DEEPSEEK_API_KEY` - DeepSeek API密钥
- `TAVILY_API_KEY` - Tavily搜索API密钥

#### 3. 网络连接问题
如果搜索功能无法正常工作，请检查：
- 网络连接是否正常
- 防火墙设置
- API服务是否可用

#### 4. 配置验证错误
如果启动时出现配置错误，请检查：
- 配置文件语法是否正确
- 环境变量是否正确设置
- 工具配置是否合理

## 🤝 贡献指南

欢迎贡献新功能和改进：

1. Fork项目
2. 创建功能分支
3. 添加新功能或修复bug
4. 提交Pull Request

### 开发建议
- 遵循PEP 8代码风格
- 添加适当的注释和文档
- 确保所有测试通过
- 更新相关文档

## 📄 许可证

MIT License

## 📞 支持

如有问题或建议，请创建Issue或联系维护者。

---

*让AI Agent更智能，让交互更自然！* 🚀 