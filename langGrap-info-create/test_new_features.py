#!/usr/bin/env python3
"""
新功能测试脚本
用于测试数学计算、时间查询、文件操作和系统信息功能
"""

from extended_tools import calculator, get_datetime, file_operations, get_system_info

def test_calculator():
    """测试数学计算功能"""
    print("🧮 测试数学计算功能...")
    test_cases = [
        "2 + 3 * 4",
        "sqrt(16)",
        "sin(pi/2)",
        "log10(100)",
        "2^3",  # 测试 ^ 转换为 **
        "2x + 3",  # 测试 2x 转换为 2*x (这个可能会失败)
    ]
    
    for expr in test_cases:
        try:
            result = calculator(expr)
            print(f"  ✅ {expr} → {result}")
        except Exception as e:
            print(f"  ❌ {expr} → 错误: {e}")
    print()

def test_datetime():
    """测试时间查询功能"""
    print("⏰ 测试时间查询功能...")
    test_cases = [
        "current",
        "format",
        "now"
    ]
    
    for query in test_cases:
        try:
            result = get_datetime(query)
            print(f"  ✅ {query}:")
            print(f"    {result[:100]}...")
        except Exception as e:
            print(f"  ❌ {query} → 错误: {e}")
    print()

def test_file_operations():
    """测试文件操作功能"""
    print("📁 测试文件操作功能...")
    
    # 测试写入
    try:
        result = file_operations("write:test_file.txt:这是测试内容\\n第二行内容")
        print(f"  ✅ 写入文件: {result}")
    except Exception as e:
        print(f"  ❌ 写入文件错误: {e}")
    
    # 测试读取
    try:
        result = file_operations("read:test_file.txt")
        print(f"  ✅ 读取文件: {result[:100]}...")
    except Exception as e:
        print(f"  ❌ 读取文件错误: {e}")
    
    # 测试列出目录
    try:
        result = file_operations("list:.")
        print(f"  ✅ 列出目录: {result[:200]}...")
    except Exception as e:
        print(f"  ❌ 列出目录错误: {e}")
    
    # 清理测试文件
    try:
        import os
        if os.path.exists("test_file.txt"):
            os.remove("test_file.txt")
            print("  🗑️ 已清理测试文件")
    except:
        pass
    print()

def test_system_info():
    """测试系统信息功能"""
    print("💻 测试系统信息功能...")
    test_cases = [
        "os",
        "memory", 
        "cpu",
        "python",
        "all"
    ]
    
    for info_type in test_cases:
        try:
            result = get_system_info(info_type)
            print(f"  ✅ {info_type}:")
            print(f"    {result[:150]}...")
        except Exception as e:
            print(f"  ❌ {info_type} → 错误: {e}")
    print()

def main():
    print("🧪 开始测试新增功能...")
    print("=" * 60)
    
    test_calculator()
    test_datetime()
    test_file_operations()
    test_system_info()
    
    print("🎉 测试完成！")

if __name__ == "__main__":
    main() 