// Agent配置文件
export const agentConfig = {
  // LLM配置
  llm: {
    model: 'claude-sonnet-4-20250514',
    temperature: 0.1,
    maxTokens: 2000,
    topP: 0.9,
    frequencyPenalty: 0.1,
    presencePenalty: 0.1
  },

  // 搜索配置
  search: {
    maxResults: 5,
    searchDepth: 'advanced',
    timeout: 30000,
    retryCount: 3
  },

  // 文件操作配置
  fileOperations: {
    allowedExtensions: ['.txt', '.md', '.json', '.js', '.ts', '.py', '.yaml', '.yml'],
    maxFileSize: 10 * 1024 * 1024, // 10MB
    defaultEncoding: 'utf8',
    backupEnabled: true
  },

  // 安全配置
  security: {
    allowedDirectories: ['./data', './output', './temp'],
    blockedDirectories: ['/etc', '/usr', '/var', '/system'],
    maxExecutionTime: 60000, // 60秒
    rateLimitPerMinute: 60
  },

  // 记忆配置
  memory: {
    maxContextLength: 10000,
    summaryEnabled: true,
    persistToFile: true,
    memoryFile: './agent-memory.json'
  },

  // 日志配置
  logging: {
    level: 'info', // debug, info, warn, error
    enableConsole: true,
    enableFile: true,
    logFile: './agent.log',
    maxLogSize: 50 * 1024 * 1024, // 50MB
    logRotation: true
  },

  // 性能配置
  performance: {
    requestDelay: 1000, // 请求间隔
    batchSize: 5,
    enableCaching: true,
    cacheTimeout: 300000, // 5分钟
    maxConcurrentRequests: 3
  },

  // 用户界面配置
  ui: {
    showTimestamp: true,
    showToolUsage: true,
    colorOutput: true,
    progressIndicator: true,
    emoji: true
  },

  // 工具配置
  tools: {
    search: {
      enabled: true,
      priority: 1
    },
    calculator: {
      enabled: true,
      priority: 2,
      precision: 10
    },
    fileOps: {
      enabled: true,
      priority: 3,
      safeMode: true
    },
    weather: {
      enabled: true,
      priority: 4,
      mockData: true // 开发环境使用模拟数据
    },
    system: {
      enabled: true,
      priority: 5,
      sensitiveInfoFilter: true
    },
    time: {
      enabled: true,
      priority: 6,
      timezone: 'Asia/Shanghai'
    }
  }
}

// 环境配置
export const environmentConfig = {
  development: {
    ...agentConfig,
    logging: {
      ...agentConfig.logging,
      level: 'debug'
    },
    performance: {
      ...agentConfig.performance,
      requestDelay: 500
    }
  },
  
  production: {
    ...agentConfig,
    logging: {
      ...agentConfig.logging,
      level: 'warn'
    },
    performance: {
      ...agentConfig.performance,
      requestDelay: 2000
    },
    security: {
      ...agentConfig.security,
      rateLimitPerMinute: 30
    }
  }
}

// 获取当前环境配置
export function getConfig() {
  const env = process.env.NODE_ENV || 'development'
  return environmentConfig[env] || agentConfig
}

// 验证配置
export function validateConfig(config) {
  const errors = []
  
  // 验证必要的API密钥
  if (!process.env.DEEPSEEK_API_KEY) {
    errors.push('DEEPSEEK_API_KEY is required')
  }
  
  if (!process.env.TAVILY_API_KEY) {
    errors.push('TAVILY_API_KEY is required')
  }
  
  // 验证配置值
  if (config.llm.temperature < 0 || config.llm.temperature > 1) {
    errors.push('Temperature must be between 0 and 1')
  }
  
  if (config.search.maxResults < 1 || config.search.maxResults > 20) {
    errors.push('maxResults must be between 1 and 20')
  }
  
  if (config.fileOperations.maxFileSize < 1024) {
    errors.push('maxFileSize must be at least 1KB')
  }
  
  return errors
}

// 更新配置
export function updateConfig(updates) {
  return {
    ...agentConfig,
    ...updates
  }
}

// 重置配置
export function resetConfig() {
  return { ...agentConfig }
}

// 导出默认配置
export default agentConfig 