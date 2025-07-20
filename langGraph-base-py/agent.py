import os
import asyncio
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# 加载环境变量
load_dotenv()

# 定义 tools - 直接使用 TavilySearch 工具
agent_tools = [
    TavilySearch(max_results=3)
]

# 定义 llm
agent_model = ChatAnthropic(
    model='claude-sonnet-4-20250514',
    temperature=0.1,
    max_tokens=2000
)

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

async def main():
    """主函数"""
    print("=== LangGraph 天气问答 Agent (Python 版) ===\n")
    
    # 获取用户输入
    location = input("你想知道哪里的天气？\n").strip()
    if not location:
        print("未输入地点，程序结束。")
        return
    
    stream_choice = input("是否需要流式输出？（输入'是'或直接回车为流式，否则为非流式）\n").strip()
    
    prompt = f"{location}天气怎么样"
    thread_id = "1"
    
    print(f"\n正在查询 {location} 的天气信息...\n")
    
    if not stream_choice or stream_choice == "是":
        # 流式输出
        print("--- 流式输出 ---")
        await run_streaming_agent(prompt, thread_id)
    else:
        # 非流式输出
        print("--- 非流式输出 ---")
        await run_non_streaming_agent(prompt, thread_id)
    
    print("\n\n查询完成！")

if __name__ == "__main__":
    asyncio.run(main()) 