/** 类型定义 */

export type CompanyType =
  | 'TECH_PLATFORM'
  | 'TECH_MATURE'
  | 'PHARMA_INNOVATION'
  | 'PHARMA_MATURE'
  | 'FINANCIAL'
  | 'MANUFACTURING';

export const CompanyTypeLabels: Record<CompanyType, string> = {
  TECH_PLATFORM: '科技平台型',
  TECH_MATURE: '科技成熟型',
  PHARMA_INNOVATION: '医药创新型',
  PHARMA_MATURE: '医药成熟型',
  FINANCIAL: '金融型',
  MANUFACTURING: '制造业型',
};

export interface Company {
  id: number;
  ticker: string;
  company_name: string;
  company_type: CompanyType;
  created_at: string;
  updated_at: string;
}

export interface Quarter {
  id: number;
  company_id: number;
  quarter: string;
  pe?: number;
  pb?: number;
  ps?: number;
  roe?: number;
  roic?: number;
  wacc?: number;
  revenue_yoy?: number;
  gross_margin?: number;
  fcf_margin?: number;
  capex_ratio?: number;
  created_at: string;
}

export interface SystemAnalysis {
  id: number;
  quarter_id: number;
  quality_score?: number;
  valuation_score?: number;
  trend_score?: number;
  labels?: string[];
  system_summary?: string;
  created_at: string;
}

export interface QuarterAIAnalysis {
  id: number;
  quarter_id: number;
  analysis_text: string;
  created_at: string;
}

export interface CompanyComprehensiveAI {
  id: number;
  company_id: number;
  analysis_text?: string;
  main_label?: string;
  risk_label?: string;
  based_quarters?: string[];
  updated_at: string;
}

export interface CompanyCard {
  id: number;
  ticker: string;
  company_name: string;
  company_type: CompanyType;
  latest_quarter?: string;
  latest_roic?: number;
  latest_wacc?: number;
  latest_valuation_score?: number;
  latest_labels?: string[];
  comprehensive_ai?: CompanyComprehensiveAI;
}

export interface CompanyDetail extends Company {
  quarters: Array<Quarter & {
    system_analysis?: SystemAnalysis;
    ai_analysis?: QuarterAIAnalysis;
  }>;
  comprehensive_ai?: CompanyComprehensiveAI;
}

