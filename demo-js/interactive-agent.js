import 'dotenv/config'
import readline from 'readline'
import chalk from 'chalk'
import { TavilySearch } from '@langchain/tavily'
import { ChatAnthropic } from '@langchain/anthropic'
import { MemorySaver } from '@langchain/langgraph'
import { createReactAgent } from '@langchain/langgraph/prebuilt'
import { Calculator } from '@langchain/community/tools/calculator'
import { DynamicTool } from '@langchain/core/tools'
import { HumanMessage } from '@langchain/core/messages'
import { getConfig, validateConfig } from './agent-config.js'
import fs from 'fs'

// 获取配置
const config = getConfig()

// 验证配置
const configErrors = validateConfig(config)
if (configErrors.length > 0) {
  console.error(chalk.red('配置错误:'))
  configErrors.forEach(error => console.error(chalk.red(`  - ${error}`)))
  process.exit(1)
}

// 创建自定义工具
const getCurrentTime = new DynamicTool({
  name: 'getCurrentTime',
  description: '获取当前日期和时间',
  func: async () => {
    const now = new Date()
    return `当前时间: ${now.toLocaleString('zh-CN', { 
      timeZone: config.tools.time.timezone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })}`
  }
})

const fileOperations = new DynamicTool({
  name: 'fileOperations',
  description: '读取、写入或列出文件。输入格式：{"action": "read|write|list", "path": "文件路径", "content": "写入内容(仅写入时需要)"}',
  func: async (input) => {
    try {
      const { action, path: filePath, content } = JSON.parse(input)
      
      // 安全检查
      if (config.security.blockedDirectories.some(dir => filePath.includes(dir))) {
        return '访问被禁止的目录'
      }
      
      // 检查文件大小
      if (action === 'read' && fs.existsSync(filePath)) {
        const stats = fs.statSync(filePath)
        if (stats.size > config.fileOperations.maxFileSize) {
          return '文件过大，无法读取'
        }
      }
      
      switch (action) {
        case 'read':
          if (fs.existsSync(filePath)) {
            return fs.readFileSync(filePath, config.fileOperations.defaultEncoding)
          } else {
            return '文件不存在'
          }
        
        case 'write':
          // 备份现有文件
          if (config.fileOperations.backupEnabled && fs.existsSync(filePath)) {
            fs.copyFileSync(filePath, `${filePath}.backup`)
          }
          fs.writeFileSync(filePath, content, config.fileOperations.defaultEncoding)
          return `文件已写入: ${filePath}`
        
        case 'list':
          if (fs.existsSync(filePath)) {
            const files = fs.readdirSync(filePath)
            return `目录内容: ${files.join(', ')}`
          } else {
            return '目录不存在'
          }
        
        default:
          return '不支持的操作，请使用 read、write 或 list'
      }
    } catch (error) {
      return `操作失败: ${error.message}`
    }
  }
})

const weatherTool = new DynamicTool({
  name: 'weatherTool',
  description: '获取指定城市的详细天气信息',
  func: async (cityName) => {
    const mockWeatherData = {
      '北京': { temperature: '15°C', humidity: '65%', windSpeed: '10km/h', condition: '晴' },
      '上海': { temperature: '18°C', humidity: '70%', windSpeed: '8km/h', condition: '多云' },
      '广州': { temperature: '22°C', humidity: '80%', windSpeed: '12km/h', condition: '阴' },
      '深圳': { temperature: '24°C', humidity: '85%', windSpeed: '15km/h', condition: '雨' }
    }
    
    const weather = mockWeatherData[cityName] || { 
      temperature: '未知', 
      humidity: '未知', 
      windSpeed: '未知', 
      condition: '数据不可用' 
    }
    
    return `${cityName}天气：
温度: ${weather.temperature}
湿度: ${weather.humidity}
风速: ${weather.windSpeed}
天气状况: ${weather.condition}`
  }
})

const systemInfo = new DynamicTool({
  name: 'systemInfo',
  description: '获取系统信息',
  func: async () => {
    const os = await import('os')
    const info = `系统信息:
操作系统: ${os.platform()} ${os.release()}
架构: ${os.arch()}
总内存: ${(os.totalmem() / 1024 / 1024 / 1024).toFixed(2)} GB
可用内存: ${(os.freemem() / 1024 / 1024 / 1024).toFixed(2)} GB
Node.js版本: ${process.version}
运行时间: ${Math.floor(process.uptime())} 秒`
    
    // 过滤敏感信息
    if (config.tools.system.sensitiveInfoFilter) {
      return info.replace(/\/Users\/[^\/]+/g, '/Users/***')
    }
    
    return info
  }
})

// 创建工具数组
const agentTools = [
  ...(config.tools.search.enabled ? [new TavilySearch({
    maxResults: config.search.maxResults,
    searchDepth: config.search.searchDepth
  })] : []),
  ...(config.tools.calculator.enabled ? [new Calculator()] : []),
  ...(config.tools.time.enabled ? [getCurrentTime] : []),
  ...(config.tools.fileOps.enabled ? [fileOperations] : []),
  ...(config.tools.weather.enabled ? [weatherTool] : []),
  ...(config.tools.system.enabled ? [systemInfo] : [])
]

// 创建LLM
const agentModel = new ChatAnthropic({
  model: config.llm.model,
  temperature: config.llm.temperature,
  maxTokens: config.llm.maxTokens
})

// 创建记忆
const agentCheckpoint = new MemorySaver()

// 创建Agent
const agent = createReactAgent({
  llm: agentModel,
  tools: agentTools,
  checkpointSaver: agentCheckpoint,
})

// 创建命令行界面
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: chalk.cyan('🤖 > ')
})

// 会话状态
let currentThreadId = '1'
let isRunning = true

// 日志记录
function log(level, message) {
  if (config.logging.enableConsole) {
    const timestamp = new Date().toISOString()
    console.log(`[${timestamp}] [${level.toUpperCase()}] ${message}`)
  }
}

// 显示启动信息
function showWelcome() {
  console.log(chalk.cyan.bold(`
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                        ║
║                                  🤖 增强型 AI Agent 交互式界面                                                       ║
║                                                                                                                        ║
║  🚀 功能特性:                                                                                                          ║
║  • 🔍 网络搜索 (TavilySearch)                                                                                        ║
║  • 🧮 数学计算 (Calculator)                                                                                          ║
║  • ⏰ 时间查询                                                                                                        ║
║  • 📁 文件操作 (读取/写入/列表)                                                                                      ║
║  • 🌤️ 天气查询                                                                                                       ║
║  • 💻 系统信息                                                                                                       ║
║  • 🧠 对话记忆                                                                                                       ║
║                                                                                                                        ║
║  🔧 命令:                                                                                                              ║
║  • /help     - 显示帮助                                                                                              ║
║  • /clear    - 清除屏幕                                                                                              ║
║  • /config   - 显示配置                                                                                              ║
║  • /thread   - 切换对话线程                                                                                          ║
║  • /history  - 显示对话历史                                                                                          ║
║  • /exit     - 退出程序                                                                                              ║
║                                                                                                                        ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
  `))
}

// 显示帮助
function showHelp() {
  console.log(chalk.yellow(`
🔧 命令说明:
  /help     - 显示此帮助信息
  /clear    - 清除屏幕
  /config   - 显示当前配置
  /thread <id> - 切换到指定对话线程
  /history  - 显示对话历史
  /exit     - 退出程序

📝 使用示例:
  • 现在几点了？
  • 帮我计算 123 + 456 * 789
  • 搜索最新的AI技术发展
  • 北京今天天气怎么样？
  • 读取README.md文件
  • 获取系统信息
  `))
}

// 显示配置
function showConfig() {
  console.log(chalk.magenta(`
🔧 当前配置:
  • 模型: ${config.llm.model}
  • 温度: ${config.llm.temperature}
  • 最大令牌: ${config.llm.maxTokens}
  • 搜索结果数: ${config.search.maxResults}
  • 记忆文件: ${config.memory.memoryFile}
  • 当前线程: ${currentThreadId}
  • 启用的工具: ${Object.keys(config.tools).filter(key => config.tools[key].enabled).join(', ')}
  `))
}

// 处理用户输入
async function handleInput(input) {
  const command = input.trim()
  
  // 处理命令
  if (command.startsWith('/')) {
    const [cmd, ...args] = command.slice(1).split(' ')
    
    switch (cmd) {
      case 'help':
        showHelp()
        break
      
      case 'clear':
        console.clear()
        showWelcome()
        break
      
      case 'config':
        showConfig()
        break
      
      case 'thread':
        if (args[0]) {
          currentThreadId = args[0]
          console.log(chalk.green(`已切换到线程: ${currentThreadId}`))
        } else {
          console.log(chalk.yellow(`当前线程: ${currentThreadId}`))
        }
        break
      
      case 'history':
        console.log(chalk.blue('对话历史功能开发中...'))
        break
      
      case 'exit':
        console.log(chalk.green('再见！👋'))
        isRunning = false
        rl.close()
        return
      
      default:
        console.log(chalk.red(`未知命令: ${cmd}。输入 /help 查看可用命令。`))
    }
    
    rl.prompt()
    return
  }
  
  // 处理正常对话
  if (command) {
    try {
      console.log(chalk.gray('🤔 思考中...'))
      
      const startTime = Date.now()
      const result = await agent.invoke(
        { messages: [new HumanMessage(command)] },
        { configurable: { thread_id: currentThreadId } }
      )
      const endTime = Date.now()
      
      const response = result.messages[result.messages.length - 1].content
      
      console.log(chalk.green(`🤖 Agent: ${response}`))
      
      if (config.ui.showTimestamp) {
        console.log(chalk.gray(`⏱️ 响应时间: ${endTime - startTime}ms`))
      }
      
      log('info', `User: ${command}`)
      log('info', `Agent: ${response}`)
      
    } catch (error) {
      console.error(chalk.red(`❌ 错误: ${error.message}`))
      log('error', `Error: ${error.message}`)
    }
  }
  
  rl.prompt()
}

// 启动交互式界面
function startInteractiveAgent() {
  console.clear()
  showWelcome()
  
  rl.on('line', handleInput)
  
  rl.on('close', () => {
    console.log(chalk.yellow('\n程序已退出'))
    process.exit(0)
  })
  
  rl.prompt()
}

// 信号处理
process.on('SIGINT', () => {
  console.log(chalk.yellow('\n正在退出...'))
  rl.close()
})

// 启动程序
startInteractiveAgent() 