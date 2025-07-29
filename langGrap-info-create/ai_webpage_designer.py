import os
import re
from typing import Dict, Any
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

# 需要导入AI模型来进行深度设计
def get_agent_model():
    """获取AI模型实例"""
    # 直接使用gemini模型
    from web_agent import create_gemini_model
    return create_gemini_model()

@tool
def ai_webpage_designer(description: str) -> str:
    """AI网页设计师 - 让AI模型深度重新设计整个网页模板
    
    Args:
        description: 用户对网页的详细描述和需求
    """
    print(f"🎨 AI网页设计师正在工作: {description[:50]}...")
    
    try:
        # 读取demo.html作为参考模板
        demo_path = os.path.join(os.path.dirname(__file__), 'demo.html')
        if not os.path.exists(demo_path):
            return "错误: 找不到demo.html模板文件"
            
        with open(demo_path, 'r', encoding='utf-8') as f:
            base_template = f.read()
        
        # 让AI模型深度分析和重新设计
        ai_model = get_agent_model()
        
        # 构建给AI的详细prompt
        design_prompt = f"""
你是一位专业的网页设计师和前端开发专家。用户要求你设计一个网页，需求如下：

用户需求: {description}

我会给你一个参考模板，但请不要仅仅修改样式，而是要根据用户需求进行深度的重新设计：

1. 可以重新安排布局结构（如改变网格布局、卡片排列等）
2. 可以修改HTML结构（添加新元素、重组现有结构等）
3. 可以创造性地设计CSS样式
4. 可以增加新的交互效果和动画
5. 可以调整响应式设计方案

但必须保证：
- 包含以下7个功能区域：天气查询、今日新闻、网页浏览、问题研究、计算器、当前时间、文件内容展示
- 保持基本的功能性JavaScript代码
- 确保网页的可访问性和用户体验

参考模板如下：
{base_template}

请生成完整的HTML代码，要有创意和个性化，充分体现用户需求的特色。
请直接返回完整的HTML代码，不需要其他解释。
"""

        print("🤖 AI模型正在深度分析和重新设计...")
        
        # 调用AI模型进行深度设计
        config = RunnableConfig(configurable={"thread_id": f"designer_{hash(description)}"})
        
        result = ai_model.invoke(
            [HumanMessage(content=design_prompt)],
            config=config
        )
        
        # 提取AI生成的HTML代码
        ai_generated_html = result.content
        
        # 确保内容是字符串格式
        if isinstance(ai_generated_html, list):
            # 如果是列表，提取文本内容
            html_text = ""
            for item in ai_generated_html:
                if isinstance(item, str):
                    html_text += item
                elif hasattr(item, 'text'):
                    html_text += str(getattr(item, 'text', ''))
                elif isinstance(item, dict):
                    # 安全地访问字典内容
                    text_content = item.get('text', '')
                    html_text += str(text_content)
                else:
                    html_text += str(item)
            ai_generated_html = html_text
        elif not isinstance(ai_generated_html, str):
            ai_generated_html = str(ai_generated_html)
        
        # 清理和验证生成的HTML
        cleaned_html = clean_and_validate_html(ai_generated_html, description)
        
        # 保存生成的网页
        output_filename = f"ai_designed_webpage_{hash(description) % 10000}.html"
        output_path = os.path.join(os.path.dirname(__file__), 'generated_pages', output_filename)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_html)
        
        print(f"✅ AI深度设计完成: {output_filename}")
        
        return f"""🎨 AI网页设计师作品完成！

📄 文件名: {output_filename}
📁 保存路径: generated_pages/{output_filename}
🌐 访问地址: http://localhost:8080/generated/{output_filename}

🤖 AI设计特色:
- 基于您的需求进行深度重新设计
- 不是简单的样式修改，而是结构性的创新
- 充分体现了"{description[:50]}..."的设计理念
- 保持了所有7个功能区域的完整性

包含功能:
🌤️ 天气查询 | 📰 今日新闻 | 🌐 网页浏览 | 🔬 问题研究
🧮 智能计算 | ⏰ 时间信息 | 📁 文件管理

🎉 这是AI真正的创造性设计作品！"""
        
    except Exception as e:
        error_msg = f"AI网页设计失败: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

def clean_and_validate_html(html_content: str, description: str) -> str:
    """清理和验证AI生成的HTML代码"""
    
    # 如果AI返回的内容包含markdown代码块，提取HTML部分
    if '```html' in html_content:
        # 提取```html和```之间的内容
        html_match = re.search(r'```html\s*\n(.*?)\n```', html_content, re.DOTALL | re.IGNORECASE)
        if html_match:
            html_content = html_match.group(1)
    elif '```' in html_content:
        # 提取```和```之间的内容
        html_match = re.search(r'```\s*\n(.*?)\n```', html_content, re.DOTALL)
        if html_match:
            html_content = html_match.group(1)
    
    # 确保HTML有基本结构
    if '<!DOCTYPE html>' not in html_content and '<html' not in html_content:
        # 如果AI只返回了部分代码，包装在完整的HTML结构中
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI设计网页 - {description[:30]}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    # 确保包含必要的功能集成代码
    if 'agentAPI' not in html_content:
        integration_script = generate_advanced_integration_script()
        # 在</body>前插入集成脚本
        html_content = html_content.replace('</body>', f'{integration_script}\n</body>')
    
    return html_content

def generate_advanced_integration_script() -> str:
    """生成高级功能集成脚本"""
    return """
<script>
// AI网页设计师 - 高级功能集成
// 检查是否已经存在aiAgentAPI，如果不存在才创建
if (!window.aiAgentAPI) {
    window.aiAgentAPI = {
        baseURL: 'http://localhost:8080',
        
        // 通用API调用函数
        async callAPI(endpoint, input) {
            try {
                const response = await fetch(`${this.baseURL}/api/preset/${endpoint}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        input: input, 
                        thread_id: 'ai_webpage_' + Date.now() 
                    })
                });
                const data = await response.json();
                return data.success ? data.response : '查询失败: ' + (data.error || '未知错误');
            } catch (error) {
                return '网络错误: ' + error.message;
            }
        },
        
        // 各种功能的便捷方法
        weather: (city = '北京') => window.aiAgentAPI.callAPI('weather', city),
        news: (topic = '今日头条') => window.aiAgentAPI.callAPI('news', topic),
        extract: (url) => window.aiAgentAPI.callAPI('extract', url),
        research: (topic) => window.aiAgentAPI.callAPI('research', topic),
        calculate: (expr) => window.aiAgentAPI.callAPI('calculate', expr),
        datetime: (query = 'current') => window.aiAgentAPI.callAPI('datetime', query),
        file: (operation) => window.aiAgentAPI.callAPI('file', operation),
        system: (type = 'all') => window.aiAgentAPI.callAPI('system', type)
    };
    console.log('🔧 创建了简化版 aiAgentAPI');
} else {
    console.log('✅ 检测到已存在完整版 aiAgentAPI，跳过重复创建');
}

// 智能结果显示函数 - 尝试使用现有的JSON处理逻辑
function showSmartResult(element, result) {
    // 检查是否存在完整的JSON处理函数
    if (typeof window.parseAndShowResult === 'function') {
        // 为element创建临时ID（如果没有）
        if (!element.id) {
            element.id = 'temp_result_' + Date.now();
        }
        console.log('🎯 使用完整版JSON处理逻辑显示结果');
        window.parseAndShowResult(element.id, result);
    } else if (typeof window.showResult === 'function') {
        // 使用showResult函数
        if (!element.id) {
            element.id = 'temp_result_' + Date.now();
        }
        console.log('📋 使用showResult函数显示结果');
        window.showResult(element.id, result);
    } else {
        // 回退到简单显示
        console.log('📝 使用简单文本显示结果');
        element.innerHTML = `<pre style="white-space: pre-wrap; font-size: 0.9em; line-height: 1.4; max-height: 300px; overflow-y: auto;">${result}</pre>`;
    }
}

// 自动为所有功能区域添加点击事件
document.addEventListener('DOMContentLoaded', function() {
    // 智能识别功能区域
    const functionalElements = document.querySelectorAll(
        '[class*="weather"], [class*="news"], [class*="browser"], [class*="research"], ' +
        '[class*="calculator"], [class*="time"], [class*="file"], [class*="system"], ' +
        '[data-function], .dashboard-card, .card, .panel, .widget'
    );
    
    functionalElements.forEach(element => {
        // 避免重复绑定
        if (element.hasAttribute('data-ai-bound')) return;
        element.setAttribute('data-ai-bound', 'true');
        
        element.style.cursor = 'pointer';
        
        // 为输入框阻止事件冒泡，这样点击输入框不会触发AI请求
        const inputs = element.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.style.cursor = 'text';
            input.addEventListener('click', function(event) {
                event.stopPropagation(); // 阻止事件冒泡
                console.log('📝 输入框可正常编辑');
            });
        });
        
        element.addEventListener('click', async function() {
            // 智能识别功能类型
            const text = this.textContent || this.className || '';
            const classList = Array.from(this.classList).join(' ');
            
            let result = '';
            let loadingElement = this.querySelector('.card-content, .content, .body, .result-container') || this;
            
            // 显示加载状态
            const originalContent = loadingElement.innerHTML;
            loadingElement.innerHTML = '<div class="loading">正在处理中...</div>';
            
            try {
                if (text.includes('天气') || classList.includes('weather')) {
                    const cityInput = this.querySelector('input[type="text"]');
                    const city = cityInput ? cityInput.value.trim() || '北京' : '北京';
                    result = await window.aiAgentAPI.weather(city);
                } else if (text.includes('新闻') || classList.includes('news')) {
                    const topicInput = this.querySelector('input[type="text"]');
                    const topic = topicInput ? topicInput.value.trim() || '科技新闻' : '科技新闻';
                    result = await window.aiAgentAPI.news(topic);
                } else if (text.includes('网页') || text.includes('浏览') || classList.includes('browser')) {
                    const urlInput = this.querySelector('input[type="text"], input[type="url"]');
                    if (urlInput && urlInput.value.trim()) {
                        result = await window.aiAgentAPI.extract(urlInput.value.trim());
                    } else {
                        result = '请在输入框中输入URL，然后点击卡片空白区域触发提取\\n示例: https://www.example.com';
                    }
                } else if (text.includes('研究') || text.includes('分析') || classList.includes('research')) {
                    const researchInput = this.querySelector('input[type="text"], textarea');
                    const topic = researchInput ? researchInput.value.trim() || '人工智能发展趋势' : '人工智能发展趋势';
                    result = await window.aiAgentAPI.research(topic);
                } else if (text.includes('计算') || classList.includes('calculator')) {
                    const calcInput = this.querySelector('input[type="text"]');
                    const expr = calcInput ? calcInput.value.trim() || 'sqrt(16) + log(10)' : 'sqrt(16) + log(10)';
                    result = await window.aiAgentAPI.calculate(expr);
                } else if (text.includes('时间') || classList.includes('time')) {
                    result = await window.aiAgentAPI.datetime('current');
                } else if (text.includes('文件') || classList.includes('file')) {
                    const fileInput = this.querySelector('input[type="text"]');
                    const operation = fileInput ? fileInput.value.trim() || 'list:.' : 'list:.';
                    result = await window.aiAgentAPI.file(operation);
                } else if (text.includes('系统') || classList.includes('system')) {
                    result = await window.aiAgentAPI.system('memory');
                } else {
                    result = '✨ AI功能区域\\n输入框可正常编辑，点击卡片其他区域触发AI请求';
                }
                
                // 使用智能结果显示
                showSmartResult(loadingElement, result);
                
            } catch (error) {
                loadingElement.innerHTML = `<div style="color: #e74c3c;">❌ 错误: ${error.message}</div>`;
            }
        });
    });
    
    console.log('🎨 AI网页设计师功能集成完成，找到', functionalElements.length, '个功能区域');
    console.log('💡 提示：输入框可正常编辑，点击卡片其他区域触发AI请求');
});
</script>"""

def get_ai_webpage_designer_tool():
    """获取AI网页设计师工具"""
    return ai_webpage_designer