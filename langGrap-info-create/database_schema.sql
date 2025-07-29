-- Supabase数据库表结构
-- 请在Supabase Dashboard的SQL编辑器中执行这些SQL语句

-- 用户提示词历史记录表
CREATE TABLE IF NOT EXISTS prompt_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    prompt_type VARCHAR(50) DEFAULT 'custom',
    model_type VARCHAR(50) DEFAULT 'simple',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户网页生成记录表
CREATE TABLE IF NOT EXISTS webpage_generations (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    html_content TEXT,
    filename VARCHAR(255),
    design_type VARCHAR(50) DEFAULT 'ai_design',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_prompt_history_user_id ON prompt_history(user_id);
CREATE INDEX IF NOT EXISTS idx_prompt_history_created_at ON prompt_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prompt_history_type ON prompt_history(prompt_type);

CREATE INDEX IF NOT EXISTS idx_webpage_generations_user_id ON webpage_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_webpage_generations_created_at ON webpage_generations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_webpage_generations_type ON webpage_generations(design_type);

-- 设置行级安全策略 (RLS)
ALTER TABLE prompt_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE webpage_generations ENABLE ROW LEVEL SECURITY;

-- 用户只能访问自己的记录
CREATE POLICY "Users can only access their own prompt history" ON prompt_history
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own webpage generations" ON webpage_generations
    FOR ALL USING (auth.uid() = user_id);

-- 给经过身份验证的用户插入权限
CREATE POLICY "Authenticated users can insert prompt history" ON prompt_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Authenticated users can insert webpage generations" ON webpage_generations
    FOR INSERT WITH CHECK (auth.uid() = user_id); 