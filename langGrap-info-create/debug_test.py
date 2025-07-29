#!/usr/bin/env python3
"""
调试脚本 - 测试Supabase连接和历史记录功能
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_supabase_connection():
    """测试Supabase连接"""
    print("🔍 测试Supabase连接...")
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ 环境变量缺失:")
            print(f"   SUPABASE_URL: {'✅' if supabase_url else '❌'}")
            print(f"   SUPABASE_ANON_KEY: {'✅' if supabase_key else '❌'}")
            return False
            
        print(f"📍 Supabase URL: {supabase_url}")
        print(f"🔑 API Key前6位: {supabase_key[:6]}...")
        
        # 创建客户端
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase客户端创建成功")
        
        # 测试连接 - 尝试查询auth.users表
        try:
            # 简单的连接测试
            result = supabase.table("prompt_history").select("*").limit(1).execute()
            print("✅ prompt_history表连接成功")
            print(f"   返回数据结构: {type(result.data)}")
            print(f"   数据条数: {len(result.data) if result.data else 0}")
            
        except Exception as table_error:
            print(f"❌ prompt_history表查询失败: {table_error}")
            print("   可能原因: 表不存在或权限不足")
            return False
            
        # 测试webpage_generations表
        try:
            result = supabase.table("webpage_generations").select("*").limit(1).execute()
            print("✅ webpage_generations表连接成功")
            print(f"   数据条数: {len(result.data) if result.data else 0}")
            
        except Exception as table_error:
            print(f"❌ webpage_generations表查询失败: {table_error}")
            
        return True
        
    except ImportError:
        print("❌ supabase库未安装")
        print("   请运行: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Supabase连接失败: {e}")
        return False

def test_auth_manager():
    """测试认证管理器"""
    print("\n🔍 测试认证管理器...")
    
    try:
        from auth_manager import get_auth_manager
        
        auth_manager = get_auth_manager()
        print("✅ AuthManager初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ AuthManager初始化失败: {e}")
        return False

def test_history_manager():
    """测试历史记录管理器"""
    print("\n🔍 测试历史记录管理器...")
    
    try:
        from history_manager import get_history_manager
        
        history_manager = get_history_manager()
        print("✅ HistoryManager初始化成功")
        
        # 测试获取历史记录 (使用正确的UUID格式)
        import uuid
        test_user_id = str(uuid.uuid4())  # 生成有效的UUID
        print(f"🆔 使用测试UUID: {test_user_id}")
        
        prompts = history_manager.get_user_prompt_history(test_user_id, limit=5)
        print(f"📝 测试获取提示词历史: {len(prompts)} 条记录")
        
        webpages = history_manager.get_user_webpage_generations(test_user_id, limit=5)
        print(f"🌐 测试获取网页生成历史: {len(webpages)} 条记录")
        
        # 测试实际用户数据查询
        print("\n🔍 检查实际数据库中的用户记录...")
        try:
            # 查询实际的用户记录
            all_prompts = history_manager.supabase.table("prompt_history").select("user_id, prompt, created_at").limit(5).execute()
            print(f"📊 数据库中总提示词记录: {len(all_prompts.data) if all_prompts.data else 0}")
            
            all_webpages = history_manager.supabase.table("webpage_generations").select("user_id, prompt, filename, created_at").limit(5).execute()
            print(f"🌐 数据库中总网页记录: {len(all_webpages.data) if all_webpages.data else 0}")
            
            if all_prompts.data:
                print("📝 最近的提示词记录:")
                for record in all_prompts.data[:3]:
                    print(f"   - 用户ID: {record['user_id']}")
                    print(f"     提示词: {record['prompt'][:50]}...")
                    print(f"     时间: {record['created_at']}")
                    
            if all_webpages.data:
                print("🌐 最近的网页记录:")
                for record in all_webpages.data[:3]:
                    print(f"   - 用户ID: {record['user_id']}")
                    print(f"     提示词: {record['prompt'][:50]}...")
                    print(f"     文件名: {record['filename']}")
                    
        except Exception as e:
            print(f"❌ 查询实际数据失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ HistoryManager初始化失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始调试Supabase历史记录功能")
    print("=" * 50)
    
    # 测试步骤
    tests = [
        ("Supabase连接", test_supabase_connection),
        ("认证管理器", test_auth_manager),
        ("历史记录管理器", test_history_manager),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试出错: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！历史记录功能应该可以正常工作")
    else:
        print("\n⚠️  部分测试失败，请检查:")
        print("   1. .env文件中的Supabase配置是否正确")
        print("   2. Supabase项目中的数据库表是否已创建")
        print("   3. 数据库权限策略是否正确设置")
        print("\n📖 参考: database_schema.sql 和 README_SUPABASE.md")

if __name__ == "__main__":
    main() 