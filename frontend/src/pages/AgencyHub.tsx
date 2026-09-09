import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Building2, Award, DollarSign, Globe, MapPin, 
  ExternalLink, ArrowLeft, ArrowRight, ShieldCheck, Mail, Phone
} from 'lucide-react';
import { updatePageMeta } from '../utils/seo';

interface AgencyHubData {
  organization: {
    id: number;
    name: string;
    org_type?: string;
    city?: string;
    state?: string;
    country?: string;
    description?: string;
    website?: string;
    founded_year?: number;
  };
  programs?: Array<{
    id: number;
    name: string;
    description?: string;
  }>;
  opportunities?: Array<{
    id: number;
    name: string;
    total_funding: number;
    due_date_display: string;
    status: string;
  }>;
  contacts?: Array<{
    id: number;
    name_display: string;
    role_type?: string;
    email?: string;
    phone?: string;
  }>;
}

export default function AgencyHub() {
  const { id } = useParams<{ id: string }>();

  const { data, isLoading, error } = useQuery<AgencyHubData>({
    queryKey: ['agency-hub', id],
    queryFn: async () => {
      const res = await fetch(`/api/organizations/${id}`);
      if (!res.ok) throw new Error('Failed to load agency');
      return res.json();
    },
    enabled: !!id,
  });

  const org = data?.organization;

  useEffect(() => {
    if (org) {
      updatePageMeta({
        title: `${org.name} - Energy Innovation Solicitations & Funding Programs`,
        description: `Explore open energy innovation funding solicitations, active programs, and historical awards administered by ${org.name}. ${org.description || ''}`,
        canonicalUrl: `https://terminal.aixenergy.io/agencies/${org.id}`,
        keywords: [org.name, 'Energy Innovation Grants', 'Public Solicitations', 'RFPs', 'Funding Programs'],
      });
    }
  }, [org]);

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  if (error || !org) {
    return (
      <div className="p-8 text-center max-w-lg mx-auto">
        <Building2 className="h-12 w-12 text-slate-400 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-slate-900">Agency Record Not Found</h2>
        <Link to="/organizations" className="inline-flex items-center gap-2 text-cyan-600 font-medium mt-4 hover:underline">
          <ArrowLeft className="h-4 w-4" /> Back to Organizations Directory
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Header Navigation */}
      <div className="flex items-center justify-between">
        <Link to="/organizations" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800">
          <ArrowLeft className="h-4 w-4" /> Back to Organizations &amp; Funders Directory
        </Link>
      </div>

      {/* Hero Card */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-xl border border-slate-800">
        <div className="max-w-3xl space-y-3">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              {org.org_type?.replace('_', ' ') || 'Funding Institution'}
            </span>
            {(org.city || org.state) && (
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" /> {[org.city, org.state].filter(Boolean).join(', ')}
              </span>
            )}
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold text-white">{org.name}</h1>

          <p className="text-slate-300 text-base leading-relaxed">
            {org.description || 'Public energy funding agency administering clean technology innovation and deployment capital.'}
          </p>

          {org.website && (
            <div className="pt-2">
              <a
                href={org.website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 text-sm font-semibold"
              >
                <Globe className="h-4 w-4" /> Official Agency Portal <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </div>
          )}
        </div>
      </div>

      {/* Active Solicitations */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Award className="h-5 w-5 text-cyan-600" /> Solicitations Administered by {org.name}
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">Active competitive grant opportunities and calls for proposals</p>
          </div>
          <Link to="/opportunities" className="text-xs font-semibold text-cyan-600 hover:underline flex items-center gap-1">
            Explore All <ArrowRight className="h-3 w-3" />
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
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {opp.status.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-400">Due: {opp.due_date_display || 'Open Enrollment'}</span>
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">{opp.name}</h3>
                </div>

                <div className="text-right whitespace-nowrap">
                  <div className="text-base font-bold text-slate-900">
                    ${opp.total_funding ? opp.total_funding.toLocaleString() : 'Open'}
                  </div>
                  <div className="text-xs text-slate-400">Program Funding</div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-sm text-slate-500">
            No active open solicitations recorded currently for this agency.
          </div>
        )}
      </div>

      {/* Agency Contacts */}
      {data?.contacts && data.contacts.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h2 className="text-base font-bold text-slate-900 mb-4">
            Key Program Officers &amp; Staff Contacts
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.contacts.map((c) => (
              <div key={c.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-1.5">
                <div className="text-sm font-bold text-slate-900">{c.name_display}</div>
                <div className="text-xs text-slate-500">{c.role_type || 'Program Lead'}</div>
                {c.email && (
                  <div className="text-xs text-cyan-600 flex items-center gap-1">
                    <Mail className="h-3 w-3" /> {c.email}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
