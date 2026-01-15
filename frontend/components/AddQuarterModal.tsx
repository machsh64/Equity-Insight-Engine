'use client';

import { useState } from 'react';
import { quarterApi } from '@/lib/api';

interface Props {
  companyId: number;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AddQuarterModal({ companyId, onClose, onSuccess }: Props) {
  const [formData, setFormData] = useState({
    quarter: '',
    pe: '',
    pb: '',
    ps: '',
    roe: '',
    roic: '',
    wacc: '',
    revenue_yoy: '',
    gross_margin: '',
    fcf_margin: '',
    capex_ratio: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data: any = {
        company_id: companyId,
        quarter: formData.quarter,
      };

      // 只添加非空字段
      if (formData.pe) data.pe = parseFloat(formData.pe);
      if (formData.pb) data.pb = parseFloat(formData.pb);
      if (formData.ps) data.ps = parseFloat(formData.ps);
      if (formData.roe) data.roe = parseFloat(formData.roe);
      if (formData.roic) data.roic = parseFloat(formData.roic);
      if (formData.wacc) data.wacc = parseFloat(formData.wacc);
      if (formData.revenue_yoy) data.revenue_yoy = parseFloat(formData.revenue_yoy);
      if (formData.gross_margin) data.gross_margin = parseFloat(formData.gross_margin);
      if (formData.fcf_margin) data.fcf_margin = parseFloat(formData.fcf_margin);
      if (formData.capex_ratio) data.capex_ratio = parseFloat(formData.capex_ratio);

      await quarterApi.create(data);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || '创建失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl my-8 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">新增季度数据</h2>

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                季度 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.quarter}
                onChange={(e) => handleChange('quarter', e.target.value)}
                placeholder="2024-Q3"
                pattern="^\d{4}-Q[1-4]$"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">PE</label>
              <input
                type="number"
                step="0.01"
                value={formData.pe}
                onChange={(e) => handleChange('pe', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">PB</label>
              <input
                type="number"
                step="0.01"
                value={formData.pb}
                onChange={(e) => handleChange('pb', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">PS</label>
              <input
                type="number"
                step="0.01"
                value={formData.ps}
                onChange={(e) => handleChange('ps', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">ROE (%)</label>
              <input
                type="number"
                step="0.01"
                value={formData.roe}
                onChange={(e) => handleChange('roe', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">ROIC (%)</label>
              <input
                type="number"
                step="0.01"
                value={formData.roic}
                onChange={(e) => handleChange('roic', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">WACC (%)</label>
              <input
                type="number"
                step="0.01"
                value={formData.wacc}
                onChange={(e) => handleChange('wacc', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">收入同比 (%)</label>
              <input
                type="number"
                step="0.01"
                value={formData.revenue_yoy}
                onChange={(e) => handleChange('revenue_yoy', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">毛利率 (%)</label>
              <input
                type="number"
                step="0.01"
                value={formData.gross_margin}
                onChange={(e) => handleChange('gross_margin', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">自由现金流率 (%)</label>
              <input
                type="number"
                step="0.01"
                value={formData.fcf_margin}
                onChange={(e) => handleChange('fcf_margin', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">CapEx/收入 (%)</label>
              <input
                type="number"
                step="0.01"
                value={formData.capex_ratio}
                onChange={(e) => handleChange('capex_ratio', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
              {error}
            </div>
          )}

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              disabled={loading}
            >
              取消
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? '创建中...' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

