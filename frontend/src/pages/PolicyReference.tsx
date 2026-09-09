import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShieldCheck, Scale, DollarSign, FileText, Zap, Search,
  ExternalLink, Sparkles, Layers, Activity, CheckCircle2,
  Building2, ArrowUpRight, X, Grid, List, Compass, Info,
  Calculator, Flame, Sun, BatteryCharging, AlertTriangle,
  FileSpreadsheet, ChevronRight, HelpCircle, Award
} from 'lucide-react';
import { api, PolicyStandard, PolicyDossier } from '../api/client';
import { IraCalculatorModal } from '../components/IraCalculatorModal';
import clsx from 'clsx';

const CATEGORY_MAP: Record<string, { label: string; color: string; icon: React.ComponentType<{ size?: number; className?: string }> }> = {
  tax_incentive: {
    label: 'IRA & Tax Incentives',
    color: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
    icon: DollarSign
  },
  safety_code: {
    label: 'Safety & Testing Codes',
    color: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    icon: ShieldCheck
  },
  interconnection_rule: {
    label: 'Interconnection & Grid Tariffs',
    color: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
    icon: Zap
  },
  state_statute: {
    label: 'State Climate Mandates',
    color: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
    icon: Scale
  },
  building_code: {
    label: 'Building & Municipal Codes',
    color: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
    icon: Building2
  },
  emissions_standard: {
    label: 'Emissions & Low-Carbon Fuels',
    color: 'bg-teal-500/10 text-teal-300 border-teal-500/30',
    icon: Flame
  },
  environmental_permitting: {
    label: 'Environmental & Siting',
    color: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
    icon: Layers
  }
};

const JURISDICTION_BADGES: Record<string, string> = {
  federal: 'bg-indigo-500/20 text-indigo-300 border-indigo-400/30',
  state: 'bg-cyan-500/20 text-cyan-300 border-cyan-400/30',
  rto_iso: 'bg-blue-500/20 text-blue-300 border-blue-400/30',
  municipal: 'bg-purple-500/20 text-purple-300 border-purple-400/30',
  international: 'bg-amber-500/20 text-amber-300 border-amber-400/30'
};

export default function PolicyReference() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');
  const [selectedPolicyId, setSelectedPolicyId] = useState<string | null>(null);
  const [isCalculatorOpen, setIsCalculatorOpen] = useState(false);
  const [calcSector, setCalcSector] = useState<string>('clean_hydrogen');

  // 1. Fetch Stats
  const { data: stats } = useQuery({
    queryKey: ['policy-stats'],
    queryFn: () => api.getPolicyStats(),
    staleTime: 10 * 60 * 1000
  });

  // 2. Fetch Policies List
  const { data: policiesData, isLoading } = useQuery({
    queryKey: ['policies-list', selectedCategory, selectedJurisdiction, selectedStatus, searchQuery],
    queryFn: () => api.getPolicies({
      category: selectedCategory !== 'all' ? selectedCategory : undefined,
      jurisdiction_level: selectedJurisdiction !== 'all' ? selectedJurisdiction : undefined,
      status: selectedStatus !== 'all' ? selectedStatus : undefined,
      search: searchQuery || undefined,
      limit: 100
    }),
    staleTime: 5 * 60 * 1000
  });

  // 3. Fetch Selected Policy Detail (for drawer)
  const { data: selectedDossier, isLoading: isLoadingDossier } = useQuery<PolicyDossier>({
    queryKey: ['policy-detail', selectedPolicyId],
    queryFn: () => api.getPolicy(selectedPolicyId!),
    enabled: Boolean(selectedPolicyId),
    staleTime: 5 * 60 * 1000
  });

  const policies = policiesData?.policies || [];

  // Filtered IRA Specific Policies for Hero Highlight
  const iraPolicies = useMemo(() => {
    return policies.filter(p => p.category === 'tax_incentive' || p.code_identifier.includes('§') || p.id.includes('ira'));
  }, [policies]);

  const openIraCalc = (sectorKey = 'clean_hydrogen') => {
    setCalcSector(sectorKey);
    setIsCalculatorOpen(true);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-16">
      
      {/* IRA Tax Credit & Direct Pay Calculator Modal */}
      <IraCalculatorModal
        isOpen={isCalculatorOpen}
        onClose={() => setIsCalculatorOpen(false)}
        defaultSector={calcSector}
      />

      {/* ── STANDARD PAGE HEADER & TELEMETRY ──────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 shadow-2xs">
              <DollarSign size={12} className="text-emerald-600" />
              <span>Federal IRA §45/§48 Tax Incentives</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-slate-500 font-mono">NFPA · UL · IEEE · EPA · NY CLCPA · CA SB100</span>
            <span className="text-xs text-slate-300">|</span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-cyan-50 text-cyan-800 border border-cyan-200 shadow-2xs">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" />
              <span>Codes &amp; Standards Knowledge Base</span>
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Policy Reference
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 max-w-3xl mt-1 leading-relaxed">
            Statutory registry of Inflation Reduction Act (IRA 2022) tax credits (§45V, §45Q, §48C, §45X, §48E, §45Z), NFPA/UL safety codes, grid interconnection rules, state climate mandates, and elective Direct Pay monetization rules.
          </p>
        </div>

        {/* Action Button: Launch IRA Calculator */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => openIraCalc('clean_hydrogen')}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-md hover:shadow-lg transition-all flex items-center gap-2 cursor-pointer"
          >
            <Calculator size={15} />
            <span>Launch IRA Direct Pay Calculator</span>
          </button>
        </div>
      </div>

      {/* ── MACRO KPI STAT ROW ─────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <span className="text-[11px] uppercase font-bold text-slate-400 block tracking-wider">Governing Policies</span>
          <span className="text-2xl font-bold text-slate-900 font-mono mt-0.5 block">{policies.length || 37}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Active Federal, State &amp; Safety Codes</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <span className="text-[11px] uppercase font-bold text-emerald-600 block tracking-wider">IRA Tax Incentives</span>
          <span className="text-2xl font-bold text-emerald-700 font-mono mt-0.5 block">{iraPolicies.length || 8}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">§45V, §45Q, §48C, §45X, §48E, §45Z</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <span className="text-[11px] uppercase font-bold text-amber-600 block tracking-wider">Safety &amp; Testing Codes</span>
          <span className="text-2xl font-bold text-slate-900 font-mono mt-0.5 block">
            {policies.filter(p => p.category === 'safety_code').length || 10}
          </span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">NFPA 855, UL 9540A, IEEE 1547</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <span className="text-[11px] uppercase font-bold text-purple-600 block tracking-wider">State &amp; Siting Mandates</span>
          <span className="text-2xl font-bold text-slate-900 font-mono mt-0.5 block">
            {policies.filter(p => p.category === 'state_statute' || p.category === 'building_code').length || 12}
          </span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">NY CLCPA, CA SB100, NYC LL154</span>
        </div>
      </div>

      {/* ── INFLATION REDUCTION ACT (IRA 2022) EXECUTIVE BANNER CARD ──── */}
      <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 rounded-3xl p-6 sm:p-8 text-white shadow-xl border border-indigo-500/30 space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[11px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                <DollarSign size={12} className="text-emerald-400" />
                Inflation Reduction Act (IRA 2022) Tax Credit Framework
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/20 border border-cyan-400/30 text-cyan-300 text-[10.5px] font-mono font-bold">
                10-Year Horizon (2022–2032+)
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white mt-1">
              Federal Energy Innovation Tax Credit &amp; Elective Direct Pay Architecture
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl mt-1 leading-relaxed">
              Provides uncapped, refundable production tax credits (PTC) and investment tax credits (ITC) alongside direct transferability and non-profit/governmental elective Direct Pay monetization under 26 U.S.C. §§ 6417 &amp; 6418.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-white/5 p-4 rounded-2xl border border-white/10 shrink-0 text-right font-mono">
            <div>
              <div className="text-[10px] uppercase font-bold text-slate-400">Bonus Adders Available</div>
              <div className="text-2xl font-black text-emerald-400">+10% to +30%</div>
              <div className="text-[10.5px] text-slate-300">Domestic Content + Energy Communities</div>
            </div>
          </div>
        </div>

        {/* 6 Core IRA Provisions Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            {
              code: '26 U.S.C. § 45V',
              title: 'Clean Hydrogen Production Tax Credit',
              benefit: 'Up to $3.00 / kg H2',
              desc: 'Tiered 10-year credit for clean electrolytic and thermal hydrogen achieving lifecycle CI < 0.45 kg CO2e/kg H2.',
              sector: 'clean_hydrogen',
              linkId: 'ira_sec_45v_clean_h2'
            },
            {
              code: '26 U.S.C. § 45Q',
              title: 'Carbon Oxide Sequestration Credit',
              benefit: 'Up to $180 / metric ton',
              desc: '12-year credit for Direct Air Capture ($180/ton) and point-source industrial capture ($85/ton) stored in Class VI wells.',
              sector: 'carbon_capture',
              linkId: 'ira_sec_45q_ccus'
            },
            {
              code: '26 U.S.C. § 48C',
              title: 'Qualifying Advanced Energy Project Credit',
              benefit: '30% CAPEX Tax Credit',
              desc: '$10B competitive allocation for building domestic manufacturing facilities for clean tech, batteries, and solar.',
              sector: 'solar_wind',
              linkId: 'ira_sec_48c_clean_mfg'
            },
            {
              code: '26 U.S.C. § 45X',
              title: 'Advanced Manufacturing Production Credit',
              benefit: 'Per-unit manufacturing subsidy',
              desc: 'Covers domestic production of PV cells ($0.04/W), wafers ($12/m2), battery cells ($35/kWh), and critical minerals (10% of cost).',
              sector: 'energy_storage',
              linkId: 'ira_sec_45x_mfg_ptc'
            },
            {
              code: '26 U.S.C. § 48 / § 48E',
              title: 'Clean Electricity Investment Tax Credit (ITC)',
              benefit: '30% to 50% CAPEX Credit',
              desc: 'Baseline 30% credit for solar, wind, and energy storage, increasing to 50% with domestic content and energy community adders.',
              sector: 'energy_storage',
              linkId: 'ira_sec_48_itc_storage'
            },
            {
              code: '26 U.S.C. § 45Z',
              title: 'Clean Fuel Production Credit',
              benefit: 'Up to $1.75 / gallon',
              desc: 'Technology-neutral clean transportation and Sustainable Aviation Fuel (SAF) credit tied to emissions intensity reduction.',
              sector: 'clean_fuels',
              linkId: 'ira_sec_45z_clean_fuels'
            }
          ].map((item) => (
            <div key={item.code} className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.08] hover:border-emerald-400/40 transition-all flex flex-col justify-between space-y-3 group">
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span className="px-2 py-0.5 rounded-md text-[10.5px] font-mono font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    {item.code}
                  </span>
                  <span className="text-xs font-mono font-bold text-emerald-400">
                    {item.benefit}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mt-2 group-hover:text-emerald-300 transition-colors">
                  {item.title}
                </h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  {item.desc}
                </p>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-white/[0.06] text-xs">
                <button
                  type="button"
                  onClick={() => setSelectedPolicyId(item.linkId)}
                  className="text-cyan-400 hover:text-cyan-300 font-semibold inline-flex items-center gap-1 cursor-pointer"
                >
                  <span>View Statutory Text</span>
                  <ChevronRight size={13} />
                </button>
                <button
                  type="button"
                  onClick={() => openIraCalc(item.sector)}
                  className="text-emerald-400 hover:text-emerald-300 font-semibold inline-flex items-center gap-1 cursor-pointer"
                >
                  <Calculator size={13} />
                  <span>Model Economics</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── FILTER & SEARCH TOOLBAR ──────────────────────────────────── */}
      <div className="w-full flex flex-col gap-4">
        <div className="bg-white rounded-2xl border border-slate-200/90 p-4 shadow-2xs flex flex-col md:flex-row gap-4 items-center justify-between">
          {/* Search Bar */}
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search code identifier (NFPA 855, § 45V), statute name, clean tech, compliance mandate..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500 transition-all font-medium"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
              >
                <X size={14} />
              </button>
            )}
          </div>

          {/* View Mode Toggle & Result Count */}
          <div className="flex items-center gap-3 shrink-0 w-full md:w-auto justify-between md:justify-end">
            <span className="text-xs font-semibold text-slate-500">
              Showing <span className="text-slate-900 font-bold">{policies.length}</span> Policies &amp; Codes
            </span>

            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
              <button
                type="button"
                onClick={() => setViewMode('cards')}
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                  viewMode === 'cards' ? 'bg-white text-emerald-700 shadow-2xs' : 'text-slate-500 hover:text-slate-800'
                }`}
                title="Card View"
              >
                <Grid size={15} />
                <span className="hidden sm:inline">Cards</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode('table')}
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                  viewMode === 'table' ? 'bg-white text-emerald-700 shadow-2xs' : 'text-slate-500 hover:text-slate-800'
                }`}
                title="Table View"
              >
                <List size={15} />
                <span className="hidden sm:inline">Table</span>
              </button>
            </div>
          </div>
        </div>

        {/* Multi-Attribute Filter Chips */}
        <div className="flex flex-col gap-2.5">
          {/* Category Filter */}
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 shrink-0 flex items-center gap-1">
              <ShieldCheck size={12} className="text-emerald-600" /> Category:
            </span>
            {[
              { id: 'all', label: 'All Policy Types' },
              { id: 'tax_incentive', label: 'IRA & Tax Incentives' },
              { id: 'safety_code', label: 'Safety & Testing (NFPA/UL)' },
              { id: 'interconnection_rule', label: 'Interconnection & Grid' },
              { id: 'state_statute', label: 'State Climate Mandates' },
              { id: 'building_code', label: 'Building Codes (NYC LL97/154)' },
              { id: 'emissions_standard', label: 'Emissions & Low Carbon Fuels' }
            ].map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer ${
                  selectedCategory === cat.id
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'bg-white text-slate-600 border border-slate-200/80 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Jurisdiction Level Filter */}
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 shrink-0 flex items-center gap-1">
              <Building2 size={12} className="text-cyan-600" /> Jurisdiction:
            </span>
            {[
              { id: 'all', label: 'All Jurisdictions' },
              { id: 'federal', label: 'Federal (US / IRA / FERC / EPA)' },
              { id: 'state', label: 'State Level (NY / CA / MA)' },
              { id: 'municipal', label: 'Municipal (NYC / FDNY)' },
              { id: 'international', label: 'International (NFPA / IEEE)' }
            ].map(jur => (
              <button
                key={jur.id}
                onClick={() => setSelectedJurisdiction(jur.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer ${
                  selectedJurisdiction === jur.id
                    ? 'bg-cyan-700 text-white shadow-xs'
                    : 'bg-white text-slate-600 border border-slate-200/80 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {jur.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── POLICIES LIST / CARD VIEW ──────────────────────────────────── */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-8">
          {[1, 2, 3, 4].map(n => (
            <div key={n} className="h-56 rounded-2xl bg-slate-100 animate-pulse border border-slate-200" />
          ))}
        </div>
      ) : policies.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center my-6">
          <ShieldCheck size={40} className="mx-auto text-slate-300 mb-3" />
          <h3 className="text-base font-bold text-slate-800">No policies match your filter criteria</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
            Try adjusting your category or search query to find relevant energy innovation tax credits, safety codes, or state climate mandates.
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setSelectedCategory('all');
              setSelectedJurisdiction('all');
              setSelectedStatus('all');
            }}
            className="mt-4 px-4 py-2 rounded-xl bg-emerald-50 text-emerald-800 text-xs font-bold hover:bg-emerald-100 transition-colors"
          >
            Reset Filters
          </button>
        </div>
      ) : viewMode === 'cards' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {policies.map((pol) => {
            const catInfo = CATEGORY_MAP[pol.category] || { label: pol.category, color: 'bg-slate-100 text-slate-700 border-slate-200', icon: FileText };
            const IconComp = catInfo.icon;

            return (
              <div
                key={pol.id}
                onClick={() => setSelectedPolicyId(pol.id)}
                className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-2xs hover:shadow-md hover:border-emerald-500/40 transition-all flex flex-col justify-between space-y-4 cursor-pointer group"
              >
                <div className="space-y-3">
                  {/* Top Bar Badges */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="px-2.5 py-0.5 rounded-lg text-xs font-mono font-bold bg-slate-900 text-white shadow-2xs">
                        {pol.code_identifier}
                      </span>
                      <span className={`px-2 py-0.5 rounded-lg text-[11px] font-semibold border ${catInfo.color}`}>
                        {catInfo.label}
                      </span>
                      <span className={`px-2 py-0.5 rounded-lg text-[10.5px] font-mono font-bold uppercase border ${JURISDICTION_BADGES[pol.jurisdiction_level] || 'bg-slate-100 text-slate-600'}`}>
                        {pol.jurisdiction_state ? `${pol.jurisdiction_state} (${pol.jurisdiction_level})` : pol.jurisdiction_level}
                      </span>
                    </div>

                    <span className="text-[11px] font-mono text-slate-400 shrink-0">
                      {pol.latest_revision || (pol.effective_year ? `Est. ${pol.effective_year}` : 'Active')}
                    </span>
                  </div>

                  {/* Title & Summary */}
                  <div>
                    <h3 className="text-base font-bold text-slate-900 group-hover:text-emerald-700 transition-colors leading-snug">
                      {pol.title}
                    </h3>
                    <p className="text-xs text-slate-600 mt-1 line-clamp-2 leading-relaxed">
                      {pol.executive_summary}
                    </p>
                  </div>

                  {/* Compliance Mandate */}
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70 text-xs">
                    <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Compliance Mandate</div>
                    <p className="text-slate-700 mt-0.5 line-clamp-2 leading-relaxed">
                      {pol.compliance_mandate}
                    </p>
                  </div>

                  {/* Associated Tax Credits & Incentives Callout */}
                  {pol.associated_incentives && (
                    <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200/80 text-xs flex items-start gap-2.5">
                      <DollarSign size={15} className="text-emerald-600 shrink-0 mt-0.5" />
                      <div>
                        <div className="text-[10px] uppercase font-bold text-emerald-800 font-mono">
                          Associated IRA Tax Credits &amp; Statutory Incentives
                        </div>
                        <p className="text-emerald-900 font-medium mt-0.5 leading-snug line-clamp-2">
                          {pol.associated_incentives}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Footer Link & Action */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs">
                  <span className="text-slate-500 font-medium">
                    Click to view full statutory compliance dossier
                  </span>
                  <div className="flex items-center gap-1 text-emerald-600 font-bold group-hover:translate-x-0.5 transition-transform">
                    <span>Explore Dossier</span>
                    <ChevronRight size={14} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Table View */
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-2xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-mono uppercase text-slate-500 font-bold">
                  <th className="py-3 px-4">Code Identifier</th>
                  <th className="py-3 px-4">Title &amp; Summary</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Jurisdiction</th>
                  <th className="py-3 px-4">Associated Incentives</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {policies.map((pol) => (
                  <tr
                    key={pol.id}
                    onClick={() => setSelectedPolicyId(pol.id)}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-slate-900 whitespace-nowrap">
                      {pol.code_identifier}
                    </td>
                    <td className="py-3 px-4 max-w-md">
                      <div className="font-bold text-slate-900">{pol.title}</div>
                      <div className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">{pol.executive_summary}</div>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded text-[10.5px] font-semibold bg-slate-100 text-slate-700">
                        {CATEGORY_MAP[pol.category]?.label || pol.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="font-mono text-slate-600 uppercase">
                        {pol.jurisdiction_state ? `${pol.jurisdiction_state} · ${pol.jurisdiction_level}` : pol.jurisdiction_level}
                      </span>
                    </td>
                    <td className="py-3 px-4 max-w-xs">
                      {pol.associated_incentives ? (
                        <span className="text-emerald-700 font-semibold line-clamp-2 text-[11px]">
                          {pol.associated_incentives}
                        </span>
                      ) : (
                        <span className="text-slate-400 font-mono text-[11px]">Mandatory Code</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedPolicyId(pol.id);
                        }}
                        className="text-emerald-600 font-bold hover:underline inline-flex items-center gap-1"
                      >
                        <span>Details</span>
                        <ChevronRight size={13} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── POLICY DOSSIER SLIDE-OVER DRAWER ─────────────────────────── */}
      {selectedPolicyId && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex justify-end animate-fade-in">
          <div className="w-full max-w-2xl bg-white h-full shadow-2xl overflow-y-auto flex flex-col justify-between border-l border-slate-200">
            
            {/* Drawer Header */}
            <div className="p-6 border-b border-slate-200 bg-slate-50/80 sticky top-0 z-10 backdrop-blur-md">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="px-2.5 py-0.5 rounded-lg text-xs font-mono font-bold bg-slate-900 text-white">
                      {selectedDossier?.code_identifier || 'Policy Standard'}
                    </span>
                    <span className="px-2 py-0.5 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {selectedDossier?.category ? CATEGORY_MAP[selectedDossier.category]?.label : 'Policy'}
                    </span>
                    <span className="text-xs font-mono text-slate-500 uppercase">
                      {selectedDossier?.jurisdiction_level}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-slate-900 mt-1">
                    {selectedDossier?.title}
                  </h2>
                </div>

                <button
                  onClick={() => setSelectedPolicyId(null)}
                  className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Drawer Body */}
            <div className="p-6 space-y-6 flex-1">
              {isLoadingDossier ? (
                <div className="py-12 text-center text-slate-400 font-mono text-xs">
                  Loading policy dossier...
                </div>
              ) : selectedDossier ? (
                <>
                  {/* Executive Summary */}
                  <div className="space-y-1.5">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Executive Summary</h3>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      {selectedDossier.executive_summary}
                    </p>
                  </div>

                  {/* Statutory Intent */}
                  {selectedDossier.statutory_intent && (
                    <div className="space-y-1.5">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Statutory Intent</h3>
                      <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                        {selectedDossier.statutory_intent}
                      </p>
                    </div>
                  )}

                  {/* Compliance Mandate */}
                  <div className="space-y-1.5">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">Compliance Mandate</h3>
                    <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200/80 text-xs text-slate-800 leading-relaxed font-medium">
                      {selectedDossier.compliance_mandate}
                    </div>
                  </div>

                  {/* Associated Tax Credits & Incentives */}
                  {selectedDossier.associated_incentives && (
                    <div className="space-y-1.5">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-600 font-mono flex items-center gap-1.5">
                        <DollarSign size={13} />
                        Associated IRA Tax Credits &amp; Subsidies
                      </h3>
                      <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 leading-relaxed font-semibold">
                        {selectedDossier.associated_incentives}
                      </div>
                    </div>
                  )}

                  {/* Commercial Friction Points */}
                  {selectedDossier.commercial_friction_points && (
                    <div className="space-y-1.5">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-amber-600 font-mono flex items-center gap-1.5">
                        <AlertTriangle size={13} />
                        Commercial Friction Points &amp; Roadblocks
                      </h3>
                      <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200 text-xs text-amber-900 leading-relaxed">
                        {selectedDossier.commercial_friction_points}
                      </div>
                    </div>
                  )}

                  {/* Linked Clean Technologies */}
                  {selectedDossier.linked_technologies && selectedDossier.linked_technologies.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-200">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
                        Direct Technology Cross-References ({selectedDossier.linked_technologies.length})
                      </h3>
                      <div className="space-y-2">
                        {selectedDossier.linked_technologies.map((tlink) => (
                          <div
                            key={tlink.technology_id}
                            className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between gap-3 text-xs"
                          >
                            <div>
                              <Link
                                to={`/technologies/${tlink.technology_id}`}
                                className="font-bold text-slate-900 hover:text-emerald-600 transition-colors flex items-center gap-1"
                              >
                                <span>{tlink.technology_name}</span>
                                <ArrowUpRight size={12} />
                              </Link>
                              {tlink.impact_summary && (
                                <p className="text-[11px] text-slate-500 mt-0.5">{tlink.impact_summary}</p>
                              )}
                            </div>
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-white border border-slate-200 shrink-0">
                              {tlink.compliance_impact?.replace('_', ' ')}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : null}
            </div>

            {/* Drawer Footer */}
            <div className="p-5 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
              {selectedDossier?.official_source_url ? (
                <a
                  href={selectedDossier.official_source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-all inline-flex items-center gap-1.5"
                >
                  <ExternalLink size={13} />
                  <span>Official Government Record</span>
                </a>
              ) : <div />}

              <button
                type="button"
                onClick={() => setSelectedPolicyId(null)}
                className="px-4 py-2 rounded-xl border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-all"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}