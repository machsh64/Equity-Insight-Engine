'use client';

import { useState } from 'react';
import { Quarter, SystemAnalysis, QuarterAIAnalysis } from '@/lib/types';
import EditQuarterModal from './EditQuarterModal';
import { quarterApi } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

interface Props {
  quarter: Quarter & {
    system_analysis?: SystemAnalysis;
    ai_analysis?: QuarterAIAnalysis;
  };
  onUpdate: () => void;
}

export default function QuarterCard({ quarter, onUpdate }: Props) {
  const [showSystemSummary, setShowSystemSummary] = useState(false);
  const [showAIAnalysis, setShowAIAnalysis] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [regeneratingAI, setRegeneratingAI] = useState(false);

  const handleRegenerateAI = async () => {
    try {
      setRegeneratingAI(true);
      await quarterApi.generateAI(quarter.id);
      // 重新加载数据
      onUpdate();
    } catch (error) {
      console.error('重新生成AI分析失败:', error);
      alert('重新生成AI分析失败，请稍后重试');
    } finally {
      setRegeneratingAI(false);
    }
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-md p-6 text-gray-900">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-xl font-bold text-gray-900">{quarter.quarter}</h3>
          <div className="flex items-center gap-3">
            {quarter.system_analysis?.labels && quarter.system_analysis.labels.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {quarter.system_analysis.labels.map((label, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                  >
                    {label}
                  </span>
                ))}
              </div>
            )}
            <button
              onClick={() => setShowEditModal(true)}
              className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              编辑
            </button>
          </div>
        </div>

        {/* 关键指标表格：两行展示（第一行指标，第二行数值） */}
        <div className="mb-4 overflow-x-auto">
          <table className="min-w-full text-sm">
            <tbody>
              <tr className="bg-gray-50">
                <td className="px-4 py-2 text-xs text-gray-500">指标</td>
                {quarter.pe !== null && quarter.pe !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-700">PE</td>
                )}
                {quarter.pb !== null && quarter.pb !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-700">PB</td>
                )}
                {quarter.ps !== null && quarter.ps !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-700">PS</td>
                )}
                {quarter.roic !== null && quarter.roic !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-700">ROIC</td>
                )}
                {quarter.wacc !== null && quarter.wacc !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-700">WACC</td>
                )}
                {quarter.roe !== null && quarter.roe !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-700">ROE</td>
                )}
                {quarter.fcf_margin !== null && quarter.fcf_margin !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-700">FCF%</td>
                )}
                {quarter.capex_ratio !== null && quarter.capex_ratio !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-700">CapEx%</td>
                )}
              </tr>
              <tr>
                <td className="px-4 py-2 text-xs text-gray-500">数值</td>
                {quarter.pe !== null && quarter.pe !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-900">{quarter.pe.toFixed(2)}</td>
                )}
                {quarter.pb !== null && quarter.pb !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-900">{quarter.pb.toFixed(2)}</td>
                )}
                {quarter.ps !== null && quarter.ps !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-900">{quarter.ps.toFixed(2)}</td>
                )}
                {quarter.roic !== null && quarter.roic !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-900">
                    {quarter.roic.toFixed(2)}%
                  </td>
                )}
                {quarter.wacc !== null && quarter.wacc !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-900">
                    {quarter.wacc.toFixed(2)}%
                  </td>
                )}
                {quarter.roe !== null && quarter.roe !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-900">
                    {quarter.roe.toFixed(2)}%
                  </td>
                )}
                {quarter.fcf_margin !== null && quarter.fcf_margin !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-900">
                    {quarter.fcf_margin.toFixed(2)}%
                  </td>
                )}
                {quarter.capex_ratio !== null && quarter.capex_ratio !== undefined && (
                  <td className="px-4 py-2 text-center text-gray-900">
                    {quarter.capex_ratio.toFixed(2)}%
                  </td>
                )}
              </tr>
            </tbody>
          </table>
        </div>

      {/* 系统分析 */}
      {quarter.system_analysis && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-gray-700">系统分析</h4>
            <button
              onClick={() => setShowSystemSummary(!showSystemSummary)}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              {showSystemSummary ? '收起' : '展开详细'}
            </button>
          </div>
      
          {showSystemSummary && quarter.system_analysis.system_summary && (
            <div className="mt-2 p-3 bg-gray-50 rounded text-sm whitespace-pre-line">
              {quarter.system_analysis.system_summary}
            </div>
          )}

          <div className="mt-2 flex gap-6 text-sm items-center">
            {/* 质量得分 + tooltip */}
            {quarter.system_analysis.quality_score !== null && (
              <div className="group relative inline-flex items-center gap-1">
                {quarter.system_analysis.quality_score != null && (
                  <span>
                    质量: {quarter.system_analysis.quality_score.toFixed(1)}
                  </span>
                )}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-80 p-3 bg-gray-800 text-white text-xs rounded shadow-lg z-10 pointer-events-none">
                  <div className="font-semibold mb-1">质量得分解读（0-100）</div>
                  <ul className="list-disc pl-4 space-y-1">
                    <li><strong>80-100</strong>：高质量 — 强劲价值创造（高ROIC、毛利率、FCF）</li>
                    <li><strong>50-80</strong>：中等 — 基本面稳定但价值创造有限</li>
                    <li><strong>0-50</strong>：低质量 — 盈利能力弱或扩张早期</li>
                  </ul>
                </div>
              </div>
            )}

            {/* 估值得分 + tooltip */}
            {quarter.system_analysis.valuation_score !== null && (
              <div className="group relative inline-flex items-center gap-1">
                {quarter.system_analysis.valuation_score != null && (
                  <span>
                    估值: {quarter.system_analysis.valuation_score.toFixed(1)}
                  </span>
                )}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-80 p-3 bg-gray-800 text-white text-xs rounded shadow-lg z-10 pointer-events-none">
                  <div className="font-semibold mb-1">估值状态解读（越高越便宜）</div>
                  <ul className="list-disc pl-4 space-y-1">
                    <li><strong>70-100</strong>：低估值 — 吸引价值投资者</li>
                    <li><strong>40-70</strong>：中等估值 — 合理但无明显安全边际</li>
                    <li><strong>0-40</strong>：高估值 — 成长溢价，常见于科技高峰期</li>
                  </ul>
                </div>
              </div>
            )}

            {/* 趋势得分 + tooltip */}
            {quarter.system_analysis.trend_score !== null && (
              <div className="group relative inline-flex items-center gap-1">
                {quarter.system_analysis.trend_score != null && (
                  <span>
                    趋势: {quarter.system_analysis.trend_score.toFixed(1)}
                  </span>
                )}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-80 p-3 bg-gray-800 text-white text-xs rounded shadow-lg z-10 pointer-events-none">
                  <div className="font-semibold mb-1">趋势得分解读（0-100）</div>
                  <ul className="list-disc pl-4 space-y-1">
                    <li><strong>70-100</strong>：积极趋势 — 指标显著改善</li>
                    <li><strong>30-70</strong>：中性 — 变化较小或混合</li>
                    <li><strong>0-30</strong>：走弱 — 基本面恶化，需警惕</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI分析 */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-semibold text-gray-700">AI分析</h4>
          <div className="flex items-center gap-3">
            {quarter.ai_analysis && (
              <button
                onClick={() => setShowAIAnalysis(!showAIAnalysis)}
                className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
              >
                {showAIAnalysis ? '收起' : '查看AI分析'}
              </button>
            )}
            <button
              onClick={handleRegenerateAI}
              disabled={regeneratingAI}
              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {regeneratingAI ? '生成中...' : quarter.ai_analysis ? '重新分析' : '生成AI分析'}
            </button>
          </div>
        </div>
          
        {/* 有AI分析且展开时：完美渲染 Markdown */}
        {quarter.ai_analysis && showAIAnalysis && (
          <div className="mt-3 overflow-hidden rounded-lg border border-blue-100 bg-blue-50/70">
            <div className="prose prose-sm max-w-none p-5 text-gray-800 
                            prose-headings:font-semibold prose-headings:text-gray-900
                            prose-strong:text-gray-900 prose-em:text-blue-700
                            prose-ul:space-y-1 prose-ol:space-y-1
                            prose-li:my-0.5
                            prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:rounded prose-pre:p-3
                            prose-table:text-xs prose-table:border prose-table:border-gray-300
                            prose-th:bg-gray-100 prose-th:text-left prose-td:py-2 prose-td:px-3">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]} 
                rehypePlugins={[rehypeRaw]}
              >
                {quarter.ai_analysis.analysis_text}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* 无AI分析时 */}
        {!quarter.ai_analysis && (
          <div className="mt-3 p-5 bg-gray-50 rounded-lg border border-gray-200 text-sm text-gray-500 text-center">
            暂无AI分析，点击右上角「生成AI分析」按钮即可生成
          </div>
        )}
      </div>
      </div>

      {showEditModal && (
        <EditQuarterModal
          quarter={quarter}
          onClose={() => setShowEditModal(false)}
          onSuccess={() => {
            setShowEditModal(false);
            onUpdate();
          }}
        />
      )}
    </>
  );
}

