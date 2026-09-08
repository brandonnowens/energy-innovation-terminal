import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  DollarSign, X, CheckCircle2, TrendingUp, ShieldCheck, 
  Building2, Landmark, PieChart, Info, HelpCircle 
} from 'lucide-react';

interface IraCalculatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultCapex?: number;
  defaultGrant?: number;
  defaultSector?: string;
  projectTitle?: string;
}

export const IraCalculatorModal: React.FC<IraCalculatorModalProps> = ({
  isOpen,
  onClose,
  defaultCapex = 20000000,
  defaultGrant = 4000000,
  defaultSector = 'clean_hydrogen',
  projectTitle = 'Clean Energy Demonstration Project'
}) => {
  const [capex, setCapex] = useState<number>(defaultCapex);
  const [grant, setGrant] = useState<number>(defaultGrant);
  const [sector, setSector] = useState<string>(defaultSector);
  const [prevailingWage, setPrevailingWage] = useState<boolean>(true);
  const [energyComm, setEnergyComm] = useState<boolean>(true);
  const [domesticContent, setDomesticContent] = useState<boolean>(true);
  const [lowIncome, setLowIncome] = useState<boolean>(false);
  const [monetization, setMonetization] = useState<'transferability' | 'direct_pay'>('transferability');
  const [transferRate, setTransferRate] = useState<number>(93);
  const [debtPct, setDebtPct] = useState<number>(30);

  const { data: calculation, isLoading } = useQuery({
    queryKey: [
      'ira-calc', capex, grant, sector, prevailingWage, 
      energyComm, domesticContent, lowIncome, monetization, transferRate, debtPct
    ],
    queryFn: async () => {
      const res = await fetch('/api/ira-calculator/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_title: projectTitle,
          technology_sector: sector,
          total_project_capex: capex,
          expected_grant_funding: grant,
          meets_prevailing_wage_apprenticeship: prevailingWage,
          is_energy_community: energyComm,
          is_domestic_content: domesticContent,
          is_low_income_community: lowIncome,
          monetization_route: monetization,
          transferability_price_cents_on_dollar: transferRate,
          senior_debt_pct: debtPct
        })
      });
      if (!res.ok) throw new Error('Calculation error');
      return res.json();
    },
    enabled: isOpen
  });

  if (!isOpen) return null;

  const sectors = [
    { id: 'clean_hydrogen', name: 'Clean Hydrogen (§45V / §48)', sub: 'Up to $3.00/kg or 50% ITC' },
    { id: 'energy_storage', name: 'Energy Storage (§48)', sub: '30% - 50% Investment Tax Credit' },
    { id: 'carbon_capture', name: 'Carbon Capture & DAC (§45Q)', sub: '$85-$180 per metric ton' },
    { id: 'advanced_nuclear', name: 'Advanced Nuclear & SMR (§45U / §48E)', sub: 'Up to $15/MWh or 50% ITC' },
    { id: 'solar_wind', name: 'Clean Electricity Solar/Wind (§48E / §45Y)', sub: '30% - 50% ITC' },
    { id: 'clean_fuels', name: 'Clean Fuels & SAF (§45Z)', sub: 'Up to $1.75/gal' }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-5xl max-h-[92vh] flex flex-col rounded-2xl border dark:border-white/10 border-slate-200 dark:bg-[#0b1329] bg-white shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b dark:border-white/10 border-slate-200 dark:bg-[#070d1e] bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-500">
              <DollarSign className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  IRA 2022 Capital Stack Co-Optimizer
                </span>
                <span className="text-xs font-mono dark:text-slate-400 text-slate-500">
                  {calculation?.ira_provision?.code || 'IRA §48 / §45'}
                </span>
              </div>
              <h2 className="text-lg font-bold dark:text-white text-slate-900 mt-0.5">
                Tax Credit Monetization & Blended WACC Studio
              </h2>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-white/10 text-slate-400 hover:text-slate-600 dark:hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Studio Body */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column: Interactive Parameters (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            
            {/* Sector Picker */}
            <div className="space-y-1">
              <label className="text-xs font-bold dark:text-slate-300 text-slate-700">Technology Sector & IRA Credit</label>
              <select
                value={sector}
                onChange={e => setSector(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg dark:bg-[#0e1626] bg-slate-50 border dark:border-white/10 border-slate-200 dark:text-white text-slate-900 outline-none font-semibold"
              >
                {sectors.map(s => (
                  <option key={s.id} value={s.id}>{s.name} — {s.sub}</option>
                ))}
              </select>
            </div>

            {/* CapEx & Grant Sliders */}
            <div className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 space-y-3">
              <div>
                <div className="flex justify-between text-xs font-bold">
                  <span className="dark:text-slate-300 text-slate-700">Total Project CapEx</span>
                  <span className="text-emerald-500 font-mono">${(capex / 1000000).toFixed(1)}M</span>
                </div>
                <input 
                  type="range" min="1000000" max="100000000" step="1000000"
                  value={capex} onChange={e => setCapex(Number(e.target.value))}
                  className="w-full h-1.5 mt-2 bg-slate-300 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-bold">
                  <span className="dark:text-slate-300 text-slate-700">Expected Grant Co-Funding</span>
                  <span className="text-cyan-500 font-mono">${(grant / 1000000).toFixed(1)}M ({((grant / capex) * 100).toFixed(0)}%)</span>
                </div>
                <input 
                  type="range" min="0" max={capex * 0.6} step="500000"
                  value={grant} onChange={e => setGrant(Number(e.target.value))}
                  className="w-full h-1.5 mt-2 bg-slate-300 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-bold">
                  <span className="dark:text-slate-300 text-slate-700">Senior Project Debt</span>
                  <span className="text-indigo-500 font-mono">{debtPct}% (${((debtPct / 100) * capex / 1000000).toFixed(1)}M)</span>
                </div>
                <input 
                  type="range" min="0" max="60" step="5"
                  value={debtPct} onChange={e => setDebtPct(Number(e.target.value))}
                  className="w-full h-1.5 mt-2 bg-slate-300 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                />
              </div>
            </div>

            {/* Bonus Adders Checkboxes */}
            <div className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 space-y-2.5">
              <span className="text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-600 block">
                IRA Statutory Bonus Adders
              </span>

              <label className="flex items-center justify-between text-xs cursor-pointer">
                <span className="dark:text-slate-300 text-slate-700">Prevailing Wage & Apprenticeship (5x Multiplier)</span>
                <input type="checkbox" checked={prevailingWage} onChange={e => setPrevailingWage(e.target.checked)} className="rounded accent-emerald-500" />
              </label>

              <label className="flex items-center justify-between text-xs cursor-pointer">
                <span className="dark:text-slate-300 text-slate-700">+10% Energy Communities Adder</span>
                <input type="checkbox" checked={energyComm} onChange={e => setEnergyComm(e.target.checked)} className="rounded accent-emerald-500" />
              </label>

              <label className="flex items-center justify-between text-xs cursor-pointer">
                <span className="dark:text-slate-300 text-slate-700">+10% U.S. Domestic Content Adder</span>
                <input type="checkbox" checked={domesticContent} onChange={e => setDomesticContent(e.target.checked)} className="rounded accent-emerald-500" />
              </label>

              <label className="flex items-center justify-between text-xs cursor-pointer">
                <span className="dark:text-slate-300 text-slate-700">+10% Low-Income Community Allocation</span>
                <input type="checkbox" checked={lowIncome} onChange={e => setLowIncome(e.target.checked)} className="rounded accent-emerald-500" />
              </label>
            </div>

            {/* Monetization Route */}
            <div className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 space-y-2">
              <span className="text-xs font-bold dark:text-slate-300 text-slate-700 block">Monetization Mechanism</span>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setMonetization('transferability')}
                  className={`py-2 px-3 rounded-lg text-xs font-bold transition cursor-pointer ${
                    monetization === 'transferability'
                      ? 'bg-emerald-500/20 text-emerald-500 border border-emerald-500/40'
                      : 'dark:bg-white/5 bg-slate-200 text-slate-600 dark:text-slate-400'
                  }`}
                >
                  Transferability (Sale)
                </button>
                <button
                  type="button"
                  onClick={() => setMonetization('direct_pay')}
                  className={`py-2 px-3 rounded-lg text-xs font-bold transition cursor-pointer ${
                    monetization === 'direct_pay'
                      ? 'bg-emerald-500/20 text-emerald-500 border border-emerald-500/40'
                      : 'dark:bg-white/5 bg-slate-200 text-slate-600 dark:text-slate-400'
                  }`}
                >
                  Direct Pay (IRS 100%)
                </button>
              </div>
              {monetization === 'transferability' && (
                <div className="pt-1 flex items-center justify-between text-xs dark:text-slate-400 text-slate-500">
                  <span>Transfer Market Price:</span>
                  <span className="font-bold text-cyan-500">{transferRate}¢ / $1 Credit</span>
                </div>
              )}
            </div>

          </div>

          {/* Right Column: Visual Capital Stack & Metrics (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            
            {/* Top 3 KPI Hero Metric Cards */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50">
                <div className="text-[11px] font-semibold dark:text-slate-400 text-slate-500">Total Tax Credit</div>
                <div className="text-2xl font-black text-emerald-500 mt-1">
                  {calculation?.tax_credit_breakdown?.total_credit_pct || 0}%
                </div>
                <div className="text-[10px] dark:text-slate-400 text-slate-500 mt-0.5 font-mono">
                  ${((calculation?.tax_credit_breakdown?.nominal_credit_usd || 0) / 1000000).toFixed(2)}M Value
                </div>
              </div>

              <div className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50">
                <div className="text-[11px] font-semibold dark:text-slate-400 text-slate-500">Equity Reduction</div>
                <div className="text-2xl font-black text-cyan-500 mt-1">
                  {calculation?.financial_metrics?.private_equity_reduction_pct || 0}%
                </div>
                <div className="text-[10px] dark:text-slate-400 text-slate-500 mt-0.5">
                  {calculation?.financial_metrics?.leverage_multiplier || 1}x Leverage
                </div>
              </div>

              <div className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50">
                <div className="text-[11px] font-semibold dark:text-slate-400 text-slate-500">Blended WACC</div>
                <div className="text-2xl font-black text-indigo-500 mt-1">
                  {calculation?.financial_metrics?.blended_wacc_pct || 0}%
                </div>
                <div className="text-[10px] line-through dark:text-slate-500 text-slate-400 mt-0.5">
                  vs {calculation?.financial_metrics?.traditional_unassisted_wacc_pct || 14.5}% Market
                </div>
              </div>
            </div>

            {/* Visual Capital Stack Waterfall Chart */}
            <div className="p-5 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider dark:text-slate-300 text-slate-700 flex items-center gap-2">
                  <PieChart className="w-4 h-4 text-emerald-500" />
                  Optimized Capital Stack Waterfall
                </h3>
                <span className="text-xs font-bold dark:text-white text-slate-900 font-mono">
                  ${(capex / 1000000).toFixed(1)}M Total Project
                </span>
              </div>

              {/* Progress Stack Bar */}
              <div className="h-6 w-full rounded-lg overflow-hidden flex bg-slate-200 dark:bg-slate-800">
                {calculation?.capital_stack_waterfall?.map((item: any, i: number) => (
                  <div
                    key={i}
                    style={{ width: `${item.pct_of_capex}%`, backgroundColor: item.color }}
                    className="h-full transition-all duration-300 relative group cursor-pointer"
                    title={`${item.source}: $${Number(item.amount_usd).toLocaleString()} (${item.pct_of_capex}%)`}
                  />
                ))}
              </div>

              {/* Legend Breakdown Grid */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                {calculation?.capital_stack_waterfall?.map((item: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2.5 rounded-lg dark:bg-[#070d1e] bg-white border dark:border-white/5 border-slate-200 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                      <span className="font-semibold dark:text-slate-300 text-slate-700 text-[11px]">{item.source}</span>
                    </div>
                    <div className="text-right font-mono font-bold dark:text-white text-slate-900 text-xs">
                      ${(item.amount_usd / 1000000).toFixed(2)}M ({item.pct_of_capex}%)
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Strategic Summary Callout */}
            <div className="p-4 rounded-xl dark:bg-emerald-500/5 bg-emerald-50 border border-emerald-500/20 text-xs dark:text-emerald-300 text-emerald-900 leading-relaxed space-y-1">
              <span className="font-bold flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                CFO & Investor Takeaway:
              </span>
              <p>
                By combining a <span className="font-bold text-cyan-400">${(grant / 1000000).toFixed(1)}M public grant</span> with <span className="font-bold text-emerald-400">${((calculation?.tax_credit_breakdown?.net_cash_proceeds_usd || 0) / 1000000).toFixed(2)}M in transferable IRA tax credits</span>, this ${ (capex / 1000000).toFixed(1) }M project requires only <span className="font-bold text-amber-400">${((calculation?.capital_stack_waterfall?.[3]?.amount_usd || 0) / 1000000).toFixed(2)}M in private sponsor equity</span>, slashing your blended WACC to <span className="font-bold text-indigo-400">{calculation?.financial_metrics?.blended_wacc_pct}%</span>.
              </p>
            </div>

          </div>

        </div>

        {/* Footer */}
        <div className="p-4 border-t dark:border-white/10 border-slate-200 dark:bg-[#070d1e] bg-slate-50 flex items-center justify-between text-xs">
          <span className="text-slate-500 font-mono">Governing Rule: {calculation?.ira_provision?.name || 'IRA §48 / §45'}</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition"
          >
            Close Capital Studio
          </button>
        </div>

      </div>
    </div>
  );
};
