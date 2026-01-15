'use client';

import { CompanyCard as CompanyCardType, CompanyTypeLabels } from '@/lib/types';

interface Props {
  company: CompanyCardType;
  onClick: () => void;
}

export default function CompanyCardComponent({ company, onClick }: Props) {
  const roicWaccDiff = company.latest_roic && company.latest_wacc
    ? company.latest_roic - company.latest_wacc
    : null;

  const getRoicWaccLabel = () => {
    if (roicWaccDiff === null) return '数据不足';
    if (roicWaccDiff >= 8) return '强价值创造';
    if (roicWaccDiff >= 3) return '价值创造';
    if (roicWaccDiff >= 0) return '微弱价值创造';
    if (roicWaccDiff >= -5) return '扩张期正常';
    return '高资本消耗';
  };

  const getValuationLabel = () => {
    if (!company.latest_valuation_score) return null;
    const score = company.latest_valuation_score;
    if (score >= 70) return '估值合理';
    if (score >= 40) return '估值适中';
    return '高估值';
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow-md p-6 cursor-pointer hover:shadow-lg transition-shadow"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{company.ticker}</h3>
          <p className="text-sm text-gray-600 mt-1">{company.company_name}</p>
        </div>
        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
          {CompanyTypeLabels[company.company_type]}
        </span>
      </div>

      {company.latest_quarter && (
        <div className="mb-4">
          <p className="text-sm text-gray-500">最新季度: {company.latest_quarter}</p>
          {roicWaccDiff !== null && (
            <div className="mt-2">
              <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                {getRoicWaccLabel()}
              </span>
            </div>
          )}
        </div>
      )}

      {company.latest_valuation_score !== null && (
        <div className="mb-4">
          <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
            {getValuationLabel()}
          </span>
        </div>
      )}

      {company.latest_labels && company.latest_labels.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {company.latest_labels.map((label, idx) => (
            <span
              key={idx}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
            >
              {label}
            </span>
          ))}
        </div>
      )}

      {company.comprehensive_ai && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          {company.comprehensive_ai.main_label && (
            <div className="mb-2">
              <span className="px-2 py-1 text-xs bg-indigo-100 text-indigo-800 rounded font-semibold">
                {company.comprehensive_ai.main_label}
              </span>
            </div>
          )}
          {company.comprehensive_ai.risk_label && (
            <div>
              <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">
                风险: {company.comprehensive_ai.risk_label}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

