import React, { useState, useMemo, useRef, useEffect } from 'react';
import {
  Zap, Landmark, Building2, HeartHandshake, FlaskConical,
  Search, ChevronDown, Check, X, Building, Globe, Filter
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from './OrgLogo';
import { useNyserda } from '../context/NyserdaContext';

export interface OrgOption {
  name: string;
  code?: string;
  full_name?: string;
  count?: number;
  active_count?: number;
  program_count?: number;
  category?: 'utility' | 'federal' | 'state' | 'foundation' | 'national_lab' | string;
  category_label?: string;
  jurisdiction?: string;
  state?: string;
  sub_type?: string;
  logo_domain?: string;
  website?: string;
}

export interface OrgSelectProps {
  value: string;
  onChange: (value: string) => void;
  options: OrgOption[];
  categories?: Array<{ id: string; label: string; count: number; icon?: string }>;
  placeholder?: string;
  label?: string;
  className?: string;
  allowClear?: boolean;
}

const CATEGORY_ICONS: Record<string, any> = {
  all: <Globe size={13} />,
  utility: <Zap size={13} className="text-amber-500" />,
  federal: <Landmark size={13} className="text-indigo-500" />,
  state: <Building2 size={13} className="text-blue-500" />,
  foundation: <HeartHandshake size={13} className="text-emerald-500" />,
  national_lab: <FlaskConical size={13} className="text-purple-500" />,
};

export function OrgSelect({
  value,
  onChange,
  options: rawOptions,
  categories,
  placeholder = "Select Organization...",
  label,
  className,
  allowClear = false,
}: OrgSelectProps) {
  const { includeNyserda, isNyserda } = useNyserda();
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const dropdownRef = useRef<HTMLDivElement>(null);

  const options = useMemo(() => {
    if (includeNyserda) return rawOptions;
    return rawOptions.filter(o => !isNyserda(o.name) && !isNyserda(o.code));
  }, [rawOptions, includeNyserda, isNyserda]);

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedOrg = useMemo(() => {
    return options.find(o => o.name === value || o.code === value) || { name: value, count: 0 };
  }, [options, value]);

  // Compute category counts
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { all: options.length };
    options.forEach(o => {
      const cat = o.category || 'other';
      counts[cat] = (counts[cat] || 0) + 1;
    });
    return counts;
  }, [options]);

  // Filtered options based on category tab & search query
  const filteredOptions = useMemo(() => {
    return options.filter(o => {
      // Category match
      if (activeCategory !== 'all' && o.category !== activeCategory) {
        return false;
      }
      // Search match
      if (!search.trim()) return true;
      const s = search.toLowerCase();
      return (
        o.name.toLowerCase().includes(s) ||
        (o.full_name && o.full_name.toLowerCase().includes(s)) ||
        (o.jurisdiction && o.jurisdiction.toLowerCase().includes(s)) ||
        (o.sub_type && o.sub_type.toLowerCase().includes(s)) ||
        (o.state && o.state.toLowerCase().includes(s))
      );
    });
  }, [options, activeCategory, search]);

  // Group filtered options by category for structured rendering
  const groupedFilteredOptions = useMemo(() => {
    if (activeCategory !== 'all') {
      return { [activeCategory]: filteredOptions };
    }
    const grouped: Record<string, OrgOption[]> = {};
    const categoryOrder = ['utility', 'federal', 'state', 'foundation', 'national_lab'];
    
    // Sort into ordered buckets
    categoryOrder.forEach(cat => { grouped[cat] = []; });
    filteredOptions.forEach(o => {
      const cat = o.category || 'state';
      if (!grouped[cat]) grouped[cat] = [];
      grouped[cat].push(o);
    });
    return grouped;
  }, [filteredOptions, activeCategory]);

  const CATEGORY_TITLES: Record<string, string> = {
    utility: '⚡ Electric & Gas Utilities',
    federal: '🏛️ Federal Agencies',
    state: '🗽 State Energy Agencies & Regulators',
    foundation: '🌱 Philanthropic Foundations',
    national_lab: '🔬 Research Institutions',
  };

  return (
    <div className={clsx("relative w-full", className)} ref={dropdownRef}>
      {label && (
        <label className="text-[11px] font-medium text-slate-500 uppercase tracking-wider mb-1.5 block">
          {label}
        </label>
      )}

      {/* Main Trigger Button */}
      <div
        className="px-3 py-2 bg-white border border-slate-200 rounded-lg shadow-sm flex items-center justify-between cursor-pointer hover:border-indigo-300 hover:shadow-md transition-all group"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2.5 min-w-0 pr-2">
          {value ? (
            <>
              <OrgLogo org={selectedOrg.name} size="xs" />
              <div className="min-w-0">
                <span className="text-[13px] font-semibold text-slate-900 group-hover:text-indigo-950 truncate block">
                  {selectedOrg.name}
                </span>
                {selectedOrg.sub_type && (
                  <span className="text-[10px] text-slate-500 font-medium block truncate">
                    {selectedOrg.sub_type} &middot; {selectedOrg.jurisdiction || 'US'}
                  </span>
                )}
              </div>
            </>
          ) : (
            <span className="text-[13px] text-slate-400 font-normal">{placeholder}</span>
          )}
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          {allowClear && value && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onChange('');
              }}
              className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100"
            >
              <X size={12} />
            </button>
          )}
          {selectedOrg.count !== undefined && selectedOrg.count > 0 && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-100">
              {selectedOrg.count} opps
            </span>
          )}
          <ChevronDown
            size={16}
            className={clsx("text-slate-400 transition-transform duration-200", isOpen && "rotate-180 text-indigo-600")}
          />
        </div>
      </div>

      {/* Dropdown Popover */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1.5 bg-white border border-slate-200 rounded-xl shadow-2xl z-50 overflow-hidden flex flex-col max-h-96 min-w-[360px] animate-in fade-in zoom-in-95 duration-100">
          
          {/* Search Header */}
          <div className="p-2.5 border-b border-slate-100 bg-slate-50/70 relative">
            <Search size={14} className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search organizations, utilities, states..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-8 pr-7 py-1.5 text-xs bg-white border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 shadow-sm"
              autoFocus
              onClick={(e) => e.stopPropagation()}
            />
            {search && (
              <button
                onClick={(e) => { e.stopPropagation(); setSearch(''); }}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X size={12} />
              </button>
            )}
          </div>

          {/* Quick Category Filter Pills */}
          <div className="flex items-center gap-1 p-2 bg-slate-50 border-b border-slate-100 overflow-x-auto text-[11px] no-scrollbar">
            <button
              type="button"
              onClick={() => setActiveCategory('all')}
              className={clsx(
                "px-2.5 py-1 rounded-md font-medium shrink-0 flex items-center gap-1 transition-colors",
                activeCategory === 'all'
                  ? "bg-indigo-600 text-white font-semibold shadow-xs"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
              )}
            >
              <Globe size={11} /> All ({categoryCounts.all || 0})
            </button>
            <button
              type="button"
              onClick={() => setActiveCategory('utility')}
              className={clsx(
                "px-2.5 py-1 rounded-md font-medium shrink-0 flex items-center gap-1 transition-colors",
                activeCategory === 'utility'
                  ? "bg-amber-600 text-white font-semibold shadow-xs"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-amber-50 hover:text-amber-700"
              )}
            >
              <Zap size={11} className={activeCategory === 'utility' ? 'text-white' : 'text-amber-500'} />
              Utilities ({categoryCounts.utility || 0})
            </button>
            <button
              type="button"
              onClick={() => setActiveCategory('federal')}
              className={clsx(
                "px-2.5 py-1 rounded-md font-medium shrink-0 flex items-center gap-1 transition-colors",
                activeCategory === 'federal'
                  ? "bg-indigo-600 text-white font-semibold shadow-xs"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-indigo-50 hover:text-indigo-700"
              )}
            >
              <Landmark size={11} className={activeCategory === 'federal' ? 'text-white' : 'text-indigo-500'} />
              Federal ({categoryCounts.federal || 0})
            </button>
            <button
              type="button"
              onClick={() => setActiveCategory('state')}
              className={clsx(
                "px-2.5 py-1 rounded-md font-medium shrink-0 flex items-center gap-1 transition-colors",
                activeCategory === 'state'
                  ? "bg-blue-600 text-white font-semibold shadow-xs"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-blue-50 hover:text-blue-700"
              )}
            >
              <Building2 size={11} className={activeCategory === 'state' ? 'text-white' : 'text-blue-500'} />
              State ({categoryCounts.state || 0})
            </button>
            {categoryCounts.foundation && (
              <button
                type="button"
                onClick={() => setActiveCategory('foundation')}
                className={clsx(
                  "px-2.5 py-1 rounded-md font-medium shrink-0 flex items-center gap-1 transition-colors",
                  activeCategory === 'foundation'
                    ? "bg-emerald-600 text-white font-semibold shadow-xs"
                    : "bg-white text-slate-600 border border-slate-200 hover:bg-emerald-50 hover:text-emerald-700"
                )}
              >
                <HeartHandshake size={11} className={activeCategory === 'foundation' ? 'text-white' : 'text-emerald-500'} />
                Philanthropy ({categoryCounts.foundation || 0})
              </button>
            )}
          </div>

          {/* Options List */}
          <div className="flex-1 overflow-y-auto p-1.5 space-y-3">
            {filteredOptions.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">
                No organizations found matching "{search}"
              </div>
            ) : (
              Object.entries(groupedFilteredOptions).map(([catKey, orgList]) => {
                if (!orgList || orgList.length === 0) return null;
                return (
                  <div key={catKey} className="space-y-1">
                    {activeCategory === 'all' && (
                      <div className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between border-b border-slate-100">
                        <span>{CATEGORY_TITLES[catKey] || catKey}</span>
                        <span>{orgList.length}</span>
                      </div>
                    )}
                    {orgList.map(org => {
                      const isSelected = org.name === value || org.code === value;
                      return (
                        <button
                          key={org.name}
                          type="button"
                          onClick={() => {
                            onChange(org.name);
                            setIsOpen(false);
                          }}
                          className={clsx(
                            "w-full text-left p-2 rounded-lg text-xs flex items-center justify-between gap-2 transition-all",
                            isSelected
                              ? "bg-indigo-50 text-indigo-950 border border-indigo-200 font-semibold"
                              : "hover:bg-slate-50 text-slate-700 border border-transparent"
                          )}
                        >
                          <div className="flex items-center gap-2.5 min-w-0">
                            <OrgLogo org={org.name} size="xs" />
                            <div className="min-w-0">
                              <div className="flex items-center gap-1.5">
                                <span className="font-semibold text-slate-900 truncate">
                                  {org.name}
                                </span>
                                {org.state && (
                                  <span className="px-1 py-0.2 rounded text-[9px] font-bold bg-slate-100 text-slate-600 uppercase">
                                    {org.state}
                                  </span>
                                )}
                              </div>
                              {org.sub_type && (
                                <p className="text-[10px] text-slate-500 truncate font-normal">
                                  {org.sub_type}
                                </p>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center gap-1.5 shrink-0">
                            {org.count !== undefined && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-600">
                                {org.count}
                              </span>
                            )}
                            {isSelected && <Check size={14} className="text-indigo-600" />}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
