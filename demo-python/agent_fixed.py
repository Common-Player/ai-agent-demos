#!/usr/bin/env python3
"""
增强版AI Agent - 基于工作版本的完整实现
"""
import os
import json
import platform
import psutil
import shutil
import time
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from agent_config import get_config, validate_config

# 加载环境变量
load_dotenv()

# 获取配置
config = get_config()

# 验证配置
config_errors = validate_config(config)
if config_errors:
    print("配置错误:")
    for error in config_errors:
        print(f"  - {error}")
    exit(1)

# 对话历史
conversation_history = []

def add_to_history(role: str, content: str):
    """添加消息到历史记录"""
    conversation_history.append({"role": role, "content": content})
    if len(conversation_history) > 20:
        conversation_history.pop(0)

# 工具函数 - 每个函数都接受一个输入参数
def get_current_time(query: str) -> str:
    """获取当前时间"""
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"

def calculator(expression: str) -> str:
    """数学计算器"""
    try:
        # 安全的数学表达式计算
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "表达式包含不允许的字符"
        
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

def weather_tool(city_name: str) -> str:
    """获取天气信息"""
    # 模拟天气数据
    mock_weather_data = {
        "北京": {"temperature": "15°C", "humidity": "65%", "wind_speed": "10km/h", "condition": "晴"},
        "上海": {"temperature": "18°C", "humidity": "70%", "wind_speed": "8km/h", "condition": "多云"},
        "广州": {"temperature": "22°C", "humidity": "80%", "wind_speed": "12km/h", "condition": "阴"},
        "深圳": {"temperature": "24°C", "humidity": "85%", "wind_speed": "15km/h", "condition": "雨"}
    }
    
    weather = mock_weather_data.get(city_name, {
        "temperature": "未知",
        "humidity": "未知", 
        "wind_speed": "未知",
        "condition": "数据不可用"
    })
    
    return f"""{city_name}天气：
温度: {weather['temperature']}
湿度: {weather['humidity']}
风速: {weather['wind_speed']}
天气状况: {weather['condition']}"""

def system_info(query: str) -> str:
    """获取系统信息"""
    try:
        memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        info = f"""系统信息:
操作系统: {platform.system()} {platform.release()}
架构: {platform.machine()}
CPU核心数: {cpu_count}
总内存: {memory.total / (1024**3):.2f} GB
可用内存: {memory.available / (1024**3):.2f} GB
内存使用率: {memory.percent}%
Python版本: {platform.python_version()}
启动时间: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}"""
        
        # 过滤敏感信息
        if config["tools"]["system"]["sensitive_info_filter"]:
            info = info.replace(os.path.expanduser("~"), "~")
        
        return info
    except Exception as e:
        return f"获取系统信息失败: {str(e)}"

def file_operations(input_str: str) -> str:
    """文件操作工具"""
    try:
        input_data = json.loads(input_str)
        action = input_data.get("action")
        file_path = input_data.get("path")
        content = input_data.get("content", "")
        
        # 安全检查
        if any(blocked in file_path for blocked in config["security"]["blocked_directories"]):
            return "访问被禁止的目录"
        
        if action == "read":
            if os.path.exists(file_path):
                # 检查文件大小
                if os.path.getsize(file_path) > config["file_operations"]["max_file_size"]:
                    return "文件过大，无法读取"
                
                with open(file_path, 'r', encoding=config["file_operations"]["default_encoding"]) as f:
                    return f.read()
            else:
                return "文件不存在"
        
        elif action == "write":
            # 备份现有文件
            if config["file_operations"]["backup_enabled"] and os.path.exists(file_path):
                shutil.copy2(file_path, f"{file_path}.backup")
            
            with open(file_path, 'w', encoding=config["file_operations"]["default_encoding"]) as f:
                f.write(content)
            return f"文件已写入: {file_path}"
        
        elif action == "list":
            if os.path.exists(file_path):
                files = os.listdir(file_path)
                return f"目录内容: {', '.join(files)}"
            else:
                return "目录不存在"
        
        else:
            return "不支持的操作，请使用 read、write 或 list"
    
    except json.JSONDecodeError:
        return "输入格式错误，请使用正确的JSON格式"
    except Exception as e:
        return f"操作失败: {str(e)}"

def search_web(query: str) -> str:
    """网络搜索工具"""
    try:
        from langchain_tavily import TavilySearchResults
        search_tool = TavilySearchResults(
            max_results=config["search"]["max_results"]
        )
        return search_tool.invoke(query)
    except ImportError:
        return "搜索功能暂不可用，请安装 langchain-tavily: pip install langchain-tavily"
    except Exception as e:
        return f"搜索失败: {str(e)}"

# 创建工具列表
def create_tools():
    """创建工具列表"""
    tools = []
    
    # 搜索工具
    if config["tools"]["search"]["enabled"]:
        tools.append(Tool(
            name="search",
            description="搜索网络信息，获取最新资讯",
            func=search_web
        ))
    
    # 计算器工具
    if config["tools"]["calculator"]["enabled"]:
        tools.append(Tool(
            name="calculator",
            description="进行数学计算，输入数学表达式",
            func=calculator
        ))
    
    # 时间工具
    if config["tools"]["time"]["enabled"]:
        tools.append(Tool(
            name="get_time",
            description="获取当前日期和时间",
            func=get_current_time
        ))
    
    # 文件操作工具
    if config["tools"]["file_ops"]["enabled"]:
        tools.append(Tool(
            name="file_operations",
            description="文件操作工具。输入JSON格式：{\"action\": \"read|write|list\", \"path\": \"文件路径\", \"content\": \"写入内容(仅写入时需要)\"}",
            func=file_operations
        ))
    
    # 天气工具
    if config["tools"]["weather"]["enabled"]:
        tools.append(Tool(
            name="weather",
            description="获取城市天气信息，输入城市名称",
            func=weather_tool
        ))
    
    # 系统信息工具
    if config["tools"]["system"]["enabled"]:
        tools.append(Tool(
            name="system_info",
            description="获取系统信息，包括操作系统、内存、CPU等",
            func=system_info
        ))
    
    return tools

# 创建Agent
def create_agent():
    """创建Agent实例"""
    llm = ChatDeepSeek(
        model=config["llm"]["model"],
        temperature=config["llm"]["temperature"],
        max_tokens=config["llm"]["max_tokens"]
    )
    
    tools = create_tools()
    
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

# 聊天函数
def chat_with_agent(message: str) -> str:
    """与Agent聊天"""
    try:
        agent = create_agent()
        
        # 构建带历史记录的消息
        context = ""
        if conversation_history:
            context = "\n\n之前的对话历史:\n"
            for msg in conversation_history[-5:]:  # 最近5条消息
                context += f"{msg['role']}: {msg['content']}\n"
        
        full_message = f"{context}\n\n当前用户问题: {message}"
        
        # 添加延迟
        time.sleep(config["performance"]["request_delay"] / 1000)
        
        # 使用invoke
        result = agent.invoke({"input": full_message})
        
        # 提取输出
        output = result.get("output", str(result))
        
        # 记录历史
        add_to_history("用户", message)
        add_to_history("助手", output)
        
        return output
    
    except Exception as e:
        return f"处理请求时出现错误: {str(e)}"

# 显示功能列表
def show_available_features():
    """显示可用功能"""
    print("""
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
  - Python版本等

🧠 记忆功能:
  - 保持对话上下文
  - 记住之前的交互

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# 运行演示
def run_demo():
    """运行演示"""
    show_available_features()
    
    # 测试案例
    test_cases = [
        "今天北京天气怎么样？",
        "帮我计算 123 + 456 * 789",
        "现在几点了？",
        "获取系统信息",
        "搜索最新的AI技术发展",
        "之前我们聊了什么？"
    ]
    
    for test_case in test_cases:
        print(f"\n🤖 用户: {test_case}")
        print("━" * 50)
        
        response = chat_with_agent(test_case)
        print(f"🔮 Agent: {response}")
        print("━" * 50)

if __name__ == "__main__":
    run_demo() 