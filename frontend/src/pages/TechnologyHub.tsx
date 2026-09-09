import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Zap, Award, DollarSign, Rss, ArrowRight, ArrowLeft,
  Share2, CheckCircle2, Building2, Flame, ShieldAlert, BookOpen
} from 'lucide-react';
import { updatePageMeta } from '../utils/seo';

interface TechHubData {
  technology: {
    id: number;
    name: string;
    headline?: string;
    sector?: string;
    trl_current?: number;
    trl_target?: number;
    plain_what_is_it?: string;
    plain_how_it_works?: string;
    plain_why_it_matters?: string;
    moonshot_goal?: string;
  };
  opportunities?: Array<{
    id: number;
    name: string;
    agency: string;
    total_funding: number;
    due_date_display: string;
    status: string;
  }>;
  recipients?: Array<{
    id: number;
    name: string;
    total_funding_received: number;
    headquarters_state: string;
    commercialization_stage: string;
  }>;
  total_funding?: number;
  total_awards?: number;
}

export default function TechnologyHub() {
  const { slug } = useParams<{ slug: string }>();

  const { data, isLoading, error } = useQuery<TechHubData>({
    queryKey: ['tech-hub', slug],
    queryFn: async () => {
      // Look up technology by name or slug from tech reference endpoint
      const res = await fetch(`/api/tech-reference/technologies`);
      if (!res.ok) throw new Error('Failed to load technologies');
      const allTechs = await res.json();
      
      const matched = allTechs.find((t: any) => {
        const s = t.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
        return s === slug || t.id.toString() === slug;
      }) || allTechs[0];

      // Fetch opportunities matching this category
      const oppRes = await fetch(`/api/opportunities?technology_area=${encodeURIComponent(matched.name)}&limit=20`);
      const oppData = oppRes.ok ? await oppRes.json() : { items: [] };

      // Fetch top recipients in this technology
      const recRes = await fetch(`/api/awards/recipients?technology=${encodeURIComponent(matched.name)}&limit=10`);
      const recData = recRes.ok ? await recRes.json() : { items: [] };

      return {
        technology: matched,
        opportunities: oppData.items || [],
        recipients: recData.items || [],
        total_funding: 850000000,
        total_awards: 420
      };
    },
    enabled: !!slug,
  });

  const tech = data?.technology;

  useEffect(() => {
    if (tech) {
      updatePageMeta({
        title: `${tech.name} Clean Energy Grants, Funding & Solicitations 2026`,
        description: `Explore active federal and state public funding opportunities, DOE grant awards, and leading clean tech startups in ${tech.name}. ${tech.headline || ''}`,
        canonicalUrl: `https://terminal.aixenergy.io/technologies/${slug}`,
        keywords: [tech.name, tech.sector || 'Clean Tech', 'Government Grants', 'DOE Funding', 'Clean Energy RFPs', 'Public Funding 2026'],
      });
    }
  }, [tech, slug]);

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !tech) {
    return (
      <div className="p-8 text-center max-w-lg mx-auto">
        <Zap className="h-12 w-12 text-slate-400 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-slate-900">Technology Hub Not Found</h2>
        <Link to="/technologies" className="inline-flex items-center gap-2 text-indigo-600 font-medium mt-4 hover:underline">
          <ArrowLeft className="h-4 w-4" /> Back to Technology Index
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Header Breadcrumbs & RSS */}
      <div className="flex items-center justify-between">
        <Link to="/technologies" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800">
          <ArrowLeft className="h-4 w-4" /> Back to Technology Reference
        </Link>
        <a
          href="/feed/rss/opportunities.xml"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-50 border border-amber-200 text-amber-800 hover:bg-amber-100 transition-all"
        >
          <Rss className="h-3.5 w-3.5" /> RSS Grants Feed
        </a>
      </div>

      {/* Hero Card */}
      <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white rounded-2xl p-6 sm:p-8 shadow-xl border border-slate-800">
        <div className="max-w-3xl space-y-3">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {tech.sector || 'Clean Energy Technology'}
            </span>
            {tech.trl_current && (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-300">
                TRL {tech.trl_current} &rarr; {tech.trl_target || 9}
              </span>
            )}
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
            {tech.name} Funding &amp; Innovation Hub
          </h1>

          <p className="text-slate-300 text-base leading-relaxed">
            {tech.headline || tech.plain_what_is_it || 'Upstream funding intelligence, competitive public solicitations, and grant track records.'}
          </p>
        </div>
      </div>

      {/* Deep Explainer Sections */}
      {(tech.plain_why_it_matters || tech.moonshot_goal) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {tech.plain_why_it_matters && (
            <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2 mb-2">
                <Flame className="h-4 w-4 text-amber-500" /> Strategic Decarbonization Mandate
              </h2>
              <p className="text-sm text-slate-700 leading-relaxed">
                {tech.plain_why_it_matters}
              </p>
            </div>
          )}

          {tech.moonshot_goal && (
            <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2 mb-2">
                <Zap className="h-4 w-4 text-indigo-600" /> Industry Moonshot &amp; Cost Targets
              </h2>
              <p className="text-sm text-slate-700 leading-relaxed">
                {tech.moonshot_goal}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Active Opportunities Section */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Award className="h-5 w-5 text-indigo-600" /> Active Public Funding Solicitations &amp; RFPs
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">Open grant programs for {tech.name}</p>
          </div>
          <Link to="/opportunities" className="text-xs font-semibold text-indigo-600 hover:underline flex items-center gap-1">
            View All Solicitations <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        {data?.opportunities && data.opportunities.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {data.opportunities.map((opp) => (
              <Link 
                key={opp.id} 
                to={`/opportunities/${opp.id}`}
                className="p-5 hover:bg-slate-50 flex flex-col sm:flex-row sm:items-center justify-between gap-4 block transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                      {opp.agency}
                    </span>
                    <span className="text-xs text-slate-400">Due: {opp.due_date_display || 'Open Enrollment'}</span>
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">{opp.name}</h3>
                </div>

                <div className="text-right whitespace-nowrap">
                  <div className="text-base font-bold text-slate-900">
                    ${opp.total_funding ? opp.total_funding.toLocaleString() : 'Open'}
                  </div>
                  <div className="text-xs text-slate-400">Total Program Funding</div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-sm text-slate-500">
            No active open solicitations found for this technology area today. Check back weekly.
          </div>
        )}
      </div>

      {/* Top Funded Innovators */}
      {data?.recipients && data.recipients.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-4">
            <Building2 className="h-5 w-5 text-slate-600" /> Leading Funded Innovators &amp; Labs in {tech.name}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.recipients.map((rec) => (
              <Link
                key={rec.id}
                to={`/recipients/${rec.id}`}
                className="p-4 rounded-xl border border-slate-200 hover:border-indigo-300 hover:shadow-md transition-all block group bg-slate-50/50"
              >
                <div className="text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                  {rec.name}
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  {rec.commercialization_stage || 'Clean Tech Innovator'} &bull; {rec.headquarters_state || 'US'}
                </div>
                <div className="text-xs font-semibold text-emerald-600 mt-2">
                  ${(rec.total_funding_received / 1_000_000).toFixed(1)}M Tracked Funding
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
