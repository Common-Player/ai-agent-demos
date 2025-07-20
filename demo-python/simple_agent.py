#!/usr/bin/env python3
"""
简化版AI Agent - 基本功能测试
"""
import os
import json
import platform
import time
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

# 加载环境变量
load_dotenv()

# 简单的配置
config = {
    "llm": {
        "model": "deepseek-chat",
        "temperature": 0.1,
        "max_tokens": 2000
    },
    "performance": {
        "request_delay": 1000
    }
}

# 对话历史
conversation_history = []

def add_to_history(role: str, content: str):
    """添加消息到历史记录"""
    conversation_history.append({"role": role, "content": content})
    if len(conversation_history) > 10:
        conversation_history.pop(0)

# 简单的工具函数
def get_current_time(query: str) -> str:
    """获取当前时间"""
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"

def simple_calculator(expression: str) -> str:
    """简单计算器"""
    try:
        # 只允许基本的数学运算
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "表达式包含不允许的字符"
        
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

def get_weather(city: str) -> str:
    """获取天气信息"""
    weather_data = {
        "北京": "晴，15°C",
        "上海": "多云，18°C", 
        "广州": "阴，22°C",
        "深圳": "雨，24°C"
    }
    return weather_data.get(city, f"{city}天气信息不可用")

# 创建工具
tools = [
    Tool(
        name="get_time",
        description="获取当前时间",
        func=get_current_time
    ),
    Tool(
        name="calculator",
        description="进行数学计算，输入数学表达式",
        func=simple_calculator
    ),
    Tool(
        name="weather",
        description="获取城市天气，输入城市名称",
        func=get_weather
    )
]

# 创建LLM
llm = ChatDeepSeek(
    model=config["llm"]["model"],
    temperature=config["llm"]["temperature"],
    max_tokens=config["llm"]["max_tokens"]
)

# 创建Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

def chat_with_agent(message: str) -> str:
    """与Agent聊天"""
    try:
        # 添加延迟
        time.sleep(config["performance"]["request_delay"] / 1000)
        
        # 使用invoke
        result = agent.invoke({"input": message})
        
        # 提取输出
        output = result.get("output", str(result))
        
        # 记录历史
        add_to_history("用户", message)
        add_to_history("助手", output)
        
        return output
    
    except Exception as e:
        return f"处理请求时出现错误: {str(e)}"

# 测试函数
def run_test():
    """运行测试"""
    print("🚀 简化版AI Agent测试")
    print("=" * 50)
    
    test_cases = [
        "现在几点了？",
        "计算 123 + 456",
        "北京天气怎么样？",
        "计算 10 * 20 + 5"
    ]
    
    for test_case in test_cases:
        print(f"\n🤖 用户: {test_case}")
        print("-" * 30)
        
        response = chat_with_agent(test_case)
        print(f"🔮 Agent: {response}")
        print("-" * 30)

if __name__ == "__main__":
    run_test() 