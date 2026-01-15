"""数据库CRUD操作"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict
from datetime import datetime
import models
import schemas
from system_analysis_engine import SystemAnalysisEngine
from ai_prompt_generator import AIPromptGenerator
from ai_service import AIService


ai_service = AIService()


# 公司相关CRUD
def create_company(db: Session, company: schemas.CompanyCreate) -> models.Company:
    """创建公司"""
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def get_companies_with_summary(db: Session) -> List[Dict]:
    """获取所有公司及其最新摘要信息（用于首页卡片）"""
    companies = db.query(models.Company).all()
    result = []
    
    for company in companies:
        # 获取最新季度
        latest_quarter = db.query(models.Quarter)\
            .filter(models.Quarter.company_id == company.id)\
            .order_by(desc(models.Quarter.quarter))\
            .first()
        
        latest_analysis = None
        latest_roic = None
        latest_wacc = None
        latest_valuation_score = None
        latest_labels = None
        
        if latest_quarter:
            latest_roic = float(latest_quarter.roic) if latest_quarter.roic else None
            latest_wacc = float(latest_quarter.wacc) if latest_quarter.wacc else None
            
            latest_analysis = db.query(models.SystemAnalysis)\
                .filter(models.SystemAnalysis.quarter_id == latest_quarter.id)\
                .first()
            
            if latest_analysis:
                latest_valuation_score = float(latest_analysis.valuation_score) if latest_analysis.valuation_score else None
                latest_labels = latest_analysis.labels
        
        # 获取综合AI分析
        comprehensive_ai = db.query(models.CompanyComprehensiveAI)\
            .filter(models.CompanyComprehensiveAI.company_id == company.id)\
            .first()
        
        result.append({
            "id": company.id,
            "ticker": company.ticker,
            "company_name": company.company_name,
            "company_type": company.company_type,
            "latest_quarter": latest_quarter.quarter if latest_quarter else None,
            "latest_roic": latest_roic,
            "latest_wacc": latest_wacc,
            "latest_valuation_score": latest_valuation_score,
            "latest_labels": latest_labels,
            "comprehensive_ai": comprehensive_ai
        })
    
    return result


def get_company_detail(db: Session, company_id: int) -> Optional[Dict]:
    """获取公司详情（包含所有季度数据）"""
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        return None
    
    # 获取所有季度数据（倒序）
    quarters = db.query(models.Quarter)\
        .filter(models.Quarter.company_id == company_id)\
        .order_by(desc(models.Quarter.quarter))\
        .all()
    
    quarter_details = []
    for quarter in quarters:
        system_analysis = db.query(models.SystemAnalysis)\
            .filter(models.SystemAnalysis.quarter_id == quarter.id)\
            .first()
        
        ai_analysis = db.query(models.QuarterAIAnalysis)\
            .filter(models.QuarterAIAnalysis.quarter_id == quarter.id)\
            .first()
        
        quarter_details.append({
            **schemas.QuarterResponse.model_validate(quarter).model_dump(),
            "system_analysis": schemas.SystemAnalysisResponse.model_validate(system_analysis).model_dump() if system_analysis else None,
            "ai_analysis": schemas.QuarterAIAnalysisResponse.model_validate(ai_analysis).model_dump() if ai_analysis else None
        })
    
    comprehensive_ai = db.query(models.CompanyComprehensiveAI)\
        .filter(models.CompanyComprehensiveAI.company_id == company_id)\
        .first()
    
    return {
        **schemas.CompanyResponse.model_validate(company).model_dump(),
        "quarters": quarter_details,
        "comprehensive_ai": schemas.CompanyComprehensiveAIResponse.model_validate(comprehensive_ai).model_dump() if comprehensive_ai else None
    }


def update_company(db: Session, company_id: int, company_update: schemas.CompanyUpdate) -> Optional[models.Company]:
    """更新公司信息"""
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        return None
    
    update_data = company_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company_id: int) -> bool:
    """删除公司"""
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        return False
    db.delete(company)
    db.commit()
    return True


# 季度数据相关CRUD
def create_quarter_with_analysis(db: Session, quarter: schemas.QuarterCreate) -> models.Quarter:
    """创建季度数据并自动触发系统分析和AI分析"""
    # 创建季度数据
    db_quarter = models.Quarter(**quarter.dict())
    db.add(db_quarter)
    db.commit()
    db.refresh(db_quarter)
    
    # 获取公司信息
    company = db.query(models.Company).filter(models.Company.id == quarter.company_id).first()
    if not company:
        raise ValueError("公司不存在")
    
    # 获取上一季度数据（用于trend计算）
    previous_quarter = db.query(models.Quarter)\
        .filter(models.Quarter.company_id == quarter.company_id)\
        .filter(models.Quarter.quarter < quarter.quarter)\
        .order_by(desc(models.Quarter.quarter))\
        .first()
    
    prev_data = {}
    if previous_quarter:
        prev_data = {
            "pe": float(previous_quarter.pe) if previous_quarter.pe else None,
            "pb": float(previous_quarter.pb) if previous_quarter.pb else None,
            "ps": float(previous_quarter.ps) if previous_quarter.ps else None,
            "roe": float(previous_quarter.roe) if previous_quarter.roe else None,
            "roic": float(previous_quarter.roic) if previous_quarter.roic else None,
            "wacc": float(previous_quarter.wacc) if previous_quarter.wacc else None,
            "revenue_yoy": float(previous_quarter.revenue_yoy) if previous_quarter.revenue_yoy else None,
            "gross_margin": float(previous_quarter.gross_margin) if previous_quarter.gross_margin else None,
            "fcf_margin": float(previous_quarter.fcf_margin) if previous_quarter.fcf_margin else None,
            "capex_ratio": float(previous_quarter.capex_ratio) if previous_quarter.capex_ratio else None
        }
    
    # 准备当前季度数据
    current_data = {
        "pe": float(db_quarter.pe) if db_quarter.pe else None,
        "pb": float(db_quarter.pb) if db_quarter.pb else None,
        "ps": float(db_quarter.ps) if db_quarter.ps else None,
        "roe": float(db_quarter.roe) if db_quarter.roe else None,
        "roic": float(db_quarter.roic) if db_quarter.roic else None,
        "wacc": float(db_quarter.wacc) if db_quarter.wacc else None,
        "revenue_yoy": float(db_quarter.revenue_yoy) if db_quarter.revenue_yoy else None,
        "gross_margin": float(db_quarter.gross_margin) if db_quarter.gross_margin else None,
        "fcf_margin": float(db_quarter.fcf_margin) if db_quarter.fcf_margin else None,
        "capex_ratio": float(db_quarter.capex_ratio) if db_quarter.capex_ratio else None
    }
    
    # 执行系统分析
    analysis_result = SystemAnalysisEngine.analyze(
        company_type=company.company_type,
        quarter_data=current_data,
        previous_quarter_data=prev_data if prev_data else None
    )
    
    # 保存系统分析结果
    db_analysis = models.SystemAnalysis(
        quarter_id=db_quarter.id,
        quality_score=analysis_result["quality_score"],
        valuation_score=analysis_result["valuation_score"],
        trend_score=analysis_result["trend_score"],
        labels=analysis_result["labels"],
        system_summary=analysis_result["system_summary"]
    )
    db.add(db_analysis)
    db.commit()
    
    # 生成AI分析
    prompt = AIPromptGenerator.generate_quarter_prompt(
        company_name=company.company_name,
        company_type=company.company_type,
        quarter=db_quarter.quarter,
        quarter_data=current_data,
        labels=analysis_result["labels"]
    )
    
    ai_text = ai_service.generate_analysis(prompt)
    
    db_ai_analysis = models.QuarterAIAnalysis(
        quarter_id=db_quarter.id,
        analysis_text=ai_text
    )
    db.add(db_ai_analysis)
    db.commit()
    
    # 检查是否需要更新综合AI分析（如果是最新4个季度之一）
    update_comprehensive_ai_if_needed(db, quarter.company_id)
    
    return db_quarter


def get_quarter_detail(db: Session, quarter_id: int) -> Optional[Dict]:
    """获取季度详情"""
    quarter = db.query(models.Quarter).filter(models.Quarter.id == quarter_id).first()
    if not quarter:
        return None
    
    system_analysis = db.query(models.SystemAnalysis)\
        .filter(models.SystemAnalysis.quarter_id == quarter_id)\
        .first()
    
    ai_analysis = db.query(models.QuarterAIAnalysis)\
        .filter(models.QuarterAIAnalysis.quarter_id == quarter_id)\
        .first()
    
    return {
        **schemas.QuarterResponse.model_validate(quarter).model_dump(),
        "system_analysis": schemas.SystemAnalysisResponse.model_validate(system_analysis).model_dump() if system_analysis else None,
        "ai_analysis": schemas.QuarterAIAnalysisResponse.model_validate(ai_analysis).model_dump() if ai_analysis else None
    }


def update_quarter_with_analysis(db: Session, quarter_id: int, quarter_update: schemas.QuarterUpdate) -> Optional[models.Quarter]:
    """更新季度数据并重新触发系统分析和AI分析"""
    quarter = db.query(models.Quarter).filter(models.Quarter.id == quarter_id).first()
    if not quarter:
        return None
    
    # 更新季度数据
    update_data = quarter_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quarter, field, value)
    
    db.commit()
    db.refresh(quarter)
    
    # 获取公司信息
    company = db.query(models.Company).filter(models.Company.id == quarter.company_id).first()
    if not company:
        return quarter
    
    # 获取上一季度数据（用于trend计算）
    previous_quarter = db.query(models.Quarter)\
        .filter(models.Quarter.company_id == quarter.company_id)\
        .filter(models.Quarter.quarter < quarter.quarter)\
        .order_by(desc(models.Quarter.quarter))\
        .first()
    
    prev_data = {}
    if previous_quarter:
        prev_data = {
            "pe": float(previous_quarter.pe) if previous_quarter.pe else None,
            "pb": float(previous_quarter.pb) if previous_quarter.pb else None,
            "ps": float(previous_quarter.ps) if previous_quarter.ps else None,
            "roe": float(previous_quarter.roe) if previous_quarter.roe else None,
            "roic": float(previous_quarter.roic) if previous_quarter.roic else None,
            "wacc": float(previous_quarter.wacc) if previous_quarter.wacc else None,
            "revenue_yoy": float(previous_quarter.revenue_yoy) if previous_quarter.revenue_yoy else None,
            "gross_margin": float(previous_quarter.gross_margin) if previous_quarter.gross_margin else None,
            "fcf_margin": float(previous_quarter.fcf_margin) if previous_quarter.fcf_margin else None,
            "capex_ratio": float(previous_quarter.capex_ratio) if previous_quarter.capex_ratio else None
        }
    
    # 准备当前季度数据
    current_data = {
        "pe": float(quarter.pe) if quarter.pe else None,
        "pb": float(quarter.pb) if quarter.pb else None,
        "ps": float(quarter.ps) if quarter.ps else None,
        "roe": float(quarter.roe) if quarter.roe else None,
        "roic": float(quarter.roic) if quarter.roic else None,
        "wacc": float(quarter.wacc) if quarter.wacc else None,
        "revenue_yoy": float(quarter.revenue_yoy) if quarter.revenue_yoy else None,
        "gross_margin": float(quarter.gross_margin) if quarter.gross_margin else None,
        "fcf_margin": float(quarter.fcf_margin) if quarter.fcf_margin else None,
        "capex_ratio": float(quarter.capex_ratio) if quarter.capex_ratio else None
    }
    
    # 重新执行系统分析
    analysis_result = SystemAnalysisEngine.analyze(
        company_type=company.company_type,
        quarter_data=current_data,
        previous_quarter_data=prev_data if prev_data else None
    )
    
    # 更新或创建系统分析结果
    existing_analysis = db.query(models.SystemAnalysis)\
        .filter(models.SystemAnalysis.quarter_id == quarter_id)\
        .first()
    
    if existing_analysis:
        existing_analysis.quality_score = analysis_result["quality_score"]
        existing_analysis.valuation_score = analysis_result["valuation_score"]
        existing_analysis.trend_score = analysis_result["trend_score"]
        existing_analysis.labels = analysis_result["labels"]
        existing_analysis.system_summary = analysis_result["system_summary"]
    else:
        db_analysis = models.SystemAnalysis(
            quarter_id=quarter.id,
            quality_score=analysis_result["quality_score"],
            valuation_score=analysis_result["valuation_score"],
            trend_score=analysis_result["trend_score"],
            labels=analysis_result["labels"],
            system_summary=analysis_result["system_summary"]
        )
        db.add(db_analysis)
    
    db.commit()
    
    # 重新生成AI分析
    prompt = AIPromptGenerator.generate_quarter_prompt(
        company_name=company.company_name,
        company_type=company.company_type,
        quarter=quarter.quarter,
        quarter_data=current_data,
        labels=analysis_result["labels"]
    )
    
    ai_text = ai_service.generate_analysis(prompt)
    
    # 更新或创建AI分析
    existing_ai = db.query(models.QuarterAIAnalysis)\
        .filter(models.QuarterAIAnalysis.quarter_id == quarter_id)\
        .first()
    
    if existing_ai:
        existing_ai.analysis_text = ai_text
    else:
        db_ai_analysis = models.QuarterAIAnalysis(
            quarter_id=quarter.id,
            analysis_text=ai_text
        )
        db.add(db_ai_analysis)
    
    db.commit()
    
    # 检查是否需要更新综合AI分析
    update_comprehensive_ai_if_needed(db, quarter.company_id)
    
    return quarter


def delete_quarter(db: Session, quarter_id: int) -> bool:
    """删除季度数据"""
    quarter = db.query(models.Quarter).filter(models.Quarter.id == quarter_id).first()
    if not quarter:
        return False
    
    company_id = quarter.company_id
    db.delete(quarter)
    db.commit()
    
    # 删除后可能需要更新综合AI分析
    update_comprehensive_ai_if_needed(db, company_id)
    
    return True


# AI分析相关CRUD
def get_quarter_ai_analysis(db: Session, quarter_id: int) -> Optional[models.QuarterAIAnalysis]:
    """获取单季度AI分析"""
    return db.query(models.QuarterAIAnalysis)\
        .filter(models.QuarterAIAnalysis.quarter_id == quarter_id)\
        .first()


def generate_quarter_ai_analysis(db: Session, quarter_id: int) -> Optional[models.QuarterAIAnalysis]:
    """手动生成单季度AI分析"""
    quarter = db.query(models.Quarter).filter(models.Quarter.id == quarter_id).first()
    if not quarter:
        return None
    
    company = db.query(models.Company).filter(models.Company.id == quarter.company_id).first()
    if not company:
        return None
    
    system_analysis = db.query(models.SystemAnalysis)\
        .filter(models.SystemAnalysis.quarter_id == quarter_id)\
        .first()
    
    if not system_analysis:
        return None
    
    # 准备数据
    quarter_data = {
        "pe": float(quarter.pe) if quarter.pe else None,
        "pb": float(quarter.pb) if quarter.pb else None,
        "ps": float(quarter.ps) if quarter.ps else None,
        "roe": float(quarter.roe) if quarter.roe else None,
        "roic": float(quarter.roic) if quarter.roic else None,
        "wacc": float(quarter.wacc) if quarter.wacc else None,
        "revenue_yoy": float(quarter.revenue_yoy) if quarter.revenue_yoy else None,
        "gross_margin": float(quarter.gross_margin) if quarter.gross_margin else None,
        "fcf_margin": float(quarter.fcf_margin) if quarter.fcf_margin else None,
        "capex_ratio": float(quarter.capex_ratio) if quarter.capex_ratio else None
    }
    
    # 生成prompt并调用AI
    prompt = AIPromptGenerator.generate_quarter_prompt(
        company_name=company.company_name,
        company_type=company.company_type,
        quarter=quarter.quarter,
        quarter_data=quarter_data,
        labels=system_analysis.labels or []
    )
    
    ai_text = ai_service.generate_analysis(prompt)
    
    # 更新或创建AI分析
    existing_ai = db.query(models.QuarterAIAnalysis)\
        .filter(models.QuarterAIAnalysis.quarter_id == quarter_id)\
        .first()
    
    if existing_ai:
        existing_ai.analysis_text = ai_text
        db.commit()
        db.refresh(existing_ai)
        return existing_ai
    else:
        db_ai_analysis = models.QuarterAIAnalysis(
            quarter_id=quarter_id,
            analysis_text=ai_text
        )
        db.add(db_ai_analysis)
        db.commit()
        db.refresh(db_ai_analysis)
        return db_ai_analysis


def get_company_comprehensive_ai(db: Session, company_id: int) -> Optional[models.CompanyComprehensiveAI]:
    """获取公司综合AI分析"""
    return db.query(models.CompanyComprehensiveAI)\
        .filter(models.CompanyComprehensiveAI.company_id == company_id)\
        .first()


def generate_company_comprehensive_ai(db: Session, company_id: int) -> Optional[models.CompanyComprehensiveAI]:
    """生成公司综合AI分析（基于最近4个季度）"""
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        return None
    
    # 获取最近4个季度
    quarters = db.query(models.Quarter)\
        .filter(models.Quarter.company_id == company_id)\
        .order_by(desc(models.Quarter.quarter))\
        .limit(4)\
        .all()
    
    if len(quarters) == 0:
        return None
    
    # 准备数据
    quarters_summary = []
    for quarter in quarters:
        system_analysis = db.query(models.SystemAnalysis)\
            .filter(models.SystemAnalysis.quarter_id == quarter.id)\
            .first()
        
        ai_analysis = db.query(models.QuarterAIAnalysis)\
            .filter(models.QuarterAIAnalysis.quarter_id == quarter.id)\
            .first()
        
        quarters_summary.append({
            "quarter": quarter.quarter,
            "system_summary": system_analysis.system_summary if system_analysis else "",
            "ai_analysis": ai_analysis.analysis_text if ai_analysis else None
        })
    
    # 生成prompt
    prompt = AIPromptGenerator.generate_comprehensive_prompt(
        ticker=company.ticker,
        company_name=company.company_name,
        company_type=company.company_type,
        quarters_summary=quarters_summary
    )
    
    # 调用AI
    ai_response = ai_service.generate_analysis(prompt)
    
    # 解析结果
    parsed = ai_service.parse_comprehensive_analysis(ai_response)
    
    # 更新或创建综合AI分析
    existing = db.query(models.CompanyComprehensiveAI)\
        .filter(models.CompanyComprehensiveAI.company_id == company_id)\
        .first()
    
    based_quarters = [q["quarter"] for q in quarters_summary]
    
    if existing:
        existing.analysis_text = parsed["analysis_text"]
        existing.main_label = parsed["main_label"]
        existing.risk_label = parsed["risk_label"]
        existing.based_quarters = based_quarters
        db.commit()
        db.refresh(existing)
        return existing
    else:
        db_comprehensive = models.CompanyComprehensiveAI(
            company_id=company_id,
            analysis_text=parsed["analysis_text"],
            main_label=parsed["main_label"],
            risk_label=parsed["risk_label"],
            based_quarters=based_quarters
        )
        db.add(db_comprehensive)
        db.commit()
        db.refresh(db_comprehensive)
        return db_comprehensive


def update_comprehensive_ai_if_needed(db: Session, company_id: int):
    """如果需要，更新综合AI分析（当季度数据变化时）"""
    # 获取最新季度
    latest_quarter = db.query(models.Quarter)\
        .filter(models.Quarter.company_id == company_id)\
        .order_by(desc(models.Quarter.quarter))\
        .first()
    
    if not latest_quarter:
        return
    
    # 检查是否有至少4个季度
    quarter_count = db.query(models.Quarter)\
        .filter(models.Quarter.company_id == company_id)\
        .count()
    
    if quarter_count >= 4:
        # 异步或同步更新综合AI分析
        generate_company_comprehensive_ai(db, company_id)

