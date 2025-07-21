import os
import asyncio
import json
import threading
import atexit
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_tavily import TavilySearch, TavilyExtract
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from extended_tools import get_extended_tools

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ 错误: langchain-google-genai 未安装，请先安装此依赖包")
    exit(1)

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)

# 全局事件循环线程
_loop = None
_loop_thread = None
_executor = ThreadPoolExecutor(max_workers=4)

def get_event_loop():
    """获取全局事件循环"""
    global _loop, _loop_thread
    
    if _loop is None or _loop.is_closed():
        loop_ready = threading.Event()
        
        def run_loop():
            global _loop
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
            loop_ready.set()  # 通知循环已准备好
            _loop.run_forever()
        
        _loop_thread = threading.Thread(target=run_loop, daemon=True)
        _loop_thread.start()
        
        # 等待循环启动
        loop_ready.wait(timeout=10)  # 最多等待10秒
        if not loop_ready.is_set():
            raise RuntimeError("事件循环启动超时")
    
    return _loop

def run_async_in_loop(coro):
    """在全局事件循环中运行协程"""
    try:
        loop = get_event_loop()
        if loop is None:
            raise RuntimeError("无法获取事件循环")
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result(timeout=300)  # 5分钟超时
    except Exception as e:
        print(f"❌ 异步操作执行失败: {str(e)}")
        return {"success": False, "error": f"操作失败: {str(e)}"}

class TavilySearchWithLogging(TavilySearch):
    """带输出日志的Tavily搜索工具"""
    
    def _run(self, query: str) -> str:
        """执行搜索并记录日志"""
        print(f"🔍 正在使用 Tavily 搜索工具查询: {query}")
        try:
            result = super()._run(query)
            print(f"✅ Tavily 搜索完成，获取到相关信息")
            if isinstance(result, dict):
                return str(result)
            return result
        except Exception as e:
            print(f"❌ Tavily 搜索出错: {str(e)}")
            return f"搜索出错: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """异步执行搜索并记录日志"""
        print(f"🔍 正在使用 Tavily 搜索工具查询: {query}")
        try:
            result = await super()._arun(query)
            print(f"✅ Tavily 搜索完成，获取到相关信息")
            if isinstance(result, dict):
                return str(result)
            return result
        except Exception as e:
            print(f"❌ Tavily 搜索出错: {str(e)}")
            return f"搜索出错: {str(e)}"

class TavilyExtractWithLogging(TavilyExtract):
    """带输出日志的Tavily内容提取工具"""
    
    def _run(self, urls: str) -> str:
        """执行内容提取并记录日志"""
        if isinstance(urls, str):
            url_list = [url.strip() for url in urls.split(',') if url.strip()]
        else:
            url_list = urls
            
        print(f"📄 正在使用 Tavily 提取工具从 {len(url_list)} 个URL提取内容...")
        try:
            result = super()._run(url_list)
            print(f"✅ Tavily 内容提取完成")
            if isinstance(result, dict):
                return str(result)
            return result
        except Exception as e:
            print(f"❌ Tavily 内容提取出错: {str(e)}")
            return f"内容提取出错: {str(e)}"
    
    async def _arun(self, urls: str) -> str:
        """异步执行内容提取并记录日志"""
        if isinstance(urls, str):
            url_list = [url.strip() for url in urls.split(',') if url.strip()]
        else:
            url_list = urls
            
        print(f"📄 正在使用 Tavily 提取工具从 {len(url_list)} 个URL提取内容...")
        try:
            result = await super()._arun(url_list)
            print(f"✅ Tavily 内容提取完成")
            if isinstance(result, dict):
                return str(result)
            return result
        except Exception as e:
            print(f"❌ Tavily 内容提取出错: {str(e)}")
            return f"内容提取出错: {str(e)}"

# 定义所有可用工具
tavily_tools = [
    TavilySearchWithLogging(
        max_results=5,
        search_depth="basic",
        include_answer=True,
        include_raw_content=True,
        include_images=False,
        name="tavily_search",
        description="强大的实时网络搜索工具，用于获取最新信息、新闻和网络内容。"
    ),
    TavilyExtractWithLogging(
        extract_depth="basic",
        include_images=False,
        name="tavily_extract",
        description="强大的网页内容提取工具，可以从指定URL中提取和处理原始内容。"
    )
]

# 合并所有工具
agent_tools = tavily_tools + get_extended_tools()

def create_gemini_model():
    """创建 Gemini 模型实例"""
    if not GEMINI_AVAILABLE:
        raise ValueError("Gemini 模型不可用，请先安装 langchain-google-genai")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("❌ 未找到 GOOGLE_API_KEY 环境变量，请在 .env 文件中配置")
        
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.1,
        max_tokens=20000,
        google_api_key=api_key
    )

# 创建 Gemini 模型和 Agent
print("🚀 初始化 Gemini 2.5 Pro 模型...")
try:
    agent_model = create_gemini_model()
    print("✅ Gemini 2.5 Pro 模型初始化成功")
    
    agent_checkpoint = MemorySaver()
    agent = create_react_agent(
        model=agent_model,
        tools=agent_tools,
        checkpointer=agent_checkpoint
    )
    print("✅ Agent 初始化成功")
    
except Exception as e:
    print(f"❌ 模型或 Agent 初始化失败: {str(e)}")
    exit(1)

async def run_agent_query(prompt: str, thread_id: str = "web_session"):
    """运行 Agent 查询并返回结果"""
    if 'agent' not in globals():
        return {"success": False, "error": "Agent 未初始化"}
        
    config = RunnableConfig(configurable={"thread_id": thread_id})
    
    try:
        print(f"🤖 开始处理查询: {prompt[:50]}...")
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=prompt)]},
            config=config
        )
        
        if result["messages"]:
            last_message = result["messages"][-1]
            print(f"✅ 查询处理完成")
            return {"success": True, "response": last_message.content}
        else:
            print(f"❌ 未收到回复")
            return {"success": False, "error": "未收到回复"}
            
    except Exception as e:
        print(f"❌ 查询处理失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        thread_id = data.get('thread_id', 'web_session')
        
        if not prompt:
            return jsonify({"success": False, "error": "请输入问题"})
        
        # 使用全局事件循环运行异步函数
        result = run_async_in_loop(run_agent_query(prompt, thread_id))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/preset/<preset_type>', methods=['POST'])
def preset_query(preset_type):
    """处理预设问题"""
    try:
        data = request.get_json()
        user_input = data.get('input', '')
        thread_id = data.get('thread_id', 'web_session')
        
        prompts = {
            'weather': f"请搜索 {user_input} 今天的天气情况，并提供详细的天气信息",
            'news': f"请搜索关于 '{user_input}' 的最新新闻，提供详细的新闻摘要和相关信息",
            'extract': f"请使用内容提取工具从以下URL提取内容并进行分析: {user_input}",
            'research': f"""请对以下主题进行综合研究: {user_input}
            
请按照以下步骤进行:
1. 首先使用搜索工具获取相关的最新信息和资料
2. 如果找到重要的网页链接，使用内容提取工具获取详细内容
3. 综合所有信息，提供详细的研究报告

主题: {user_input}""",
            'calculate': f"请使用计算工具计算以下表达式: {user_input}",
            'datetime': f"请使用时间工具查询: {user_input}",
            'file': f"请使用文件操作工具执行: {user_input}",
            'system': f"请使用系统信息工具获取: {user_input}"
        }
        
        prompt = prompts.get(preset_type)
        if not prompt:
            return jsonify({"success": False, "error": "无效的预设类型"})
        
        # 使用全局事件循环运行异步函数
        result = run_async_in_loop(run_agent_query(prompt, thread_id))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def cleanup():
    """清理资源"""
    global _loop, _loop_thread, _executor
    
    if _loop and not _loop.is_closed():
        _loop.call_soon_threadsafe(_loop.stop)
    
    if _executor:
        _executor.shutdown(wait=True)

atexit.register(cleanup)

if __name__ == '__main__':
    print("🔧 正在启动 Web Agent 服务...")
    print(f"📊 当前可用工具数量: {len(agent_tools)}")
    for i, tool in enumerate(agent_tools, 1):
        print(f"  {i}. {tool.name}: {tool.description}")
    
    # 初始化事件循环
    print("🔄 初始化异步事件循环...")
    get_event_loop()
    print("✅ 事件循环初始化完成")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=8080)
    finally:
        cleanup() 