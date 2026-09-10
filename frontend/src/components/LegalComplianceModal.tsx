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
      title: '1. Independent Platform & Non-Affiliation Notice',
      content: 'The Energy Innovation Terminal and the U.S. Energy Innovation Database are independent, third-party research and computational analytics tools developed by Clean Energy Research, LLC outside of any official government capacity. This platform is NOT an official tool, publication, or product of the New York State Energy Research and Development Authority (NYSERDA), the State of New York, the United States Department of Energy (DOE), the Advanced Research Projects Agency-Energy (ARPA-E), the California Energy Commission (CEC), the Massachusetts Energy Innovation Center (MassCEC), the National Science Foundation (NSF), or any other federal, state, regional, or municipal governmental entity. No endorsement, partnership, sponsorship, or official affiliation by or with any government agency is stated or implied.'
    },
    {
      icon: FileText,
      iconColor: 'text-cyan-500',
      title: '2. Sourced Exclusively from Public Open Records',
      content: 'All opportunity solicitations, historical award disbursements, statutory regulatory dockets, patent references, recipient names, and program guidelines indexed within this platform are derived exclusively from publicly available open records, published government websites, public disclosure portals, and official open data repositories. Key public sources include New York Open Data (data.ny.gov), NYSERDA Published Solicitations Portal (nyserda.ny.gov/funding-opportunities), Grants.gov, USAspending.gov, ARPA-E eXCHANGE, CEC Solicitations, DOE EERE Exchange, US Patent & Trademark Office (USPTO), and state public utility commission dockets. All data collection conforms to applicable Freedom of Information (FOIL/FOIA) and Open Data statutory provisions.'
    },
    {
      icon: Lock,
      iconColor: 'text-blue-500',
      title: '3. Zero Non-Public, Proprietary, or Deliberative Information',
      content: 'This platform strictly contains NO non-public, confidential, proprietary, deliberative, evaluator scoring, internal draft, or privileged agency information. All match algorithms, compatibility rankings, readiness indicators, probability indices, and synthesized briefs are independent computational estimates generated algorithmically from published public texts and historical award patterns. No internal agency scoring rubrics, evaluator deliberations, or pre-decisional intelligence are utilized or contained herein.'
    },
    {
      icon: Scale,
      iconColor: 'text-purple-500',
      title: '4. Independent Development & Resource Separation',
      content: 'This platform and the U.S. Energy Innovation Database were conceived, developed, and engineered independently by Clean Energy Research, LLC. No official government agency equipment, facilities, official working hours, proprietary software, or public resources were used in the creation, hosting, or ongoing operation of this software platform. The perspectives, analyses, taxonomy structures, and algorithmic outputs expressed herein are solely those of Clean Energy Research, LLC and do not reflect the official policies, positions, or evaluations of any public authority or employer.'
    },
    {
      icon: Building2,
      iconColor: 'text-amber-500',
      title: '5. Nominative Fair Use of Agency Names & Trademarks',
      content: 'All organization names, agency acronyms, program titles, and logos (including but not limited to NYSERDA, DOE, ARPA-E, CEC, MassCEC, NSF, EPA, NYPA, ConEd, and National Grid) are the registered or unregistered trademarks of their respective owners. Their display on this platform is solely for descriptive, nominative identification and public-interest informational reference purposes under 15 U.S.C. § 1125 (Lanham Act Fair Use). Such identification does not indicate or imply endorsement, sponsorship, or affiliation.'
    },
    {
      icon: AlertTriangle,
      iconColor: 'text-rose-500',
      title: '6. No Guarantee of Funding / Official Verification Requirement',
      content: 'Use of this platform does not constitute an official proposal submission to NYSERDA, US DOE, or any other funding organization, nor does it confer any competitive advantage, scoring preference, or official consideration in any competitive solicitation process. Funding criteria, eligibility rules, deadlines, and funding envelopes are subject to change by issuing authorities at any time. Prospective applicants MUST consult the official, authoritative RFP, PON, FOA, or solicitation documents published directly on each agency\'s official website prior to preparing or submitting grant applications or executing contractual commitments.'
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
                    Legal, Ethics &amp; Compliance Statement
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    PUBLIC OPEN DATA
                  </span>
                </div>
                <h3 className="text-lg font-black tracking-tight text-white flex items-center gap-1.5 mt-0.5">
                  Public Records Provenance &amp; Non-Affiliation Notice
                </h3>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
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
              <strong>Executive Notice:</strong> The Energy Innovation Terminal is an independent computational research tool built exclusively on <strong>publicly accessible open government records</strong>. It is not affiliated with, sponsored by, or an official product of NYSERDA, the State of New York, the US DOE, or any government body. No confidential, proprietary, or non-public data is used.
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

          {/* Applicable Statutory Authorities Referenced */}
          <div className={clsx(
            "p-3.5 rounded-xl border text-[11px] font-mono",
            isDark ? "bg-white/[0.01] border-white/[0.06] text-slate-400" : "bg-slate-100 border-slate-200 text-slate-600"
          )}>
            <div className="font-bold text-slate-300 mb-1 flex items-center gap-1.5">
              <ShieldAlert size={13} className="text-emerald-400" />
              <span>Statutory Compliance &amp; Safe Harbor References</span>
            </div>
            <p className="text-[10px] leading-relaxed">
              New York Public Officers Law §§ 73, 74 · New York Freedom of Information Law (FOIL, Public Officers Law art. 6) · New York State Open Data Executive Order No. 95 · Federal Freedom of Information Act (FOIA, 5 U.S.C. § 552) · Federal Financial Accountability and Transparency Act (FFATA) · 15 U.S.C. § 1125 (Lanham Act Nominative Fair Use).
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
            <span>Independent Research &amp; Open Data Compliant</span>
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
