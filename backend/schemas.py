"""Pydantic模型（API请求/响应）"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from models import CompanyType


# 公司相关Schema
class CompanyBase(BaseModel):
    ticker: str
    company_name: str
    company_type: CompanyType


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    company_type: Optional[CompanyType] = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# 季度数据相关Schema
class QuarterBase(BaseModel):
    quarter: str = Field(..., pattern=r"^\d{4}-Q[1-4]$")
    pe: Optional[float] = None
    pb: Optional[float] = None
    ps: Optional[float] = None
    roe: Optional[float] = None
    roic: Optional[float] = None
    wacc: Optional[float] = None
    revenue_yoy: Optional[float] = None
    gross_margin: Optional[float] = None
    fcf_margin: Optional[float] = None
    capex_ratio: Optional[float] = None


class QuarterCreate(QuarterBase):
    company_id: int


class QuarterUpdate(QuarterBase):
    pass  # 所有字段都是可选的


class QuarterResponse(QuarterBase):
    id: int
    company_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# 系统分析相关Schema
class SystemAnalysisResponse(BaseModel):
    id: int
    quarter_id: int
    quality_score: Optional[float]
    valuation_score: Optional[float]
    trend_score: Optional[float]
    labels: Optional[List[str]]
    system_summary: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# AI分析相关Schema
class QuarterAIAnalysisResponse(BaseModel):
    id: int
    quarter_id: int
    analysis_text: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CompanyComprehensiveAIResponse(BaseModel):
    id: int
    company_id: int
    analysis_text: Optional[str]
    main_label: Optional[str]
    risk_label: Optional[str]
    based_quarters: Optional[List[str]]
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# 详情页完整数据Schema
class QuarterDetailResponse(QuarterResponse):
    system_analysis: Optional[SystemAnalysisResponse] = None
    ai_analysis: Optional[QuarterAIAnalysisResponse] = None


class CompanyDetailResponse(CompanyResponse):
    quarters: List[QuarterDetailResponse] = []
    comprehensive_ai: Optional[CompanyComprehensiveAIResponse] = None


# 首页卡片数据Schema
class CompanyCardResponse(BaseModel):
    id: int
    ticker: str
    company_name: str
    company_type: CompanyType
    latest_quarter: Optional[str] = None
    latest_roic: Optional[float] = None
    latest_wacc: Optional[float] = None
    latest_valuation_score: Optional[float] = None
    latest_labels: Optional[List[str]] = None
    comprehensive_ai: Optional[CompanyComprehensiveAIResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

