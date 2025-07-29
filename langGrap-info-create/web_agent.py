import os
import asyncio
import json
import threading
import atexit
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify, render_template, Response, session
from flask_cors import CORS
from flask_session import Session
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_tavily import TavilySearch, TavilyExtract
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from extended_tools import get_extended_tools
# 删除未使用的 webpage_generator 导入
from ai_webpage_designer import get_ai_webpage_designer_tool
from auth_manager import get_auth_manager
from history_manager import get_history_manager

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ 错误: langchain-google-genai 未安装，请先安装此依赖包")
    exit(1)

try:
    from langchain_openai import ChatOpenAI
    from pydantic import SecretStr
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  警告: langchain-openai 未安装，deepseek模型将不可用")

try:
    from langchain_anthropic import ChatAnthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    print("⚠️  警告: langchain-anthropic 未安装，Claude模型将不可用")

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)

# Flask会话配置
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'ai_agent:'
Session(app)

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
        return future.result(timeout=3000)  # 5分钟超时
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
extended_tools = get_extended_tools()
ai_designer_tool = get_ai_webpage_designer_tool()
agent_tools = tavily_tools + extended_tools + [ai_designer_tool]

def create_deepseek_model():
    """创建 DeepSeek 模型实例"""
    if not OPENAI_AVAILABLE:
        raise ValueError("DeepSeek 模型不可用，请先安装 langchain-openai")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("❌ 未找到 DEEPSEEK_API_KEY 环境变量，请在 .env 文件中配置")
        
    return ChatOpenAI(
        model="deepseek-chat",
        temperature=0.1,
        api_key=SecretStr(api_key) if api_key else None,
        base_url="https://api.deepseek.com"
    )

def create_gemini_model(model_name="gemini-2.5-pro"):
    """创建 Gemini 模型实例"""
    if not GEMINI_AVAILABLE:
        raise ValueError("Gemini 模型不可用，请先安装 langchain-google-genai")
    print("🔄 创建 Gemini 模型实例")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("❌ 未找到 GOOGLE_API_KEY 环境变量，请在 .env 文件中配置")
    print("🔄 创建 Gemini 模型实例2")
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.1,
        max_tokens=20000,
        google_api_key=api_key
    )



# 模型配置映射
MODEL_CONFIG = {
    # 简单任务使用 DeepSeek
    'simple': {
        'name': 'DeepSeek Chat',
        'types': ['weather', 'extract', 'calculate', 'datetime', 'file'],
        'create_func': create_deepseek_model
    },
    # 复杂研究任务使用 Gemini Flash
    'research': {
        'name': 'Gemini 2.5 Flash',
        'types': ['research', 'news'],
        'create_func': lambda: create_gemini_model("gemini-2.5-pro")
    },
    # AI设计师任务使用 Gemini Pro
    'ai_design': {
        'name': 'Gemini 2.5 Pro',
        'types': ['ai_design'],
        'create_func': lambda: create_gemini_model("gemini-2.5-pro")
    }
}

# 创建所有模型和对应的 Agent
print("🚀 初始化多模型系统...")
models = {}
agents = {}

for model_type, config in MODEL_CONFIG.items():
    try:
        print(f"📦 正在初始化 {config['name']}...")
        model = config['create_func']()
        models[model_type] = model
        
        # 为每个模型创建对应的 Agent
        # 简单任务不使用checkpoint，避免上下文积累导致token超限
        if model_type == 'simple':
            # DeepSeek模型token限制较小，不使用历史记忆
            agent = create_react_agent(
                model=model,
                tools=agent_tools,
                checkpointer=None
            )
            print(f"  📝 {config['name']} 配置为无记忆模式（避免token超限）")
        else:
            # 复杂任务使用checkpoint，保持对话连贯性
            checkpoint = MemorySaver()
            agent = create_react_agent(
                model=model,
                tools=agent_tools,
                checkpointer=checkpoint
            )
            print(f"  📝 {config['name']} 配置为记忆模式")
        agents[model_type] = agent
        print(f"✅ {config['name']} 初始化成功")
        
    except Exception as e:
        print(f"❌ {config['name']} 初始化失败: {str(e)}")
        # 如果简单任务模型失败，尝试使用Gemini Flash作为备选
        if model_type == 'simple':
            try:
                print("🔄 尝试使用 Gemini Flash 作为简单任务的备选模型...")
                fallback_model = create_gemini_model("gemini-2.5-pro")
                models[model_type] = fallback_model
                # 备选模型也使用无记忆模式，保持与原配置一致
                agent = create_react_agent(
                    model=fallback_model,
                    tools=agent_tools,
                    checkpointer=None
                )
                agents[model_type] = agent
                print("✅ 备选模型初始化成功（无记忆模式）")
            except Exception as fallback_error:
                print(f"❌ 备选模型也初始化失败: {str(fallback_error)}")
                exit(1)
        # 如果AI设计师模型失败，使用相同的备选逻辑
        elif model_type == 'ai_design':
            try:
                print("🔄 AI设计师模型初始化失败，尝试使用备选模型...")
                fallback_model = create_gemini_model("gemini-2.5-pro")
                models[model_type] = fallback_model
                # AI设计师任务使用记忆模式
                checkpoint = MemorySaver()
                agent = create_react_agent(
                    model=fallback_model,
                    tools=agent_tools,
                    checkpointer=checkpoint
                )
                agents[model_type] = agent
                print("✅ AI设计师备选模型初始化成功（记忆模式）")
            except Exception as fallback_error:
                print(f"❌ AI设计师备选模型也初始化失败: {str(fallback_error)}")
                print(f"⚠️  AI设计师功能将不可用")
        else:
            print(f"⚠️  {config['name']} 不可用，相关功能可能受影响")

def get_model_type_for_preset(preset_type):
    """根据预设类型获取对应的模型类型"""
    for model_type, config in MODEL_CONFIG.items():
        if preset_type in config['types']:
            return model_type
    return 'simple'  # 默认使用简单任务模型

print("✅ 多模型系统初始化完成")

async def run_agent_query(prompt: str, thread_id: str = "web_session", model_type: str = "simple"):
    """运行 Agent 查询并返回结果"""
    if model_type not in agents:
        return {"success": False, "error": f"模型类型 {model_type} 未初始化"}
        
    agent = agents[model_type]
    model_name = MODEL_CONFIG[model_type]['name']
    
    # 根据模型类型决定是否使用thread_id配置
    if model_type == 'simple':
        # 简单任务不使用记忆，不需要thread_id配置
        config = None
        print(f"🤖 使用 {model_name} (无记忆模式) 处理查询: {prompt[:50]}...")
    else:
        # 复杂任务使用记忆功能
        config = RunnableConfig(configurable={"thread_id": thread_id})
        print(f"🤖 使用 {model_name} (记忆模式) 处理查询: {prompt[:50]}...")
    
    try:
        if config:
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
        else:
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=prompt)]}
            )
        
        if result["messages"]:
            last_message = result["messages"][-1]
            print(f"✅ {model_name} 查询处理完成")
            return {"success": True, "response": last_message.content}
        else:
            print(f"❌ {model_name} 未收到回复")
            return {"success": False, "error": "未收到回复"}
            
    except Exception as e:
        print(f"❌ {model_name} 查询处理失败: {str(e)}")
        return {"success": False, "error": str(e)}

def get_current_user():
    """获取当前登录用户信息"""
    access_token = session.get('access_token')
    if not access_token:
        return None
    
    try:
        auth_manager = get_auth_manager()
        return auth_manager.get_current_user(access_token)
    except Exception as e:
        print(f"❌ 获取当前用户失败: {e}")
        return None

@app.route('/')
def index():
    """主页面"""
    user = get_current_user()
    # 如果集成了用户认证，使用增强版模板
    return render_template('index.html', user=user)

@app.route('/auth')
def auth_page():
    """用户认证页面"""
    return render_template('auth.html')

@app.route('/generated/<filename>')
def serve_generated_page(filename):
    """提供生成的网页文件"""
    try:
        generated_path = os.path.join(os.path.dirname(__file__), 'generated_pages', filename)
        if os.path.exists(generated_path):
            with open(generated_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "网页文件不存在", 404
    except Exception as e:
        return f"访问错误: {str(e)}", 500

@app.route('/demo.html')
def serve_demo():
    """提供demo.html文件"""
    try:
        demo_path = os.path.join(os.path.dirname(__file__), 'demo.html')
        if os.path.exists(demo_path):
            with open(demo_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "demo.html文件不存在", 404
    except Exception as e:
        return f"访问demo.html错误: {str(e)}", 500

# 用户认证路由
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        username = data.get('username', '').strip()
        
        if not email or not password:
            return jsonify({"success": False, "message": "邮箱和密码不能为空"})
        
        auth_manager = get_auth_manager()
        result = auth_manager.register(email, password, username)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "message": f"注册失败: {str(e)}"})

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({"success": False, "message": "邮箱和密码不能为空"})
        
        auth_manager = get_auth_manager()
        result = auth_manager.login(email, password)
        
        if result['success']:
            # 保存会话信息
            session['access_token'] = result['session']['access_token']
            session['refresh_token'] = result['session']['refresh_token']
            session['user_id'] = result['user']['id']
            session['user_email'] = result['user']['email']
            session['username'] = result['user']['username']
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "message": f"登录失败: {str(e)}"})

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    try:
        auth_manager = get_auth_manager()
        result = auth_manager.logout()
        
        # 清除会话信息
        session.clear()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "message": f"登出失败: {str(e)}"})

@app.route('/api/user', methods=['GET'])
def get_user_info():
    """获取当前用户信息"""
    user = get_current_user()
    if user:
        return jsonify({"success": True, "user": user})
    else:
        return jsonify({"success": False, "message": "未登录"})

# 用户历史记录路由
@app.route('/api/history/prompts', methods=['GET'])
def get_prompt_history():
    """获取用户提示词历史记录"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "请先登录"})
    
    try:
        limit = request.args.get('limit', 50, type=int)
        prompt_type = request.args.get('type')
        
        history_manager = get_history_manager()
        access_token = session.get('access_token')
        
        # 确保access_token存在
        if not access_token:
            return jsonify({
                "success": False,
                "error": "未找到用户访问令牌"
            })
        
        history = history_manager.get_user_prompt_history(
            user['id'], limit, prompt_type, access_token
        )
        
        print(f"📊 获取用户 {user['id']} 的提示词历史: {len(history)} 条记录")
        
        return jsonify({
            "success": True,
            "history": history,
            "total": len(history)
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"获取历史记录失败: {str(e)}"})

@app.route('/api/history/webpages', methods=['GET'])
def get_webpage_history():
    """获取用户网页生成历史记录"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "请先登录"})
    
    try:
        limit = request.args.get('limit', 20, type=int)
        
        history_manager = get_history_manager()
        access_token = session.get('access_token')
        
        # 确保access_token存在
        if not access_token:
            return jsonify({
                "success": False,
                "error": "未找到用户访问令牌"
            })
        
        history = history_manager.get_user_webpage_generations(user['id'], limit, access_token)
        
        print(f"🌐 获取用户 {user['id']} 的网页生成历史: {len(history)} 条记录")
        
        return jsonify({
            "success": True,
            "history": history,
            "total": len(history)
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"获取网页生成记录失败: {str(e)}"})

@app.route('/api/history/stats', methods=['GET'])
def get_user_stats():
    """获取用户统计信息"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "请先登录"})
    
    try:
        history_manager = get_history_manager()
        stats = history_manager.get_user_statistics(user['id'])
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"获取统计信息失败: {str(e)}"})

# 删除未使用的 /api/chat 路由

@app.route('/api/preset/<preset_type>', methods=['POST'])
def preset_query(preset_type):
    """处理预设问题"""
    try:
        data = request.get_json()
        user_input = data.get('input', '')
        thread_id = data.get('thread_id', 'web_session')
        
        prompts = {
            'weather': f"""请搜索 {user_input} 今天的天气情况，获取详细信息后，严格按照以下JSON格式返回，不要包含任何其他文字说明：

{{
    "type": "weather",
    "city": "{user_input}",
    "temperature": {{"current": "具体温度值", "high": "最高温度", "low": "最低温度"}},
    "condition": "天气现象",
    "humidity": "湿度值",
    "wind": "风力风向", 
    "airQuality": "空气质量状况",
    "suggestions": ["生活建议1", "生活建议2", "生活建议3"],
    "details": "天气详细描述"
}}

重要：只返回JSON数据，不要添加任何解释文字。""",
            'news': f"""请搜索关于 '{user_input}' 的最新新闻，获取信息后严格按照以下JSON格式返回：

{{
    "type": "news",
    "topic": "{user_input}",
    "articles": [
        {{
            "title": "新闻标题",
            "summary": "新闻摘要",
            "source": "新闻来源",
            "time": "发布时间"
        }}
    ],
    "summary": "整体新闻概述",
    "keyPoints": ["关键点1", "关键点2", "关键点3"]
}}

重要：只返回JSON数据，不要添加任何解释文字。""",
            'extract': f"""请使用内容提取工具从URL：{user_input} 提取内容，分析后严格按照以下JSON格式返回：

{{
    "type": "extract",
    "url": "{user_input}",
    "title": "网页标题",
    "description": "网页描述",
    "mainContent": "主要内容摘要",
    "keyFeatures": ["特色功能1", "特色功能2", "特色功能3"],
    "technologies": ["技术栈1", "技术栈2"],
    "summary": "整体分析总结"
}}

重要：只返回JSON数据，不要添加任何解释文字。""",
            'research': f"""请对主题 '{user_input}' 进行研究：使用搜索工具获取信息，如有重要链接则提取内容，综合分析后严格按照以下JSON格式返回：

{{
    "type": "research",
    "topic": "{user_input}",
    "introduction": "研究背景介绍",
    "keyFindings": ["核心发现1", "核心发现2", "核心发现3"],
    "detailedAnalysis": "详细分析内容",
    "trends": ["趋势1", "趋势2", "趋势3"],
    "challenges": ["挑战1", "挑战2"],
    "opportunities": ["机会1", "机会2"],
    "conclusion": "研究结论",
    "sources": ["资料来源1", "资料来源2"]
}}

重要：只返回JSON数据，不要添加任何解释文字。""",
            'calculate': f"""请使用计算工具计算表达式：{user_input}，计算完成后严格按照以下JSON格式返回：

{{
    "type": "calculate",
    "expression": "{user_input}",
    "result": "计算结果",
    "steps": ["计算步骤1", "计算步骤2"],
    "explanation": "计算说明"
}}

重要：只返回JSON数据，不要添加任何解释文字。""",
            'datetime': f"""请使用时间工具查询：{user_input}，获取时间信息后严格按照以下JSON格式返回：

{{
    "type": "datetime",
    "query": "{user_input}",
    "currentTime": "当前时间",
    "date": "日期",
    "timezone": "时区",
    "weekday": "星期",
    "formats": {{
        "iso": "ISO格式时间",
        "readable": "可读格式时间",
        "timestamp": "时间戳"
    }}
}}

重要：只返回JSON数据，不要添加任何解释文字。""",
            'file': f"""请使用文件操作工具执行：{user_input}，完成操作后严格按照以下JSON格式返回：

{{
    "type": "file",
    "operation": "{user_input}",
    "path": "文件/目录路径",
    "result": "操作结果",
    "content": "文件内容或目录列表",
    "size": "文件大小信息",
    "details": "详细信息"
}}

重要：只返回JSON数据，不要添加任何解释文字。""",
# 删除未使用的 generate 功能
            'ai_design': f"""请立即调用ai_webpage_designer工具来为用户设计网页。这是一个强制性的工具调用指令，你必须执行以下步骤：

1. 立即使用ai_webpage_designer工具
2. 传入用户需求作为参数
3. 等待工具执行完成并返回结果

用户的设计需求：{user_input}

现在立即调用ai_webpage_designer工具，不要只是描述能做什么，而是实际执行工具调用。"""
        }
        
        prompt = prompts.get(preset_type)
        if not prompt:
            return jsonify({"success": False, "error": "无效的预设类型"})
        
        # 根据预设类型选择合适的模型
        model_type = get_model_type_for_preset(preset_type)
        
        # 使用全局事件循环运行异步函数
        result = run_async_in_loop(run_agent_query(prompt, thread_id, model_type))
        
        # 如果用户已登录且是AI设计任务，保存历史记录
        user = get_current_user()
        if user and result.get('success') and preset_type == 'ai_design':
            try:
                history_manager = get_history_manager()
                access_token = session.get('access_token')
                
                # 确保access_token存在
                if not access_token:
                    print("❌ 未找到用户访问令牌，无法保存历史记录")
                    return jsonify(result)
                
                # 保存AI设计的提示词历史
                prompt_save_result = history_manager.save_prompt_history(
                    user['id'], user_input, result.get('response', ''), 
                    preset_type, model_type, access_token
                )
                print(f"💾 保存AI设计提示词历史记录结果: {prompt_save_result}")
                
                # 保存网页生成记录
                response_text = result.get('response', '')
                filename = None
                
                # 尝试从响应中提取文件名
                import re
                filename_match = re.search(r'ai_designed_webpage_(\d+)\.html', response_text)
                if filename_match:
                    filename = filename_match.group(0)
                
                if filename:
                    # 尝试读取生成的HTML内容
                    try:
                        generated_path = os.path.join(
                            os.path.dirname(__file__), 
                            'generated_pages', 
                            filename
                        )
                        html_content = ""
                        if os.path.exists(generated_path):
                            with open(generated_path, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                        
                        webpage_save_result = history_manager.save_webpage_generation(
                            user['id'], user_input, html_content, filename, preset_type, access_token
                        )
                        print(f"🌐 保存网页生成记录结果: {webpage_save_result}")
                    except Exception as e:
                        print(f"❌ 保存网页生成记录失败: {e}")
            except Exception as e:
                print(f"❌ 保存用户历史记录失败: {e}")
        
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