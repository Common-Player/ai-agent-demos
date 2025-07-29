import os
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_tavily import TavilySearch, TavilyExtract
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ 错误: langchain-google-genai 未安装，请先安装此依赖包")
    exit(1)

# 加载环境变量
load_dotenv()

class TavilySearchWithLogging(TavilySearch):
    """带输出日志的Tavily搜索工具"""
    
    def _run(self, query: str) -> str:
        """执行搜索并记录日志"""
        print(f"🔍 正在使用 Tavily 搜索工具查询: {query}")
        try:
            result = super()._run(query)
            print(f"✅ Tavily 搜索完成，获取到相关信息")
            # 确保返回字符串类型
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
            # 确保返回字符串类型
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
        # 处理输入：如果是字符串，尝试解析为列表
        if isinstance(urls, str):
            # 简单处理：假设是单个URL或者逗号分隔的URL列表
            url_list = [url.strip() for url in urls.split(',') if url.strip()]
        else:
            url_list = urls
            
        print(f"📄 正在使用 Tavily 提取工具从 {len(url_list)} 个URL提取内容...")
        try:
            # 直接传递 URL 列表
            result = super()._run(url_list)
            print(f"✅ Tavily 内容提取完成")
            # 确保返回字符串类型
            if isinstance(result, dict):
                return str(result)
            return result
        except Exception as e:
            print(f"❌ Tavily 内容提取出错: {str(e)}")
            return f"内容提取出错: {str(e)}"
    
    async def _arun(self, urls: str) -> str:
        """异步执行内容提取并记录日志"""
        # 处理输入：如果是字符串，尝试解析为列表
        if isinstance(urls, str):
            url_list = [url.strip() for url in urls.split(',') if url.strip()]
        else:
            url_list = urls
            
        print(f"📄 正在使用 Tavily 提取工具从 {len(url_list)} 个URL提取内容...")
        try:
            # 直接传递 URL 列表
            result = await super()._arun(url_list)
            print(f"✅ Tavily 内容提取完成")
            # 确保返回字符串类型
            if isinstance(result, dict):
                return str(result)
            return result
        except Exception as e:
            print(f"❌ Tavily 内容提取出错: {str(e)}")
            return f"内容提取出错: {str(e)}"

# 定义所有可用的 Tavily 工具
agent_tools = [
    TavilySearchWithLogging(
        max_results=5,
        search_depth="basic",
        include_answer=True,
        include_raw_content=True,
        include_images=False,
        name="tavily_search",
        description="强大的实时网络搜索工具，用于获取最新信息、新闻和网络内容。支持自定义搜索深度、结果数量和域名过滤。"
    ),
    TavilyExtractWithLogging(
        extract_depth="basic",
        include_images=False,
        name="tavily_extract",
        description="强大的网页内容提取工具，可以从指定URL中提取和处理原始内容，适用于数据收集、内容分析和研究任务。输入应该是URL列表，用逗号分隔。"
    )
]

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

# 创建 Gemini 模型
print("🚀 初始化 Gemini 2.5 Pro 模型...")
try:
    agent_model = create_gemini_model()
    print("✅ Gemini 2.5 Pro 模型初始化成功")
except Exception as e:
    print(f"❌ 模型初始化失败: {str(e)}")
    exit(1)

# 初始化内存保存器
agent_checkpoint = MemorySaver()

# 创建 Agent
agent = create_react_agent(
    model=agent_model,
    tools=agent_tools,
    checkpointer=agent_checkpoint
)

async def run_streaming_agent(prompt: str, thread_id: str = "1"):
    """运行流式输出的 Agent"""
    config = {"configurable": {"thread_id": thread_id}}
    
    async for chunk in agent.astream(
        {"messages": [HumanMessage(content=prompt)]},
        config=config,
        stream_mode="updates"
    ):
        if "agent" in chunk and "messages" in chunk["agent"]:
            messages = chunk["agent"]["messages"]
            if messages:
                last_msg = messages[-1]
                if hasattr(last_msg, 'content') and last_msg.content:
                    if isinstance(last_msg.content, str):
                        print(last_msg.content, end='', flush=True)
                    elif isinstance(last_msg.content, list):
                        for part in last_msg.content:
                            if hasattr(part, 'type') and part.type == 'text':
                                print(part.text, end='', flush=True)
        elif "tools" in chunk:
            # 工具调用信息已经在自定义工具中处理
            pass
        elif "messages" in chunk:
            messages = chunk["messages"]
            if messages:
                last_msg = messages[-1]
                if hasattr(last_msg, 'content') and last_msg.content:
                    if isinstance(last_msg.content, str):
                        print(last_msg.content, end='', flush=True)
                    elif isinstance(last_msg.content, list):
                        for part in last_msg.content:
                            if hasattr(part, 'type') and part.type == 'text':
                                print(part.text, end='', flush=True)

async def run_non_streaming_agent(prompt: str, thread_id: str = "1"):
    """运行非流式输出的 Agent"""
    config = {"configurable": {"thread_id": thread_id}}
    
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=config
    )
    
    if result["messages"]:
        last_message = result["messages"][-1]
        print(last_message.content)

def show_demo_menu():
    """显示功能演示菜单"""
    print("\n" + "="*60)
    print("🤖 LangGraph 多功能 Agent (Gemini 2.5 Pro + Tavily 完整版)")
    print("="*60)
    print("\n📋 可用功能演示:")
    print("1. 天气查询 (搜索功能)")
    print("2. 新闻搜索 (高级搜索)")
    print("3. 网页内容提取 (从URL提取内容)")
    print("4. 综合研究任务 (搜索+提取)")
    print("5. 自定义问题")
    print("0. 退出")
    print("-" * 60)

async def demo_weather_search():
    """演示天气查询功能"""
    location = input("请输入要查询天气的城市名称: ").strip()
    if not location:
        print("❌ 未输入城市名称")
        return
        
    prompt = f"请搜索 {location} 今天的天气情况，并提供详细的天气信息"
    print(f"\n🌤️ 正在查询 {location} 的天气信息...\n")
    
    stream_choice = input("是否使用流式输出？(y/N): ").strip().lower()
    if stream_choice in ['y', 'yes', '是']:
        await run_streaming_agent(prompt)
    else:
        await run_non_streaming_agent(prompt)

async def demo_news_search():
    """演示新闻搜索功能"""
    topic = input("请输入要搜索的新闻主题: ").strip()
    if not topic:
        print("❌ 未输入搜索主题")
        return
        
    prompt = f"请搜索关于 '{topic}' 的最新新闻，提供详细的新闻摘要和相关信息"
    print(f"\n📰 正在搜索关于 '{topic}' 的最新新闻...\n")
    
    stream_choice = input("是否使用流式输出？(y/N): ").strip().lower()
    if stream_choice in ['y', 'yes', '是']:
        await run_streaming_agent(prompt)
    else:
        await run_non_streaming_agent(prompt)

async def demo_content_extraction():
    """演示网页内容提取功能"""
    print("请输入要提取内容的网页URL（可以输入多个，用逗号分隔）:")
    print("示例: https://example.com, https://another-site.com")
    
    urls = input("URLs: ").strip()
    if not urls:
        print("❌ 未输入URL")
        return
        
    prompt = f"请使用内容提取工具从以下URL提取内容并进行分析: {urls}"
    print(f"\n📄 正在从指定URL提取内容...\n")
    
    stream_choice = input("是否使用流式输出？(y/N): ").strip().lower()
    if stream_choice in ['y', 'yes', '是']:
        await run_streaming_agent(prompt)
    else:
        await run_non_streaming_agent(prompt)

async def demo_comprehensive_research():
    """演示综合研究任务"""
    topic = input("请输入研究主题: ").strip()
    if not topic:
        print("❌ 未输入研究主题")
        return
        
    prompt = f"""请对以下主题进行综合研究: {topic}
    
    请按照以下步骤进行:
    1. 首先使用搜索工具获取相关的最新信息和资料
    2. 如果找到重要的网页链接，使用内容提取工具获取详细内容
    3. 综合所有信息，提供详细的研究报告
    
    主题: {topic}"""
    
    print(f"\n🔬 正在进行关于 '{topic}' 的综合研究...\n")
    
    stream_choice = input("是否使用流式输出？(y/N): ").strip().lower()
    if stream_choice in ['y', 'yes', '是']:
        await run_streaming_agent(prompt)
    else:
        await run_non_streaming_agent(prompt)

async def demo_custom_question():
    """演示自定义问题"""
    question = input("请输入您的问题: ").strip()
    if not question:
        print("❌ 未输入问题")
        return
        
    print(f"\n🤔 正在处理您的问题: {question}\n")
    
    stream_choice = input("是否使用流式输出？(y/N): ").strip().lower()
    if stream_choice in ['y', 'yes', '是']:
        await run_streaming_agent(question)
    else:
        await run_non_streaming_agent(question)

async def main():
    """主函数"""
    while True:
        show_demo_menu()
        
        try:
            choice = input("\n请选择功能 (0-5): ").strip()
            
            if choice == "0":
                print("\n👋 感谢使用，再见！")
                break
            elif choice == "1":
                await demo_weather_search()
            elif choice == "2":
                await demo_news_search()
            elif choice == "3":
                await demo_content_extraction()
            elif choice == "4":
                await demo_comprehensive_research()
            elif choice == "5":
                await demo_custom_question()
            else:
                print("❌ 无效选择，请输入 0-5 之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            
        # 询问是否继续
        continue_choice = input("\n按回车键继续，或输入 'q' 退出: ").strip().lower()
        if continue_choice in ['q', 'quit', 'exit', '退出']:
            print("\n👋 感谢使用，再见！")
            break

if __name__ == "__main__":
    print("🔧 正在初始化多功能 Tavily Agent...")
    print(f"📊 当前可用工具数量: {len(agent_tools)}")
    for i, tool in enumerate(agent_tools, 1):
        print(f"  {i}. {tool.name}: {tool.description}")
    
    asyncio.run(main()) 