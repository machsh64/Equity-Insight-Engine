"""FastAPI主应用"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import crud
import schemas
from database import get_db, engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Equity Insight Engine API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Equity Insight Engine API"}


# 公司相关API
@app.post("/api/companies", response_model=schemas.CompanyResponse)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    """创建公司"""
    return crud.create_company(db, company)


@app.get("/api/companies", response_model=List[schemas.CompanyCardResponse])
def get_companies(db: Session = Depends(get_db)):
    """获取所有公司（首页卡片数据）"""
    return crud.get_companies_with_summary(db)


@app.get("/api/companies/{company_id}", response_model=schemas.CompanyDetailResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """获取公司详情（包含所有季度数据）"""
    company = crud.get_company_detail(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")
    return company


@app.put("/api/companies/{company_id}", response_model=schemas.CompanyResponse)
def update_company(company_id: int, company_update: schemas.CompanyUpdate, db: Session = Depends(get_db)):
    """更新公司信息"""
    company = crud.update_company(db, company_id, company_update)
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")
    return company


@app.delete("/api/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """删除公司"""
    success = crud.delete_company(db, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="公司不存在")
    return {"message": "删除成功"}


# 季度数据相关API
@app.post("/api/quarters", response_model=schemas.QuarterResponse)
def create_quarter(quarter: schemas.QuarterCreate, db: Session = Depends(get_db)):
    """创建季度数据（会自动触发系统分析和AI分析）"""
    return crud.create_quarter_with_analysis(db, quarter)


@app.get("/api/quarters/{quarter_id}", response_model=schemas.QuarterDetailResponse)
def get_quarter(quarter_id: int, db: Session = Depends(get_db)):
    """获取季度详情"""
    quarter = crud.get_quarter_detail(db, quarter_id)
    if not quarter:
        raise HTTPException(status_code=404, detail="季度数据不存在")
    return quarter


@app.put("/api/quarters/{quarter_id}", response_model=schemas.QuarterResponse)
def update_quarter(quarter_id: int, quarter_update: schemas.QuarterUpdate, db: Session = Depends(get_db)):
    """更新季度数据（会自动重新触发系统分析和AI分析）"""
    quarter = crud.update_quarter_with_analysis(db, quarter_id, quarter_update)
    if not quarter:
        raise HTTPException(status_code=404, detail="季度数据不存在")
    return quarter


@app.delete("/api/quarters/{quarter_id}")
def delete_quarter(quarter_id: int, db: Session = Depends(get_db)):
    """删除季度数据"""
    success = crud.delete_quarter(db, quarter_id)
    if not success:
        raise HTTPException(status_code=404, detail="季度数据不存在")
    return {"message": "删除成功"}


# AI分析相关API
@app.get("/api/quarters/{quarter_id}/ai", response_model=schemas.QuarterAIAnalysisResponse)
def get_quarter_ai(quarter_id: int, db: Session = Depends(get_db)):
    """获取单季度AI分析"""
    ai_analysis = crud.get_quarter_ai_analysis(db, quarter_id)
    if not ai_analysis:
        raise HTTPException(status_code=404, detail="AI分析不存在")
    return ai_analysis


@app.post("/api/quarters/{quarter_id}/ai/generate")
def generate_quarter_ai(quarter_id: int, db: Session = Depends(get_db)):
    """手动触发生成单季度AI分析"""
    result = crud.generate_quarter_ai_analysis(db, quarter_id)
    if not result:
        raise HTTPException(status_code=404, detail="季度数据不存在")
    return {"message": "AI分析生成成功", "analysis": result}


@app.get("/api/companies/{company_id}/comprehensive-ai", response_model=schemas.CompanyComprehensiveAIResponse)
def get_comprehensive_ai(company_id: int, db: Session = Depends(get_db)):
    """获取公司综合AI分析"""
    ai = crud.get_company_comprehensive_ai(db, company_id)
    if not ai:
        raise HTTPException(status_code=404, detail="综合AI分析不存在")
    return ai


@app.post("/api/companies/{company_id}/comprehensive-ai/generate")
def generate_comprehensive_ai(company_id: int, db: Session = Depends(get_db)):
    """手动触发生成公司综合AI分析"""
    result = crud.generate_company_comprehensive_ai(db, company_id)
    if not result:
        raise HTTPException(status_code=404, detail="公司不存在或季度数据不足")
    return {"message": "综合AI分析生成成功", "analysis": result}

