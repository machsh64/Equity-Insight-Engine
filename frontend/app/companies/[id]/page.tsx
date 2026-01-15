'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { companyApi, quarterApi } from '@/lib/api';
import { CompanyDetail, CompanyTypeLabels } from '@/lib/types';
import QuarterCard from '@/components/QuarterCard';
import AddQuarterModal from '@/components/AddQuarterModal';
import EditCompanyModal from '@/components/EditCompanyModal';

export default function CompanyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const companyId = parseInt(params.id as string);

  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    if (companyId) {
      loadCompany();
    }
  }, [companyId]);

  const loadCompany = async () => {
    try {
      setLoading(true);
      const response = await companyApi.getById(companyId);
      setCompany(response.data);
    } catch (error) {
      console.error('加载公司详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddQuarter = () => {
    setShowAddModal(true);
  };

  const handleQuarterAdded = () => {
    setShowAddModal(false);
    loadCompany();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">公司不存在</p>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            返回首页
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/')}
            className="mb-4 text-blue-600 hover:text-blue-800"
          >
            ← 返回首页
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{company.ticker}</h1>
              <p className="text-lg text-gray-600 mt-1">{company.company_name}</p>
              <span className="inline-block mt-2 px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded">
                {CompanyTypeLabels[company.company_type]}
              </span>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowEditModal(true)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                编辑公司
              </button>
              <button
                onClick={handleAddQuarter}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                + 新增季度
              </button>
            </div>
          </div>
        </div>

        {/* 综合AI分析 */}
        {company.comprehensive_ai && (
          <div className="mb-8 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">综合AI分析</h2>
            {company.comprehensive_ai.main_label && (
              <div className="mb-2">
                <span className="px-3 py-1 text-sm bg-indigo-100 text-indigo-800 rounded font-semibold">
                  {company.comprehensive_ai.main_label}
                </span>
              </div>
            )}
            {company.comprehensive_ai.risk_label && (
              <div className="mb-4">
                <span className="px-3 py-1 text-sm bg-red-100 text-red-800 rounded">
                  风险: {company.comprehensive_ai.risk_label}
                </span>
              </div>
            )}
            {company.comprehensive_ai.analysis_text && (
              <p className="text-gray-700 leading-relaxed">
                {company.comprehensive_ai.analysis_text}
              </p>
            )}
          </div>
        )}

        {/* 季度列表 */}
        <div>
          <h2 className="text-2xl font-bold mb-4">季度数据</h2>
          {company.quarters.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow-md">
              <p className="text-gray-600 mb-4">暂无季度数据</p>
              <button
                onClick={handleAddQuarter}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                添加第一个季度
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {company.quarters.map((quarter) => (
                <QuarterCard
                  key={quarter.id}
                  quarter={quarter}
                  onUpdate={loadCompany}
                />
              ))}
            </div>
          )}
        </div>

        {showAddModal && (
          <AddQuarterModal
            companyId={companyId}
            onClose={() => setShowAddModal(false)}
            onSuccess={handleQuarterAdded}
          />
        )}

        {showEditModal && company && (
          <EditCompanyModal
            company={company}
            onClose={() => setShowEditModal(false)}
            onSuccess={() => {
              setShowEditModal(false);
              loadCompany();
            }}
          />
        )}
      </div>
    </div>
  );
}

