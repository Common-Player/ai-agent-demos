import os
import re
import json
import math
import platform
import psutil
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """执行数学计算，支持基础运算、三角函数、对数等。
    
    Args:
        expression: 数学表达式，例如: 2+3*4, sqrt(16), sin(pi/2), log(10)
    """
    print(f"🧮 正在计算: {expression}")
    try:
        # 安全的数学表达式评估
        # 允许的函数和常量
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow
        })
        
        # 预处理表达式，替换一些常用写法
        expression = expression.replace("^", "**")  # 指数运算
        expression = re.sub(r'(\d)([a-zA-Z])', r'\\1*\\2', expression)  # 2x -> 2*x
        
        # 计算结果
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        print(f"✅ 计算完成: {expression} = {result}")
        return f"计算结果: {expression} = {result}"
        
    except Exception as e:
        error_msg = f"计算错误: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def get_datetime(query: str = "current") -> str:
    """获取当前时间、日期信息或进行时间查询。
    
    Args:
        query: 查询类型，可以是 current(当前时间)、now(现在)、format(格式示例) 等
    """
    print(f"⏰ 正在查询时间: {query}")
    try:
        now = datetime.now()
        
        if query.lower() in ["current", "now", "现在"]:
            result = f"""当前时间信息:
📅 日期: {now.strftime('%Y年%m月%d日')} ({now.strftime('%A')})
🕐 时间: {now.strftime('%H:%M:%S')}
🌍 时区: {now.astimezone().tzname()}
📊 详细: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}
🗓️ 星期: {now.strftime('%A')} (第{now.isocalendar()[1]}周)
🌙 今年第{now.timetuple().tm_yday}天"""
        
        elif "format" in query.lower():
            # 提供多种格式
            result = f"""时间格式示例:
标准格式: {now.strftime('%Y-%m-%d %H:%M:%S')}
美式格式: {now.strftime('%m/%d/%Y %I:%M %p')}
中文格式: {now.strftime('%Y年%m月%d日 %H时%M分%S秒')}
ISO格式: {now.isoformat()}
时间戳: {int(now.timestamp())}"""
        
        else:
            # 通用查询
            result = f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        
        print(f"✅ 时间查询完成")
        return result
        
    except Exception as e:
        error_msg = f"时间查询错误: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def file_operations(operation: str) -> str:
    """文件操作工具：读取文件内容、写入文件、列出目录。
    
    Args:
        operation: 操作格式，例如:
                  - read:/path/to/file (读取文件)
                  - list:/path/to/dir (列出目录)
                  - write:/path/to/file:content (写入文件)
    """
    print(f"📁 正在执行文件操作: {operation[:50]}...")
    try:
        parts = operation.split(":", 2)
        if len(parts) < 2:
            return "操作格式错误。示例: read:/path/to/file 或 list:/path/to/dir 或 write:/path/to/file:content"
        
        action = parts[0].lower().strip()
        path = parts[1].strip()
        
        if action == "read":
            if not os.path.exists(path):
                return f"文件不存在: {path}"
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 限制输出长度
            if len(content) > 2000:
                content = content[:2000] + "\\n...(内容过长，已截断)"
            
            print(f"✅ 文件读取完成: {path}")
            return f"文件内容 ({path}):  \\n{content}"
        
        elif action == "list":
            if not os.path.exists(path):
                return f"目录不存在: {path}"
            
            if not os.path.isdir(path):
                return f"不是目录: {path}"
            
            items = []
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(item_path)
                    items.append(f"📄 {item} ({_format_size(size)})")
            
            print(f"✅ 目录列表获取完成: {path}")
            return f"目录内容 ({path}):\\n" + "\\n".join(items[:50])  # 限制显示50个
        
        elif action == "write":
            if len(parts) < 3:
                return "写入格式错误。示例: write:/path/to/file:要写入的内容"
            
            content = parts[2]
            dir_path = os.path.dirname(path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 文件写入完成: {path}")
            return f"已写入文件: {path}\\n内容长度: {len(content)} 字符"
        
        else:
            return f"不支持的操作: {action}。支持的操作: read, list, write"
    
    except Exception as e:
        error_msg = f"文件操作错误: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

def _format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f}KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f}MB"
    else:
        return f"{size_bytes/(1024**3):.1f}GB"

@tool
def get_system_info(info_type: str = "all") -> str:
    """获取系统信息：操作系统、内存、CPU、Python版本等。
    
    Args:
        info_type: 信息类型，可以是 os, memory, cpu, python, all
    """
    print(f"💻 正在获取系统信息: {info_type}")
    try:
        info_type = info_type.lower().strip()
        
        result_parts = []
        
        if info_type in ["os", "all"]:
            os_info = f"""🖥️ 操作系统信息:
系统: {platform.system()} {platform.release()}
版本: {platform.version()}
架构: {platform.machine()}
处理器: {platform.processor() or '未知'}
主机名: {platform.node()}"""
            result_parts.append(os_info)
        
        if info_type in ["memory", "all"]:
            memory = psutil.virtual_memory()
            memory_info = f"""💾 内存信息:
总内存: {_format_bytes(memory.total)}
已使用: {_format_bytes(memory.used)} ({memory.percent:.1f}%)
可用: {_format_bytes(memory.available)}
缓存: {_format_bytes(memory.cached)}"""
            result_parts.append(memory_info)
        
        if info_type in ["cpu", "all"]:
            cpu_info = f"""⚡ CPU信息:
CPU核心: {psutil.cpu_count()} 物理核心, {psutil.cpu_count(logical=True)} 逻辑核心
CPU使用率: {psutil.cpu_percent(interval=1):.1f}%
负载平均: {os.getloadavg() if hasattr(os, 'getloadavg') else '不可用'}"""
            result_parts.append(cpu_info)
        
        if info_type in ["python", "all"]:
            python_info = f"""🐍 Python信息:
Python版本: {platform.python_version()}
Python实现: {platform.python_implementation()}
编译器: {platform.python_compiler()}"""
            result_parts.append(python_info)
        
        if not result_parts:
            return f"不支持的信息类型: {info_type}。支持: os, memory, cpu, python, all"
        
        result = "\\n\\n".join(result_parts)
        print(f"✅ 系统信息获取完成")
        return result
        
    except Exception as e:
        error_msg = f"系统信息获取错误: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

def _format_bytes(bytes_value):
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f}PB"

# 创建所有工具实例
def get_extended_tools():
    """获取所有扩展工具"""
    return [
        calculator,
        get_datetime, 
        file_operations,
        get_system_info
    ] 