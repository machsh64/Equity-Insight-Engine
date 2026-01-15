"""系统分析引擎 - 完全确定性计算模块"""
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from models import CompanyType


def normalize(value: Optional[float], low: float, mid: float, high: float) -> float:
    """
    通用normalize函数（0-100）
    
    value ≤ low → 0
    low < value ≤ mid → 线性 0→50
    mid < value ≤ high → 线性 50→100
    value > high → 100
    """
    if value is None:
        return 50.0  # 默认中间值
    
    if value <= low:
        return 0.0
    elif value <= mid:
        # 线性插值: 0 -> 50
        ratio = (value - low) / (mid - low)
        return ratio * 50.0
    elif value <= high:
        # 线性插值: 50 -> 100
        ratio = (value - mid) / (high - mid)
        return 50.0 + ratio * 50.0
    else:
        return 100.0


def calculate_roic_wacc_label(roic: Optional[float], wacc: Optional[float]) -> str:
    """计算ROIC-WACC标签"""
    if roic is None or wacc is None:
        return "数据不足"
    
    diff = roic - wacc
    
    if diff >= 8:
        return "强价值创造"
    elif diff >= 3:
        return "价值创造"
    elif diff >= 0:
        return "微弱价值创造"
    elif diff >= -5:
        return "扩张期正常"
    else:
        return "高资本消耗"


def calculate_delta(current: Optional[float], previous: Optional[float]) -> float:
    """计算变化量（用于trend_score）"""
    if current is None or previous is None:
        return 0.0
    return current - previous


class SystemAnalysisEngine:
    """系统分析引擎"""
    
    @staticmethod
    def analyze_tech_platform(
        pe: Optional[float],
        pb: Optional[float],
        ps: Optional[float],
        roic: Optional[float],
        wacc: Optional[float],
        gross_margin: Optional[float],
        fcf_margin: Optional[float],
        capex_ratio: Optional[float],
        prev_roic: Optional[float] = None,
        prev_gross_margin: Optional[float] = None,
        prev_capex_ratio: Optional[float] = None
    ) -> Dict:
        """TECH_PLATFORM类型分析"""
        # 估值归一化
        normalize_ps = normalize(ps, 5, 15, 30)
        normalize_pe = normalize(pe, 20, 50, 100)
        normalize_pb = normalize(pb, 5, 15, 30)
        
        # Quality Score
        roic_val = roic if roic else 0
        wacc_val = wacc if wacc else 0
        gross_margin_val = gross_margin if gross_margin else 0
        fcf_margin_val = fcf_margin if fcf_margin else 0
        
        quality_score = (
            roic_val * 0.35 +
            max(roic_val - wacc_val, 0) * 0.35 +
            gross_margin_val * 0.15 +
            fcf_margin_val * 0.15
        ) * 100
        
        # Valuation Score (高分=便宜)
        valuation_score = 100 - (
            normalize_ps * 0.40 +
            normalize_pe * 0.30 +
            normalize_pb * 0.30
        )
        
        # Trend Score
        delta_roic = calculate_delta(roic, prev_roic)
        delta_gross_margin = calculate_delta(gross_margin, prev_gross_margin)
        delta_capex_ratio = calculate_delta(capex_ratio, prev_capex_ratio)
        
        trend_score = (
            delta_roic * 0.40 +
            delta_gross_margin * 0.30 +
            (-delta_capex_ratio) * 0.30  # CapEx下降为正向
        ) * 100 + 50
        
        # 限制在0-100范围
        quality_score = max(0, min(100, quality_score))
        valuation_score = max(0, min(100, valuation_score))
        trend_score = max(0, min(100, trend_score))
        
        # 生成标签
        labels = []
        roic_wacc_label = calculate_roic_wacc_label(roic, wacc)
        
        if quality_score >= 80 and valuation_score >= 70:
            labels.append("高质量 · 估值合理")
        elif quality_score >= 80 and valuation_score < 40:
            labels.append("高质量 · 高估值（成长溢价）")
        
        if roic and wacc and roic < wacc and trend_score >= 70:
            labels.append("扩张后期 · 关注ROIC拐点")
        
        if trend_score <= 30:
            labels.append("基本面走弱")
        
        # 生成system_summary
        system_summary = f"质量得分：{quality_score:.1f}/100\n"
        system_summary += f"估值状态：{valuation_score:.1f}/100（越高越便宜）\n"
        system_summary += f"趋势得分：{trend_score:.1f}/100\n"
        system_summary += f"ROIC-WACC：{roic_wacc_label}\n"
        if labels:
            system_summary += f"标签：{', '.join(labels)}"
        
        return {
            "quality_score": round(quality_score, 2),
            "valuation_score": round(valuation_score, 2),
            "trend_score": round(trend_score, 2),
            "labels": labels,
            "system_summary": system_summary
        }
    
    @staticmethod
    def analyze_tech_mature(
        pe: Optional[float],
        pb: Optional[float],
        ps: Optional[float],
        roic: Optional[float],
        fcf_margin: Optional[float],
        roe: Optional[float],
        revenue_yoy: Optional[float] = None,
        prev_roic: Optional[float] = None,
        prev_revenue_yoy: Optional[float] = None
    ) -> Dict:
        """TECH_MATURE类型分析"""
        normalize_pe = normalize(pe, 15, 25, 40)
        normalize_pb = normalize(pb, 4, 8, 15)
        normalize_ps = normalize(ps, 4, 8, 15)
        
        roic_val = roic if roic else 0
        fcf_margin_val = fcf_margin if fcf_margin else 0
        roe_val = roe if roe else 0
        
        quality_score = (
            roic_val * 0.45 +
            fcf_margin_val * 0.30 +
            roe_val * 0.25
        ) * 100
        
        valuation_score = 100 - (
            normalize_pe * 0.50 +
            normalize_pb * 0.30 +
            normalize_ps * 0.20
        )
        
        delta_roic = calculate_delta(roic, prev_roic)
        delta_revenue_yoy = calculate_delta(revenue_yoy, prev_revenue_yoy)
        
        trend_score = (
            delta_roic * 0.50 +
            delta_revenue_yoy * 0.50
        ) * 100 + 50
        
        quality_score = max(0, min(100, quality_score))
        valuation_score = max(0, min(100, valuation_score))
        trend_score = max(0, min(100, trend_score))
        
        labels = []
        if quality_score >= 85:
            labels.append("成熟高质量")
        if valuation_score >= 70:
            labels.append("估值合理区")
        if trend_score >= 70:
            labels.append("稳健增长")
        
        system_summary = f"质量得分：{quality_score:.1f}/100\n"
        system_summary += f"估值状态：{valuation_score:.1f}/100（越高越便宜）\n"
        system_summary += f"趋势得分：{trend_score:.1f}/100\n"
        if labels:
            system_summary += f"标签：{', '.join(labels)}"
        
        return {
            "quality_score": round(quality_score, 2),
            "valuation_score": round(valuation_score, 2),
            "trend_score": round(trend_score, 2),
            "labels": labels,
            "system_summary": system_summary
        }
    
    @staticmethod
    def analyze_pharma_innovation(
        pe: Optional[float],
        pb: Optional[float],
        ps: Optional[float],
        roic: Optional[float],
        wacc: Optional[float],
        fcf_margin: Optional[float],
        roe: Optional[float],
        gross_margin: Optional[float] = None,
        prev_roic: Optional[float] = None,
        prev_fcf_margin: Optional[float] = None,
        prev_gross_margin: Optional[float] = None
    ) -> Dict:
        """PHARMA_INNOVATION类型分析"""
        normalize_pb = normalize(pb, 8, 20, 40)
        normalize_pe = normalize(pe, 20, 50, 100)
        normalize_ps = normalize(ps, 8, 20, 40)
        
        roic_val = roic if roic else 0
        wacc_val = wacc if wacc else 0
        fcf_margin_val = fcf_margin if fcf_margin else 0
        roe_val = roe if roe else 0
        
        quality_score = (
            roic_val * 0.40 +
            max(roic_val - wacc_val, 0) * 0.30 +
            fcf_margin_val * 0.20 +
            roe_val * 0.10
        ) * 100
        
        valuation_score = 100 - (
            normalize_pb * 0.45 +
            normalize_pe * 0.35 +
            normalize_ps * 0.20
        )
        
        delta_roic = calculate_delta(roic, prev_roic)
        delta_fcf_margin = calculate_delta(fcf_margin, prev_fcf_margin)
        delta_gross_margin = calculate_delta(gross_margin, prev_gross_margin)
        
        trend_score = (
            delta_roic * 0.40 +
            delta_fcf_margin * 0.30 +
            delta_gross_margin * 0.30
        ) * 100 + 50
        
        quality_score = max(0, min(100, quality_score))
        valuation_score = max(0, min(100, valuation_score))
        trend_score = max(0, min(100, trend_score))
        
        labels = []
        pb_val = pb if pb else 0
        if quality_score >= 80 and pb_val > 30:
            labels.append("高质量医药 · 创新溢价")
        if pb_val > 35 and trend_score < 40:
            labels.append("高估值 · 成长放缓风险")
        
        system_summary = f"质量得分：{quality_score:.1f}/100\n"
        system_summary += f"估值状态：{valuation_score:.1f}/100（越高越便宜）\n"
        system_summary += f"趋势得分：{trend_score:.1f}/100\n"
        if pb:
            if pb < 10:
                pb_label = "质量存疑"
            elif pb <= 20:
                pb_label = "合理"
            elif pb <= 35:
                pb_label = "创新溢价"
            else:
                pb_label = "需持续兑现增长"
            system_summary += f"PB区间：{pb_label}\n"
        if labels:
            system_summary += f"标签：{', '.join(labels)}"
        
        return {
            "quality_score": round(quality_score, 2),
            "valuation_score": round(valuation_score, 2),
            "trend_score": round(trend_score, 2),
            "labels": labels,
            "system_summary": system_summary
        }
    
    @staticmethod
    def analyze_pharma_mature(
        pe: Optional[float],
        pb: Optional[float],
        roe: Optional[float],
        fcf_margin: Optional[float],
        gross_margin: Optional[float],
        prev_roe: Optional[float] = None,
        prev_fcf_margin: Optional[float] = None
    ) -> Dict:
        """PHARMA_MATURE类型分析"""
        normalize_pb = normalize(pb, 1, 3, 6)
        normalize_pe = normalize(pe, 10, 18, 30)
        
        roe_val = roe if roe else 0
        fcf_margin_val = fcf_margin if fcf_margin else 0
        gross_margin_val = gross_margin if gross_margin else 0
        
        quality_score = (
            roe_val * 0.50 +
            fcf_margin_val * 0.30 +
            gross_margin_val * 0.20
        ) * 100
        
        valuation_score = 100 - (
            normalize_pb * 0.60 +
            normalize_pe * 0.40
        )
        
        delta_roe = calculate_delta(roe, prev_roe)
        delta_fcf_margin = calculate_delta(fcf_margin, prev_fcf_margin)
        
        trend_score = (
            delta_roe * 0.60 +
            delta_fcf_margin * 0.40
        ) * 100 + 50
        
        quality_score = max(0, min(100, quality_score))
        valuation_score = max(0, min(100, valuation_score))
        trend_score = max(0, min(100, trend_score))
        
        labels = []
        if quality_score >= 75:
            labels.append("成熟稳定制药")
        if valuation_score >= 70:
            labels.append("低估值安全边际")
        
        system_summary = f"质量得分：{quality_score:.1f}/100\n"
        system_summary += f"估值状态：{valuation_score:.1f}/100（越高越便宜）\n"
        system_summary += f"趋势得分：{trend_score:.1f}/100\n"
        if labels:
            system_summary += f"标签：{', '.join(labels)}"
        
        return {
            "quality_score": round(quality_score, 2),
            "valuation_score": round(valuation_score, 2),
            "trend_score": round(trend_score, 2),
            "labels": labels,
            "system_summary": system_summary
        }
    
    @staticmethod
    def analyze_financial(
        pb: Optional[float],
        roe: Optional[float],
        fcf_margin: Optional[float],
        prev_roe: Optional[float] = None
    ) -> Dict:
        """FINANCIAL类型分析"""
        roe_val = roe if roe else 0
        fcf_margin_val = fcf_margin if fcf_margin else 0
        
        if roe_val < 12:
            quality_score = 0
        else:
            quality_score = (
                roe_val * 0.60 +
                fcf_margin_val * 0.40
            ) * 100
        
        valuation_score = 100 - normalize(pb, 0.8, 1.5, 3.0)
        
        delta_roe = calculate_delta(roe, prev_roe)
        trend_score = delta_roe * 100 + 50
        
        quality_score = max(0, min(100, quality_score))
        valuation_score = max(0, min(100, valuation_score))
        trend_score = max(0, min(100, trend_score))
        
        labels = []
        if roe_val >= 15:
            labels.append("高ROE金融")
        pb_val = pb if pb else 0
        if pb_val < 1:
            labels.append("深度低估")
        
        system_summary = f"质量得分：{quality_score:.1f}/100\n"
        system_summary += f"估值状态：{valuation_score:.1f}/100（越高越便宜）\n"
        system_summary += f"趋势得分：{trend_score:.1f}/100\n"
        if labels:
            system_summary += f"标签：{', '.join(labels)}"
        
        return {
            "quality_score": round(quality_score, 2),
            "valuation_score": round(valuation_score, 2),
            "trend_score": round(trend_score, 2),
            "labels": labels,
            "system_summary": system_summary
        }
    
    @staticmethod
    def analyze_manufacturing(
        pb: Optional[float],
        ps: Optional[float],
        roic: Optional[float],
        gross_margin: Optional[float],
        fcf_margin: Optional[float],
        revenue_yoy: Optional[float] = None,
        prev_roic: Optional[float] = None,
        prev_gross_margin: Optional[float] = None,
        prev_revenue_yoy: Optional[float] = None
    ) -> Dict:
        """MANUFACTURING类型分析"""
        normalize_pb = normalize(pb, 1, 2.5, 5)
        normalize_ps = normalize(ps, 0.5, 1.5, 3)
        
        roic_val = roic if roic else 0
        gross_margin_val = gross_margin if gross_margin else 0
        fcf_margin_val = fcf_margin if fcf_margin else 0
        
        quality_score = (
            roic_val * 0.40 +
            gross_margin_val * 0.30 +
            fcf_margin_val * 0.30
        ) * 100
        
        valuation_score = 100 - (
            normalize_pb * 0.50 +
            normalize_ps * 0.50
        )
        
        delta_roic = calculate_delta(roic, prev_roic)
        delta_gross_margin = calculate_delta(gross_margin, prev_gross_margin)
        delta_revenue_yoy = calculate_delta(revenue_yoy, prev_revenue_yoy)
        
        trend_score = (
            delta_roic * 0.40 +
            delta_gross_margin * 0.40 +
            delta_revenue_yoy * 0.20
        ) * 100 + 50
        
        quality_score = max(0, min(100, quality_score))
        valuation_score = max(0, min(100, valuation_score))
        trend_score = max(0, min(100, trend_score))
        
        labels = []
        if quality_score >= 70 and valuation_score >= 70:
            labels.append("周期底部 · 高质量")
        if trend_score >= 70:
            labels.append("周期复苏迹象")
        
        system_summary = f"质量得分：{quality_score:.1f}/100\n"
        system_summary += f"估值状态：{valuation_score:.1f}/100（越高越便宜）\n"
        system_summary += f"趋势得分：{trend_score:.1f}/100\n"
        if labels:
            system_summary += f"标签：{', '.join(labels)}"
        
        return {
            "quality_score": round(quality_score, 2),
            "valuation_score": round(valuation_score, 2),
            "trend_score": round(trend_score, 2),
            "labels": labels,
            "system_summary": system_summary
        }
    
    @staticmethod
    def analyze(
        company_type: CompanyType,
        quarter_data: Dict,
        previous_quarter_data: Optional[Dict] = None
    ) -> Dict:
        """
        主分析函数
        
        Args:
            company_type: 公司类型
            quarter_data: 当前季度数据字典
            previous_quarter_data: 上一季度数据字典（用于计算trend）
        """
        prev = previous_quarter_data or {}
        
        if company_type == CompanyType.TECH_PLATFORM:
            return SystemAnalysisEngine.analyze_tech_platform(
                pe=quarter_data.get("pe"),
                pb=quarter_data.get("pb"),
                ps=quarter_data.get("ps"),
                roic=quarter_data.get("roic"),
                wacc=quarter_data.get("wacc"),
                gross_margin=quarter_data.get("gross_margin"),
                fcf_margin=quarter_data.get("fcf_margin"),
                capex_ratio=quarter_data.get("capex_ratio"),
                prev_roic=prev.get("roic"),
                prev_gross_margin=prev.get("gross_margin"),
                prev_capex_ratio=prev.get("capex_ratio")
            )
        elif company_type == CompanyType.TECH_MATURE:
            return SystemAnalysisEngine.analyze_tech_mature(
                pe=quarter_data.get("pe"),
                pb=quarter_data.get("pb"),
                ps=quarter_data.get("ps"),
                roic=quarter_data.get("roic"),
                fcf_margin=quarter_data.get("fcf_margin"),
                roe=quarter_data.get("roe"),
                revenue_yoy=quarter_data.get("revenue_yoy"),
                prev_roic=prev.get("roic"),
                prev_revenue_yoy=prev.get("revenue_yoy")
            )
        elif company_type == CompanyType.PHARMA_INNOVATION:
            return SystemAnalysisEngine.analyze_pharma_innovation(
                pe=quarter_data.get("pe"),
                pb=quarter_data.get("pb"),
                ps=quarter_data.get("ps"),
                roic=quarter_data.get("roic"),
                wacc=quarter_data.get("wacc"),
                fcf_margin=quarter_data.get("fcf_margin"),
                roe=quarter_data.get("roe"),
                gross_margin=quarter_data.get("gross_margin"),
                prev_roic=prev.get("roic"),
                prev_fcf_margin=prev.get("fcf_margin"),
                prev_gross_margin=prev.get("gross_margin")
            )
        elif company_type == CompanyType.PHARMA_MATURE:
            return SystemAnalysisEngine.analyze_pharma_mature(
                pe=quarter_data.get("pe"),
                pb=quarter_data.get("pb"),
                roe=quarter_data.get("roe"),
                fcf_margin=quarter_data.get("fcf_margin"),
                gross_margin=quarter_data.get("gross_margin"),
                prev_roe=prev.get("roe"),
                prev_fcf_margin=prev.get("fcf_margin")
            )
        elif company_type == CompanyType.FINANCIAL:
            return SystemAnalysisEngine.analyze_financial(
                pb=quarter_data.get("pb"),
                roe=quarter_data.get("roe"),
                fcf_margin=quarter_data.get("fcf_margin"),
                prev_roe=prev.get("roe")
            )
        elif company_type == CompanyType.MANUFACTURING:
            return SystemAnalysisEngine.analyze_manufacturing(
                pb=quarter_data.get("pb"),
                ps=quarter_data.get("ps"),
                roic=quarter_data.get("roic"),
                gross_margin=quarter_data.get("gross_margin"),
                fcf_margin=quarter_data.get("fcf_margin"),
                revenue_yoy=quarter_data.get("revenue_yoy"),
                prev_roic=prev.get("roic"),
                prev_gross_margin=prev.get("gross_margin"),
                prev_revenue_yoy=prev.get("revenue_yoy")
            )
        else:
            raise ValueError(f"不支持的公司类型: {company_type}")

