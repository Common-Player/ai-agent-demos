#!/usr/bin/env python3
"""
交互式AI Agent界面
"""
import os
import sys
import time
import signal
from typing import Dict, Any
from colorama import init, Fore, Style, Back
from agent import chat_with_agent, config, conversation_history

# 初始化colorama
init(autoreset=True)

# 会话状态
current_thread_id = "1"
is_running = True

def signal_handler(signum, frame):
    """信号处理器"""
    global is_running
    print(f"\n{Fore.YELLOW}正在退出...{Style.RESET_ALL}")
    is_running = False
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)

def print_separator(char="━", length=70, color=Fore.CYAN):
    """打印分隔线"""
    print(f"{color}{char * length}{Style.RESET_ALL}")

def print_box(content: str, title: str = "", color=Fore.CYAN):
    """打印边框"""
    lines = content.strip().split('\n')
    max_length = max(len(line) for line in lines)
    
    # 标题
    if title:
        print(f"{color}╔{'═' * (max_length + 2)}╗{Style.RESET_ALL}")
        print(f"{color}║{title.center(max_length + 2)}║{Style.RESET_ALL}")
        print(f"{color}╠{'═' * (max_length + 2)}╣{Style.RESET_ALL}")
    else:
        print(f"{color}╔{'═' * (max_length + 2)}╗{Style.RESET_ALL}")
    
    # 内容
    for line in lines:
        print(f"{color}║{Style.RESET_ALL} {line:<{max_length}} {color}║{Style.RESET_ALL}")
    
    # 底部
    print(f"{color}╚{'═' * (max_length + 2)}╝{Style.RESET_ALL}")

def show_welcome():
    """显示欢迎界面"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    welcome_text = """
🤖 增强型 AI Agent 交互式界面

🚀 功能特性:
• 🔍 网络搜索 (TavilySearch)
• 🧮 数学计算 (Calculator)
• ⏰ 时间查询
• 📁 文件操作 (读取/写入/列表)
• 🌤️ 天气查询
• 💻 系统信息
• 🧠 对话记忆

🔧 命令:
• /help     - 显示帮助
• /clear    - 清除屏幕
• /config   - 显示配置
• /history  - 显示对话历史
• /reset    - 重置对话历史
• /exit     - 退出程序

💡 提示: 直接输入问题开始对话
"""
    
    print_box(welcome_text, "🤖 AI Agent", Fore.BLUE)

def show_help():
    """显示帮助信息"""
    help_text = """
🔧 命令说明:
  /help     - 显示此帮助信息
  /clear    - 清除屏幕
  /config   - 显示当前配置
  /history  - 显示对话历史
  /reset    - 重置对话历史
  /exit     - 退出程序

📝 使用示例:
  • 现在几点了？
  • 帮我计算 123 + 456 * 789
  • 搜索最新的AI技术发展
  • 北京今天天气怎么样？
  • 读取README.md文件
  • 获取系统信息
"""
    
    print_box(help_text, "📖 帮助", Fore.GREEN)

def show_config():
    """显示配置信息"""
    config_text = f"""
模型: {config['llm']['model']}
温度: {config['llm']['temperature']}
最大令牌: {config['llm']['max_tokens']}
搜索结果数: {config['search']['max_results']}
当前线程: {current_thread_id}

启用的工具:
"""
    
    enabled_tools = [key for key, value in config["tools"].items() if value.get("enabled", False)]
    config_text += "  • " + "\n  • ".join(enabled_tools)
    
    print_box(config_text, "🔧 当前配置", Fore.MAGENTA)

def show_history():
    """显示对话历史"""
    if not conversation_history:
        print(f"{Fore.YELLOW}📝 暂无对话历史{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📚 对话历史:{Style.RESET_ALL}")
    print_separator()
    
    for i, msg in enumerate(conversation_history[-10:]):  # 显示最近10条
        role = msg["role"]
        content = msg["content"]
        
        if len(content) > 100:
            content = content[:100] + "..."
        
        role_color = Fore.BLUE if role == "用户" else Fore.GREEN
        print(f"{role_color}[{role}]:{Style.RESET_ALL} {content}")
        
        if i < len(conversation_history[-10:]) - 1:
            print(f"{Fore.CYAN}{'─' * 50}{Style.RESET_ALL}")
    
    print_separator()

def reset_history():
    """重置对话历史"""
    global conversation_history
    conversation_history.clear()
    print(f"{Fore.GREEN}✅ 对话历史已重置{Style.RESET_ALL}")

def process_command(command: str) -> bool:
    """处理命令"""
    cmd_parts = command[1:].split()
    cmd = cmd_parts[0] if cmd_parts else ""
    
    if cmd == "help":
        show_help()
    elif cmd == "clear":
        show_welcome()
    elif cmd == "config":
        show_config()
    elif cmd == "history":
        show_history()
    elif cmd == "reset":
        reset_history()
    elif cmd == "exit":
        print(f"{Fore.GREEN}👋 再见！{Style.RESET_ALL}")
        return False
    else:
        print(f"{Fore.RED}❌ 未知命令: {cmd}。输入 /help 查看可用命令。{Style.RESET_ALL}")
    
    return True

def show_thinking():
    """显示思考动画"""
    thinking_chars = ["🤔", "💭", "🧠", "⚡"]
    for i in range(4):
        print(f"\r{thinking_chars[i % len(thinking_chars)]} 思考中...", end="", flush=True)
        time.sleep(0.5)
    print("\r" + " " * 20, end="\r")  # 清除思考提示

def main():
    """主函数"""
    global is_running
    
    # 显示欢迎信息
    show_welcome()
    
    while is_running:
        try:
            # 获取用户输入
            user_input = input(f"\n{Fore.CYAN}🤖 > {Style.RESET_ALL}").strip()
            
            if not user_input:
                continue
            
            # 处理命令
            if user_input.startswith("/"):
                if not process_command(user_input):
                    break
                continue
            
            # 处理普通对话
            print(f"\n{Fore.BLUE}用户:{Style.RESET_ALL} {user_input}")
            print_separator("─", 50, Fore.CYAN)
            
            # 显示思考动画
            show_thinking()
            
            # 获取响应
            response = chat_with_agent(user_input)
            
            # 显示响应
            print(f"{Fore.GREEN}🤖 Agent:{Style.RESET_ALL}")
            print(response)
            
            # 显示时间戳
            if config["ui"]["show_timestamp"]:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"{Style.DIM}⏱️ {timestamp}{Style.RESET_ALL}")
            
            print_separator("─", 50, Fore.CYAN)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}正在退出...{Style.RESET_ALL}")
            break
        except EOFError:
            print(f"\n{Fore.YELLOW}程序已退出{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ 错误: {e}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}程序已退出{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 