#!/usr/bin/env python3
"""
快速安装和设置脚本
"""
import os
import subprocess
import sys

def install_requirements():
    """安装依赖项"""
    print("正在安装依赖项...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖项安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装依赖项失败: {e}")
        return False
    return True

def create_env_file():
    """创建.env文件"""
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} 已存在")
        return True
    
    print(f"正在创建 {env_file} 文件...")
    env_content = """# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Tavily Search API Key
TAVILY_API_KEY=your_tavily_api_key_here
"""
    
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        print(f"✅ {env_file} 创建完成")
        print("🚨 请编辑 .env 文件并填入正确的API密钥")
        return True
    except Exception as e:
        print(f"❌ 创建 {env_file} 失败: {e}")
        return False

def main():
    print("=== Python Agent 设置脚本 ===\n")
    
    # 安装依赖项
    if not install_requirements():
        return
    
    # 创建.env文件
    if not create_env_file():
        return
    
    print("\n=== 设置完成 ===")
    print("下一步：")
    print("1. 编辑 .env 文件，填入正确的API密钥")
    print("2. 运行: python agent.py")

if __name__ == "__main__":
    main() 