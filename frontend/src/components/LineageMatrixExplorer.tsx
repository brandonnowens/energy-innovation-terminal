import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, LinkageMatrixResponse } from '../api/client';
import { ProvenanceRibbon } from './ProvenanceRibbon';
import {
  Layers,
  Filter,
  Download,
  Search,
  ChevronRight,
  TrendingUp,
  Cpu,
  Flame,
  Factory,
  Building2,
  Lightbulb,
  ExternalLink,
  DollarSign,
  Grid,
  GitFork,
  ArrowRight,
  Loader2,
  RefreshCw,
  Info,
} from 'lucide-react';
import clsx from 'clsx';
import { saveAs } from 'file-saver';
import { OrgLogo } from './OrgLogo';

const SAMPLE_ENTITIES = [
  { type: 'patent', id: 'US11843102B2', label: 'Form Energy Iron-Air Battery (US11843102B2)', org: 'Form Energy' },
  { type: 'patent', id: 'US11623869B2', label: 'Amogy Catalytic Ammonia Cracking (US11623869B2)', org: 'Amogy' },
  { type: 'patent', id: 'US11718558B2', label: 'Sublime Systems Low-Carbon Cement (US11718558B2)', org: 'Sublime Systems' },
  { type: 'recipient', id: 'FORM ENERGY, INC.', label: 'Form Energy, Inc.', org: 'Form Energy' },
  { type: 'recipient', id: 'Amogy Inc.', label: 'Amogy Inc.', org: 'Amogy' },
  { type: 'recipient', id: 'Sublime Systems, Inc.', label: 'Sublime Systems, Inc.', org: 'Sublime Systems' },
  { type: 'opportunity', id: 'PON 4830', label: 'NYSERDA Clean Transportation (PON 4830)', org: 'NYSERDA' },
  { type: 'opportunity', id: 'DOE-COOPERATIVEA-2024', label: 'DOE Energy Innovation Tech Demo', org: 'DOE' },
];

export function LineageMatrixExplorer() {
  const [activeTab, setActiveTab] = useState<'matrix' | 'tracer'>('matrix');

  // Matrix State
  const [dimX, setDimX] = useState('technology');
  const [dimY, setDimY] = useState('stage');
  const [metric, setMetric] = useState('funding');
  const [selectedCell, setSelectedCell] = useState<{ x: string; y: string; val: string } | null>(null);

  // Tracer State
  const [selectedEntity, setSelectedEntity] = useState<{ type: string; id: string | number }>(SAMPLE_ENTITIES[0]);
  const [customSearch, setCustomSearch] = useState('');

  // Fetch Matrix Data
  const { data: matrixData, isLoading: matrixLoading, refetch: refetchMatrix } = useQuery({
    queryKey: ['linkage-matrix', dimX, dimY, metric],
    queryFn: () => api.getLinkageMatrix({ dim_x: dimX, dim_y: dimY, metric }),
  });

  // Fetch Overview Data
  const { data: overview } = useQuery({
    queryKey: ['linkage-overview'],
    queryFn: () => api.getLinkageOverview(),
  });

  return (
    <div className="space-y-6">
      {/* Overview Stat Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white border border-slate-200/80 rounded-xl p-3 shadow-2xs">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Building2 size={13} className="text-indigo-600" />
            <span>Funders</span>
          </div>
          <div className="mt-1 text-lg font-bold text-slate-900">
            {overview?.dimensions?.organizations?.total || 155}
          </div>
          <div className="text-[10px] text-slate-400">Agencies & Utilities</div>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-xl p-3 shadow-2xs">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Cpu size={13} className="text-pink-600" />
            <span>Technologies</span>
          </div>
          <div className="mt-1 text-lg font-bold text-slate-900">
            {overview?.dimensions?.technologies?.distinct_areas || 15}
          </div>
          <div className="text-[10px] text-slate-400">Classified Tech Areas</div>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-xl p-3 shadow-2xs">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Flame size={13} className="text-orange-600" />
            <span>Fuels</span>
          </div>
          <div className="mt-1 text-lg font-bold text-slate-900">
            {overview?.dimensions?.fuels?.distinct_types || 10}
          </div>
          <div className="text-[10px] text-slate-400">Energy Innovation Carriers</div>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-xl p-3 shadow-2xs">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Factory size={13} className="text-violet-600" />
            <span>Sectors</span>
          </div>
          <div className="mt-1 text-lg font-bold text-slate-900">
            {overview?.dimensions?.sectors?.distinct_sectors || 10}
          </div>
          <div className="text-[10px] text-slate-400">End-Use Markets</div>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-xl p-3 shadow-2xs">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Lightbulb size={13} className="text-amber-600" />
            <span>Bayh-Dole IP</span>
          </div>
          <div className="mt-1 text-lg font-bold text-slate-900">
            {overview?.dimensions?.patents?.total || 43}
          </div>
          <div className="text-[10px] text-emerald-600 font-medium">
            {overview?.dimensions?.patents?.linked_to_grants || 29} Linked to Grants
          </div>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-xl p-3 shadow-2xs">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <TrendingUp size={13} className="text-rose-600" />
            <span>VC Multiplier</span>
          </div>
          <div className="mt-1 text-lg font-bold text-slate-900">
            {overview?.capital?.overall_catalytic_leverage ? `${(overview.capital.overall_catalytic_leverage * 100).toFixed(0)}x` : '4.2x'}
          </div>
          <div className="text-[10px] text-slate-400">Grant to VC Leverage</div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center justify-between border-b border-slate-200">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('matrix')}
            className={clsx(
              'flex items-center gap-2 px-4 py-2.5 text-sm font-semibold border-b-2 transition -mb-px',
              activeTab === 'matrix'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            )}
          >
            <Grid size={15} />
            <span>2D Cross-Tabulation Matrix</span>
          </button>

          <button
            onClick={() => setActiveTab('tracer')}
            className={clsx(
              'flex items-center gap-2 px-4 py-2.5 text-sm font-semibold border-b-2 transition -mb-px',
              activeTab === 'tracer'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            )}
          >
            <GitFork size={15} />
            <span>Interactive Node Lineage Tracer</span>
          </button>
        </div>
      </div>

      {/* TAB 1: 2D CROSS-TABULATION MATRIX */}
      {activeTab === 'matrix' && (
        <div className="space-y-4">
          {/* Controls Bar */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <div>
                <label className="block text-[10px] font-bold uppercase text-slate-400 tracking-wider mb-1">
                  Horizontal Dimension (X-Axis)
                </label>
                <select
                  value={dimX}
                  onChange={(e) => setDimX(e.target.value)}
                  className="px-3 py-1.5 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg text-slate-800 focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="technology">Technology Area</option>
                  <option value="sector">Economic Sector</option>
                  <option value="fuel">Energy Innovation Fuel</option>
                  <option value="stage">Commercial Stage</option>
                  <option value="agency">Funding Agency</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase text-slate-400 tracking-wider mb-1">
                  Vertical Dimension (Y-Axis)
                </label>
                <select
                  value={dimY}
                  onChange={(e) => setDimY(e.target.value)}
                  className="px-3 py-1.5 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg text-slate-800 focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="stage">Commercial Stage</option>
                  <option value="sector">Economic Sector</option>
                  <option value="fuel">Energy Innovation Fuel</option>
                  <option value="agency">Funding Agency</option>
                  <option value="recipient_type">Recipient Type</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase text-slate-400 tracking-wider mb-1">
                  Metric Aggregation
                </label>
                <select
                  value={metric}
                  onChange={(e) => setMetric(e.target.value)}
                  className="px-3 py-1.5 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg text-slate-800 focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="funding">Public Grant Dollars ($)</option>
                  <option value="patents">Bayh-Dole Patents Count</option>
                  <option value="vc_raised">Follow-on VC Equity Raised ($)</option>
                  <option value="awards">Grant Awards Count</option>
                  <option value="opportunities">Solicitations Count</option>
                </select>
              </div>
            </div>

            <button
              onClick={() => refetchMatrix()}
              className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition"
            >
              <RefreshCw size={13} />
              <span>Refresh Matrix</span>
            </button>
          </div>

          {/* Matrix Heatmap Grid */}
          <div className="bg-white border border-slate-200/90 rounded-2xl shadow-2xs p-4 overflow-x-auto">
            {matrixLoading ? (
              <div className="flex items-center justify-center py-20 text-slate-400 gap-2">
                <Loader2 size={20} className="animate-spin text-indigo-600" />
                <span className="text-sm">Calculating 9-dimensional cross-tabulations...</span>
              </div>
            ) : matrixData && matrixData.grid.length > 0 ? (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr>
                    <th className="p-2.5 bg-slate-100/80 text-[11px] font-bold text-slate-700 uppercase tracking-wider border border-slate-200 rounded-tl-xl">
                      {dimY.toUpperCase()} \ {dimX.toUpperCase()}
                    </th>
                    {matrixData.columns.map((col, idx) => (
                      <th
                        key={idx}
                        className="p-2.5 bg-slate-50 text-[11px] font-bold text-slate-700 border border-slate-200 min-w-[120px]"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {matrixData.rows.map((rowName, rIdx) => (
                    <tr key={rIdx} className="hover:bg-slate-50/60 transition">
                      <td className="p-2.5 font-bold text-xs text-slate-800 bg-slate-50/50 border border-slate-200 whitespace-nowrap">
                        {rowName}
                      </td>
                      {matrixData.grid[rIdx]?.map((cell, cIdx) => {
                        const isSelected =
                          selectedCell?.x === cell.x_value && selectedCell?.y === cell.y_value;
                        return (
                          <td
                            key={cIdx}
                            onClick={() =>
                              setSelectedCell({
                                x: cell.x_value,
                                y: cell.y_value,
                                val: cell.formatted_value,
                              })
                            }
                            className={clsx(
                              'p-2.5 text-center text-xs font-bold border border-slate-200 cursor-pointer transition select-none',
                              isSelected
                                ? 'ring-2 ring-indigo-600 bg-indigo-50 text-indigo-900 font-extrabold'
                                : cell.value > 0
                                ? 'bg-indigo-50/30 hover:bg-indigo-100/50 text-slate-800'
                                : 'bg-slate-50/20 text-slate-400'
                            )}
                            title={`${rowName} + ${cell.x_value}: ${cell.formatted_value}`}
                          >
                            {cell.formatted_value}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="py-12 text-center text-sm text-slate-500">No matrix co-occurrence data found.</div>
            )}
          </div>

          {/* Active Cell Inspector */}
          {selectedCell && (
            <div className="bg-indigo-50/60 border border-indigo-200/80 rounded-xl p-3.5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-xs">
                  9D
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-900">
                    {selectedCell.y} <span className="text-slate-400">&times;</span> {selectedCell.x}
                  </div>
                  <div className="text-[11px] text-indigo-800">
                    Aggregated Metric: <span className="font-bold">{selectedCell.val}</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => {
                  setSelectedEntity({ type: 'opportunity', id: selectedCell.x });
                  setActiveTab('tracer');
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-2xs transition"
              >
                <span>Trace Lineage Trajectory</span>
                <ArrowRight size={13} />
              </button>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: INTERACTIVE NODE LINEAGE TRACER */}
      {activeTab === 'tracer' && (
        <div className="space-y-4">
          {/* Quick Select & Search Sandbox */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Select or Search an Entity to Trace Across All 9 Dimensions:
            </div>

            {/* Exemplar Quick Chips */}
            <div className="flex flex-wrap items-center gap-2">
              {SAMPLE_ENTITIES.map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedEntity(sample)}
                  className={clsx(
                    'px-2.5 py-1.5 rounded-xl text-xs font-semibold border transition flex items-center gap-2 shadow-2xs',
                    selectedEntity.id === sample.id
                      ? 'bg-indigo-600 text-white border-indigo-600 ring-2 ring-indigo-300'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  )}
                >
                  <OrgLogo org={sample.org} size="xs" />
                  <span>{sample.label}</span>
                </button>
              ))}
            </div>

            {/* Custom Input */}
            <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
              <div className="relative flex-1">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Or enter any patent number, company name, solicitation ID..."
                  value={customSearch}
                  onChange={(e) => setCustomSearch(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && customSearch.trim()) {
                      setSelectedEntity({ type: 'patent', id: customSearch.trim() });
                    }
                  }}
                  className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <button
                onClick={() => {
                  if (customSearch.trim()) {
                    setSelectedEntity({ type: 'patent', id: customSearch.trim() });
                  }
                }}
                className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-2xs transition"
              >
                Trace
              </button>
            </div>
          </div>

          {/* Live Provenance HUD Ribbon */}
          <ProvenanceRibbon
            entityType={selectedEntity.type as any}
            entityId={selectedEntity.id}
          />
        </div>
      )}
    </div>
  );
}
