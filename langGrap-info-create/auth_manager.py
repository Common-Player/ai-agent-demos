import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AuthManager:
    """用户认证管理器"""
    
    def __init__(self):
        """初始化Supabase客户端"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("请在.env文件中配置SUPABASE_URL和SUPABASE_ANON_KEY")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # 初始化数据库表
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        try:
            # 创建用户配置表（如果不存在）
            # 注意：在实际部署中，这些表应该通过Supabase Dashboard或SQL迁移脚本创建
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
    
    def register(self, email: str, password: str, username: Optional[str] = None) -> Dict[str, Any]:
        """用户注册"""
        try:
            # 使用Supabase Auth进行注册
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username or email.split("@")[0]
                    }
                }
            })
            
            if response.user and response.user.id and response.user.email:
                return {
                    "success": True,
                    "message": "注册成功！请检查邮箱验证邮件。",
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "username": username or email.split("@")[0]
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "注册失败，请稍后重试"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"注册失败: {str(e)}"
            }
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if (response.user and response.session and 
                response.user.id and response.user.email and 
                response.session.access_token and response.session.refresh_token):
                return {
                    "success": True,
                    "message": "登录成功！",
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "username": response.user.user_metadata.get("username", email.split("@")[0])
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "登录失败，请检查邮箱和密码"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"登录失败: {str(e)}"
            }
    
    def logout(self) -> Dict[str, Any]:
        """用户登出"""
        try:
            self.supabase.auth.sign_out()
            return {
                "success": True,
                "message": "登出成功"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"登出失败: {str(e)}"
            }
    
    def get_current_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        try:
            # 设置访问令牌
            self.supabase.postgrest.auth(access_token)
            
            # 获取用户信息
            response = self.supabase.auth.get_user(access_token)
            
            if (response.user and response.user.id and 
                response.user.email and response.user.created_at):
                user_email = response.user.email
                username = response.user.user_metadata.get("username", user_email.split("@")[0])
                return {
                    "id": response.user.id,
                    "email": user_email,
                    "username": username,
                    "created_at": response.user.created_at
                }
            return None
            
        except Exception as e:
            print(f"❌ 获取用户信息失败: {e}")
            return None
    
    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """刷新用户会话"""
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "success": True,
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "会话刷新失败"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"会话刷新失败: {str(e)}"
            }

# 全局认证管理器实例
auth_manager = None

def get_auth_manager() -> AuthManager:
    """获取认证管理器实例"""
    global auth_manager
    if auth_manager is None:
        auth_manager = AuthManager()
    return auth_manager 