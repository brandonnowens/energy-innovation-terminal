import React, { useState, useRef, useEffect, useMemo } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api, AnalysisInput, SayYesOrganization, GroupedOpportunityOrg } from '../api/client';

import {
  Loader2, CheckCircle2, AlertTriangle, AlertCircle, ExternalLink,
  DollarSign, Calendar, Target, Clock, ArrowRight, Zap, TrendingUp,
  CircleDot, ChevronDown, X, Search, Sparkles, FileDown,
  Building2, Landmark, HeartHandshake, Filter, Globe, Share2,
  Check, Copy, Compass, Layers, ShieldCheck, PieChart,
  BarChart3, Plus, Settings2, KeyRound, PlugZap, SlidersHorizontal,
  MapPin, FileText, FlaskConical
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';
import { ProjectDocumentUploader } from '../components/ProjectDocumentUploader';
import { SayYesDecisionMakerMatrix } from '../components/SayYesDecisionMakerMatrix';
import { Top25OpportunitiesTable, MatchItem } from '../components/Top25OpportunitiesTable';
import { ExtractedProjectProfile, TestConnectionResponse, LlmStatusResponse } from '../api/client';
import { useNyserda } from '../context/NyserdaContext';

// ─── Types ───────────────────────────────────────────────────────────────────

interface AnalysisResponse {
  analysis_id: number;
  profile: {
    summary: string;
    technology_areas: string[];
    activity_types: string[];
    estimated_trl: number | null;
    applicant_type: string | null;
    ny_location: string | null;
    target_location: string | null;
    project_cost: number | null;
    workstreams: Array<{ name: string; description: string; activity_type: string }>;
    uncertainties: string[];
  };
  summary: string;
  matches: {
    strong_matches: MatchItem[];
    conditional_matches: MatchItem[];
    component_matches: MatchItem[];
    watchlist: MatchItem[];
  };
  top_50_opportunities?: MatchItem[];
  top_25_opportunities?: MatchItem[];
  top_20_opportunities?: MatchItem[];
  raw_top_20_opportunities?: MatchItem[];
  raw_top_25_opportunities?: MatchItem[];
  top_50_say_yes?: SayYesOrganization[];
  top_25_say_yes?: SayYesOrganization[];
  top_15_say_yes?: SayYesOrganization[];
  top_10_say_yes?: SayYesOrganization[];
  top_say_yes?: SayYesOrganization[];
  grouped_opportunities?: GroupedOpportunityOrg[];
  programs: Array<{ program_id: number; name: string; program_type: string; description: string; url: string; target_stage: string; relevance_score: number }>;
  precedents: PrecedentItem[];
  funding_architecture: FundingArch[];
  executive_briefing?: {
    is_llm_generated: boolean;
    model_used: string;
    executive_summary_paragraphs: string[];
    executive_summary_text: string;
    strategic_takeaways: string[];
    grant_capture_strategy?: string;
    regulatory_and_permitting_roadmap?: string;
  };
  disclaimer: string;
}

interface PrecedentItem {
  id: number;
  project_title: string;
  contractor_name: string;
  contractor_type: string;
  project_type: string;
  technology_1: string;
  award_amount: number;
  award_date: string;
  contractor_city: string;
  contractor_state: string;
}

interface FundingArch {
  workstream: string;
  activity_type: string;
  opportunity: string;
  opportunity_name: string;
  fit_score: number;
  max_award: number | null;
  reasoning_type: string;
}

function fmt(val: number | null | undefined): string {
  if (!val) return '—';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toFixed(0)}`;
}

export interface OrgMeta {
  code: string;
  label: string;
  desc: string;
  category: 'utility' | 'federal' | 'state' | 'foundation' | string;
  category_label: string;
  state?: string;
  count?: number;
  active_count?: number;
}

export const ORGANIZATIONS: OrgMeta[] = [
  { code: 'Con Edison', label: 'Con Edison', desc: 'Consolidated Edison, Inc. (Electric & Gas Utility)', category: 'utility', category_label: 'Electric & Gas Utility', state: 'NY' },
  { code: 'Pacific Gas and Electric', label: 'PG&E', desc: 'Pacific Gas and Electric Company', category: 'utility', category_label: 'Electric & Gas Utility', state: 'CA' },
  { code: 'Southern California Edison', label: 'SCE', desc: 'Southern California Edison', category: 'utility', category_label: 'Electric & Gas Utility', state: 'CA' },
  { code: 'National Grid', label: 'National Grid', desc: 'National Grid USA (Electric & Gas Utility)', category: 'utility', category_label: 'Electric & Gas Utility', state: 'NY/MA' },
  { code: 'Florida Power & Light', label: 'FPL', desc: 'Florida Power & Light (NextEra Energy)', category: 'utility', category_label: 'Electric & Gas Utility', state: 'FL' },
  { code: 'Commonwealth Edison', label: 'ComEd', desc: 'Commonwealth Edison Company (Exelon)', category: 'utility', category_label: 'Electric & Gas Utility', state: 'IL' },
  { code: 'Georgia Power', label: 'Georgia Power', desc: 'Georgia Power Company (Southern Company)', category: 'utility', category_label: 'Electric & Gas Utility', state: 'GA' },
  { code: 'AEP Ohio', label: 'AEP Ohio', desc: 'American Electric Power Ohio', category: 'utility', category_label: 'Electric & Gas Utility', state: 'OH' },
  { code: 'PECO Energy', label: 'PECO', desc: 'PECO Energy Company (Exelon)', category: 'utility', category_label: 'Electric & Gas Utility', state: 'PA' },
  { code: 'Dominion Energy Virginia', label: 'Dominion Energy', desc: 'Dominion Energy Virginia', category: 'utility', category_label: 'Electric & Gas Utility', state: 'VA' },
  { code: 'Puget Sound Energy', label: 'PSE', desc: 'Puget Sound Energy', category: 'utility', category_label: 'Electric & Gas Utility', state: 'WA' },
  { code: 'Xcel Energy', label: 'Xcel Energy', desc: 'Public Service Company of Colorado', category: 'utility', category_label: 'Electric & Gas Utility', state: 'CO' },
  { code: 'DOE', label: 'DOE', desc: 'U.S. Department of Energy', category: 'federal', category_label: 'Federal Agency' },
  { code: 'ARPA-E', label: 'ARPA-E', desc: 'Advanced Research Projects Agency – Energy', category: 'federal', category_label: 'Federal Agency' },
  { code: 'NSF', label: 'NSF', desc: 'National Science Foundation', category: 'federal', category_label: 'Federal Agency' },
  { code: 'EPA', label: 'EPA', desc: 'U.S. Environmental Protection Agency', category: 'federal', category_label: 'Federal Agency' },
  { code: 'NYSERDA', label: 'NYSERDA', desc: 'New York State Energy Research and Development Authority', category: 'state', category_label: 'State Energy Agency', state: 'NY' },
  { code: 'Empire State Development', label: 'Empire State Development', desc: 'Empire State Development (ESD & NY Ventures)', category: 'state', category_label: 'State Agency', state: 'NY' },
  { code: 'CEC', label: 'CEC', desc: 'California Energy Commission', category: 'state', category_label: 'State Energy Agency', state: 'CA' },
  { code: 'California GO-Biz', label: 'California GO-Biz', desc: 'California Governor\'s Office of Business and Economic Development', category: 'state', category_label: 'State Agency', state: 'CA' },
  { code: 'MassCEC', label: 'MassCEC', desc: 'Massachusetts Clean Energy Center', category: 'state', category_label: 'State Energy Agency', state: 'MA' },
  { code: 'MassVentures', label: 'MassVentures', desc: 'Massachusetts Technology Development Corporation', category: 'state', category_label: 'State Agency', state: 'MA' },
  { code: 'TX SECO', label: 'TX SECO', desc: 'Texas State Energy Conservation Office', category: 'state', category_label: 'State Energy Agency', state: 'TX' },
  { code: 'Colorado CEO', label: 'Colorado CEO', desc: 'Colorado Energy Office', category: 'state', category_label: 'State Energy Agency', state: 'CO' },
  { code: 'Colorado OEDIT', label: 'Colorado OEDIT', desc: 'Colorado Office of Economic Development & International Trade', category: 'state', category_label: 'State Agency', state: 'CO' },
  { code: 'IL DCEO', label: 'IL DCEO', desc: 'Illinois Department of Commerce & Economic Opportunity', category: 'state', category_label: 'State Agency', state: 'IL' },
  { code: 'NJEDA', label: 'NJEDA', desc: 'New Jersey Economic Development Authority', category: 'state', category_label: 'State Agency', state: 'NJ' },
  { code: 'JobsOhio', label: 'JobsOhio', desc: 'JobsOhio Clean Energy & Advanced Manufacturing', category: 'state', category_label: 'State Agency', state: 'OH' },
  { code: 'MEDC', label: 'MEDC', desc: 'Michigan Economic Development Corporation', category: 'state', category_label: 'State Agency', state: 'MI' },
  { code: 'Ben Franklin Tech Partners', label: 'Ben Franklin Tech Partners', desc: 'Ben Franklin Technology Partners (Pennsylvania)', category: 'state', category_label: 'State Agency', state: 'PA' },
  { code: 'MD MEA', label: 'MD MEA', desc: 'Maryland Energy Administration', category: 'state', category_label: 'State Energy Agency', state: 'MD' },
  { code: 'TEDCO', label: 'TEDCO', desc: 'Maryland Technology Development Corporation', category: 'state', category_label: 'State Agency', state: 'MD' },
  { code: 'WA Commerce', label: 'WA Commerce', desc: 'Washington State Department of Commerce', category: 'state', category_label: 'State Energy Agency', state: 'WA' },
  { code: 'VIPC', label: 'VIPC', desc: 'Virginia Innovation Partnership Corporation', category: 'state', category_label: 'State Agency', state: 'VA' },
  { code: 'MN DEED', label: 'MN DEED', desc: 'Minnesota Department of Employment & Economic Development', category: 'state', category_label: 'State Agency', state: 'MN' },
  { code: 'WI OEI', label: 'WI OEI', desc: 'Wisconsin Office of Energy Innovation', category: 'state', category_label: 'State Energy Agency', state: 'WI' },
  { code: 'NM EMNRD', label: 'NM EMNRD', desc: 'New Mexico Energy, Minerals & Natural Resources Dept', category: 'state', category_label: 'State Energy Agency', state: 'NM' },
  { code: 'Efficiency Maine', label: 'Efficiency Maine', desc: 'Efficiency Maine Trust', category: 'state', category_label: 'State Energy Agency', state: 'ME' },
  { code: 'Connecticut Innovations', label: 'Connecticut Innovations', desc: 'Connecticut Innovations ClimateTech Fund', category: 'state', category_label: 'State Agency', state: 'CT' },
];

const ORG_TYPE_LABELS: Record<string, { label: string }> = {
  all: { label: 'All Organizations' },
  utility: { label: 'Electric & Gas Utilities' },
  federal: { label: 'Federal Agencies' },
  state: { label: 'State Energy Agencies' },
  foundation: { label: 'Philanthropic Foundations' },
};

const APPLICANT_TYPES = [
  { value: 'business', label: 'Commercial Business / Startup' },
  { value: 'university', label: 'University / Research Institution' },
  { value: 'nonprofit', label: 'Non-Profit / NGO' },
  { value: 'municipality', label: 'Municipal / Local Government' },
  { value: 'consortium', label: 'Consortium / Multi-Partner' },
];

const TECH_AREAS = [
  'Energy Storage',
  'Grid Modernization',
  'Clean Hydrogen',
  'Solar PV & Dual-Use',
  'Offshore Wind & Marine',
  'Industrial Decarbonization',
  'Building Decarbonization & Heat Pumps',
  'Electric Vehicles & Charging Infrastructure',
  'Carbon Capture, Utilization & Storage (CCUS)',
  'Microgrids & Resilience',
  'Nuclear & Advanced Fission/Fusion',
  'Geothermal Systems',
  'Bioenergy & Sustainable Aviation Fuels',
  'Clean Transportation & Heavy Fleets',
  'Agrivoltaics & Land Stewardship',
];

const ACTIVITY_TYPES = [
  'Applied R&D',
  'Pilot Demonstration',
  'Commercial Scale-Up',
  'Feasibility & Front-End Engineering (FEED)',
  'Technology Commercialization',
  'Workforce Development',
  'Community Engagement & Planning',
];

const SECTORS = [
  'Electric Power Sector',
  'Commercial Buildings',
  'Industrial & Manufacturing',
  'Transportation & Logistics',
  'Residential Buildings',
  'Agriculture & Forestry',
  'Municipal & Public Infrastructure',
];

const FUEL_TYPES = [
  'Electricity',
  'Clean Hydrogen',
  'Solar / Sunlight',
  'Wind Energy',
  'Geothermal Heat',
  'Biomass / Biofuel',
  'Waste Heat',
  'Ambient Air / Thermal',
];

export interface SampleProject {
  id: string;
  name: string;
  badge: string;
  icon: string;
  description: string;
  location: string;
  applicantType: string;
  estimatedCost: string;
  trl: number;
  timeline: string;
  partners: string;
  technologyAreas: string[];
  activityTypes: string[];
  sectors: string[];
  fuelTypes: string[];
}

export const SAMPLE_PROJECT_PRESETS: SampleProject[] = [
  {
    id: 'iron_air_storage',
    name: 'Long-Duration Iron-Air Battery (100h LDES)',
    badge: 'Storage & Grid',
    icon: '⚡',
    description: 'Deploying a 10 MW / 1,000 MWh multi-day iron-air long-duration battery storage system (LDES) to eliminate peak fossil peaker run hours and resolve transmission bottlenecks under utility interconnection.',
    location: 'New York, NY',
    applicantType: 'business',
    estimatedCost: '25000000',
    trl: 6,
    timeline: '2026-2029',
    partners: 'Con Edison, US DOE, EPRI',
    technologyAreas: ['Energy Storage', 'Grid Modernization'],
    activityTypes: ['Pilot Demonstration', 'Commercial Scale-Up'],
    sectors: ['Electric Power Sector'],
    fuelTypes: ['Electricity']
  },
  {
    id: 'thermal_heat_pumps',
    name: 'Commercial Thermal Energy Network & Industrial Heat Pumps',
    badge: 'Buildings & Decarb',
    icon: '🏢',
    description: 'Engineering and installing large-scale industrial high-temperature air-to-water heat pump networks (160°C) with thermal energy storage across multi-building commercial campuses.',
    location: 'Boston, MA',
    applicantType: 'consortium',
    estimatedCost: '8500000',
    trl: 5,
    timeline: '2026-2028',
    partners: 'National Grid, MassCEC, Eversource',
    technologyAreas: ['Building Decarbonization & Heat Pumps', 'Industrial Decarbonization'],
    activityTypes: ['Pilot Demonstration', 'Feasibility & Front-End Engineering (FEED)'],
    sectors: ['Commercial Buildings', 'Industrial & Manufacturing'],
    fuelTypes: ['Ambient Air / Thermal', 'Electricity']
  },
  {
    id: 'green_hydrogen_soec',
    name: 'Clean Hydrogen & High-Temp Solid Oxide Electrolyzers',
    badge: 'H2 & E-Fuels',
    icon: '🧪',
    description: 'Demonstrating high-temperature solid oxide electrolyzer cells (SOEC) co-located with renewable power to produce clean hydrogen and green ammonia for heavy transportation and industrial heat.',
    location: 'Bakersfield, CA',
    applicantType: 'university',
    estimatedCost: '15000000',
    trl: 4,
    timeline: '2026-2030',
    partners: 'US DOE, California Energy Commission (CEC), UC Berkeley',
    technologyAreas: ['Clean Hydrogen', 'Offshore Wind & Marine'],
    activityTypes: ['Applied R&D', 'Pilot Demonstration'],
    sectors: ['Transportation & Logistics', 'Industrial & Manufacturing'],
    fuelTypes: ['Clean Hydrogen', 'Wind Energy']
  },
  {
    id: 'agrivoltaics_microgrid',
    name: 'Agrivoltaics & Dual-Use Smart Solar Microgrid',
    badge: 'Solar & Resilience',
    icon: '☀️',
    description: 'Deploying elevated bi-facial solar PV racking combined with autonomous microgrid controls and battery storage on agricultural land to maintain active farming while feeding rural distribution substations.',
    location: 'Ithaca, NY',
    applicantType: 'business',
    estimatedCost: '4200000',
    trl: 6,
    timeline: '2026-2028',
    partners: 'Cornell University, NYSEG, EPRI',
    technologyAreas: ['Solar PV & Dual-Use', 'Microgrids & Resilience', 'Agrivoltaics & Land Stewardship'],
    activityTypes: ['Pilot Demonstration', 'Community Engagement & Planning'],
    sectors: ['Electric Power Sector', 'Agriculture & Forestry'],
    fuelTypes: ['Solar / Sunlight', 'Electricity']
  }
];


// ─── MultiSelect Dropdown ────────────────────────────────────────────────────

function MultiSelect({ label, options, selected, onChange, placeholder }: {
  label: string; options: string[]; selected: string[];
  onChange: (v: string[]) => void; placeholder?: string;
}) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState('');
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const filtered = options.filter(o => o.toLowerCase().includes(q.toLowerCase()));
  const toggle = (opt: string) => {
    onChange(selected.includes(opt) ? selected.filter(s => s !== opt) : [...selected, opt]);
  };

  return (
    <div ref={ref} className="relative">
      <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">{label}</label>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={clsx(
          'w-full flex items-center justify-between gap-2 px-3 py-2 rounded-xl border text-xs transition-all text-left shadow-2xs cursor-pointer',
          'bg-slate-50 dark:bg-black/30 border-slate-200 dark:border-white/10 text-slate-900 dark:text-white',
          open && 'border-indigo-500 ring-2 ring-indigo-500/20'
        )}
      >
        <span className="truncate">
          {selected.length ? `${selected.length} selected` : (placeholder || 'Select...')}
        </span>
        <ChevronDown size={14} className={clsx('shrink-0 text-slate-400 transition-transform', open && 'rotate-180')} />
      </button>

      {/* Selected tags */}
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1.5">
          {selected.map(s => (
            <span key={s} className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-500/30 font-semibold">
              {s}
              <X size={10} className="cursor-pointer hover:opacity-75" onClick={(e) => { e.stopPropagation(); toggle(s); }} />
            </span>
          ))}
        </div>
      )}

      {/* Dropdown */}
      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white dark:bg-[#0d1424] border border-slate-200 dark:border-white/15 rounded-xl shadow-xl max-h-60 overflow-hidden animate-in fade-in slide-in-from-top-1 duration-150">
          <div className="p-2 border-b border-slate-100 dark:border-white/10">
            <div className="flex items-center gap-2 px-2 h-8 bg-slate-50 dark:bg-black/40 rounded-lg border border-slate-200 dark:border-white/10">
              <Search size={12} className="text-slate-400" />
              <input
                autoFocus
                type="text"
                value={q}
                onChange={e => setQ(e.target.value)}
                placeholder="Search..."
                className="w-full text-xs bg-transparent outline-none text-slate-900 dark:text-white placeholder:text-slate-400"
              />
            </div>
          </div>
          <div className="overflow-y-auto max-h-44 py-1">
            {filtered.map(opt => (
              <button
                key={opt}
                type="button"
                onClick={() => toggle(opt)}
                className={clsx(
                  'w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-left transition-colors cursor-pointer',
                  selected.includes(opt)
                    ? 'bg-indigo-50 text-indigo-900 dark:bg-indigo-950/40 dark:text-indigo-200 font-semibold'
                    : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/[0.04]'
                )}
              >
                <div className={clsx(
                  'w-3.5 h-3.5 rounded-sm border flex items-center justify-center shrink-0',
                  selected.includes(opt)
                    ? 'bg-indigo-600 border-indigo-600 text-white'
                    : 'border-slate-300 dark:border-white/20 bg-white dark:bg-black/30'
                )}>
                  {selected.includes(opt) && <Check size={10} className="text-white" />}
                </div>
                {opt}
              </button>
            ))}
            {filtered.length === 0 && <div className="px-3 py-2 text-xs text-slate-400">No results</div>}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Organization Multi-Selector ─────────────────────────────────────────────

function OrganizationMultiSelector({
  organizations,
  selected,
  onChange,
  suggestedAgencies,
}: {
  organizations: OrgMeta[];
  selected: string[];
  onChange: (selected: string[]) => void;
  suggestedAgencies?: string[];
}) {
  const [activeType, setActiveType] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [selectedState, setSelectedState] = useState<string>('all');
  const [isExpanded, setIsExpanded] = useState(true);

  const availableStates = useMemo(() => {
    const set = new Set<string>();
    organizations.forEach(o => {
      if (o.state && o.state !== 'US') set.add(o.state);
    });
    return Array.from(set).sort();
  }, [organizations]);

  const recommendedOrgCodes = useMemo(() => {
    if (!suggestedAgencies || !suggestedAgencies.length) return [];
    const lowerSuggestions = suggestedAgencies.map(s => s.toLowerCase().trim());
    return organizations
      .filter(o => 
        lowerSuggestions.some(s => 
          o.code.toLowerCase() === s || 
          o.label.toLowerCase() === s || 
          o.desc.toLowerCase().includes(s) || 
          s.includes(o.code.toLowerCase()) || 
          s.includes(o.label.toLowerCase())
        )
      )
      .map(o => o.code);
  }, [organizations, suggestedAgencies]);

  const orgCountsByType = useMemo(() => {
    const totalMap: Record<string, number> = { all: organizations.length, utility: 0, federal: 0, state: 0, foundation: 0 };
    const selMap: Record<string, number> = { all: selected.length, utility: 0, federal: 0, state: 0, foundation: 0 };

    organizations.forEach((o) => {
      const cat = o.category || 'utility';
      totalMap[cat] = (totalMap[cat] || 0) + 1;
      if (selected.includes(o.code)) {
        selMap[cat] = (selMap[cat] || 0) + 1;
      }
    });

    return { total: totalMap, selected: selMap };
  }, [organizations, selected]);

  const filteredOrgs = useMemo(() => {
    return organizations.filter((o) => {
      if (activeType !== 'all' && o.category !== activeType) return false;
      if (selectedState !== 'all' && o.state !== selectedState) return false;
      if (!search.trim()) return true;
      const s = search.toLowerCase();
      return o.code.toLowerCase().includes(s) || o.label.toLowerCase().includes(s) || o.desc.toLowerCase().includes(s) || (o.state && o.state.toLowerCase().includes(s));
    });
  }, [organizations, activeType, selectedState, search]);

  const activeCategoryCodes = useMemo(() => {
    return new Set(
      organizations
        .filter(o => activeType === 'all' || o.category === activeType)
        .filter(o => selectedState === 'all' || o.state === selectedState)
        .map(o => o.code)
    );
  }, [organizations, activeType, selectedState]);

  const selectAllActiveCategory = () => {
    const next = Array.from(new Set([...selected, ...activeCategoryCodes]));
    onChange(next);
  };

  const clearActiveCategory = () => {
    onChange(selected.filter(c => !activeCategoryCodes.has(c)));
  };

  const toggleOrg = (code: string) => {
    if (selected.includes(code)) {
      onChange(selected.filter(c => c !== code));
    } else {
      onChange([...selected, code]);
    }
  };

  return (
    <div className="space-y-3">
      {/* Header Bar */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
            Funding Organizations &amp; Utilities
          </label>
          <span className="text-[10.5px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-500/30">
            {selected.length} of {organizations.length} Selected
          </span>
          {recommendedOrgCodes.length > 0 && (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/30 dark:text-amber-300 dark:border-amber-500/30 flex items-center gap-1">
              <Sparkles size={10} /> {recommendedOrgCodes.length} In-State &amp; Federal Matches
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 text-xs flex-wrap">
          {recommendedOrgCodes.length > 0 && (
            <>
              <button
                type="button"
                onClick={() => onChange(recommendedOrgCodes)}
                className="text-[11px] font-bold text-amber-700 dark:text-amber-300 hover:underline transition-colors cursor-pointer flex items-center gap-1 bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded-md border border-amber-200 dark:border-amber-500/30"
              >
                <Sparkles size={11} />
                High Propensity Only ({recommendedOrgCodes.length})
              </button>
              <span className="text-slate-300 dark:text-slate-600">·</span>
            </>
          )}
          <button
            type="button"
            onClick={selectAllActiveCategory}
            className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 hover:underline transition-colors cursor-pointer"
          >
            {activeType === 'all' ? 'Select all' : `Select all ${ORG_TYPE_LABELS[activeType]?.label || ''}`}
          </button>
          <span className="text-slate-300 dark:text-slate-600">·</span>
          <button
            type="button"
            onClick={clearActiveCategory}
            className="text-[11px] font-medium text-slate-500 hover:text-slate-800 dark:hover:text-white transition-colors cursor-pointer"
          >
            {activeType === 'all' ? 'Clear all' : 'Clear'}
          </button>
          <span className="text-slate-300 dark:text-slate-600">·</span>
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-[11px] font-medium text-slate-500 hover:text-slate-800 dark:hover:text-white transition-colors cursor-pointer"
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="p-4 bg-slate-50 dark:bg-black/30 border border-slate-200 dark:border-white/10 rounded-xl space-y-3 animate-in fade-in duration-150">
          {/* Organization Type Menu Tabs & Search Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-1 bg-white dark:bg-white/[0.03] p-1 rounded-xl border border-slate-200 dark:border-white/10 shadow-2xs overflow-x-auto no-scrollbar">
              {[
                { id: 'all', label: 'All', icon: Globe },
                { id: 'utility', label: 'Utilities', icon: Zap },
                { id: 'federal', label: 'Federal', icon: Landmark },
                { id: 'state', label: 'State Agencies', icon: Building2 },
                { id: 'foundation', label: 'Philanthropy', icon: HeartHandshake },
              ].map((t) => {
                const Icon = t.icon;
                const isCurrent = activeType === t.id;
                const selCount = orgCountsByType.selected[t.id] || 0;
                const totCount = orgCountsByType.total[t.id] || 0;

                return (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setActiveType(t.id)}
                    className={clsx(
                      'px-2.5 py-1 rounded-lg text-xs font-semibold transition-all shrink-0 flex items-center gap-1.5 cursor-pointer',
                      isCurrent
                        ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-500/30 shadow-2xs'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5'
                    )}
                  >
                    <Icon size={12} className={isCurrent ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400'} />
                    <span>{t.label}</span>
                    <span
                      className={clsx(
                        'text-[9px] px-1.5 py-0.2 rounded-full font-bold font-mono',
                        isCurrent
                          ? 'bg-indigo-200 text-indigo-900 dark:bg-indigo-900/60 dark:text-indigo-200'
                          : 'bg-slate-200 dark:bg-white/10 text-slate-600 dark:text-slate-400'
                      )}
                    >
                      {selCount}/{totCount}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* State Filter & Search */}
            <div className="flex items-center gap-2 flex-1 sm:max-w-md">
              {availableStates.length > 0 && (
                <select
                  value={selectedState}
                  onChange={(e) => setSelectedState(e.target.value)}
                  className="px-2.5 py-1 bg-white dark:bg-black/40 border border-slate-200 dark:border-white/10 rounded-xl text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-indigo-500 shrink-0"
                >
                  <option value="all">All States ({availableStates.length})</option>
                  {availableStates.map(st => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              )}
              <div className="relative flex-1">
                <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Filter by name, state, acronym..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-7 pr-6 py-1 bg-white dark:bg-black/40 border border-slate-200 dark:border-white/10 rounded-xl text-xs text-slate-900 dark:text-white placeholder:text-slate-400 outline-none focus:border-indigo-500"
                />
                {search && (
                  <button
                    type="button"
                    onClick={() => setSearch('')}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 dark:hover:text-white cursor-pointer"
                  >
                    <X size={11} />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Interactive Organization Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-1.5 max-h-72 overflow-y-auto pr-1">
            {filteredOrgs.map((org) => {
              const isSelected = selected.includes(org.code);
              const isRecommended = recommendedOrgCodes.includes(org.code);
              return (
                <button
                  key={org.code}
                  type="button"
                  title={org.desc}
                  onClick={() => toggleOrg(org.code)}
                  className={clsx(
                    'p-2 rounded-xl border text-left transition-all relative group flex flex-col justify-between min-h-[56px] cursor-pointer',
                    isSelected
                      ? isRecommended
                        ? 'bg-amber-50/80 dark:bg-amber-950/20 border-amber-300 dark:border-amber-500/40 text-slate-900 dark:text-white shadow-2xs'
                        : 'bg-indigo-50/80 dark:bg-indigo-950/30 border-indigo-200 dark:border-indigo-500/40 text-slate-900 dark:text-white shadow-2xs'
                      : 'bg-white dark:bg-white/[0.02] border-slate-200/80 dark:border-white/5 hover:border-slate-300 dark:hover:border-white/15 text-slate-600 dark:text-slate-400'
                  )}
                >
                  <div className="flex items-center justify-between gap-1 w-full">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <OrgLogo org={org.code} size="xs" showTooltip={false} />
                      <span
                        className={clsx(
                          'text-[11px] font-bold truncate',
                          isSelected ? 'text-slate-900 dark:text-white' : 'text-slate-700 dark:text-slate-300'
                        )}
                      >
                        {org.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      {isRecommended && (
                        <span className="text-[7.5px] font-bold px-1 rounded bg-amber-100 text-amber-800 border border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-500/40">
                          ★ Match
                        </span>
                      )}
                      {org.state && (
                        <span className="text-[8px] font-bold px-1 rounded bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-300 font-mono">
                          {org.state}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-1 text-[9px]">
                    <span className="text-slate-500 dark:text-slate-400 truncate max-w-[90px]">
                      {org.count !== undefined ? `${org.count} opps` : org.category_label}
                    </span>
                    <div
                      className={clsx(
                        'w-3.5 h-3.5 rounded-sm flex items-center justify-center border shrink-0',
                        isSelected ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-slate-300 dark:border-white/20 bg-white dark:bg-black/30'
                      )}
                    >
                      {isSelected && <Check size={9} className="text-white" />}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {filteredOrgs.length === 0 && (
            <div className="py-4 text-center text-xs text-slate-400">
              No organizations found matching &ldquo;{search}&rdquo;
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Executive Summary & Strategic Diligence Card ────────────────────────────

function ExecutiveSummaryCard({ data }: { data: AnalysisResponse }) {
  const briefing = data.executive_briefing;
  if (!briefing) return null;

  return (
    <div className="bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 p-5 shadow-2xs space-y-4 text-slate-900 dark:text-white">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-white/5 pb-3">
        <div className="flex items-center gap-2.5">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-500/30">
            <Sparkles size={12} className="text-indigo-600 dark:text-indigo-400" />
            <span>Executive Strategic Diligence</span>
          </span>
          <span className="text-xs text-slate-300 dark:text-slate-600">|</span>
          <span className="text-[11px] font-mono font-bold text-slate-500 dark:text-slate-400">
            AI Opportunity Briefing
          </span>
        </div>

        <div className="text-xs text-slate-500 dark:text-slate-400 font-mono">
          Model: {briefing.model_used || 'GPT-4o'}
        </div>
      </div>

      {/* Structured Executive Summary Paragraphs */}
      <div className="space-y-2.5 text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
        {briefing.executive_summary_paragraphs?.map((p, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/80 dark:border-white/5"
            dangerouslySetInnerHTML={{ __html: p }}
          />
        ))}
      </div>

      {/* Strategic Takeaways Grid */}
      {briefing.strategic_takeaways?.length > 0 && (
        <div className="pt-1">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-1.5">
            <Target size={13} className="text-indigo-600 dark:text-indigo-400" /> Key Strategic Takeaways
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {briefing.strategic_takeaways.map((takeaway, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/80 dark:border-white/5 text-xs text-slate-800 dark:text-slate-200 flex items-start gap-2"
              >
                <span className="text-indigo-600 dark:text-indigo-400 font-bold mt-0.5">•</span>
                <span className="leading-snug">{takeaway}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tactical Strategy Modules */}
      {(briefing.grant_capture_strategy || briefing.regulatory_and_permitting_roadmap) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          {briefing.grant_capture_strategy && (
            <div className="p-3.5 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-500/30 text-xs text-indigo-900 dark:text-indigo-100 space-y-1">
              <div className="font-bold text-indigo-700 dark:text-indigo-300 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                <Layers size={13} /> Grant Capture Sequencing
              </div>
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[11.5px]">{briefing.grant_capture_strategy}</p>
            </div>
          )}
          {briefing.regulatory_and_permitting_roadmap && (
            <div className="p-3.5 rounded-xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-500/30 text-xs text-amber-900 dark:text-amber-100 space-y-1">
              <div className="font-bold text-amber-800 dark:text-amber-300 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                <ShieldCheck size={13} /> Regulatory &amp; Permitting Roadmap
              </div>
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[11.5px]">{briefing.regulatory_and_permitting_roadmap}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Download PDF Summary Report Button ──────────────────────────────────────

function DownloadPdfButton({ data }: { data: AnalysisResponse }) {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    try {
      setDownloading(true);
      const blob = await api.downloadProjectAnalysisPdf(data);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const rawTitle = data.profile.summary || (data as any).extracted_profile?.project_title || 'Project_Match_Analysis';
      const cleanTitle = rawTitle.slice(0, 30).replace(/[^a-zA-Z0-9_-]/g, '_').replace(/_+/g, '_');
      a.download = `${cleanTitle || 'Project'}_Match_and_Financing_Report.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Failed to download PDF summary report:', err);
      alert('Failed to generate PDF summary report. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleDownload}
      disabled={downloading}
      className={clsx(
        "inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-xl transition-all shadow-2xs cursor-pointer",
        downloading
          ? "bg-slate-100 dark:bg-white/10 text-slate-400 border border-slate-200 dark:border-white/10"
          : "bg-gradient-to-r from-[#00E5FF] to-[#00F5A0] hover:opacity-95 text-slate-950 font-bold shadow-glow-cyan-sm"
      )}
    >
      {downloading ? <Loader2 size={13} className="animate-spin text-slate-950" /> : <FileDown size={13} />}
      <span>{downloading ? 'Compiling Report...' : 'Download PDF Report'}</span>
    </button>
  );
}

// ─── Copy Decision Brief Button ─────────────────────────────────────────────

function CopyBriefButton({ data }: { data: AnalysisResponse }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const strong = data.matches.strong_matches || [];
    const conditional = data.matches.conditional_matches || [];
    const topMatches = [...strong, ...conditional].slice(0, 5);

    const lines = [
      `# Energy Innovation Terminal · STRATEGIC DECISION BRIEF`,
      `**Generated:** ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`,
      ``,
      `## Project Profile`,
      `- **Technologies:** ${data.profile.technology_areas.join(', ') || 'Energy Innovation'}`,
      `- **Activity Types:** ${data.profile.activity_types.join(', ') || 'Demonstration / R&D'}`,
      `- **Estimated TRL:** ${data.profile.estimated_trl || 'N/A'} | **Location:** ${data.profile.target_location || data.profile.ny_location || 'National / US'}`,
      `- **Project Scope:** ${data.profile.summary || 'Energy innovation deployment'}`,
      ``,
      `## Recommended Funding Solicitations`,
      ...topMatches.map((m, idx) => 
        `${idx + 1}. **${m.solicitation_number}** — ${m.name} (${m.agency || 'Agency'})
   - **Fit:** ${Math.round(m.fit_score * 100)}% (${m.match_type})
   - **Funding:** ${m.max_per_award ? `Up to $${(m.max_per_award/1e6).toFixed(2)}M` : (m.total_funding ? `$${(m.total_funding/1e6).toFixed(1)}M Total` : 'Varies')}
   - **Strategy:** ${m.why_it_fits}`
      ),
    ];

    navigator.clipboard.writeText(lines.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      type="button"
      onClick={handleCopy}
      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-xl border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-200 bg-white dark:bg-white/5 hover:bg-slate-50 dark:hover:bg-white/10 transition-all shadow-2xs cursor-pointer"
    >
      {copied ? <CheckCircle2 size={13} className="text-emerald-500" /> : <Copy size={13} />}
      <span>{copied ? 'Copied Brief' : 'Copy Brief'}</span>
    </button>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function AnalyzeProject() {
  const { includeNyserda, isNyserda } = useNyserda();
  const { data: agenciesData } = useQuery({
    queryKey: ['agencies'],
    queryFn: () => api.getAgencies(),
  });

  const baseOrganizations = useMemo(() => {
    if (includeNyserda) return ORGANIZATIONS;
    return ORGANIZATIONS.filter(o => !isNyserda(o.code));
  }, [includeNyserda, isNyserda]);

  const organizations: OrgMeta[] = useMemo(() => {
    const items = agenciesData?.items || [];
    let list: OrgMeta[] = [];
    if (!items.length) {
      list = baseOrganizations;
    } else {
      list = items.map((ag: any) => ({
        code: ag.name,
        label: ag.name,
        desc: ag.description || `${ag.name} (${ag.sub_type || ag.category_label || 'Energy Entity'})`,
        category: ag.category || 'utility',
        category_label: ag.category_label || (ag.category === 'utility' ? 'Electric & Gas Utility' : 'Funding Organization'),
        state: ag.state || '',
        count: ag.count,
        active_count: ag.active_count,
      }));
    }
    if (includeNyserda) return list;
    return list.filter(o => !isNyserda(o.code) && !isNyserda(o.label));
  }, [agenciesData, baseOrganizations, includeNyserda, isNyserda]);

  const [hasCustomAgencies, setHasCustomAgencies] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [shredOppId, setShredOppId] = useState<number | null>(null);
  const [isCharacterizingText, setIsCharacterizingText] = useState(false);
  const [charError, setCharError] = useState<string | null>(null);

  // LLM & OpenAI Connection Status State
  const [showApiModal, setShowApiModal] = useState(false);
  const [apiProvider, setApiProvider] = useState<'openai' | 'gemini' | 'anthropic'>('openai');
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [isTestingApi, setIsTestingApi] = useState(false);
  const [apiTestResponse, setApiTestResponse] = useState<TestConnectionResponse | null>(null);

  const { data: llmStatus, refetch: refetchLlmStatus } = useQuery<LlmStatusResponse>({
    queryKey: ['llm-status'],
    queryFn: () => api.getLlmStatus(),
    staleTime: 20000,
  });

  const handleTestApiConnection = async () => {
    setIsTestingApi(true);
    setApiTestResponse(null);
    try {
      const res = await api.testLlmConnection({
        provider: apiProvider,
        apiKey: apiKeyInput.trim() || undefined,
        model: selectedModel,
        saveKey: true,
      });
      setApiTestResponse(res);
      refetchLlmStatus();
    } catch (err: any) {
      setApiTestResponse({
        connected: false,
        provider: apiProvider,
        message: err.message || 'Connection test failed',
      });
    } finally {
      setIsTestingApi(false);
    }
  };

  const [input, setInput] = useState<AnalysisInput>(() => ({
    description: '', location: '', applicantType: '', estimatedCost: '',
    trl: 5, timeline: '', partners: '',
    technologyAreas: [], activityTypes: [], sectors: [], fuelTypes: [],
    agencies: (includeNyserda ? ORGANIZATIONS : ORGANIZATIONS.filter(o => !isNyserda(o.code))).map(o => o.code),
  }));

  // Keep input agencies synced when live data loads or when includeNyserda changes
  useEffect(() => {
    if (!hasCustomAgencies && organizations.length > 0) {
      setInput(prev => ({
        ...prev,
        agencies: organizations.map(o => o.code),
      }));
    } else if (!includeNyserda) {
      setInput(prev => ({
        ...prev,
        agencies: (prev.agencies || []).filter(a => !isNyserda(a)),
      }));
    }
  }, [organizations, hasCustomAgencies, includeNyserda, isNyserda]);

  const mutation = useMutation<AnalysisResponse, Error, AnalysisInput>({
    mutationFn: (data) => api.analyzeProject(data) as unknown as Promise<AnalysisResponse>,
  });

  const [extractedTitle, setExtractedTitle] = useState<string | null>(null);

  const detectStateFromLocation = (loc: string): string => {
    const l = (loc || '').toLowerCase().trim();
    if (l.includes('ca') || l.includes('california') || l.includes('san francisco') || l.includes('los angeles') || l.includes('san diego') || l.includes('sacramento') || l.includes('oakland') || l.includes('san jose')) return 'CA';
    if (l.includes('ma') || l.includes('massachusetts') || l.includes('boston') || l.includes('cambridge') || l.includes('worcester')) return 'MA';
    if (l.includes('tx') || l.includes('texas') || l.includes('houston') || l.includes('austin') || l.includes('dallas') || l.includes('san antonio')) return 'TX';
    if (l.includes('co') || l.includes('colorado') || l.includes('denver') || l.includes('boulder') || l.includes('colorado springs')) return 'CO';
    if (l.includes('il') || l.includes('illinois') || l.includes('chicago') || l.includes('cook county')) return 'IL';
    if (l.includes('nj') || l.includes('new jersey') || l.includes('newark') || l.includes('jersey city') || l.includes('trenton')) return 'NJ';
    if (l.includes('pa') || l.includes('pennsylvania') || l.includes('philadelphia') || l.includes('pittsburgh')) return 'PA';
    if (l.includes('oh') || l.includes('ohio') || l.includes('columbus') || l.includes('cleveland') || l.includes('cincinnati')) return 'OH';
    if (l.includes('mi') || l.includes('michigan') || l.includes('detroit') || l.includes('ann arbor') || l.includes('lansing')) return 'MI';
    if (l.includes('md') || l.includes('maryland') || l.includes('baltimore') || l.includes('annapolis')) return 'MD';
    if (l.includes('va') || l.includes('virginia') || l.includes('richmond') || l.includes('norfolk') || l.includes('arlington')) return 'VA';
    if (l.includes('wa') || l.includes('washington') || l.includes('seattle') || l.includes('spokane') || l.includes('tacoma')) return 'WA';
    if (l.includes('mn') || l.includes('minnesota') || l.includes('minneapolis') || l.includes('st. paul')) return 'MN';
    if (l.includes('wi') || l.includes('wisconsin') || l.includes('madison') || l.includes('milwaukee')) return 'WI';
    if (l.includes('nm') || l.includes('new mexico') || l.includes('albuquerque') || l.includes('santa fe')) return 'NM';
    if (l.includes('me') || l.includes('maine') || l.includes('portland') || l.includes('augusta')) return 'ME';
    if (l.includes('ct') || l.includes('connecticut') || l.includes('hartford') || l.includes('new haven') || l.includes('stamford')) return 'CT';
    if (l.includes('fl') || l.includes('florida') || l.includes('miami') || l.includes('orlando') || l.includes('tampa')) return 'FL';
    if (l.includes('ny') || l.includes('new york') || l.includes('brooklyn') || l.includes('manhattan') || l.includes('queens') || l.includes('bronx') || l.includes('albany') || l.includes('buffalo') || l.includes('rochester') || l.includes('syracuse') || l.includes('long island')) return 'NY';
    return 'NY';
  };

  const handleProfileExtracted = (extracted: ExtractedProjectProfile) => {
    const projState = detectStateFromLocation(extracted.location || '');

    // 1. All in-state state agencies MUST be automatically included by default
    const inStateAgencies = organizations
      .filter(o => o.category === 'state' && o.state === projState)
      .map(o => o.code);

    // 2. Suggested agencies from AI extraction
    let matchedAgencies: string[] = [];
    if (extracted.suggested_agencies && extracted.suggested_agencies.length > 0) {
      const lowerSuggestions = extracted.suggested_agencies.map(s => s.toLowerCase().trim());
      matchedAgencies = organizations
        .filter(o => 
          lowerSuggestions.some(s => 
            o.code.toLowerCase() === s || 
            o.label.toLowerCase() === s || 
            o.desc.toLowerCase().includes(s) || 
            s.includes(o.code.toLowerCase()) || 
            s.includes(o.label.toLowerCase())
          )
        )
        .map(o => o.code);
    }

    // 3. Federal agencies & foundations
    const federalAgencies = organizations
      .filter(o => o.category === 'federal')
      .map(o => o.code);

    // Combine: All In-State State Agencies + Matched In-Territory Utilities + Federal Bodies
    const selectedAgencies = Array.from(new Set([
      ...inStateAgencies,
      ...matchedAgencies,
      ...federalAgencies,
    ]));

    setInput(prev => ({
      ...prev,
      description: extracted.summary,
      technologyAreas: extracted.technology_areas,
      activityTypes: extracted.activity_types,
      sectors: extracted.sectors,
      fuelTypes: extracted.fuel_types,
      trl: extracted.estimated_trl,
      estimatedCost: String(extracted.estimated_cost),
      applicantType: extracted.applicant_type,
      location: extracted.location,
      timeline: extracted.timeline,
      partners: extracted.partners ? extracted.partners.join(', ') : '',
      extractedProfile: extracted,
      agencies: selectedAgencies.length > 0 ? selectedAgencies : organizations.map(o => o.code),
    }));
    setExtractedTitle(extracted.project_title);
  };

  const handleSelectSampleProject = (preset: SampleProject) => {
    const projState = detectStateFromLocation(preset.location);
    const inStateAgencies = organizations
      .filter(o => o.category === 'state' && o.state === projState)
      .map(o => o.code);
    const federalAgencies = organizations
      .filter(o => o.category === 'federal')
      .map(o => o.code);
    const utilityAgencies = organizations
      .filter(o => o.category === 'utility' && (o.state === projState || o.state?.includes(projState)))
      .map(o => o.code);
    const defaultSelectedOrgs = Array.from(new Set([...inStateAgencies, ...utilityAgencies, ...federalAgencies]));

    setInput({
      description: preset.description,
      location: preset.location,
      applicantType: preset.applicantType,
      estimatedCost: preset.estimatedCost,
      trl: preset.trl,
      timeline: preset.timeline,
      partners: preset.partners,
      technologyAreas: preset.technologyAreas,
      activityTypes: preset.activityTypes,
      sectors: preset.sectors,
      fuelTypes: preset.fuelTypes,
      agencies: defaultSelectedOrgs.length > 0 ? defaultSelectedOrgs : organizations.map(o => o.code),
    });
    setExtractedTitle(preset.name);
    setShowAdvanced(true);
  };

  const handleAutoCharacterizeText = async () => {
    if (!input.description?.trim()) return;
    setIsCharacterizingText(true);
    setCharError(null);
    try {
      const res = await api.extractTextProfile(input.description);
      if (res.extracted_profile) {
        handleProfileExtracted(res.extracted_profile);
      }
    } catch (err: any) {
      setCharError(err.message || 'Project characterization failed');
    } finally {
      setIsCharacterizingText(false);
    }
  };

  const hasInput = !!(input.description?.trim() || input.technologyAreas?.length || input.activityTypes?.length
    || input.sectors?.length || input.fuelTypes?.length || input.applicantType);

  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); if (hasInput) mutation.mutate(input); };

  const data = mutation.data;
  const inputClass = 'w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-white/10 text-xs bg-slate-50 dark:bg-black/30 text-slate-900 dark:text-white shadow-2xs focus:border-indigo-500 outline-none transition-all placeholder:text-slate-400 font-medium';

  return (
    <div className="max-w-7xl mx-auto space-y-6 relative pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-500/30">
              <Sparkles size={12} className="text-indigo-600 dark:text-indigo-400" />
              <span>Multi-Agency Matching Engine</span>
            </span>
            <span className="text-xs text-slate-300 dark:text-slate-600">|</span>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">5,747 Solicitations Index</span>
            <span className="text-xs text-slate-300 dark:text-slate-600">|</span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>PostgreSQL Vector Matching</span>
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Match Opportunities
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 dark:text-slate-400 max-w-3xl mt-1 leading-relaxed">
            Upload project documents or provide technical scope to automatically configure matching parameters. Surface the <strong>Top 15 Organizations most likely to say YES</strong> and <strong>Top 25 High-Conviction Solicitations</strong> screened for technical readiness, financial scale, and statutory mandate fit.
          </p>
        </div>

        {/* OpenAI / LLM API Connection Verification Button */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            type="button"
            onClick={() => setShowApiModal(true)}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl border border-slate-200 dark:border-white/10 text-xs font-bold text-slate-700 dark:text-slate-200 bg-white dark:bg-[#0d1424] hover:bg-slate-50 dark:hover:bg-white/5 transition-all shadow-2xs cursor-pointer"
          >
            <span className={clsx("w-2 h-2 rounded-full", llmStatus?.openai?.configured ? "bg-emerald-500 animate-pulse" : "bg-amber-500")} />
            <span>{llmStatus?.openai?.configured ? 'OpenAI Active (GPT-4o)' : 'Verify OpenAI API'}</span>
            <Settings2 size={13} className="text-slate-400 ml-0.5" />
          </button>
        </div>
      </div>

      {/* AI Document Upload & Extraction Studio */}
      <ProjectDocumentUploader
        onProfileExtracted={handleProfileExtracted}
        isAnalyzingParent={mutation.isPending}
      />

      {extractedTitle && (
        <div className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-500/30 text-emerald-900 dark:text-emerald-200 text-xs animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={14} className="text-emerald-600 dark:text-emerald-400 shrink-0" />
            <span>Synthesized profile for <strong>{extractedTitle}</strong>. Selected <strong>{input.agencies?.length || 0}</strong> top relevant funding organizations. Review parameters below and click <strong>&ldquo;Match Opportunities&rdquo;</strong>.</span>
          </div>
          <button
            type="button"
            onClick={() => setExtractedTitle(null)}
            className="text-emerald-700 dark:text-emerald-300 hover:underline font-bold text-xs cursor-pointer ml-2"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Parameters Form Card */}
      <div className="bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 p-5 shadow-2xs space-y-5">
        {/* Quick Test Sample Projects */}
        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-black/20 border border-slate-200/80 dark:border-white/5 space-y-2.5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
            <span className="text-[11px] font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
              <Sparkles size={12} className="text-indigo-600 dark:text-indigo-400" />
              <span>Quick Test Presets · 1-Click Sample Clean Energy Projects</span>
            </span>
            <span className="text-[10.5px] text-slate-500 dark:text-slate-400">Click any preset to autofill scope, budget &amp; taxonomy:</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
            {SAMPLE_PROJECT_PRESETS.map((preset) => (
              <button
                key={preset.id}
                type="button"
                onClick={() => handleSelectSampleProject(preset)}
                className="p-2.5 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.03] hover:border-indigo-400 dark:hover:border-indigo-500/50 hover:bg-indigo-50/50 dark:hover:bg-indigo-950/20 text-left transition-all group cursor-pointer shadow-2xs flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="text-base">{preset.icon}</span>
                    <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-300 font-mono">
                      {preset.badge}
                    </span>
                  </div>
                  <div className="text-[11.5px] font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 line-clamp-1">
                    {preset.name}
                  </div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-tight">
                    {preset.description}
                  </div>
                </div>
                <div className="mt-2 pt-1.5 border-t border-slate-100 dark:border-white/5 flex items-center justify-between text-[9.5px] text-indigo-600 dark:text-indigo-400 font-bold group-hover:underline">
                  <span>Load Scope</span>
                  <span>TRL {preset.trl} →</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Description */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Project Description &amp; Scope</label>
                {extractedTitle && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30">
                    Interpreted Scope
                  </span>
                )}
              </div>
              {input.description && (
                <button
                  type="button"
                  onClick={() => setInput({ ...input, description: '' })}
                  className="text-[11px] font-semibold text-slate-400 hover:text-slate-700 dark:hover:text-white transition-colors cursor-pointer"
                >
                  Clear description
                </button>
              )}
            </div>
            <textarea
              value={input.description}
              onChange={e => setInput({ ...input, description: e.target.value })}
              className={clsx(inputClass, 'min-h-[110px] resize-y leading-relaxed')}
              placeholder="Paste a detailed project description, scope of work, technical specifications, or executive summary..."
            />

            {/* Quick Auto-Characterize Action Button */}
            <div className="flex flex-wrap items-center justify-between gap-2 mt-2">
              <button
                type="button"
                disabled={isCharacterizingText || !input.description?.trim()}
                onClick={handleAutoCharacterizeText}
                className={clsx(
                  'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-2xs cursor-pointer',
                  input.description?.trim()
                    ? 'bg-cyan-500/15 text-[#00E5FF] border border-cyan-500/30 hover:bg-cyan-500/25 shadow-glow-cyan-sm'
                    : 'bg-slate-100 text-slate-400 dark:bg-white/5 dark:text-slate-500 border border-slate-200 dark:border-white/5 cursor-not-allowed'
                )}
              >
                {isCharacterizingText ? (
                  <>
                    <Loader2 size={13} className="animate-spin text-[#00E5FF]" />
                    <span>Interpreting Project Parameters...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={13} className="text-[#00E5FF]" />
                    <span>Auto-Characterize Project &amp; Set Parameters</span>
                  </>
                )}
              </button>

              {charError && (
                <span className="text-xs text-rose-500 font-medium">
                  {charError}
                </span>
              )}
            </div>
          </div>

          {/* Upgraded Multi-Type Organization Selector */}
          <OrganizationMultiSelector
            organizations={organizations}
            selected={input.agencies || []}
            suggestedAgencies={input.extractedProfile?.suggested_agencies}
            onChange={(selectedOrgs) => {
              setHasCustomAgencies(true);
              setInput({ ...input, agencies: selectedOrgs });
            }}
          />

          {/* Collapsible Advanced Parameters */}
          <div className="border-t border-slate-100 dark:border-white/5 pt-4">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center justify-between w-full text-left py-1 text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <SlidersHorizontal size={14} className="text-slate-400" />
                <span>Adjust Project Parameters (TRL, Location, Budget, Taxonomy)</span>
              </div>
              <ChevronDown size={14} className={clsx('transition-transform duration-200 text-slate-400', showAdvanced && 'rotate-180')} />
            </button>

            {/* Parameter Fields */}
            <div className={clsx('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4', !showAdvanced && 'hidden')}>
              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">Project Location</label>
                <div className="relative">
                  <MapPin size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input type="text" value={input.location} onChange={e => setInput({ ...input, location: e.target.value })}
                    placeholder="e.g. Brooklyn, NY" className={clsx(inputClass, 'pl-8')} />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">Estimated Cost ($)</label>
                <div className="relative">
                  <DollarSign size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input type="text" value={input.estimatedCost} onChange={e => setInput({ ...input, estimatedCost: e.target.value })}
                    placeholder="e.g. 5000000" className={clsx(inputClass, 'pl-8')} />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">Applicant Entity Type</label>
                <select value={input.applicantType} onChange={e => setInput({ ...input, applicantType: e.target.value })} className={inputClass}>
                  <option value="">Select type...</option>
                  {APPLICANT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">Target Timeline</label>
                <input type="text" value={input.timeline} onChange={e => setInput({ ...input, timeline: e.target.value })}
                  placeholder="e.g. 2025-2027" className={inputClass} />
              </div>

              <div className="sm:col-span-2 lg:col-span-4">
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">Confirmed / Proposed Partners</label>
                <input type="text" value={input.partners} onChange={e => setInput({ ...input, partners: e.target.value })}
                  placeholder="e.g. Con Edison, Columbia University, Energy Storage Systems Inc." className={inputClass} />
              </div>

              <MultiSelect label="Technology Areas" options={TECH_AREAS} selected={input.technologyAreas || []}
                onChange={v => setInput({ ...input, technologyAreas: v })} />
              <MultiSelect label="Activity Types" options={ACTIVITY_TYPES} selected={input.activityTypes || []}
                onChange={v => setInput({ ...input, activityTypes: v })} />
              <MultiSelect label="Target Sectors" options={SECTORS} selected={input.sectors || []}
                onChange={v => setInput({ ...input, sectors: v })} />
              <MultiSelect label="Fuel / Resource Types" options={FUEL_TYPES} selected={input.fuelTypes || []}
                onChange={v => setInput({ ...input, fuelTypes: v })} />

              {/* TRL Slider */}
              <div className="sm:col-span-2 lg:col-span-4 pt-2">
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Technology Readiness Level (TRL)</label>
                  <span className="text-xs font-mono text-indigo-600 dark:text-indigo-400 font-bold">TRL {input.trl ?? 5}</span>
                </div>
                <div>
                  {(() => {
                    const trlVal = input.trl ?? 5;
                    const trlDescriptions: Record<number, string> = {
                      1: 'Basic Principles Observed — Scientific research begins to be translated into applied R&D.',
                      2: 'Technology Concept Formulated — Practical applications identified. Papers establish concept.',
                      3: 'Experimental Proof of Concept — Active laboratory studies validate component predictions.',
                      4: 'Technology Validated in Lab — Components integrated to verify laboratory feasibility.',
                      5: 'Technology Validated in Relevant Environment — Integrated with realistic supporting elements.',
                      6: 'Technology Demonstrated in Relevant Environment — Representative pilot prototype operating.',
                      7: 'System Prototype Demonstration in Operational Environment — Near planned operational scale.',
                      8: 'System Complete and Qualified — Fully proven under rigorous operational conditions.',
                      9: 'System Proven in Operational Environment — Full commercial deployment and market scale.'
                    };
                    return (
                      <>
                        <input
                          type="range" min="1" max="9" step="1"
                          className="w-full h-2 rounded-lg appearance-none cursor-pointer bg-slate-200 dark:bg-white/10 accent-indigo-600"
                          value={trlVal} onChange={e => setInput({ ...input, trl: parseInt(e.target.value) })}
                        />
                        <div className="flex justify-between px-[2px] mt-1.5">
                          {[1,2,3,4,5,6,7,8,9].map(n => (
                            <button
                              key={n}
                              type="button"
                              onClick={() => setInput({ ...input, trl: n })}
                              className={clsx(
                                'w-5 h-5 rounded-full text-[9.5px] font-bold transition-all cursor-pointer',
                                n === trlVal
                                  ? 'bg-indigo-600 text-white font-black scale-110 shadow-2xs'
                                  : 'bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                              )}
                            >
                              {n}
                            </button>
                          ))}
                        </div>
                        <div className="mt-3 p-3 rounded-xl border text-xs bg-slate-50 dark:bg-black/30 border-slate-200 dark:border-white/10">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-900 dark:text-white font-mono">TRL {trlVal}</span>
                            <span className={clsx(
                              'px-2 py-0.5 rounded-full text-[9.5px] font-bold uppercase tracking-wider font-mono',
                              trlVal <= 3 ? 'bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-500/30' :
                              trlVal <= 6 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30' :
                              'bg-purple-50 text-purple-700 border border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-500/30'
                            )}>
                              {trlVal <= 3 ? 'Fundamental Research' : trlVal <= 6 ? 'Pilot & Demonstration' : 'Commercial Deployment'}
                            </span>
                          </div>
                          <p className="text-slate-600 dark:text-slate-400 mt-1 leading-relaxed text-[11.5px]">
                            {trlDescriptions[trlVal] || trlDescriptions[5]}
                          </p>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </div>
            </div>
          </div>

          {/* Submit Action */}
          <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-white/5">
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              {[
                input.technologyAreas?.length && `${input.technologyAreas.length} tech`,
                input.activityTypes?.length && `${input.activityTypes.length} activity`,
                input.sectors?.length && `${input.sectors.length} sector`,
                input.fuelTypes?.length && `${input.fuelTypes.length} fuel`,
              ].filter(Boolean).join(' · ')}
            </div>
            <button
              type="submit"
              disabled={mutation.isPending || !hasInput}
              className="bg-[#00E5FF] hover:bg-[#33ebff] text-slate-950 text-xs font-bold h-10 px-6 rounded-xl shadow-glow-cyan-sm hover:shadow-glow-cyan transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 cursor-pointer"
            >
              {mutation.isPending ? (
                <>
                  <Loader2 size={14} className="animate-spin text-slate-950" />
                  <span>Analyzing Opportunities...</span>
                </>
              ) : (
                <>
                  <Sparkles size={14} className="text-slate-950" />
                  <span>Match Opportunities</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* ─── Loading State ─── */}
      {mutation.isPending && (
        <div className="p-12 text-center bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 shadow-2xs space-y-3 animate-in fade-in duration-200">
          <Loader2 size={28} className="animate-spin text-indigo-600 dark:text-indigo-400 mx-auto" />
          <div className="text-sm font-bold text-slate-800 dark:text-slate-200">Evaluating Multi-Agency Opportunities &amp; Ranking Top Organizations...</div>
          <div className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">Running deep opportunity-by-opportunity vector matching and scoring criteria assessment against PostgreSQL.</div>
        </div>
      )}

      {/* ─── Error State ─── */}
      {mutation.isError && (
        <div className="p-4 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-500/30 text-rose-800 dark:text-rose-200 rounded-2xl flex items-start gap-3 text-xs">
          <AlertCircle size={16} className="text-rose-500 shrink-0 mt-0.5" />
          <div><span className="font-bold">Error:</span> {mutation.error?.message || 'Failed to analyze project matching'}</div>
        </div>
      )}

      {/* ─── Results Section ─── */}
      {mutation.isSuccess && data && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {/* Top level actions bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 py-2 border-b border-slate-200 dark:border-white/10">
            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400">
                <span className="font-bold text-slate-900 dark:text-white text-sm">
                  {data.top_10_say_yes?.length || data.top_say_yes?.length || 10}
                </span>
                <span>Top Sponsoring Organizations</span>
              </div>
              <div className="w-px h-3.5 bg-slate-200 dark:border-white/10" />
              <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400">
                <span className="font-bold text-slate-900 dark:text-white text-sm">
                  {data.top_20_opportunities?.length || data.top_50_opportunities?.length || data.top_25_opportunities?.length || 0}
                </span>
                <span>High-Conviction Solicitations (≥75% Fit)</span>
              </div>
              <div className="w-px h-3.5 bg-slate-200 dark:border-white/10" />
              <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400">
                <span className="font-bold text-slate-900 dark:text-white text-sm">{data.precedents?.length || 0}</span>
                <span>Precedents Analyzed</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <DownloadPdfButton data={data} />
              <CopyBriefButton data={data} />
            </div>
          </div>

          {/* 1. Executive Summary & Strategic Diligence Briefing */}
          <ExecutiveSummaryCard data={data} />

          {/* 2. Top Sponsoring Organizations Decision-Maker Outreach & 'Say Yes' Propensity Matrix */}
          {(data.top_10_say_yes || data.top_say_yes || data.top_15_say_yes || data.top_50_say_yes) && (
            <SayYesDecisionMakerMatrix
              organizations={data.top_10_say_yes || data.top_say_yes || data.top_15_say_yes || data.top_50_say_yes || []}
              projectTitle={extractedTitle || input.extractedProfile?.project_title || 'Proposed Project'}
              projectLocation={input.location}
              onSelectOpportunity={(oppId) => setShredOppId(oppId)}
            />
          )}

          {/* 3. High-Conviction Solicitations Grouped by Organization & Flat Table */}
          <Top25OpportunitiesTable
            matches={data.top_20_opportunities || data.top_50_opportunities || data.top_25_opportunities || (data.matches ? [
              ...(data.matches.strong_matches || []),
              ...(data.matches.conditional_matches || []),
              ...(data.matches.component_matches || []),
              ...(data.matches.watchlist || []),
            ] : [])}
            groupedOpportunities={data.grouped_opportunities}
            rawTopMatches={data.raw_top_20_opportunities || data.raw_top_25_opportunities}
            projectTitle={extractedTitle || input.extractedProfile?.project_title || 'Proposed Project'}
            onOpenShredder={(oppId) => setShredOppId(oppId)}
          />

          {/* 4. Multi-Agency Funding Sequencing & Empirical Precedents */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Multi-Agency Roadmap */}
            <div className="bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 p-5 shadow-2xs space-y-3">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-500/30">
                  <Layers size={12} className="text-indigo-600 dark:text-indigo-400" />
                  <span>3. Multi-Agency Sequencing</span>
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Non-Dilutive Funding Sequencing
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Structured grant capture sequence across state and federal demonstration vehicles.
              </p>
              {data.funding_architecture?.length > 0 ? (
                <div className="space-y-1.5 pt-1">
                  {data.funding_architecture.map((fa, i) => (
                    <div key={i} className="flex items-center justify-between gap-2 text-xs p-2.5 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/60 dark:border-white/5">
                      <span className="text-slate-800 dark:text-slate-200 font-medium truncate flex-1">{fa.workstream}</span>
                      <span className="text-indigo-600 dark:text-indigo-400 font-bold shrink-0 font-mono">→ {fa.opportunity}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-slate-400 py-3">Direct federal &amp; state grant alignment.</div>
              )}
            </div>

            {/* Empirical Precedents */}
            <div className="bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 p-5 shadow-2xs space-y-3">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/30 dark:text-amber-300 dark:border-amber-500/30">
                  <Building2 size={12} className="text-amber-600 dark:text-amber-400" />
                  <span>4. Historical Precedents</span>
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Historical Award Precedents
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Empirical selection track records from similar technology deployments in PostgreSQL.
              </p>
              {data.precedents?.length > 0 ? (
                <div className="space-y-1.5 pt-1">
                  {data.precedents.slice(0, 4).map((p, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/60 dark:border-white/5 space-y-0.5">
                      <div className="text-xs font-bold text-slate-900 dark:text-white leading-snug">{p.project_title}</div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center justify-between">
                        <span>{p.contractor_name}</span>
                        <span className="font-bold font-mono text-emerald-600 dark:text-emerald-400">{p.award_amount ? fmt(p.award_amount) : ''}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-slate-400 py-3">No historical precedent matches recorded.</div>
              )}
            </div>
          </div>

          {/* 5. National Lab Testbed & Scale-Up Capital Nexus */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* National Lab Validation Testbeds */}
            <div className="bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 p-5 shadow-2xs space-y-3">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-teal-50 text-teal-700 border border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:border-teal-500/30">
                  <FlaskConical size={12} className="text-teal-600 dark:text-teal-400" />
                  <span>5. DOE National Lab Testbed Alignment</span>
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Recommended Independent Validation Workstreams
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Suggested third-party hardware validation and specialized testbed access mechanisms (User Proposals / CRADA / SPP).
              </p>
              <div className="space-y-2 pt-1 text-xs">
                <div className="p-3 rounded-xl bg-teal-50/50 dark:bg-teal-950/20 border border-teal-200/60 dark:border-teal-500/20 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 dark:text-white">NREL Energy Systems Integration Facility (ESIF)</span>
                    <span className="px-1.5 py-0.2 rounded bg-teal-100 dark:bg-teal-900/50 text-teal-800 dark:text-teal-200 text-[10px] font-mono font-bold">TRL 5–8</span>
                  </div>
                  <div className="text-[11px] text-slate-600 dark:text-slate-300">
                    Grid-forming megawatt inverter hardware-in-the-loop (PHIL) &amp; continuous thermal runaway testing.
                  </div>
                  <div className="text-[10px] text-teal-700 dark:text-teal-400 font-mono pt-0.5 flex items-center justify-between">
                    <span>Access: CRADA / General User</span>
                    <span>Golden, CO</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/60 dark:border-white/5 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 dark:text-white">SLAC Stanford Synchrotron Radiation Lightsource (SSRL)</span>
                    <span className="px-1.5 py-0.2 rounded bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200 text-[10px] font-mono font-bold">TRL 3–6</span>
                  </div>
                  <div className="text-[11px] text-slate-600 dark:text-slate-300">
                    Operando X-ray absorption spectroscopy and nanoscale degradation analysis for novel electrodes/catalysts.
                  </div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono pt-0.5 flex items-center justify-between">
                    <span>Access: General User Proposal (GUP)</span>
                    <span>Menlo Park, CA</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Scale-Up Capital Continuum Nexus */}
            <div className="bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 p-5 shadow-2xs space-y-3">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30">
                  <TrendingUp size={12} className="text-emerald-600 dark:text-emerald-400" />
                  <span>6. Commercial Scale-Up &amp; Tax Equity</span>
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Multi-Stage Commercial Scaling Pathways
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                Post-grant follow-on financing structure across private venture equity, DOE LPO Title 17 loans, and IRA §48C credits.
              </p>
              <div className="space-y-2 pt-1 text-xs">
                <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-500/20 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 dark:text-white">IRA §48C Advanced Energy Project Credit</span>
                    <span className="px-1.5 py-0.2 rounded bg-emerald-100 dark:bg-emerald-900/50 text-emerald-800 dark:text-emerald-200 text-[10px] font-mono font-bold">30% ITC</span>
                  </div>
                  <div className="text-[11px] text-slate-600 dark:text-slate-300">
                    Direct qualification pathway for clean energy equipment manufacturing and critical minerals extraction.
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/60 dark:border-white/5 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 dark:text-white">DOE Loan Programs Office (Title 17 / CIFIA)</span>
                    <span className="px-1.5 py-0.2 rounded bg-indigo-100 dark:bg-indigo-900/50 text-indigo-800 dark:text-indigo-200 text-[10px] font-mono font-bold">Commercial Debt</span>
                  </div>
                  <div className="text-[11px] text-slate-600 dark:text-slate-300">
                    Senior secured debt financing at U.S. Treasury + spread for first-of-a-kind commercial manufacturing facilities.
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Statutory Independence & Public Information Notice Banner */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/80 dark:border-white/5 text-[11.5px] text-slate-500 dark:text-slate-400 leading-relaxed space-y-1">
            <div className="flex items-center gap-2 font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-[10.5px]">
              <ShieldCheck size={14} className="text-indigo-600 dark:text-indigo-400" />
              Public Information &amp; Regulatory Notice
            </div>
            <p>{data.disclaimer}</p>
          </div>
        </div>
      )}

      {/* OpenAI & LLM API Connection Verification Modal */}
      {showApiModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="relative w-full max-w-lg bg-white dark:bg-[#0d1424] border border-slate-200 dark:border-white/15 rounded-2xl shadow-2xl p-6 text-slate-900 dark:text-white space-y-5">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-500/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                  <PlugZap size={18} />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">OpenAI API Connection Settings</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Verify connectivity for project matching &amp; document parsing</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowApiModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>

            {/* Live Connection Status Overview */}
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/80 dark:border-white/10 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500 dark:text-slate-400 font-medium">Current Provider Status:</span>
                <span className={clsx(
                  "px-2 py-0.5 rounded-full font-bold uppercase text-[10px] tracking-wider flex items-center gap-1.5",
                  llmStatus?.openai?.configured
                    ? "bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30"
                    : "bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-500/30"
                )}>
                  <div className={clsx("w-1.5 h-1.5 rounded-full", llmStatus?.openai?.configured ? "bg-emerald-500 animate-pulse" : "bg-amber-500")} />
                  {llmStatus?.openai?.configured ? 'Active & Configured' : 'Key Unverified'}
                </span>
              </div>
              {llmStatus?.openai?.masked_key && (
                <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                  <span>Masked API Key:</span>
                  <span className="font-mono text-indigo-600 dark:text-indigo-400 font-bold">{llmStatus.openai.masked_key}</span>
                </div>
              )}
            </div>

            {/* Provider and Model Selection */}
            <div className="space-y-3.5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">AI Engine</label>
                  <select
                    value={apiProvider}
                    onChange={(e) => setApiProvider(e.target.value as any)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white outline-none focus:border-indigo-500"
                  >
                    <option value="openai">OpenAI (GPT-4o)</option>
                    <option value="gemini">Google Gemini</option>
                    <option value="anthropic">Anthropic Claude</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">Model Selection</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white outline-none focus:border-indigo-500"
                  >
                    {apiProvider === 'openai' ? (
                      <>
                        <option value="gpt-4o">gpt-4o (Recommended)</option>
                        <option value="gpt-4o-mini">gpt-4o-mini (Fast)</option>
                        <option value="o3-mini">o3-mini (Reasoning)</option>
                      </>
                    ) : apiProvider === 'gemini' ? (
                      <>
                        <option value="gemini-2.5-flash">gemini-2.5-flash</option>
                        <option value="gemini-2.5-pro">gemini-2.5-pro</option>
                      </>
                    ) : (
                      <>
                        <option value="claude-3-5-sonnet-20241022">claude-3-5-sonnet</option>
                        <option value="claude-3-5-haiku-20241022">claude-3-5-haiku</option>
                      </>
                    )}
                  </select>
                </div>
              </div>

              {/* Custom API Key Input */}
              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1 flex items-center justify-between">
                  <span>API Key (Optional Override)</span>
                  <span className="text-[10px] text-slate-400 font-normal">Leave blank to use environment default</span>
                </label>
                <div className="relative">
                  <input
                    type="password"
                    value={apiKeyInput}
                    onChange={(e) => setApiKeyInput(e.target.value)}
                    placeholder={llmStatus?.openai?.masked_key ? `Configured (${llmStatus.openai.masked_key})` : "sk-..."}
                    className="w-full px-3 py-2 pl-9 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 outline-none focus:border-indigo-500 font-mono"
                  />
                  <KeyRound size={13} className="absolute left-3 top-2.5 text-slate-400" />
                </div>
              </div>
            </div>

            {/* Test Connection Results Alert */}
            {apiTestResponse && (
              <div className={clsx(
                "p-3 rounded-xl border text-xs leading-relaxed animate-in fade-in duration-200",
                apiTestResponse.connected
                  ? "bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-500/30 text-emerald-900 dark:text-emerald-200"
                  : "bg-rose-50 dark:bg-rose-950/30 border-rose-200 dark:border-rose-500/30 text-rose-800 dark:text-rose-200"
              )}>
                <div className="flex items-start gap-2">
                  {apiTestResponse.connected ? (
                    <CheckCircle2 size={15} className="text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle size={15} className="text-rose-500 shrink-0 mt-0.5" />
                  )}
                  <div className="space-y-0.5">
                    <div className="font-bold">{apiTestResponse.message}</div>
                    {apiTestResponse.available_models && apiTestResponse.available_models.length > 0 && (
                      <div className="text-[10.5px] text-emerald-700 dark:text-emerald-300">
                        Models verified: {apiTestResponse.available_models.join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-white/10">
              <button
                type="button"
                onClick={() => setShowApiModal(false)}
                className="px-3.5 py-1.5 rounded-xl border border-slate-200 dark:border-white/10 text-xs font-bold text-slate-700 dark:text-slate-200 bg-white dark:bg-white/5 hover:bg-slate-50 dark:hover:bg-white/10 transition-colors cursor-pointer"
              >
                Close
              </button>
              <button
                type="button"
                onClick={handleTestApiConnection}
                disabled={isTestingApi}
                className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold flex items-center gap-1.5 shadow-2xs transition-all cursor-pointer disabled:opacity-50"
              >
                {isTestingApi ? (
                  <>
                    <Loader2 size={13} className="animate-spin text-white" />
                    <span>Verifying...</span>
                  </>
                ) : (
                  <>
                    <PlugZap size={13} />
                    <span>Test Connection</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
