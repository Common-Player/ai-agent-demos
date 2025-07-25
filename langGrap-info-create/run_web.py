#!/usr/bin/env python3
"""
Web Agent 启动脚本
运行方式: python run_web.py
"""

import os
import sys

def check_env_file():
    """检查 .env 文件是否存在"""
    if not os.path.exists('.env'):
        print("❌ 未找到 .env 文件")
        print("请创建 .env 文件并添加以下内容：")
        print()
        print("# Google Gemini API 密钥")
        print("GOOGLE_API_KEY=your_google_api_key_here")
        print()
        print("# Tavily API 密钥") 
        print("TAVILY_API_KEY=your_tavily_api_key_here")
        print()
        print("获取 API 密钥:")
        print("1. Google API Key: https://makersuite.google.com/app/apikey")
        print("2. Tavily API Key: https://tavily.com/")
        return False
    return True

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        import langchain
        import langchain_google_genai
        import langchain_tavily
        import langgraph
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def main():
    print("🚀 启动 LangGraph AI Agent Web 界面")
    print("="*50)
    
    # 检查环境
    if not check_env_file():
        return
        
    if not check_dependencies():
        return
        
    print("✅ 环境检查通过")
    print()
    print("🌐 正在启动 Web 服务器...")
    print("📍 访问地址: http://localhost:8080")
    print("🛑 按 Ctrl+C 停止服务")
    print()
    print("💡 主要功能:")
    print("  🤖 AI网页设计师 - 主页面核心功能")
    print("    ✨ 深度理解设计需求，重新构思整个网页")
    print("    🎨 智能生成布局、色彩、动画和交互效果")
    print("    🚀 创造独特的视觉设计体验")
    print()
    print("  📊 完整功能演示 - demo.html")
    print("    🌤️ 天气查询、📰 新闻搜索、📄 网页提取")
    print("    🔬 综合研究、🧮 数学计算、⏰ 时间查询")
    print("    📁 文件操作、💻 系统信息")
    print("    🧠 记忆功能 - 保持对话上下文")
    print("-" * 50)
    
    # 启动 web 应用
    try:
        from web_agent import app
        app.run(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 