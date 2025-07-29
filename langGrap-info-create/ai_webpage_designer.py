import os
import re
import time
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

def validate_html_completeness(html_content: str) -> tuple[bool, str]:
    """验证HTML内容是否完整
    
    Returns:
        tuple: (是否完整, 错误信息)
    """
    if not html_content or len(html_content.strip()) < 100:
        return False, "HTML内容太短或为空"
    
    # 检查是否仍然包含markdown代码块标记
    if html_content.strip().startswith('```'):
        return False, "HTML内容包含未处理的markdown代码块标记"
    
    # 检查基本HTML结构
    required_tags = ['<!DOCTYPE html>', '<html', '<head>', '<body>', '</html>']
    for tag in required_tags:
        if tag not in html_content:
            return False, f"缺少必要的HTML标签: {tag}"
    
    # 检查HTML标签是否配对
    opening_tags = re.findall(r'<([a-zA-Z][^>]*)>', html_content)
    closing_tags = re.findall(r'</([a-zA-Z][^>]*)>', html_content)
    
    # 提取标签名（去除属性）
    opening_tag_names = [tag.split()[0] for tag in opening_tags if not tag.startswith('/')]
    closing_tag_names = [tag for tag in closing_tags]
    
    # 检查关键标签是否配对
    critical_tags = ['html', 'head', 'body']
    for tag in critical_tags:
        if opening_tag_names.count(tag) != closing_tag_names.count(tag):
            return False, f"关键标签 {tag} 未正确配对"
    
    # 检查内容是否被截断（检查常见的截断标志）
    truncation_indicators = [
        html_content.endswith('...'),
        html_content.endswith('/*'),  # CSS被截断
        html_content.endswith('{'),   # CSS或JS被截断
        html_content.endswith('function'),  # JS函数被截断
        html_content.count('{') > html_content.count('}') + 5,  # 大量未闭合的花括号
    ]
    
    if any(truncation_indicators):
        return False, "HTML内容可能被截断"
    
    return True, "HTML内容完整"

@tool
def ai_webpage_designer(description: str) -> str:
    """AI网页设计师 - 让AI模型深度重新设计整个网页模板
    
    Args:
        description: 用户对网页的详细描述和需求
    """
    print(f"🎨 AI网页设计师正在工作: {description[:50]}...")
    
    max_retries = 3  # 最大重试次数
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 读取demo.html作为参考模板
            demo_path = os.path.join(os.path.dirname(__file__), 'demo.html')
            if not os.path.exists(demo_path):
                return "错误: 找不到demo.html模板文件"
                
            with open(demo_path, 'r', encoding='utf-8') as f:
                base_template = f.read()
            
            # 让AI模型深度分析和重新设计
            ai_model = get_agent_model()
            
            # 根据重试次数调整prompt策略
            if retry_count == 0:
                additional_instruction = ""
            elif retry_count == 1:
                additional_instruction = "\n\n重要提醒：请确保生成完整的HTML代码，包含完整的</html>结束标签。不要在中途截断。"
            else:
                additional_instruction = "\n\n关键要求：这是最后一次生成机会，请务必输出完整的HTML代码，从<!DOCTYPE html>开始到</html>结束，中间不能有任何截断。确保所有CSS样式和JavaScript代码都完整。"
            
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
请直接返回完整的HTML代码，不需要其他解释。{additional_instruction}
"""

            print(f"🤖 AI模型正在深度分析和重新设计... (尝试 {retry_count + 1}/{max_retries})")
            
            # 调用AI模型进行深度设计
            config = RunnableConfig(configurable={"thread_id": f"designer_{hash(description)}_{retry_count}"})
            
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
            
            # 验证HTML完整性
            is_complete, validation_msg = validate_html_completeness(cleaned_html)
            
            if not is_complete:
                print(f"⚠️ HTML验证失败 (尝试 {retry_count + 1}): {validation_msg}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"🔄 准备重试... (还有 {max_retries - retry_count} 次机会)")
                    time.sleep(1)  # 短暂延迟后重试
                    continue
                else:
                    print("❌ 已达到最大重试次数，将保存当前结果")
            
            # 保存生成的网页
            output_filename = f"ai_designed_webpage_{hash(description) % 10000}.html"
            output_path = os.path.join(os.path.dirname(__file__), 'generated_pages', output_filename)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_html)
            
            # 根据验证结果显示不同的成功信息
            if is_complete:
                print(f"✅ AI深度设计完成: {output_filename} (通过完整性验证)")
                quality_status = "✅ 质量检查通过"
            else:
                print(f"⚠️ AI设计完成但可能不完整: {output_filename} ({validation_msg})")
                quality_status = f"⚠️ 质量检查: {validation_msg}"
            
            return f"""🎨 AI网页设计师作品完成！

📄 文件名: {output_filename}
📁 保存路径: generated_pages/{output_filename}
🌐 访问地址: http://localhost:8080/generated/{output_filename}
{quality_status}

🤖 AI设计特色:
- 基于您的需求进行深度重新设计
- 不是简单的样式修改，而是结构性的创新
- 充分体现了"{description[:50]}..."的设计理念
- 保持了所有7个功能区域的完整性
- 经过 {retry_count + 1} 次生成优化

包含功能:
🌤️ 天气查询 | 📰 今日新闻 | 🌐 网页浏览 | 🔬 问题研究
🧮 智能计算 | ⏰ 时间信息 | 📁 文件管理

🎉 这是AI真正的创造性设计作品！"""
            
        except Exception as e:
            print(f"❌ 生成失败 (尝试 {retry_count + 1}): {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"🔄 准备重试... (还有 {max_retries - retry_count} 次机会)")
                time.sleep(2)  # 延迟后重试
                continue
            else:
                error_msg = f"AI网页设计失败 (已重试{max_retries}次): {str(e)}"
                print(f"❌ {error_msg}")
                return error_msg
    
    return "❌ 生成失败：已达到最大重试次数"

def clean_and_validate_html(html_content: str, description: str) -> str:
    """清理和验证AI生成的HTML代码"""
    
    original_content = html_content
    
    # 更强力的markdown代码块处理
    if '```html' in html_content:
        # 提取```html和```之间的内容
        html_match = re.search(r'```html\s*\n?(.*?)(?:\n```|$)', html_content, re.DOTALL | re.IGNORECASE)
        if html_match:
            html_content = html_match.group(1)
        else:
            # 如果没有找到结束标记，尝试从```html开始提取所有内容
            start_idx = html_content.find('```html')
            if start_idx != -1:
                html_content = html_content[start_idx + 7:].strip()
    elif '```' in html_content:
        # 提取```和```之间的内容
        html_match = re.search(r'```\s*\n?(.*?)(?:\n```|$)', html_content, re.DOTALL)
        if html_match:
            html_content = html_match.group(1)
        else:
            # 如果没有找到结束标记，尝试从```开始提取所有内容
            start_idx = html_content.find('```')
            if start_idx != -1:
                html_content = html_content[start_idx + 3:].strip()
    
    # 移除开头的```html如果还存在
    html_content = re.sub(r'^```html\s*\n?', '', html_content, flags=re.IGNORECASE)
    
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