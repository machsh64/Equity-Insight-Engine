"""数据库模型"""
from sqlalchemy import Column, Integer, String, Numeric, Text, ARRAY, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base


class CompanyType(str, enum.Enum):
    """公司类型枚举"""
    TECH_PLATFORM = "TECH_PLATFORM"
    TECH_MATURE = "TECH_MATURE"
    PHARMA_INNOVATION = "PHARMA_INNOVATION"
    PHARMA_MATURE = "PHARMA_MATURE"
    FINANCIAL = "FINANCIAL"
    MANUFACTURING = "MANUFACTURING"


class Company(Base):
    """公司模型"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, nullable=False, index=True)
    company_name = Column(String, nullable=False)
    company_type = Column(Enum(CompanyType), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # 关系
    quarters = relationship("Quarter", back_populates="company", cascade="all, delete-orphan")
    comprehensive_ai = relationship("CompanyComprehensiveAI", back_populates="company", uselist=False)


class Quarter(Base):
    """季度财务数据模型"""
    __tablename__ = "quarters"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    quarter = Column(String, nullable=False)
    pe = Column(Numeric(10, 2))
    pb = Column(Numeric(10, 2))
    ps = Column(Numeric(10, 2))
    roe = Column(Numeric(10, 2))
    roic = Column(Numeric(10, 2))
    wacc = Column(Numeric(10, 2))
    revenue_yoy = Column(Numeric(10, 2))
    gross_margin = Column(Numeric(10, 2))
    fcf_margin = Column(Numeric(10, 2))
    capex_ratio = Column(Numeric(10, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 关系
    company = relationship("Company", back_populates="quarters")
    system_analysis = relationship("SystemAnalysis", back_populates="quarter", uselist=False, cascade="all, delete-orphan")
    ai_analysis = relationship("QuarterAIAnalysis", back_populates="quarter", uselist=False, cascade="all, delete-orphan")


class SystemAnalysis(Base):
    """系统分析结果模型"""
    __tablename__ = "system_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    quarter_id = Column(Integer, ForeignKey("quarters.id", ondelete="CASCADE"), unique=True, nullable=False)
    quality_score = Column(Numeric(5, 2))
    valuation_score = Column(Numeric(5, 2))
    trend_score = Column(Numeric(5, 2))
    labels = Column(ARRAY(Text))
    system_summary = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 关系
    quarter = relationship("Quarter", back_populates="system_analysis")


class QuarterAIAnalysis(Base):
    """单季度AI分析模型"""
    __tablename__ = "quarter_ai_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    quarter_id = Column(Integer, ForeignKey("quarters.id", ondelete="CASCADE"), unique=True, nullable=False)
    analysis_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 关系
    quarter = relationship("Quarter", back_populates="ai_analysis")


class CompanyComprehensiveAI(Base):
    """公司综合AI分析模型"""
    __tablename__ = "company_comprehensive_ai"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), unique=True, nullable=False)
    analysis_text = Column(Text)
    main_label = Column(String)
    risk_label = Column(String)
    based_quarters = Column(ARRAY(Text))
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # 关系
    company = relationship("Company", back_populates="comprehensive_ai")

