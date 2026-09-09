import React from 'react';
import { VenturePatentView } from '../components/VenturePatentView';
import { Lightbulb } from 'lucide-react';
import { useSEO } from '../utils/seo';

export default function VenturePatentsPage() {
  useSEO({
    title: 'USPTO Bayh-Dole Patents & Energy Innovation VC Linkages',
    description: 'Track how non-dilutive government grants catalyze breakthrough energy innovation technology patents and multi-billion-dollar private venture capital investments.',
    canonicalUrl: 'https://terminal.aixenergy.io/patents',
    keywords: ['energy innovation patents', 'Bayh-Dole Act energy grants', 'cleantech venture capital', 'USPTO energy technology', 'climate tech funding rounds'],
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
              <Lightbulb size={12} className="text-amber-600" />
              <span>USPTO Bayh-Dole &amp; VC Attributions</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-slate-500">Commercialization Intelligence</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Venture &amp; Patent Commercialization Hub
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 max-w-3xl mt-1 leading-relaxed">
            Track how non-dilutive government funding catalyzes breakthrough energy innovation technology patents and multi-billion-dollar private venture capital rounds.
          </p>
        </div>
      </div>

      <VenturePatentView />
    </div>
  );
}

