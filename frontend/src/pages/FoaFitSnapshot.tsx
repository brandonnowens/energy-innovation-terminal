import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { apiFetch } from '../api/client';
import { useSEO } from '../utils/seo';
import {
  Building2, Search, Target, AlertTriangle, ChevronRight,
  Download, Printer, AlertCircle, Calendar, ShieldCheck, FileText, CheckCircle2
} from 'lucide-react';
import clsx from 'clsx';

const TECH_AREAS = [
  'Energy Storage', 'Grid Modernization', 'Clean Hydrogen',
  'Geothermal Systems', 'Carbon Capture', 'Industrial Decarbonization',
  'Solar', 'Wind', 'Electric Vehicles', 'Building Efficiency'
];

const APPLICANT_TYPES = [
  'Commercial Business/Startup',
  'University/Research',
  'Non-Profit',
  'Consortium'
];

type ExampleSolicitation = {
  id: number;
  name: string;
  solicitation_number: string;
  agency: string;
  status: string;
  due_date?: string | null;
  max_per_award?: number | null;
};

type FoaClass = {
  agency: string;
  agency_code: string;
  class_label: string;
  window_risk: 'closing_soon' | 'open' | 'forecasted' | 'closed';
  fit_score: number;
  why_fit: string;
  example_solicitations: ExampleSolicitation[];
};

type MisfitWarning = {
  class_label: string;
  agency_code: string;
  why_wrong: string;
  risk_type: string;
  fit_score?: number;
};

type SnapshotData = {
  company: {
    name: string;
    description: string;
    tech_tags: string[];
    trl?: number | null;
    applicant_type: string;
  };
  snapshot_date: string;
  top_foa_classes: FoaClass[];
  misfit_warnings: MisfitWarning[];
  recommended_next_action: string;
  generated_by: string;
};

export default function FoaFitSnapshot() {
  useSEO({
    title: 'FOA / Company Fit Snapshot | Energy Innovation Terminal',
    description: 'Get a one-page FOA/company fit snapshot showing which federal and state funding solicitation classes match your hardtech company — and which to avoid.',
  });

  const [searchParams] = useSearchParams();
  
  const initialTags = searchParams.get('tags') 
    ? searchParams.get('tags')!.split(',').map(t => t.trim()).filter(Boolean)
    : [];

  const [form, setForm] = useState({
    companyName: searchParams.get('company') || '',
    description: searchParams.get('description') || '',
    techTags: initialTags,
    trl: searchParams.get('trl') ? parseInt(searchParams.get('trl')!) : 4,
    applicantType: searchParams.get('type') || 'Commercial Business/Startup',
    location: searchParams.get('location') || '',
  });

  const [snapshot, setSnapshot] = useState<SnapshotData | null>(null);

  const mutation = useMutation({
    mutationFn: async (formData: typeof form) => {
      const res = await apiFetch('/api/company-fit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: formData.companyName,
          description: formData.description,
          tech_tags: formData.techTags,
          trl: formData.trl,
          applicant_type: formData.applicantType,
          location: formData.location,
        }),
      });
      if (!res.ok) throw new Error('Failed to generate snapshot');
      return res.json() as Promise<SnapshotData>;
    },
    onSuccess: (data) => setSnapshot(data),
  });

  const toggleTag = (tag: string) => {
    setForm(prev => ({
      ...prev,
      techTags: prev.techTags.includes(tag) 
        ? prev.techTags.filter(t => t !== tag)
        : [...prev.techTags, tag]
    }));
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPDF = async () => {
    try {
      const params = new URLSearchParams({
        company_name: form.companyName,
        description: form.description,
        tech_tags: form.techTags.join(','),
        trl: form.trl.toString(),
        applicant_type: form.applicantType,
        location: form.location,
      });
      const url = `/api/company-fit/snapshot-pdf?${params.toString()}`;
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `FOA_Snapshot_${form.companyName.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      console.error('Failed to download PDF:', err);
    }
  };

  const isFormValid = form.companyName.length > 0 && form.description.length >= 20;

  const renderWindowRiskBadge = (risk: string) => {
    switch (risk) {
      case 'closing_soon':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400 border border-red-200 dark:border-red-800">
            <AlertTriangle size={12} /> ⚠ Closing Soon
          </span>
        );
      case 'open':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400 border border-green-200 dark:border-green-800">
            <CheckCircle2 size={12} /> ✓ Open Window
          </span>
        );
      case 'forecasted':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-800">
            <Calendar size={12} /> ◔ Forecasted
          </span>
        );
      case 'closed':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
            — Closed
          </span>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 w-full">
      <style>
        {`
          @media print {
            nav, header, .no-print, button, .sidebar { display: none !important; }
            .snapshot-card { box-shadow: none !important; border: 1px solid #ccc !important; }
            body { background: white !important; }
            .snapshot-card { page-break-inside: avoid; margin: 0 !important; }
          }
        `}
      </style>

      {!snapshot ? (
        <div className="space-y-6">
          <div className="border-b border-slate-200 dark:border-white/10 pb-4">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Target className="text-cyan-500" />
              FOA / Company Fit Snapshot
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Analyze a company's technology and readiness to identify matching funding opportunities.
            </p>
          </div>

          <div className="bg-white dark:bg-[#0b1329] border border-slate-200 dark:border-white/10 rounded-xl p-6 shadow-sm">
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Company Name *</label>
                <input
                  type="text"
                  value={form.companyName}
                  onChange={e => setForm(f => ({ ...f, companyName: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition"
                  placeholder="e.g. Acme Clean Energy"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Short Description * (min 20 chars)</label>
                <textarea
                  value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition"
                  placeholder="Describe the company's core technology and business model..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Tech Areas</label>
                <div className="flex flex-wrap gap-2">
                  {TECH_AREAS.map(tag => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => toggleTag(tag)}
                      className={clsx(
                        "px-3 py-1.5 rounded-full text-xs font-medium border transition-colors",
                        form.techTags.includes(tag)
                          ? "bg-cyan-100 border-cyan-300 text-cyan-800 dark:bg-cyan-900/40 dark:border-cyan-700 dark:text-cyan-300"
                          : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100 dark:bg-slate-800/50 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-800"
                      )}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Applicant Type</label>
                  <select
                    value={form.applicantType}
                    onChange={e => setForm(f => ({ ...f, applicantType: e.target.value }))}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition"
                  >
                    {APPLICANT_TYPES.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">TRL Level: {form.trl}</label>
                  <input
                    type="range"
                    min="1"
                    max="9"
                    value={form.trl}
                    onChange={e => setForm(f => ({ ...f, trl: parseInt(e.target.value) }))}
                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer dark:bg-slate-700 mt-3"
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>1 (Concept)</span>
                    <span>9 (Commercial)</span>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Location (Optional)</label>
                <input
                  type="text"
                  value={form.location}
                  onChange={e => setForm(f => ({ ...f, location: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition"
                  placeholder="City, State"
                />
              </div>

              <div className="pt-4 flex justify-end">
                <button
                  onClick={() => mutation.mutate(form)}
                  disabled={!isFormValid || mutation.isPending}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {mutation.isPending ? 'Generating...' : 'Generate Snapshot'}
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="no-print flex items-center justify-between mb-4">
            <button 
              onClick={() => setSnapshot(null)}
              className="text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 font-medium flex items-center gap-1"
            >
              ← Edit Company Details
            </button>
            <div className="flex gap-2">
              <button 
                onClick={handlePrint}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 text-sm font-medium transition"
              >
                <Printer size={14} /> Print
              </button>
              <button 
                onClick={handleDownloadPDF}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-indigo-600 text-white hover:bg-indigo-700 text-sm font-medium transition"
              >
                <Download size={14} /> Download PDF
              </button>
            </div>
          </div>

          <div className="snapshot-card bg-white dark:bg-[#0b1329] border border-slate-200 dark:border-white/10 rounded-xl shadow-lg overflow-hidden">
            {/* Header */}
            <div className="bg-slate-900 text-white px-6 py-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div className="flex items-center gap-2 font-bold text-lg">
                <Target className="text-cyan-400" size={24} />
                FOA / Company Fit Snapshot
              </div>
              <div className="text-right">
                <div className="font-bold text-lg">{form.companyName}</div>
                <div className="text-xs text-slate-400">{new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</div>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Company Block */}
              <div className="bg-slate-50 dark:bg-slate-900/50 rounded-lg p-4 border border-slate-100 dark:border-slate-800">
                <div className="flex flex-wrap items-center gap-4 text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                  <div className="flex items-center gap-1.5">
                    <span className="text-slate-500">Tech:</span>
                    <span className="text-indigo-600 dark:text-indigo-400">{form.techTags.join(', ') || 'N/A'}</span>
                  </div>
                  <div className="w-px h-4 bg-slate-300 dark:bg-slate-700"></div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-slate-500">TRL:</span>
                    <span>{form.trl}</span>
                  </div>
                  <div className="w-px h-4 bg-slate-300 dark:bg-slate-700"></div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-slate-500">Type:</span>
                    <span>{form.applicantType}</span>
                  </div>
                  {form.location && (
                    <>
                      <div className="w-px h-4 bg-slate-300 dark:bg-slate-700"></div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-slate-500">Loc:</span>
                        <span>{form.location}</span>
                      </div>
                    </>
                  )}
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed line-clamp-3">
                  {form.description}
                </p>
              </div>

              {/* Top FOA Classes */}
              <div className="space-y-4">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800 pb-2">
                  Top Recommended FOA Classes
                </h3>
                
                <div className="grid gap-4">
                  {(snapshot.top_foa_classes || []).map((foa, idx) => (
                    <div key={idx} className="border border-slate-200 dark:border-slate-800 rounded-lg p-4 bg-white dark:bg-slate-900/20">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                            {foa.agency}
                          </span>
                          <span className="font-bold text-slate-900 dark:text-white">
                            {foa.class_label}
                          </span>
                          {renderWindowRiskBadge(foa.window_risk)}
                        </div>
                        <div className="flex items-center gap-2 min-w-[120px]">
                          <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div 
                              className={clsx(
                                "h-full rounded-full",
                                (foa.fit_score * 100) >= 80 ? "bg-green-500" : (foa.fit_score * 100) >= 60 ? "bg-yellow-500" : "bg-red-500"
                              )} 
                              style={{ width: `${Math.round(foa.fit_score * 100)}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-bold text-slate-700 dark:text-slate-300">{Math.round(foa.fit_score * 100)}%</span>
                        </div>
                      </div>
                      
                      <p className="text-sm text-slate-600 dark:text-slate-400 mb-3 italic">
                        "{foa.why_fit}"
                      </p>
                      
                      {foa.example_solicitations && foa.example_solicitations.length > 0 && (
                        <div className="mt-3">
                          <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">Example Solicitations:</div>
                          <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-1">
                            {foa.example_solicitations.map((ex, i) => (
                              <li key={i} className="flex items-start gap-1.5">
                                <span className="text-slate-400 mt-0.5">•</span>
                                <span>
                                  {ex.solicitation_number && <span className="font-mono text-[10px] text-cyan-600 dark:text-cyan-400 mr-1">{ex.solicitation_number}</span>}
                                  {ex.name}
                                  {ex.max_per_award && <span className="text-slate-400 ml-1">(up to ${(ex.max_per_award / 1_000_000).toFixed(1)}M)</span>}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {(!snapshot.top_foa_classes || snapshot.top_foa_classes.length === 0) && (
                    <div className="text-sm text-slate-500 italic p-4 text-center border border-dashed border-slate-300 rounded">
                      No matching FOA classes identified based on the provided inputs.
                    </div>
                  )}
                </div>
              </div>

              {/* Misfit Warnings */}
              {snapshot.misfit_warnings && snapshot.misfit_warnings.length > 0 && (
                <div className="space-y-3">
                  {snapshot.misfit_warnings.map((warning, i) => (
                    <div key={i} className="border border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-950/20 rounded-lg p-4">
                      <h4 className="text-sm font-bold text-red-800 dark:text-red-400 flex items-center gap-2 mb-2">
                        <AlertTriangle size={16} /> ⚠ Wrong FOA Class to Avoid
                      </h4>
                      <div className="font-semibold text-red-900 dark:text-red-300 text-sm mb-1">
                        {warning.class_label}
                        {warning.risk_type && (
                          <span className="ml-2 text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400">
                            {warning.risk_type.replace('_', ' ')}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-red-700 dark:text-red-400/80 leading-relaxed">
                        {warning.why_wrong}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Recommended Next Action */}
              <div className="border border-amber-200 dark:border-amber-900/50 bg-amber-50 dark:bg-amber-950/30 rounded-lg p-4">
                <div className="flex gap-2">
                  <div className="mt-0.5 text-amber-600 dark:text-amber-500">▶</div>
                  <div>
                    <div className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-500 mb-1">
                      Recommended Next Action
                    </div>
                    <p className="text-sm font-medium text-amber-900 dark:text-amber-200">
                      {snapshot.recommended_next_action || "Refine technology descriptions and monitor upcoming solicitation announcements."}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
