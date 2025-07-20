# 🤖 增强型AI Agent (JavaScript版本)

这是一个基于LangChain和DeepSeek的多功能AI Agent，具备多种实用工具和对话记忆能力。

## 🔧 系统要求

- **Node.js**: 18.0.0 或更高版本
- **npm**: 8.0.0 或更高版本
- **操作系统**: macOS, Linux, Windows

## ✨ 主要功能

### 🔍 搜索功能
- **网络搜索**: 使用TavilySearch进行高级网络搜索
- **实时信息**: 获取最新的新闻、资讯和信息
- **深度搜索**: 支持高级搜索模式，返回更丰富的结果

### 🧮 计算功能
- **数学计算**: 支持复杂的数学表达式计算
- **公式解析**: 自动解析和计算各种数学公式
- **实时计算**: 快速响应计算请求

### ⏰ 时间功能
- **当前时间**: 获取准确的当前日期和时间
- **时区支持**: 默认使用中国时区（Asia/Shanghai）
- **格式化显示**: 友好的时间格式展示

### 📁 文件操作
- **读取文件**: 读取本地文件内容
- **写入文件**: 创建或修改文件
- **目录列表**: 查看目录内容
- **错误处理**: 完善的文件操作错误处理

### 🌤️ 天气查询
- **城市天气**: 获取指定城市的详细天气信息
- **详细数据**: 包括温度、湿度、风速等信息
- **多城市支持**: 支持多个主要城市的天气查询

### 💻 系统信息
- **操作系统**: 获取系统版本和架构信息
- **内存状态**: 总内存和可用内存统计
- **运行环境**: Node.js版本和运行时间

### 🧠 记忆功能
- **对话上下文**: 保持完整的对话历史
- **会话管理**: 支持多个独立的对话线程
- **状态持久化**: 自动保存和恢复对话状态

## 🚀 快速开始

### 1. 检查Node.js版本

```bash
node --version
# 应该显示 v18.0.0 或更高版本
```

如果版本过低，请升级Node.js：
- 从 [Node.js官网](https://nodejs.org/) 下载最新版本
- 或使用 `nvm` 管理器：`nvm install 18 && nvm use 18`

### 2. 安装依赖

```bash
npm install
```

### 3. 环境配置

创建`.env`文件（复制`env-example.txt`并重命名）：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 4. 运行Agent

```bash
# 运行基础版本
npm start

# 运行交互式界面
npm run interactive

# 开发模式（更多调试信息）
npm run dev
```

## 🔧 使用示例

### 基本对话
```javascript
// 获取当前时间
await chatWithAgent('现在几点了？')

// 数学计算
await chatWithAgent('帮我计算 123 + 456 * 789')

// 网络搜索
await chatWithAgent('搜索最新的AI技术发展')
```

### 文件操作
```javascript
// 读取文件
await chatWithAgent('读取README.md文件的内容')

// 写入文件
await chatWithAgent('创建一个新文件test.txt，内容是"Hello World"')

// 列出目录
await chatWithAgent('列出当前目录的所有文件')
```

### 天气查询
```javascript
// 查询天气
await chatWithAgent('北京今天天气怎么样？')
await chatWithAgent('上海的天气情况如何？')
```

### 系统信息
```javascript
// 获取系统信息
await chatWithAgent('显示系统信息')
await chatWithAgent('当前内存使用情况如何？')
```

## 🛠️ 技术栈

- **LangChain**: 核心框架
- **DeepSeek**: 大语言模型
- **TavilySearch**: 网络搜索工具
- **LangGraph**: 状态管理和记忆
- **Node.js**: 运行环境

## 📝 自定义工具

### 添加新工具

您可以轻松添加新的自定义工具：

```javascript
const customTool = new DynamicTool({
  name: 'customTool',
  description: '工具描述',
  func: async (input) => {
    // 工具逻辑
    return '工具结果'
  }
})

// 添加到工具列表
const agentTools = [
  // ... 其他工具
  customTool
]
```

### 工具开发指南

1. 使用`DynamicTool`创建自定义工具
2. 提供清晰的`name`和`description`
3. 实现`func`方法处理输入
4. 添加适当的错误处理
5. 返回有用的结果信息

## 🔒 错误处理

Agent包含完善的错误处理机制：

- **API错误**: 自动重试和错误提示
- **文件操作错误**: 文件不存在、权限问题等
- **网络错误**: 搜索失败、连接超时等
- **输入验证**: 参数格式检查

## 📊 性能优化

- **延迟控制**: 避免API限制的智能延迟
- **内存管理**: 高效的状态管理
- **缓存机制**: 减少重复请求
- **错误恢复**: 自动错误恢复机制

## 🤝 贡献指南

欢迎贡献新功能和改进：

1. Fork项目
2. 创建功能分支
3. 添加新功能或修复bug
4. 提交Pull Request

## 📄 许可证

MIT License

## 📞 支持

如有问题或建议，请创建Issue或联系维护者。

---

*让AI Agent更智能，让交互更自然！* 🚀 