# Equity Insight Engine (EIE)

一个以「财务质量 + 估值 + 趋势 + AI 解读」为核心的长期股票观测与潜力筛选系统。

## 系统特点

- **结构化记录**：统一、可量化的参数体系，减少主观情绪干扰
- **确定性分析**：系统分析引擎基于明确的规则进行计算
- **AI 解读**：提供长期视角的深度解读，帮助理解财务变化
- **类型化分析**：针对不同公司类型（科技平台、成熟科技、创新药等）采用不同的分析模型

## 系统边界

❗ **重要声明**：本系统严格遵守以下边界：

- 绝不输出 Buy / Sell / Hold 等交易建议
- 绝不输出目标价或预期回报率
- 所有标签、得分、AI 分析仅用于描述当前状态、区间、趋势、风险
- 系统仅提供结构化信息与客观解读，帮助用户自行判断
- 用户需自行承担所有投资决策责任

## 技术栈

### 后端
- **框架**: FastAPI (Python)
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy
- **AI服务**: OpenAI API (可扩展支持其他LLM)

### 前端
- **框架**: Next.js 14 (React)
- **样式**: Tailwind CSS
- **类型**: TypeScript

## 快速开始

### 前置要求

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+

### 1. 数据库设置

```bash
# 创建数据库
createdb equity_insight_engine

# 执行Schema
psql -d equity_insight_engine -f database/schema.sql
```

### 2. 后端设置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，设置数据库连接和API密钥
# 主要配置项：
# - DATABASE_URL: 数据库连接字符串
# - AI_SERVICE_URL: AI服务URL（可选，支持自定义AI服务）
# - AI_SERVICE_MODEL: AI模型名称（默认: gpt-4）
# - AI_SERVICE_API_KEY: AI服务API Key

# 运行后端
uvicorn main:app --reload --host 0.0.0.0 --port 8000
或
python run.py
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

访问 http://localhost:3000 查看应用。

## 项目结构

```
Equity-Insight-Engine/
├── backend/                 # 后端代码
│   ├── main.py             # FastAPI主应用
│   ├── models.py           # 数据库模型
│   ├── schemas.py          # Pydantic模型
│   ├── crud.py             # CRUD操作
│   ├── database.py         # 数据库连接
│   ├── config.py           # 配置
│   ├── system_analysis_engine.py  # 系统分析引擎
│   ├── ai_prompt_generator.py     # AI Prompt生成器
│   └── ai_service.py       # AI服务
├── frontend/               # 前端代码
│   ├── app/               # Next.js App Router
│   ├── components/        # React组件
│   └── lib/               # 工具函数和类型
├── database/              # 数据库相关
│   └── schema.sql         # 数据库Schema
└── README.md
```

## API文档

后端运行后，访问 http://localhost:8000/docs 查看Swagger API文档。

## 使用说明

1. **添加公司**：在首页点击"添加股票"，输入ticker、公司名称和公司类型
2. **添加季度数据**：进入公司详情页，点击"新增季度"，输入财务数据
3. **查看分析**：系统会自动计算系统分析结果并生成AI分析
4. **综合判断**：当有4个或更多季度数据时，系统会生成综合AI分析
5. **季度数据获取**: 季度数据获取可以通过grok等模型官网拉取检索，参照提示词如下
```txt
你是一个专业的金融数据检索助手，请基于公开、可信的数据来源
（如公司 10-Q / 10-K 财报、Macrotrends、TIKR、Gurufocus、SeekingAlpha 等）
为我检索并计算以下数据。

【公司信息】
- 公司名称：{公司名称}
- 股票代码：{股票代码}
- 财务季度：{年份 + 季度}（例如：2025 Q4）

【必须遵循的统一口径规则】
1. 所有估值类指标（PE / PB / PS）使用“该季度对应时间点的 TTM 数据”
2. 毛利率、自由现金流率、CapEx/收入 均使用 TTM（最近 12 个月）
3. 收入同比（YoY）必须为“季度同比”，即与去年同季度比较
4. 若某项数据无法从可靠来源获得，请返回 null，不得估算或编造
5. 所有百分比类指标请以“百分比数值”返回（例如 73.41，而不是 0.7341）

【需要返回的数据字段】

一、估值指标（TTM）
- PE（市盈率）
- PB（市净率）
- PS（市销率）

二、盈利与资本效率
- ROE（TTM）
- ROIC（TTM）
- WACC（最近一期可得估算值）

三、增长与经营质量
- 收入同比 YoY（%）（该季度 vs 去年同季度）
- 毛利率（TTM，%）
- 自由现金流率（TTM，%）

四、资本投入
- CapEx / 收入（TTM，%）

【计算规则说明】
- 自由现金流率 = (经营现金流 - CapEx) / 收入
- CapEx 数据来源于现金流量表中的 Capital Expenditures（取绝对值）
- 若来源直接提供该比率，可直接使用，但需注明来源

【输出格式要求】
请以 JSON 格式返回，字段名严格如下，不得新增字段：

{
  "pe": number | null,
  "pb": number | null,
  "ps": number | null,
  "roe": number | null,
  "roic": number | null,
  "wacc": number | null,
  "revenue_yoy": number | null,
  "gross_margin": number | null,
  "fcf_margin": number | null,
  "capex_to_revenue": number | null,
  "data_sources": {
    "pe_pb_ps": "来源说明",
    "roe_roic": "来源说明",
    "wacc": "来源说明",
    "financials": "财报或数据网站名称"
  }
}

请确保数据真实、可追溯，并避免主观判断或分析。
```

## 公司类型说明

- **TECH_PLATFORM**: 科技平台型（如NVDA、TSLA）
- **TECH_MATURE**: 科技成熟型（如AAPL、MSFT）
- **PHARMA_INNOVATION**: 医药创新型（如LLY、NVO）
- **PHARMA_MATURE**: 医药成熟型（如PFE、MRK）
- **FINANCIAL**: 金融型（银行、保险）
- **MANUFACTURING**: 制造业型（周期/制造业）

## 许可证

MIT License

