import React from 'react';
import {
  ShieldAlert, ShieldCheck, Scale, FileText, CheckCircle2,
  ExternalLink, X, Lock, AlertTriangle, Building2, Info
} from 'lucide-react';
import clsx from 'clsx';
import { useTheme } from '../context/ThemeContext';
import { EnergyInnovationTerminalLogo } from './EnergyInnovationTerminalLogo';

interface LegalComplianceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function LegalComplianceModal({ isOpen, onClose }: LegalComplianceModalProps) {
  const { isDark } = useTheme();

  if (!isOpen) return null;

  const sections = [
    {
      icon: ShieldCheck,
      iconColor: 'text-emerald-500',
      title: '1. Independent Research Platform & Non-Affiliation Notice',
      content: 'The Energy Innovation Terminal and the U.S. Energy Innovation Database are independent computational analytics and academic research tools published by Clean Energy Research, LLC outside of any official government capacity. This platform is NOT an official tool, publication, policy statement, or service of any federal, state, regional, or municipal governmental entity, public utility commission, or public energy authority. No endorsement, partnership, sponsorship, or official affiliation by or with any governmental agency is stated or implied.'
    },
    {
      icon: FileText,
      iconColor: 'text-cyan-500',
      title: '2. Sourced Exclusively from Public Open Records',
      content: 'All opportunity solicitations, funding program guidelines, historical award disbursements, statutory regulatory dockets, patent references, recipient names, and financial attributions indexed within this platform are derived exclusively from publicly available open government records, published state disclosure portals, open data repositories, and official public notices. Key public sources include open data feeds (data.gov, state open data portals), Grants.gov, USAspending.gov, published agency solicitation directories, USPTO patent gazettes, and state public utility commission dockets. All data collection conforms to applicable Freedom of Information (FOIA/FOIL) and Open Data statutory frameworks.'
    },
    {
      icon: Lock,
      iconColor: 'text-blue-500',
      title: '3. Zero Non-Public, Proprietary, or Deliberative Information',
      content: 'This platform strictly contains NO confidential, non-public, proprietary, pre-decisional, evaluator scoring, internal draft, or privileged agency communications. All match scores, compatibility rankings, readiness indicators, probability indices, and synthesized briefs are independent computational estimates generated algorithmically from published public texts and historical award patterns. No internal scoring rubrics or evaluator deliberations from any funding body are utilized or contained herein.'
    },
    {
      icon: Scale,
      iconColor: 'text-purple-500',
      title: '4. Public Sector Contributor & Safe Harbor Protection',
      content: 'This platform and database were conceived, developed, and engineered independently by Clean Energy Research, LLC. Contributing researchers, developers, advisors, and data curators who may be employed by or affiliated with public sector entities, state energy organizations, national research laboratories, or academic institutions contribute strictly in an independent, personal research capacity outside of any official duties, working hours, or government resources. No official agency equipment, facilities, or non-public information were used in the creation or operation of this platform. No analyses, algorithms, taxonomies, opinions, forecasts, or data representations expressed herein reflect the official positions, findings, policies, or endorsements of their respective employers or any governmental agency.'
    },
    {
      icon: Building2,
      iconColor: 'text-amber-500',
      title: '5. Nominative Fair Use of Agency Names & Trademarks',
      content: 'All organization names, agency acronyms, program titles, and logos referenced on this platform are the registered or unregistered trademarks of their respective owners. Their display is solely for descriptive, nominative identification and public-interest informational reference under 15 U.S.C. § 1125 (Lanham Act Fair Use). Such references do not indicate or imply endorsement, sponsorship, or official affiliation.'
    },
    {
      icon: AlertTriangle,
      iconColor: 'text-rose-500',
      title: '6. No Guarantee of Funding / Official Verification Requirement',
      content: 'Use of this platform does not constitute an official proposal submission to any funding organization, nor does it confer any competitive advantage, scoring preference, or official consideration in any competitive solicitation process. Funding criteria, eligibility rules, deadlines, and funding envelopes are subject to change by issuing authorities at any time. Prospective applicants MUST consult the official, authoritative RFP, PON, FOA, or solicitation documents published directly on each issuing agency\'s official website prior to preparing or submitting grant applications or executing contractual commitments.'
    }
  ];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity animate-in fade-in"
        onClick={onClose}
      />

      {/* Modal Container */}
      <div
        className={clsx(
          "relative w-full max-w-3xl rounded-2xl shadow-2xl overflow-hidden border transition-all duration-200 z-10 my-auto",
          isDark
            ? "bg-[#090e1a] border-cyan-500/30 text-slate-100 shadow-[0_0_50px_rgba(0,210,255,0.15)]"
            : "bg-white border-slate-200 text-slate-900 shadow-2xl"
        )}
      >
        {/* Header */}
        <div className="relative px-6 py-5 bg-gradient-to-r from-[#04101e] via-[#08182b] to-[#04101e] border-b border-cyan-500/30 overflow-hidden">
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-3.5">
              <div className="p-2 rounded-xl bg-cyan-950/60 border border-cyan-500/40 shadow-[0_0_20px_rgba(0,210,255,0.3)]">
                <Scale className="text-cyan-400" size={22} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
                    Legal &amp; Compliance Statement
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    PUBLIC OPEN RECORDS
                  </span>
                </div>
                <h3 className="text-lg font-black tracking-tight text-white flex items-center gap-1.5 mt-0.5">
                  Public Records Provenance &amp; Contributor Safe Harbor Notice
                </h3>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-4 max-h-[72vh] overflow-y-auto no-scrollbar">
          {/* Executive Summary Banner */}
          <div className={clsx(
            "p-4 rounded-xl border flex items-start gap-3",
            isDark ? "bg-cyan-950/20 border-cyan-500/30 text-cyan-200" : "bg-cyan-50 border-cyan-200 text-cyan-950"
          )}>
            <Info size={18} className="shrink-0 mt-0.5 text-cyan-400" />
            <p className="text-xs leading-relaxed font-medium">
              <strong>Executive Notice:</strong> The Energy Innovation Terminal is an independent computational research tool built strictly upon <strong>publicly accessible open government records</strong>. It is not affiliated with, sponsored by, or an official product of any state or federal governmental entity. Contributing researchers and analysts contribute solely in an independent, personal research capacity; no content reflects the official views or policies of any public employer or agency.
            </p>
          </div>

          {/* Section Cards */}
          <div className="space-y-3">
            {sections.map((sec, idx) => {
              const Icon = sec.icon;
              return (
                <div
                  key={idx}
                  className={clsx(
                    "p-4 rounded-xl border transition-colors",
                    isDark ? "bg-white/[0.02] border-white/[0.08]" : "bg-slate-50 border-slate-200"
                  )}
                >
                  <div className="flex items-center gap-2.5 mb-1.5">
                    <Icon size={15} className={clsx("shrink-0", sec.iconColor)} />
                    <h4 className={clsx(
                      "text-xs font-bold uppercase tracking-wider",
                      isDark ? "text-slate-200" : "text-slate-800"
                    )}>
                      {sec.title}
                    </h4>
                  </div>
                  <p className={clsx(
                    "text-xs leading-relaxed pl-6",
                    isDark ? "text-slate-400" : "text-slate-600"
                  )}>
                    {sec.content}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Statutory References */}
          <div className={clsx(
            "p-3.5 rounded-xl border text-[11px] font-mono",
            isDark ? "bg-white/[0.01] border-white/[0.06] text-slate-400" : "bg-slate-100 border-slate-200 text-slate-600"
          )}>
            <div className="font-bold text-slate-300 mb-1 flex items-center gap-1.5">
              <ShieldAlert size={13} className="text-emerald-400" />
              <span>Statutory Compliance &amp; Safe Harbor Provisions</span>
            </div>
            <p className="text-[10px] leading-relaxed">
              Federal Freedom of Information Act (FOIA, 5 U.S.C. § 552) · State Freedom of Information &amp; Open Records Statutory Acts · Federal Financial Accountability and Transparency Act (FFATA) · 15 U.S.C. § 1125 (Lanham Act Nominative Fair Use). All public sector employee contributions conducted in personal academic research capacity under applicable ethics safe harbors.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className={clsx(
          "px-6 py-3.5 border-t flex flex-col sm:flex-row items-center justify-between gap-3 text-xs",
          isDark ? "bg-[#060a14] border-white/[0.08]" : "bg-slate-50 border-slate-200"
        )}>
          <div className="text-[10.5px] font-mono text-slate-400 flex items-center gap-1.5">
            <ShieldCheck size={13} className="text-emerald-400" />
            <span>Independent Research · Open Public Records Compliant</span>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-900 hover:bg-slate-200 transition-colors shadow-xs cursor-pointer"
          >
            Acknowledge &amp; Close
          </button>
        </div>
      </div>
    </div>
  );
}
