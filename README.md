# LangGraph Agent 示例项目

这个项目包含了使用 LangGraph 框架构建智能代理的示例，提供了 JavaScript 和 Python 两个版本的实现。

## 项目结构

```
├── langGraph-base/          # Node.js/JavaScript 版本
│   ├── agent.js            # 主要代理逻辑
│   ├── package.json        # Node.js 依赖配置
│   └── README.md           # JavaScript 版本说明
│
├── langGraph-base-py/       # Python 版本  
│   ├── agent.py            # Python 代理实现
│   ├── requirements.txt    # Python 依赖配置
│   ├── 安装指南.md         # 安装指导
│   └── README.md           # Python 版本说明
│
└── demo-*/                  # 其他演示项目
```

## 快速开始

### JavaScript 版本
```bash
cd langGraph-base
npm install
node agent.js
```

### Python 版本
```bash
cd langGraph-base-py
pip install -r requirements.txt
python agent.py
```

## 环境配置

两个版本都需要配置相应的 API 密钥，请参考各目录下的 README.md 文件了解详细配置方法。

## 功能特性

- 🤖 智能对话代理
- 🔍 网络搜索集成（Tavily Search）
- 💬 流式和非流式输出支持
- 🧠 对话记忆管理
- 🌐 多语言支持

## 许可证

MIT License

## 贡献

欢迎提交 Pull Request 和 Issue！ 