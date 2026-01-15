'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { companyApi } from '@/lib/api';
import { CompanyCard, CompanyTypeLabels } from '@/lib/types';
import CompanyCardComponent from '@/components/CompanyCard';
import AddCompanyModal from '@/components/AddCompanyModal';

export default function HomePage() {
  const router = useRouter();
  const [companies, setCompanies] = useState<CompanyCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      setLoading(true);
      const response = await companyApi.getAll();
      setCompanies(response.data);
    } catch (error) {
      console.error('加载公司列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCompany = () => {
    setShowAddModal(true);
  };

  const handleCompanyAdded = () => {
    setShowAddModal(false);
    loadCompanies();
  };

  const handleCardClick = (companyId: number) => {
    router.push(`/companies/${companyId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Equity Insight Engine</h1>
          <button
            onClick={handleAddCompany}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + 添加股票
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <p className="mt-4 text-gray-600">加载中...</p>
          </div>
        ) : companies.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">暂无股票数据</p>
            <button
              onClick={handleAddCompany}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              添加第一个股票
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {companies.map((company) => (
              <CompanyCardComponent
                key={company.id}
                company={company}
                onClick={() => handleCardClick(company.id)}
              />
            ))}
          </div>
        )}

        {showAddModal && (
          <AddCompanyModal
            onClose={() => setShowAddModal(false)}
            onSuccess={handleCompanyAdded}
          />
        )}
      </div>
    </div>
  );
}

