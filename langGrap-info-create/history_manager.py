import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class HistoryManager:
    """用户历史记录管理器"""
    
    def __init__(self):
        """初始化Supabase客户端"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("请在.env文件中配置SUPABASE_URL和SUPABASE_ANON_KEY")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def save_prompt_history(self, user_id: str, prompt: str, response: str, 
                          prompt_type: str = "custom", model_type: str = "simple", access_token: str = None) -> Dict[str, Any]:
        """保存用户提示词历史记录"""
        try:
            data = {
                "user_id": user_id,
                "prompt": prompt,
                "response": response,
                "prompt_type": prompt_type,
                "model_type": model_type,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # 如果提供了访问令牌，设置认证头
            if access_token:
                self.supabase.postgrest.auth(access_token)
            
            result = self.supabase.table("prompt_history").insert(data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "message": "历史记录保存成功",
                    "record_id": result.data[0]["id"]
                }
            else:
                return {
                    "success": False,
                    "message": "历史记录保存失败"
                }
                
        except Exception as e:
            print(f"❌ 保存历史记录失败: {e}")
            return {
                "success": False,
                "message": f"保存失败: {str(e)}"
            }
    
    def save_webpage_generation(self, user_id: str, prompt: str, html_content: str, 
                              filename: str, design_type: str = "ai_design", access_token: str = None) -> Dict[str, Any]:
        """保存用户网页生成记录"""
        try:
            data = {
                "user_id": user_id,
                "prompt": prompt,
                "html_content": html_content,
                "filename": filename,
                "design_type": design_type,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # 如果提供了访问令牌，设置认证头
            if access_token:
                self.supabase.postgrest.auth(access_token)
            
            result = self.supabase.table("webpage_generations").insert(data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "message": "网页生成记录保存成功",
                    "record_id": result.data[0]["id"]
                }
            else:
                return {
                    "success": False,
                    "message": "网页生成记录保存失败"
                }
                
        except Exception as e:
            print(f"❌ 保存网页生成记录失败: {e}")
            return {
                "success": False,
                "message": f"保存失败: {str(e)}"
            }
    
    def get_user_prompt_history(self, user_id: str, limit: int = 50, 
                              prompt_type: Optional[str] = None, access_token: str = None) -> List[Dict[str, Any]]:
        """获取用户提示词历史记录"""
        try:
            # 如果提供了访问令牌，设置认证头
            if access_token:
                self.supabase.postgrest.auth(access_token)
                
            query = self.supabase.table("prompt_history").select("*").eq("user_id", user_id)
            
            if prompt_type:
                query = query.eq("prompt_type", prompt_type)
            
            result = query.order("created_at", desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ 获取历史记录失败: {e}")
            return []
    
    def get_user_webpage_generations(self, user_id: str, limit: int = 20, access_token: str = None) -> List[Dict[str, Any]]:
        """获取用户网页生成历史记录"""
        try:
            # 如果提供了访问令牌，设置认证头
            if access_token:
                self.supabase.postgrest.auth(access_token)
                
            result = self.supabase.table("webpage_generations").select("*").eq(
                "user_id", user_id
            ).order("created_at", desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ 获取网页生成记录失败: {e}")
            return []
    
    def delete_prompt_history(self, user_id: str, record_id: int) -> Dict[str, Any]:
        """删除用户指定的历史记录"""
        try:
            result = self.supabase.table("prompt_history").delete().eq(
                "id", record_id
            ).eq("user_id", user_id).execute()
            
            if result.data:
                return {
                    "success": True,
                    "message": "历史记录删除成功"
                }
            else:
                return {
                    "success": False,
                    "message": "历史记录删除失败或记录不存在"
                }
                
        except Exception as e:
            print(f"❌ 删除历史记录失败: {e}")
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }
    
    def delete_webpage_generation(self, user_id: str, record_id: int) -> Dict[str, Any]:
        """删除用户指定的网页生成记录"""
        try:
            result = self.supabase.table("webpage_generations").delete().eq(
                "id", record_id
            ).eq("user_id", user_id).execute()
            
            if result.data:
                return {
                    "success": True,
                    "message": "网页生成记录删除成功"
                }
            else:
                return {
                    "success": False,
                    "message": "网页生成记录删除失败或记录不存在"
                }
                
        except Exception as e:
            print(f"❌ 删除网页生成记录失败: {e}")
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户使用统计信息"""
        try:
            # 获取提示词历史统计
            prompt_stats = self.supabase.table("prompt_history").select(
                "prompt_type", count="exact"
            ).eq("user_id", user_id).execute()
            
            # 获取网页生成统计
            webpage_stats = self.supabase.table("webpage_generations").select(
                "design_type", count="exact"
            ).eq("user_id", user_id).execute()
            
            # 统计不同类型的数量
            prompt_type_counts = {}
            if prompt_stats.data:
                for record in prompt_stats.data:
                    prompt_type = record.get("prompt_type", "unknown")
                    prompt_type_counts[prompt_type] = prompt_type_counts.get(prompt_type, 0) + 1
            
            webpage_type_counts = {}
            if webpage_stats.data:
                for record in webpage_stats.data:
                    design_type = record.get("design_type", "unknown")
                    webpage_type_counts[design_type] = webpage_type_counts.get(design_type, 0) + 1
            
            return {
                "total_prompts": len(prompt_stats.data) if prompt_stats.data else 0,
                "total_webpages": len(webpage_stats.data) if webpage_stats.data else 0,
                "prompt_type_breakdown": prompt_type_counts,
                "webpage_type_breakdown": webpage_type_counts
            }
            
        except Exception as e:
            print(f"❌ 获取用户统计失败: {e}")
            return {
                "total_prompts": 0,
                "total_webpages": 0,
                "prompt_type_breakdown": {},
                "webpage_type_breakdown": {}
            }

# 全局历史记录管理器实例
history_manager = None

def get_history_manager() -> HistoryManager:
    """获取历史记录管理器实例"""
    global history_manager
    if history_manager is None:
        history_manager = HistoryManager()
    return history_manager 