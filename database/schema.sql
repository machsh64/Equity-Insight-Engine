-- Equity Insight Engine 数据库Schema
-- PostgreSQL

-- 创建公司类型枚举
CREATE TYPE company_type AS ENUM (
    'TECH_PLATFORM',
    'TECH_MATURE',
    'PHARMA_INNOVATION',
    'PHARMA_MATURE',
    'FINANCIAL',
    'MANUFACTURING'
);

-- 公司基础信息
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    company_type company_type NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 季度财务快照
CREATE TABLE quarters (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    quarter TEXT NOT NULL,      -- 格式: "2024-Q3"
    pe DECIMAL,
    pb DECIMAL,
    ps DECIMAL,
    roe DECIMAL,                -- %
    roic DECIMAL,               -- %
    wacc DECIMAL,               -- %
    revenue_yoy DECIMAL,        -- %
    gross_margin DECIMAL,       -- %
    fcf_margin DECIMAL,         -- %
    capex_ratio DECIMAL,        -- CapEx / Revenue %
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, quarter)
);

-- 系统分析结果（确定性计算）
CREATE TABLE system_analyses (
    id SERIAL PRIMARY KEY,
    quarter_id INTEGER REFERENCES quarters(id) ON DELETE CASCADE,
    quality_score NUMERIC(5,2),
    valuation_score NUMERIC(5,2),
    trend_score NUMERIC(5,2),
    labels TEXT[],              -- e.g. {'高质量', '高估值'}
    system_summary TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(quarter_id)
);

-- 单季度 AI 分析结果（持久化）
CREATE TABLE quarter_ai_analyses (
    id SERIAL PRIMARY KEY,
    quarter_id INTEGER REFERENCES quarters(id) ON DELETE CASCADE,
    analysis_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(quarter_id)
);

-- 首页综合 AI 分析（基于最近 4 个季度）
CREATE TABLE company_comprehensive_ai (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    analysis_text TEXT,         -- 150 字以内综合判断
    main_label TEXT,
    risk_label TEXT,
    based_quarters TEXT[],      -- 记录用到的 quarter
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id)
);

-- 创建索引以优化查询性能
CREATE INDEX idx_quarters_company_id ON quarters(company_id);
CREATE INDEX idx_quarters_quarter ON quarters(quarter DESC);
CREATE INDEX idx_system_analyses_quarter_id ON system_analyses(quarter_id);
CREATE INDEX idx_quarter_ai_analyses_quarter_id ON quarter_ai_analyses(quarter_id);

