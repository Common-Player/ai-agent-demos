#!/usr/bin/env python3
"""
Agent配置文件
"""
import os
from typing import Dict, Any, List

# 基础配置
agent_config = {
    # LLM配置
    "llm": {
        "model": "deepseek-chat",
        "temperature": 0.1,
        "max_tokens": 2000,
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    },
    
    # 搜索配置
    "search": {
        "max_results": 5,
        "search_depth": "advanced",
        "timeout": 30000,
        "retry_count": 3
    },
    
    # 文件操作配置
    "file_operations": {
        "allowed_extensions": [".txt", ".md", ".json", ".py", ".yaml", ".yml"],
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "default_encoding": "utf-8",
        "backup_enabled": True
    },
    
    # 安全配置
    "security": {
        "allowed_directories": ["./data", "./output", "./temp"],
        "blocked_directories": ["/etc", "/usr", "/var", "/system"],
        "max_execution_time": 60000,  # 60秒
        "rate_limit_per_minute": 60
    },
    
    # 记忆配置
    "memory": {
        "max_context_length": 10000,
        "summary_enabled": True,
        "persist_to_file": True,
        "memory_file": "./agent_memory.json"
    },
    
    # 日志配置
    "logging": {
        "level": "info",  # debug, info, warn, error
        "enable_console": True,
        "enable_file": True,
        "log_file": "./agent.log",
        "max_log_size": 50 * 1024 * 1024,  # 50MB
        "log_rotation": True
    },
    
    # 性能配置
    "performance": {
        "request_delay": 1000,  # 请求间隔
        "batch_size": 5,
        "enable_caching": True,
        "cache_timeout": 300000,  # 5分钟
        "max_concurrent_requests": 3
    },
    
    # 用户界面配置
    "ui": {
        "show_timestamp": True,
        "show_tool_usage": True,
        "color_output": True,
        "progress_indicator": True,
        "emoji": True
    },
    
    # 工具配置
    "tools": {
        "search": {
            "enabled": True,
            "priority": 1
        },
        "calculator": {
            "enabled": True,
            "priority": 2,
            "precision": 10
        },
        "file_ops": {
            "enabled": True,
            "priority": 3,
            "safe_mode": True
        },
        "weather": {
            "enabled": True,
            "priority": 4,
            "mock_data": True  # 开发环境使用模拟数据
        },
        "system": {
            "enabled": True,
            "priority": 5,
            "sensitive_info_filter": True
        },
        "time": {
            "enabled": True,
            "priority": 6,
            "timezone": "Asia/Shanghai"
        }
    }
}

# 环境配置
environment_config = {
    "development": {
        **agent_config,
        "logging": {
            **agent_config["logging"],
            "level": "debug"
        },
        "performance": {
            **agent_config["performance"],
            "request_delay": 500
        }
    },
    
    "production": {
        **agent_config,
        "logging": {
            **agent_config["logging"],
            "level": "warn"
        },
        "performance": {
            **agent_config["performance"],
            "request_delay": 2000
        },
        "security": {
            **agent_config["security"],
            "rate_limit_per_minute": 30
        }
    }
}

def get_config() -> Dict[str, Any]:
    """获取当前环境配置"""
    env = os.getenv("ENVIRONMENT", "development")
    return environment_config.get(env, agent_config)

def validate_config(config: Dict[str, Any]) -> List[str]:
    """验证配置"""
    errors = []
    
    # 验证必要的API密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        errors.append("DEEPSEEK_API_KEY is required")
    
    if not os.getenv("TAVILY_API_KEY"):
        errors.append("TAVILY_API_KEY is required")
    
    # 验证配置值
    if config["llm"]["temperature"] < 0 or config["llm"]["temperature"] > 1:
        errors.append("Temperature must be between 0 and 1")
    
    if config["search"]["max_results"] < 1 or config["search"]["max_results"] > 20:
        errors.append("max_results must be between 1 and 20")
    
    if config["file_operations"]["max_file_size"] < 1024:
        errors.append("max_file_size must be at least 1KB")
    
    return errors

def update_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """更新配置"""
    return {**agent_config, **updates}

def reset_config() -> Dict[str, Any]:
    """重置配置"""
    return agent_config.copy() 