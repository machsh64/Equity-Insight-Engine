"""AI Prompt生成器 - 根据公司类型生成不同的Prompt"""
from models import CompanyType
from typing import Dict, List, Optional


class AIPromptGenerator:
    """AI Prompt生成器"""
    
    COMPANY_TYPE_NAMES = {
        CompanyType.TECH_PLATFORM: "科技平台型",
        CompanyType.TECH_MATURE: "科技成熟型",
        CompanyType.PHARMA_INNOVATION: "医药创新型",
        CompanyType.PHARMA_MATURE: "医药成熟型",
        CompanyType.FINANCIAL: "金融型",
        CompanyType.MANUFACTURING: "制造业型"
    }
    
    @staticmethod
    def generate_quarter_prompt(
        company_name: str,
        company_type: CompanyType,
        quarter: str,
        quarter_data: Dict,
        labels: List[str]
    ) -> str:
        """生成单季度AI分析Prompt"""
        company_type_name = AIPromptGenerator.COMPANY_TYPE_NAMES.get(company_type, "未知类型")
        
        if company_type == CompanyType.TECH_PLATFORM:
            return AIPromptGenerator._tech_platform_quarter_prompt(
                company_name, quarter, quarter_data, labels
            )
        elif company_type == CompanyType.TECH_MATURE:
            return AIPromptGenerator._tech_mature_quarter_prompt(
                company_name, quarter, quarter_data, labels
            )
        elif company_type == CompanyType.PHARMA_INNOVATION:
            return AIPromptGenerator._pharma_innovation_quarter_prompt(
                quarter, quarter_data, labels
            )
        elif company_type == CompanyType.PHARMA_MATURE:
            return AIPromptGenerator._pharma_mature_quarter_prompt(
                company_name, quarter, quarter_data, labels
            )
        elif company_type == CompanyType.FINANCIAL:
            return AIPromptGenerator._financial_quarter_prompt(
                company_name, quarter, quarter_data, labels
            )
        elif company_type == CompanyType.MANUFACTURING:
            return AIPromptGenerator._manufacturing_quarter_prompt(
                company_name, quarter, quarter_data, labels
            )
        else:
            return AIPromptGenerator._generic_quarter_prompt(
                company_name, company_type_name, quarter, quarter_data, labels
            )
    
    @staticmethod
    def _tech_platform_quarter_prompt(company_name: str, quarter: str, data: Dict, labels: List[str]) -> str:
        roic = data.get("roic", "N/A")
        wacc = data.get("wacc", "N/A")
        roic_wacc = (roic - wacc) if (roic != "N/A" and wacc != "N/A") else "N/A"
        
        return f"""你是一名长期价值投资分析师。
公司类型：科技平台型

公司：{company_name}
季度：{quarter}
关键数据：
PE={data.get('pe', 'N/A')}  PS={data.get('ps', 'N/A')}  PB={data.get('pb', 'N/A')}
ROIC={roic}%  WACC={wacc}%  ROIC-WACC={roic_wacc}%
毛利率={data.get('gross_margin', 'N/A')}%  自由现金流率={data.get('fcf_margin', 'N/A')}%  CapEx/收入={data.get('capex_ratio', 'N/A')}%

系统结论标签：{', '.join(labels) if labels else '无'}

请从长期视角分析：
1. 公司当前所处阶段（高速扩张 / 增长兑现 / 成熟减速）
2. 高估值是否仍由基本面支撑
3. 最关键的 2 个未来观察指标
4. 一条主要中长期风险

要求：
- 不给出买卖建议或目标价
- 不重复系统标签内容
- 语言客观、严谨，200字以内"""
    
    @staticmethod
    def _tech_mature_quarter_prompt(company_name: str, quarter: str, data: Dict, labels: List[str]) -> str:
        roic = data.get("roic", "N/A")
        wacc = data.get("wacc", "N/A")
        roic_wacc = (roic - wacc) if (roic != "N/A" and wacc != "N/A") else "N/A"
        
        return f"""你是一名专注成熟科技公司的长期投资分析师。
公司类型：科技成熟型

公司：{company_name}
季度：{quarter}
关键数据：
PE={data.get('pe', 'N/A')}  PS={data.get('ps', 'N/A')}  PB={data.get('pb', 'N/A')}
ROIC={roic}%  WACC={wacc}%  ROIC-WACC={roic_wacc}%
毛利率={data.get('gross_margin', 'N/A')}%  自由现金流率={data.get('fcf_margin', 'N/A')}%  CapEx/收入={data.get('capex_ratio', 'N/A')}%

系统结论标签：{', '.join(labels) if labels else '无'}

请分析：
1. 公司是否仍保持竞争壁垒
2. 现金流质量与回购/分红能力
3. 增长是否进入平稳期
4. 主要长期风险

要求：
- 不给出买卖建议或目标价
- 不重复系统标签内容
- 语言客观、严谨，200字以内"""
    
    @staticmethod
    def _pharma_innovation_quarter_prompt(company_name: str, quarter: str, data: Dict, labels: List[str]) -> str:
        return f"""你是一名专注创新药领域的长期投资分析师。
公司类型：医药创新型

公司：{company_name}
季度：{quarter}
关键数据：
ROIC={data.get('roic', 'N/A')}%  WACC={data.get('wacc', 'N/A')}%  PB={data.get('pb', 'N/A')}  PE={data.get('pe', 'N/A')}
收入同比={data.get('revenue_yoy', 'N/A')}%  自由现金流率={data.get('fcf_margin', 'N/A')}%

系统标签：{', '.join(labels) if labels else '无'}

请分析：
1. 当前 PB 估值是否仍合理（结合 ROIC 与成长）
2. 创新管线溢价是否仍有基础
3. 成长兑现的最关键变量
4. 一条中长期风险（专利悬崖、竞争等）

要求：
- 不给出目标价或买卖建议
- 客观分析，200字以内"""
    
    @staticmethod
    def _pharma_mature_quarter_prompt(company_name: str, quarter: str, data: Dict, labels: List[str]) -> str:
        return f"""你是一名专注成熟制药公司的长期投资分析师。
公司类型：医药成熟型

公司：{company_name}
季度：{quarter}
关键数据：
PE={data.get('pe', 'N/A')}  PB={data.get('pb', 'N/A')}
ROE={data.get('roe', 'N/A')}%  自由现金流率={data.get('fcf_margin', 'N/A')}%  毛利率={data.get('gross_margin', 'N/A')}%

系统标签：{', '.join(labels) if labels else '无'}

请分析：
1. 公司是否处于稳定成熟期
2. 现金流与分红能力
3. 主要风险（专利到期、竞争等）
4. 长期价值维持能力

要求：
- 不给出买卖建议或目标价
- 客观分析，200字以内"""
    
    @staticmethod
    def _financial_quarter_prompt(company_name: str, quarter: str, data: Dict, labels: List[str]) -> str:
        return f"""你是一名专注金融行业的长期投资分析师。
公司类型：金融型

公司：{company_name}
季度：{quarter}
关键数据：
PB={data.get('pb', 'N/A')}  ROE={data.get('roe', 'N/A')}%  自由现金流率={data.get('fcf_margin', 'N/A')}%

系统标签：{', '.join(labels) if labels else '无'}

请分析：
1. 公司盈利能力与ROE质量
2. 估值合理性（PB角度）
3. 主要风险（信用风险、利率风险等）
4. 长期价值创造能力

要求：
- 不给出买卖建议或目标价
- 客观分析，200字以内"""
    
    @staticmethod
    def _manufacturing_quarter_prompt(company_name: str, quarter: str, data: Dict, labels: List[str]) -> str:
        return f"""你是一名专注制造业的长期投资分析师。
公司类型：制造业型

公司：{company_name}
季度：{quarter}
关键数据：
PB={data.get('pb', 'N/A')}  PS={data.get('ps', 'N/A')}
ROIC={data.get('roic', 'N/A')}%  毛利率={data.get('gross_margin', 'N/A')}%  自由现金流率={data.get('fcf_margin', 'N/A')}%

系统标签：{', '.join(labels) if labels else '无'}

请分析：
1. 公司所处周期阶段
2. 盈利能力与现金流质量
3. 估值是否反映周期位置
4. 主要风险（周期波动、竞争等）

要求：
- 不给出买卖建议或目标价
- 客观分析，200字以内"""
    
    @staticmethod
    def _generic_quarter_prompt(
        company_type_name: str,
        quarter: str,
        data: Dict,
        labels: List[str]
    ) -> str:
        return f"""你是一名长期价值投资分析师。
公司类型：{company_type_name}

公司：{company_name}
季度：{quarter}
关键数据：
PE={data.get('pe', 'N/A')}  PB={data.get('pb', 'N/A')}  PS={data.get('ps', 'N/A')}
ROIC={data.get('roic', 'N/A')}%  ROE={data.get('roe', 'N/A')}%

系统标签：{', '.join(labels) if labels else '无'}

请从长期视角分析公司当前状态、关键观察指标和主要风险。

要求：
- 不给出买卖建议或目标价
- 客观分析，200字以内"""
    
    @staticmethod
    def generate_comprehensive_prompt(
        ticker: str,
        company_name: str,
        company_type: CompanyType,
        quarters_summary: List[Dict]
    ) -> str:
        """生成首页综合AI分析Prompt"""
        company_type_name = AIPromptGenerator.COMPANY_TYPE_NAMES.get(company_type, "未知类型")
        
        summary_text = ""
        ai_text = ""
        
        for i, q in enumerate(quarters_summary, 1):
            summary_text += f"{q['quarter']}: {q['system_summary']}\n"
            if q.get('ai_analysis'):
                ai_text += f"{q['quarter']} AI分析: {q['ai_analysis']}\n"
        
        return f"""你是一名长期价值投资分析师。
公司：{ticker} {company_name}（{company_type_name}）

最近 4 个季度系统总结：
{summary_text}

对应 AI 单季度分析：
{ai_text}

请给出：
1. 一段 120-150 字的综合长期判断（当前阶段、质量趋势、估值合理性）
2. 一个主标签（例如"高质量成长"、"成熟稳定"、"周期复苏"）
3. 一个风险标签（例如"成长放缓风险"、"高估值压力"）

严格要求：
- 不给出任何买卖建议或目标价
- 语言客观、中性

请按以下格式输出：
分析：[你的分析文本]
主标签：[主标签]
风险标签：[风险标签]"""

