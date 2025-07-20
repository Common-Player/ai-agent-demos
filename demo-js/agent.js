import 'dotenv/config'
import { TavilySearch } from '@langchain/tavily'
import { ChatAnthropic } from '@langchain/anthropic'
import { MemorySaver } from '@langchain/langgraph'
import { createReactAgent } from '@langchain/langgraph/prebuilt'
import { Calculator } from '@langchain/community/tools/calculator'
import { DynamicTool } from '@langchain/core/tools'
import { HumanMessage } from '@langchain/core/messages'
import fs from 'fs'
import path from 'path'

// 创建自定义工具 - 获取当前时间
const getCurrentTime = new DynamicTool({
  name: 'getCurrentTime',
  description: '获取当前日期和时间',
  func: async () => {
    const now = new Date()
    return `当前时间: ${now.toLocaleString('zh-CN', { 
      timeZone: 'Asia/Shanghai',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })}`
  }
})

// 创建自定义工具 - 文件操作
const fileOperations = new DynamicTool({
  name: 'fileOperations',
  description: '读取、写入或列出文件。输入格式：{"action": "read|write|list", "path": "文件路径", "content": "写入内容(仅写入时需要)"}',
  func: async (input) => {
    try {
      const { action, path: filePath, content } = JSON.parse(input)
      
      switch (action) {
        case 'read':
          if (fs.existsSync(filePath)) {
            return fs.readFileSync(filePath, 'utf8')
          } else {
            return '文件不存在'
          }
        
        case 'write':
          fs.writeFileSync(filePath, content, 'utf8')
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

// 创建自定义工具 - 天气查询增强
const weatherTool = new DynamicTool({
  name: 'weatherTool',
  description: '获取指定城市的详细天气信息，包括温度、湿度、风速等',
  func: async (cityName) => {
    // 这里可以接入真实的天气API，现在用模拟数据
    const mockWeatherData = {
      '北京': { temperature: '15°C', humidity: '65%', windSpeed: '10km/h', condition: '晴' },
      '上海': { temperature: '18°C', humidity: '70%', windSpeed: '8km/h', condition: '多云' },
      '广州': { temperature: '22°C', humidity: '80%', windSpeed: '12km/h', condition: '阴' }
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

// 创建自定义工具 - 系统信息
const systemInfo = new DynamicTool({
  name: 'systemInfo',
  description: '获取系统信息，包括操作系统、Node.js版本等',
  func: async () => {
    const os = await import('os')
    return `系统信息:
操作系统: ${os.platform()} ${os.release()}
架构: ${os.arch()}
总内存: ${(os.totalmem() / 1024 / 1024 / 1024).toFixed(2)} GB
可用内存: ${(os.freemem() / 1024 / 1024 / 1024).toFixed(2)} GB
Node.js版本: ${process.version}
运行时间: ${Math.floor(process.uptime())} 秒`
  }
})

// 定义增强的工具集
const agentTools = [
    new TavilySearch({
        maxResults: 5,
        searchDepth: 'advanced'
    }),
    new Calculator(),
    getCurrentTime,
    fileOperations,
    weatherTool,
    systemInfo
]

// 定义 llm 配置
const agentModel = new ChatAnthropic({
  model: 'claude-sonnet-4-20250514',
  temperature: 0.1,
  maxTokens: 2000
})

// 初始化记忆
const agentCheckpoint = new MemorySaver()

// 创建增强的agent
const agent = createReactAgent({
  llm: agentModel,
  tools: agentTools,
  checkpointSaver: agentCheckpoint,
})

// 创建交互式聊天函数
async function chatWithAgent(message, threadId = '1') {
  try {
    console.log(`\n🤖 用户: ${message}`)
    console.log('━'.repeat(50))
    
    const result = await agent.invoke(
      { messages: [new HumanMessage(message)] },
      { configurable: { thread_id: threadId } }
    )
    
    const response = result.messages[result.messages.length - 1].content
    console.log(`🔮 Agent: ${response}`)
    console.log('━'.repeat(50))
    
    return response
  } catch (error) {
    console.error('❌ 错误:', error.message)
    return '抱歉，处理您的请求时出现了错误。'
  }
}

// 显示可用功能
function showAvailableFeatures() {
  console.log(`
🚀 Agent 功能列表:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 搜索功能:
  - 网络搜索（TavilySearch）
  - 获取最新信息和资讯

🧮 计算功能:
  - 数学计算
  - 支持复杂表达式

⏰ 时间功能:
  - 获取当前时间
  - 日期时间查询

📁 文件操作:
  - 读取文件内容
  - 写入文件
  - 列出目录内容

🌤️ 天气查询:
  - 获取城市天气信息
  - 温度、湿度、风速等详细信息

💻 系统信息:
  - 获取操作系统信息
  - 内存使用情况
  - Node.js版本等

🧠 记忆功能:
  - 保持对话上下文
  - 记住之前的交互

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`)
}

// 执行测试和演示
async function runDemo() {
  showAvailableFeatures()
  
  // 测试各种功能
  const testCases = [
    '今天北京天气怎么样？',
    '帮我计算 123 + 456 * 789',
    '现在几点了？',
    '搜索最新的AI技术发展',
    '获取系统信息',
    '之前我们聊了什么？'
  ]
  
  for (const testCase of testCases) {
    await chatWithAgent(testCase)
    // 添加延迟以避免API限制
    await new Promise(resolve => setTimeout(resolve, 1000))
  }
}

// 运行演示
runDemo().catch(console.error)