/** API客户端 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: "/api/",
  headers: {
    'Content-Type': 'application/json',
  },
});

// 公司相关API
export const companyApi = {
  getAll: () => api.get('/companies'),
  getById: (id: number) => api.get(`/companies/${id}`),
  create: (data: { ticker: string; company_name: string; company_type: string }) =>
    api.post('/companies', data),
  update: (id: number, data: { ticker?: string; company_name?: string; company_type?: string }) =>
    api.put(`/companies/${id}`, data),
  delete: (id: number) => api.delete(`/companies/${id}`),
};

// 季度数据相关API
export const quarterApi = {
  create: (data: {
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
  }) => api.post('/quarters', data),
  update: (id: number, data: {
    quarter?: string;
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
  }) => api.put(`/quarters/${id}`, data),
  getById: (id: number) => api.get(`/quarters/${id}`),
  delete: (id: number) => api.delete(`/quarters/${id}`),
  getAI: (id: number) => api.get(`/quarters/${id}/ai`),
  generateAI: (id: number) => api.post(`/quarters/${id}/ai/generate`),
};

// 综合AI分析API
export const comprehensiveAIApi = {
  get: (companyId: number) => api.get(`/companies/${companyId}/comprehensive-ai`),
  generate: (companyId: number) => api.post(`/companies/${companyId}/comprehensive-ai/generate`),
};

export default api;

