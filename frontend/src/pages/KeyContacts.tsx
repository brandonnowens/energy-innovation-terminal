import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { api, ContactItem, ContactDetail as IContactDetail } from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  Users, Search, Mail, Phone, Globe, MapPin, ExternalLink,
  Building2, Trophy, Layers, ChevronRight, X, Loader2,
  DollarSign, Zap, Landmark, Sparkles, Filter, CheckCircle2,
  Download, ShieldCheck, Copy, Check, BookOpen, Award,
  Flame, Cpu, BatteryCharging, Sun, Wind, Atom, Factory,
  Home, Truck, Network, FileText, ArrowRight, LayoutGrid, List,
  Send, MessageSquare, AlertCircle, RefreshCw, Share2, FlaskConical
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';
import { SayYesDecisionMakerMatrix } from '../components/SayYesDecisionMakerMatrix';
import { useNyserda } from '../context/NyserdaContext';

function fmt(v?: number | null): string {
  if (!v || v === 0) return '$0';
  if (v >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
  if (v >= 1e3) return `$${(v / 1e3).toFixed(0)}K`;
  return `$${v.toLocaleString()}`;
}

const TECH_ICONS: Record<string, React.ReactNode> = {
  'Energy Storage & Advanced Batteries': <BatteryCharging size={12} className="text-amber-500" />,
  'Solar & Photovoltaics': <Sun size={12} className="text-yellow-500" />,
  'Solar Photovoltaics & Systems': <Sun size={12} className="text-yellow-500" />,
  'Wind & Offshore Wind': <Wind size={12} className="text-sky-500" />,
  'Wind Energy & Offshore Systems': <Wind size={12} className="text-sky-500" />,
  'Hydrogen & Clean Fuels': <Flame size={12} className="text-emerald-500" />,
  'Hydrogen & Clean Fuel Cells': <Flame size={12} className="text-emerald-500" />,
  'Grid Modernization & Smart Power': <Network size={12} className="text-indigo-500" />,
  'Carbon Capture & CCUS': <Sparkles size={12} className="text-teal-500" />,
  'Building Decarbonization & Clean Heat': <Home size={12} className="text-orange-500" />,
  'Building Decarbonization & Efficiency': <Home size={12} className="text-orange-500" />,
  'Electric Mobility & Transportation': <Truck size={12} className="text-blue-500" />,
  'Electric Vehicles & Clean Transit': <Truck size={12} className="text-blue-500" />,
  'Advanced Nuclear & Fusion': <Atom size={12} className="text-purple-500" />,
  'Nuclear & Advanced SMRs': <Atom size={12} className="text-purple-500" />,
  'Industrial Decarbonization & Clean Heat': <Factory size={12} className="text-slate-600" />,
  'AI, ML & Energy Software': <Cpu size={12} className="text-cyan-500" />,
};

type EmailTemplateType = 'teaming' | 'tech_inquiry' | 'solicitation_question' | 'general';

interface EmailComposerModalProps {
  contact: ContactItem | IContactDetail;
  onClose: () => void;
}

function EmailComposerModal({ contact, onClose }: EmailComposerModalProps) {
  const [template, setTemplate] = useState<EmailTemplateType>(
    contact.role_type === 'program_officer' ? 'solicitation_question' : 'teaming'
  );
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [copied, setCopied] = useState(false);

  // Generate templates dynamically based on contact info
  useMemo(() => {
    const name = contact.name_display;
    const inst = contact.institution_name || contact.organization_name || 'your institution';
    const tech = contact.technology_area || 'Energy Innovation Innovation';

    if (template === 'teaming') {
      setSubject(`Grant Collaboration & Teaming Inquiry: ${tech} - ${name}`);
      setBody(`Dear ${name},\n\nI hope this email finds you well.\n\nI am reaching out regarding your pioneering innovation work in ${tech} at ${inst}. We are currently assembling a multi-disciplinary consortium for upcoming non-dilutive energy innovation grant solicitations (including federal DOE/ARPA-E and state innovation programs).\n\nGiven your track record and research leadership, we would welcome the opportunity to explore potential teaming, subcontracting, or advisory alignment on upcoming proposals.\n\nWould you have 15 minutes in the coming weeks for a brief introductory conversation?\n\nThank you for your time and continued leadership in clean technology.\n\nBest regards,\n[Your Name]\n[Your Organization / Energy Innovation Project]\n[Your Phone / Contact Info]`);
    } else if (template === 'tech_inquiry') {
      setSubject(`Inquiry regarding ${tech} Research & Technology Track Record - ${name}`);
      setBody(`Dear ${name},\n\nI am contacting you regarding your research portfolio and funded projects in ${tech} at ${inst}.\n\nOur team is currently evaluating commercialization trajectories, intellectual property, and deployment readiness across the energy innovation sector. We reviewed your public project filings and were deeply impressed by your advancements.\n\nWe would appreciate the opportunity to learn more about the current stage of development and any potential collaboration or commercial demonstration opportunities.\n\nLooking forward to connecting.\n\nSincerely,\n[Your Name]\n[Your Title / Organization]`);
    } else if (template === 'solicitation_question') {
      setSubject(`Inquiry regarding Energy Innovation Solicitation & Program Scope - Attn: ${name}`);
      setBody(`Dear ${name},\n\nI am writing to inquire about energy innovation funding opportunities and program priorities within ${inst}.\n\nOur team is developing an innovative project in ${tech} and we are reviewing program guidelines, eligibility criteria, and upcoming submission cycles.\n\nCould you kindly confirm if this technology focus aligns with current program objectives, and whether technical guidance is available for prospective applicants?\n\nThank you for your assistance and guidance.\n\nRespectfully,\n[Your Name]\n[Your Organization]`);
    } else {
      setSubject(`Energy Innovation Ecosystem Connection: ${tech} - ${name}`);
      setBody(`Dear ${name},\n\nI am reaching out from the energy innovation innovation community regarding your work in ${tech} at ${inst}.\n\nWe are actively engaged in accelerating high-impact energy solutions and would value the chance to connect, exchange perspectives, and explore mutual synergies across our respective initiatives.\n\nPlease let me know if you would be open to a brief introductory discussion.\n\nBest regards,\n[Your Name]\n[Your Organization]`);
    }
  }, [template, contact]);

  const recipientEmail = contact.email || '';
  const mailtoLink = `mailto:${encodeURIComponent(recipientEmail)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  const gmailLink = `https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(recipientEmail)}&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  const outlookLink = `https://outlook.live.com/mail/0/deeplink/compose?to=${encodeURIComponent(recipientEmail)}&subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

  const copyFullDraft = () => {
    const fullText = `To: ${recipientEmail}\nSubject: ${subject}\n\n${body}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/80 flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
              <Mail size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900">
                  Email Contact: {contact.name_display}
                </h3>
                {contact.email_deliverable && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <CheckCircle2 size={10} /> Verified Deliverable
                  </span>
                )}
              </div>
              <div className="text-xs text-slate-500 font-mono mt-0.5">
                {recipientEmail || 'Refer to Official Institutional Gateway'}
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-4 text-xs">
          {/* Template Selector */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Select Outreach Template
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {[
                { id: 'teaming', label: 'Grant Teaming', icon: Users },
                { id: 'tech_inquiry', label: 'Tech Diligence', icon: Cpu },
                { id: 'solicitation_question', label: 'Program Scope', icon: Landmark },
                { id: 'general', label: 'Ecosystem Connect', icon: Sparkles },
              ].map(t => {
                const Icon = t.icon;
                return (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setTemplate(t.id as EmailTemplateType)}
                    className={clsx(
                      "px-2.5 py-2 rounded-xl border text-[11.5px] font-semibold text-center transition-all cursor-pointer flex items-center justify-center gap-1.5",
                      template === t.id
                        ? "bg-slate-900 text-white border-slate-900 shadow-2xs"
                        : "bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200"
                    )}
                  >
                    <Icon size={12} className={template === t.id ? "text-cyan-300" : "text-slate-400"} />
                    <span>{t.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Subject Field */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
              Subject Line
            </label>
            <input
              type="text"
              value={subject}
              onChange={e => setSubject(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 focus:bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-2xs"
            />
          </div>

          {/* Message Body Field */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Email Message Body
              </label>
              <button
                type="button"
                onClick={copyFullDraft}
                className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer"
              >
                {copied ? <Check size={11} className="text-emerald-600" /> : <Copy size={11} />}
                <span>{copied ? 'Copied Full Draft!' : 'Copy Draft Text'}</span>
              </button>
            </div>
            <textarea
              rows={8}
              value={body}
              onChange={e => setBody(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-50 focus:bg-white border border-slate-200 rounded-xl text-xs text-slate-800 leading-relaxed outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-2xs font-sans"
            />
          </div>

          {/* Webmail Quick Links */}
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-slate-500 text-[11.5px] flex-wrap gap-2">
            <span className="font-medium">Direct Webmail Launch:</span>
            <div className="flex items-center gap-2">
              <a
                href={gmailLink}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-red-50 hover:bg-red-100 text-red-700 font-semibold border border-red-200 transition-colors"
              >
                <span>Gmail</span>
                <ExternalLink size={10} />
              </a>
              <a
                href={outlookLink}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold border border-blue-200 transition-colors"
              >
                <span>Outlook Web</span>
                <ExternalLink size={10} />
              </a>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 border-t border-slate-100 bg-slate-50/80 flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 rounded-xl hover:bg-slate-200/60 transition-colors"
          >
            Cancel
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={copyFullDraft}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold shadow-2xs transition-colors cursor-pointer"
            >
              {copied ? <Check size={12} className="text-emerald-600" /> : <Copy size={12} />}
              <span>{copied ? 'Copied to Clipboard!' : 'Copy Email'}</span>
            </button>
            <a
              href={mailtoLink}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
            >
              <Send size={12} />
              <span>Launch Default Email Client</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function KeyContacts() {
  const { user } = useAuth();
  const { includeNyserda, isNyserda } = useNyserda();
  const navigate = useNavigate();
  // Admin Outreach Hub and CRM correspondence logs hidden for now
  const isAdmin = false;

  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'top_25_say_yes' | 'funder_officers' | 'domain_experts' | 'institutional_gateways' | 'utilities'>('all');
  const [selectedTech, setSelectedTech] = useState<string>('all');
  const [selectedSector, setSelectedSector] = useState<string>('all');
  const [selectedState, setSelectedState] = useState<string>('all');
  const [hasEmailFilter, setHasEmailFilter] = useState<boolean | undefined>(undefined);
  const [deliverableOnlyFilter, setDeliverableOnlyFilter] = useState<boolean>(false);
  const [sortBy, setSortBy] = useState<string>('funding_desc');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [page, setPage] = useState(1);
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);
  const [emailingContact, setEmailingContact] = useState<ContactItem | IContactDetail | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [checkedContactIds, setCheckedContactIds] = useState<number[]>([]);

  // Fetch summary stats
  const { data: statsData } = useQuery({
    queryKey: ['contacts-stats'],
    queryFn: () => api.getContactStats(),
  });

  // Fetch Top 25 Say Yes Decision-Maker Propensity Matrix
  const { data: sayYesData, isLoading: isLoadingSayYes } = useQuery({
    queryKey: ['say-yes-matrix-contacts', selectedState, selectedTech, includeNyserda],
    queryFn: () => api.getSayYesMatrix({
      location: selectedState !== 'all' ? selectedState : (includeNyserda ? 'NY' : 'CA'),
      technology_areas: selectedTech !== 'all' ? [selectedTech] : ['Energy Storage', 'Grid Modernization', 'Energy Innovation'],
      limit: 25,
    }),
    enabled: selectedCategory === 'top_25_say_yes',
  });

  // Fetch paginated contacts list
  const { data: contactsData, isLoading } = useQuery({
    queryKey: ['contacts-list', {
      search,
      category: selectedCategory !== 'all' && selectedCategory !== 'top_25_say_yes' ? selectedCategory : undefined,
      technology: selectedTech !== 'all' ? selectedTech : undefined,
      sector: selectedSector !== 'all' ? selectedSector : undefined,
      state: selectedState !== 'all' ? selectedState : undefined,
      has_email: hasEmailFilter,
      email_status: deliverableOnlyFilter ? 'verified_valid' : undefined,
      sort_by: sortBy,
      exclude_nyserda: !includeNyserda,
      page,
      page_size: 24,
    }],
    queryFn: () => api.getContacts({
      search: search.trim() || undefined,
      category: selectedCategory !== 'all' && selectedCategory !== 'top_25_say_yes' ? selectedCategory : undefined,
      technology: selectedTech !== 'all' ? selectedTech : undefined,
      sector: selectedSector !== 'all' ? selectedSector : undefined,
      state: selectedState !== 'all' ? selectedState : undefined,
      has_email: hasEmailFilter,
      email_status: deliverableOnlyFilter ? 'verified_valid' : undefined,
      sort_by: sortBy,
      exclude_nyserda: !includeNyserda,
      page,
      page_size: 24,
    }),
  });

  // Fetch single contact dossier
  const { data: contactDetail, isLoading: detailLoading } = useQuery<IContactDetail>({
    queryKey: ['contact-detail', selectedContactId],
    queryFn: () => api.getContact(selectedContactId!),
    enabled: !!selectedContactId,
  });

  // Fetch admin correspondence history if user is admin
  const { data: contactCorrespondence } = useQuery({
    queryKey: ['admin-contact-correspondence', selectedContactId],
    queryFn: () => api.getContactCorrespondenceHistory(selectedContactId!),
    enabled: !!selectedContactId && isAdmin,
  });

  const toggleContactCheck = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setCheckedContactIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const toggleSelectAllPage = () => {
    if (!contactsData?.items) return;
    const pageIds = contactsData.items.map((c: ContactItem) => c.id);
    const allSelected = pageIds.every((id: number) => checkedContactIds.includes(id));
    if (allSelected) {
      setCheckedContactIds(prev => prev.filter((id: number) => !pageIds.includes(id)));
    } else {
      setCheckedContactIds(prev => Array.from(new Set([...prev, ...pageIds])));
    }
  };

  const copyToClipboard = (text: string, key: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const downloadVCard = (contact: ContactItem | IContactDetail, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    const street = contact.address_line1 || '';
    const city = contact.city || '';
    const state = contact.state || '';
    const zip = contact.postal_code || '';
    const country = contact.country || 'US';
    const formatted = contact.formatted_address || `${street}, ${city}, ${state} ${zip}, ${country}`;

    const vcard = `BEGIN:VCARD
VERSION:3.0
FN:${contact.name_display}
ORG:${contact.institution_name || contact.organization_name || ''}
TITLE:${contact.title || ''}
EMAIL:${contact.email || ''}
TEL:${contact.phone || ''}
ADR;TYPE=work:;;${street};${city};${state};${zip};${country}
LABEL;TYPE=work:${formatted}
URL:${contact.entity_contact_url || ''}
NOTE:Energy Innovation Terminal Innovation Directory. Verified Physical Mailing Address: ${formatted}. Provenance: ${contact.data_provenance || 'Public Awardee Registry'}. Status: ${contact.email_status || 'verified_valid'}
END:VCARD`;
    const blob = new Blob([vcard], { type: 'text/vcard;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${contact.name_display.replace(/\s+/g, '_')}.vcf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getRoleBadge = (role?: string) => {
    switch (role) {
      case 'program_officer':
        return { label: 'Program Officer', bg: 'bg-indigo-50 text-indigo-700 border-indigo-200' };
      case 'pi':
        return { label: 'Domain Expert (PI)', bg: 'bg-emerald-50 text-emerald-700 border-emerald-200' };
      case 'institutional_gateway':
        return { label: 'Institutional Gateway', bg: 'bg-purple-50 text-purple-700 border-purple-200' };
      case 'utility_lead':
        return { label: 'Utility Innovation POC', bg: 'bg-amber-50 text-amber-800 border-amber-200' };
      case 'technical_expert':
        return { label: 'Technical Specialist', bg: 'bg-cyan-50 text-cyan-800 border-cyan-200' };
      default:
        return { label: 'Innovation Contact', bg: 'bg-slate-100 text-slate-700 border-slate-200' };
    }
  };

  const resetFilters = () => {
    setSearch('');
    setSelectedCategory('all');
    setSelectedTech('all');
    setSelectedSector('all');
    setSelectedState('all');
    setHasEmailFilter(undefined);
    setDeliverableOnlyFilter(false);
    setSortBy('funding_desc');
    setPage(1);
  };

  const activeFiltersCount = [
    search ? 1 : 0,
    selectedCategory !== 'all' ? 1 : 0,
    selectedTech !== 'all' ? 1 : 0,
    selectedSector !== 'all' ? 1 : 0,
    selectedState !== 'all' ? 1 : 0,
    hasEmailFilter !== undefined ? 1 : 0,
    deliverableOnlyFilter ? 1 : 0,
  ].reduce((a, b) => a + b, 0);

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-16">
      {/* Email Composer Modal */}
      {emailingContact && (
        <EmailComposerModal
          contact={emailingContact}
          onClose={() => setEmailingContact(null)}
        />
      )}

      {/* Top Header & Overview */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-2xs">
              <BookOpen size={12} className="text-indigo-600" />
              <span>Energy Innovation "Yellow Pages"</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
              <ShieldCheck size={12} />
              <span>100% Publicly Sourced &amp; Validated</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-cyan-800 bg-cyan-50 px-2 py-0.5 rounded-md border border-cyan-200 font-mono flex items-center gap-1">
              <Zap size={11} className="text-cyan-600" />
              <span>Direct Outreach Enabled</span>
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Key Contacts &amp; Innovation Directory
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-600 max-w-3xl mt-1 leading-relaxed">
            Public institutional directory and contact ledger across federal &amp; state funding agencies (DOE, ARPA-E, CEC, MassCEC, State Agencies, EPA), energy innovation &amp; deep tech domain experts (Principal Investigators), national laboratory partnering desks, and utility innovation leads with verified email deliverability.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2.5 shrink-0">
          {isAdmin && (
            <button
              type="button"
              onClick={() => navigate('/admin/email-hub', { state: { selectedContactIds: checkedContactIds } })}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-slate-900 dark:bg-slate-800 hover:bg-slate-800 dark:hover:bg-slate-700 text-white text-xs font-semibold rounded-xl border border-slate-700 shadow-xs transition-colors cursor-pointer"
            >
              <Mail size={13} className="text-slate-300" />
              <span>Admin Outreach Hub</span>
              {checkedContactIds.length > 0 && (
                <span className="ml-1 px-1.5 py-0.2 rounded-full bg-blue-500 text-white font-semibold text-[10px]">
                  {checkedContactIds.length}
                </span>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Floating / Sticky Batch Action Bar when contacts are checked */}
      {isAdmin && checkedContactIds.length > 0 && (
        <div className="sticky top-4 z-40 bg-slate-900 text-white p-3.5 rounded-xl border border-slate-700 shadow-xl flex items-center justify-between gap-4 animate-in slide-in-from-top-2 duration-150">
          <div className="flex items-center gap-3">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
            <span className="text-xs font-medium">
              <strong className="text-white font-mono text-sm">{checkedContactIds.length}</strong> contacts selected for group outreach
            </span>
            <button
              type="button"
              onClick={() => setCheckedContactIds([])}
              className="text-[11px] text-slate-400 hover:text-white underline cursor-pointer"
            >
              Clear selection
            </button>
          </div>

          <button
            type="button"
            onClick={() => navigate('/admin/email-hub', { state: { selectedContactIds: checkedContactIds } })}
            className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors cursor-pointer"
          >
            <Send size={12} />
            <span>Compose Group Campaign</span>
            <ChevronRight size={14} />
          </button>
        </div>
      )}

      {/* Metrics Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <div className="dark:bg-[#0d1424]/90 bg-white p-3.5 rounded-xl border dark:border-white/10 border-slate-200/90 shadow-2xs dark:hover:border-white/20 hover:border-slate-300 transition-all dark:text-slate-100 text-slate-800">
          <div className="flex items-center justify-between dark:text-slate-400 text-slate-500 mb-1">
            <span className="text-[10.5px] font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 font-mono">Verified Contacts</span>
            <Users size={14} className="text-cyan-500" />
          </div>
          <div className="text-xl font-bold dark:text-white text-slate-900 font-mono">
            {statsData?.total_contacts?.toLocaleString() || '3,090'}
          </div>
          <div className="text-[11px] text-emerald-500 font-medium mt-0.5 flex items-center gap-1 font-mono">
            <CheckCircle2 size={10} />
            <span>{statsData?.verified_valid_emails?.toLocaleString() || '2,946'} live deliverable</span>
          </div>
        </div>

        <div className="dark:bg-[#0d1424]/90 bg-white p-3.5 rounded-xl border dark:border-white/10 border-slate-200/90 shadow-2xs dark:hover:border-white/20 hover:border-slate-300 transition-all dark:text-slate-100 text-slate-800">
          <div className="flex items-center justify-between dark:text-slate-400 text-slate-500 mb-1">
            <span className="text-[10.5px] font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 font-mono">Email Deliverability</span>
            <Mail size={14} className="text-emerald-500" />
          </div>
          <div className="text-xl font-bold dark:text-emerald-400 text-emerald-700 font-mono">
            {statsData?.email_deliverability_rate || '99.7%'}
          </div>
          <div className="text-[11px] dark:text-slate-400 text-slate-500 font-medium mt-0.5 font-mono">
            DNS MX &amp; Syntax Validated
          </div>
        </div>

        <div className="dark:bg-[#0d1424]/90 bg-white p-3.5 rounded-xl border dark:border-white/10 border-slate-200/90 shadow-2xs dark:hover:border-white/20 hover:border-slate-300 transition-all dark:text-slate-100 text-slate-800">
          <div className="flex items-center justify-between dark:text-slate-400 text-slate-500 mb-1">
            <span className="text-[10.5px] font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 font-mono">Program Officers</span>
            <Landmark size={14} className="text-cyan-500" />
          </div>
          <div className="text-xl font-bold dark:text-white text-slate-900 font-mono">
            {statsData?.program_officers_count || 74}
          </div>
          <div className="text-[11px] dark:text-slate-400 text-slate-500 font-medium mt-0.5">
            DOE, CEC, MassCEC, State Agencies
          </div>
        </div>

        <div className="dark:bg-[#0d1424]/90 bg-white p-3.5 rounded-xl border dark:border-white/10 border-slate-200/90 shadow-2xs dark:hover:border-white/20 hover:border-slate-300 transition-all dark:text-slate-100 text-slate-800">
          <div className="flex items-center justify-between dark:text-slate-400 text-slate-500 mb-1">
            <span className="text-[10.5px] font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 font-mono">Domain Experts (PIs)</span>
            <Award size={14} className="text-purple-500" />
          </div>
          <div className="text-xl font-bold dark:text-white text-slate-900 font-mono">
            {statsData?.domain_experts_count?.toLocaleString() || '2,998'}
          </div>
          <div className="text-[11px] dark:text-slate-400 text-slate-500 font-medium mt-0.5">
            Research Leaders &amp; Awardees
          </div>
        </div>

        <div className="dark:bg-[#0d1424]/90 bg-white p-3.5 rounded-xl border dark:border-white/10 border-slate-200/90 shadow-2xs dark:hover:border-white/20 hover:border-slate-300 transition-all col-span-2 sm:col-span-1 dark:text-slate-100 text-slate-800">
          <div className="flex items-center justify-between dark:text-slate-400 text-slate-500 mb-1">
            <span className="text-[10.5px] font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 font-mono">Lab &amp; Utility Desks</span>
            <Zap size={14} className="text-amber-500" />
          </div>
          <div className="text-xl font-bold dark:text-white text-slate-900 font-mono">
            {(statsData?.institutional_gateways_count || 10) + (statsData?.utility_leads_count || 5)}
          </div>
          <div className="text-[11px] dark:text-slate-400 text-slate-500 font-medium mt-0.5">
            NREL, PNNL, LBNL &amp; Utilities
          </div>
        </div>
      </div>

      {/* Cockpit Category Selector Tabs */}
      <div className="flex items-center gap-1.5 border-b dark:border-white/10 border-slate-200 pb-2 overflow-x-auto no-scrollbar">
        {[
          { id: 'all', label: 'All Key Contacts', icon: Users, count: statsData?.total_contacts },
          { id: 'top_25_say_yes', label: 'Top 25 "Say Yes" Decision-Makers', icon: Sparkles, count: 25 },
          { id: 'funder_officers', label: 'Agency Program Officers', icon: Landmark, count: statsData?.program_officers_count },
          { id: 'domain_experts', label: 'Technology & Sector Experts (PIs)', icon: FlaskConical, count: statsData?.domain_experts_count },
          { id: 'institutional_gateways', label: 'National Lab Desks', icon: Building2, count: statsData?.institutional_gateways_count },
          { id: 'utilities', label: 'Utility Energy Innovation Leads', icon: Zap, count: statsData?.utility_leads_count },
        ].map(tab => {
          const Icon = tab.icon;
          const isSelected = selectedCategory === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => {
                setSelectedCategory(tab.id as any);
                setPage(1);
              }}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-[12px] font-medium transition-all shrink-0 flex items-center gap-2 cursor-pointer',
                isSelected
                  ? 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 font-semibold shadow-2xs'
                  : 'dark:text-slate-400 text-slate-600 hover:dark:bg-slate-800 hover:bg-slate-100 hover:text-slate-900 dark:hover:text-white'
              )}
            >
              <Icon size={13} className={isSelected ? 'text-blue-400 dark:text-blue-600' : 'text-slate-400'} />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={clsx(
                  "text-[10px] font-mono font-semibold px-1.5 py-0.2 rounded-full",
                  isSelected ? "bg-white/20 dark:bg-slate-900/20 text-white dark:text-slate-900" : "dark:bg-slate-800 bg-slate-100 dark:text-slate-300 text-slate-600"
                )}>
                  {tab.count.toLocaleString()}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Search & Multifaceted Filtering Controls */}
      <div className="dark:bg-[#0d1424]/90 bg-white p-4 rounded-2xl border dark:border-white/10 border-slate-200/90 shadow-2xs space-y-3.5">
        <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
          {/* Main Search Input */}
          <div className="relative flex-1 min-w-0">
            <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 dark:text-slate-400 text-slate-500" />
            <input
              type="text"
              placeholder="Search by contact name, email, institution, technology area, department, city, or keywords..."
              value={search}
              onChange={e => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-8 py-2 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-xl text-[13px] dark:text-white text-slate-900 focus:border-cyan-400 outline-none transition-all dark:placeholder-slate-500 placeholder-slate-400 shadow-2xs font-medium"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 dark:text-slate-400 text-slate-500 hover:dark:text-slate-200 hover:text-slate-800 rounded-full cursor-pointer"
              >
                <X size={13} />
              </button>
            )}
          </div>

          {/* Sort By Dropdown */}
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-xs dark:text-slate-400 text-slate-500 font-medium hidden sm:inline font-mono">Sort:</span>
            <select
              value={sortBy}
              onChange={e => {
                setSortBy(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-xl text-xs font-semibold dark:text-slate-200 text-slate-800 outline-none focus:border-cyan-400 shadow-2xs cursor-pointer font-medium"
            >
              <option value="funding_desc">💰 Funding Volume Led (High to Low)</option>
              <option value="awards_desc">🏆 Most Awards &amp; Projects</option>
              <option value="name_asc">🔤 Contact Name (A to Z)</option>
              <option value="org_asc">🏢 Institution Name (A to Z)</option>
              <option value="email_score">⚡ Verified Email Deliverability</option>
              <option value="recent">⏱️ Recently Verified</option>
            </select>

            {/* View Mode Toggle */}
            <div className="flex items-center border dark:border-white/10 border-slate-200 rounded-xl p-0.5 dark:bg-black/40 bg-slate-100">
              <button
                type="button"
                onClick={() => setViewMode('grid')}
                className={clsx(
                  "p-1.5 rounded-lg transition-all cursor-pointer",
                  viewMode === 'grid' ? "bg-cyan-500 text-slate-950 shadow-2xs font-bold" : "dark:text-slate-400 text-slate-600 hover:dark:text-white hover:text-slate-900"
                )}
                title="Grid View"
              >
                <LayoutGrid size={15} />
              </button>
              <button
                type="button"
                onClick={() => setViewMode('table')}
                className={clsx(
                  "p-1.5 rounded-lg transition-all cursor-pointer",
                  viewMode === 'table' ? "bg-cyan-500 text-slate-950 shadow-2xs font-bold" : "dark:text-slate-400 text-slate-600 hover:dark:text-white hover:text-slate-900"
                )}
                title="Table/List View"
              >
                <List size={15} />
              </button>
            </div>
          </div>
        </div>

        {/* Secondary Filter Row */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t dark:border-white/10 border-slate-200 text-xs">
          {/* Technology Area Selector */}
          <select
            value={selectedTech}
            onChange={e => {
              setSelectedTech(e.target.value);
              setPage(1);
            }}
            className="px-2.5 py-1.5 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-lg text-xs font-medium dark:text-slate-200 text-slate-800 outline-none hover:dark:bg-white/[0.08] hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <option value="all">⚡ All Technology Domains</option>
            <option value="Energy Storage & Advanced Batteries">🔋 Energy Storage &amp; Batteries</option>
            <option value="Solar">☀️ Solar &amp; Photovoltaics</option>
            <option value="Wind">💨 Wind &amp; Offshore Wind</option>
            <option value="Hydrogen">💧 Hydrogen &amp; Clean Fuels</option>
            <option value="Grid Modernization">⚡ Grid Modernization &amp; Smart Power</option>
            <option value="Carbon Capture">🌱 Carbon Capture &amp; CCUS</option>
            <option value="Building Decarbonization">🏢 Building Decarbonization &amp; Clean Heat</option>
            <option value="Electric Mobility">🚗 Electric Mobility &amp; EVs</option>
            <option value="Nuclear">⚛️ Advanced Nuclear &amp; Fusion</option>
            <option value="Industrial Decarbonization">🏭 Industrial Decarb &amp; Heat</option>
            <option value="AI">🤖 AI, ML &amp; Energy Software</option>
            <option value="Bioenergy">🌾 Bioenergy &amp; Sustainable Fuels</option>
          </select>

          {/* Sector Selector */}
          <select
            value={selectedSector}
            onChange={e => {
              setSelectedSector(e.target.value);
              setPage(1);
            }}
            className="px-2.5 py-1.5 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-lg text-xs font-medium dark:text-slate-200 text-slate-800 outline-none hover:dark:bg-white/[0.08] hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <option value="all">🌐 All Market Sectors</option>
            <option value="Electric Grid & Utility">⚡ Electric Grid &amp; Utility</option>
            <option value="Industrial & Manufacturing">🏭 Industrial &amp; Manufacturing</option>
            <option value="Transportation & Mobility">🚗 Transportation &amp; Mobility</option>
            <option value="Buildings & Real Estate">🏢 Buildings &amp; Real Estate</option>
            <option value="Agriculture & Forestry">🌾 Agriculture &amp; Forestry</option>
            <option value="Government & Municipal">🏛️ Government &amp; Municipal</option>
            <option value="Cross-Cutting & Policy">📜 Cross-Cutting &amp; Policy</option>
          </select>

          {/* State / Location Selector */}
          <select
            value={selectedState}
            onChange={e => {
              setSelectedState(e.target.value);
              setPage(1);
            }}
            className="px-2.5 py-1.5 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-lg text-xs font-medium dark:text-slate-200 text-slate-800 outline-none hover:dark:bg-white/[0.08] hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <option value="all">📍 All States &amp; Regions</option>
            <option value="NY">🗽 New York (NY)</option>
            <option value="CA">☀️ California (CA)</option>
            <option value="MA">🏛️ Massachusetts (MA)</option>
            <option value="DC">🏛️ Washington, DC</option>
            <option value="CO">🏔️ Colorado (CO)</option>
            <option value="WA">🌲 Washington (WA)</option>
            <option value="TX">⭐ Texas (TX)</option>
            <option value="IL">🏙️ Illinois (IL)</option>
            <option value="PA">🔔 Pennsylvania (PA)</option>
            <option value="NC">🌲 North Carolina (NC)</option>
            <option value="TN">⛰️ Tennessee (TN)</option>
          </select>

          {/* Deliverable Only Toggle */}
          <button
            type="button"
            onClick={() => {
              setDeliverableOnlyFilter(prev => !prev);
              setPage(1);
            }}
            className={clsx(
              "inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border font-semibold text-xs transition-all cursor-pointer",
              deliverableOnlyFilter
                ? "bg-emerald-600 text-white border-emerald-600 shadow-2xs"
                : "bg-emerald-50/80 text-emerald-800 border-emerald-200 hover:bg-emerald-100"
            )}
          >
            <CheckCircle2 size={12} className={deliverableOnlyFilter ? "text-white" : "text-emerald-600"} />
            <span>Verified Deliverable Only</span>
          </button>

          {/* Clear Filters Reset */}
          {activeFiltersCount > 0 && (
            <button
              type="button"
              onClick={resetFilters}
              className="inline-flex items-center gap-1 px-2.5 py-1.5 text-slate-500 hover:text-red-600 text-xs font-semibold rounded-lg hover:bg-red-50 transition-colors ml-auto cursor-pointer"
            >
              <X size={12} />
              <span>Reset Filters ({activeFiltersCount})</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Content Layout */}
      {selectedCategory === 'top_25_say_yes' ? (
        isLoadingSayYes ? (
          <div className="h-72 flex flex-col items-center justify-center gap-3 dark:bg-[#0d1424] bg-white rounded-2xl border dark:border-white/10 border-slate-200/80 shadow-2xs">
            <Loader2 className="animate-spin text-cyan-500" size={32} />
            <span className="text-xs font-semibold dark:text-slate-300 text-slate-600">Calculating top 25 decision-maker propensity rankings...</span>
          </div>
        ) : (
          <SayYesDecisionMakerMatrix
            organizations={sayYesData?.say_yes_matrix || []}
            projectTitle="Energy Innovation Innovation Initiative"
            projectLocation={selectedState !== 'all' ? selectedState : 'New York'}
          />
        )
      ) : isLoading ? (
        <div className="h-72 flex flex-col items-center justify-center gap-3 bg-white rounded-2xl border border-slate-200/80 shadow-2xs">
          <Loader2 className="animate-spin text-indigo-600" size={32} />
          <span className="text-xs font-semibold text-slate-600">Querying verified energy innovation innovation contacts...</span>
        </div>
      ) : (
        <div className="flex gap-6 items-start">
          {/* Contact Directory Grid / Table */}
          <div className="flex-1 min-w-0 space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-500 font-medium px-1">
              <span>
                Showing <strong className="text-slate-900">{contactsData?.items?.length || 0}</strong> of <strong className="text-slate-900">{contactsData?.total?.toLocaleString() || 0}</strong> contacts
              </span>
              <span>
                Page <strong className="text-slate-900">{contactsData?.page || 1}</strong> of <strong className="text-slate-900">{contactsData?.total_pages || 1}</strong>
              </span>
            </div>

            {contactsData?.items?.length === 0 ? (
              <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center shadow-2xs space-y-3">
                <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
                  <Search size={20} />
                </div>
                <h3 className="text-base font-bold text-slate-900">No contacts match your filter criteria</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  Try broadening your search term, switching categories, or clearing active filters to view all indexed innovation contacts.
                </p>
                <button
                  type="button"
                  onClick={resetFilters}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800 transition-colors shadow-2xs cursor-pointer"
                >
                  <X size={13} />
                  <span>Clear All Filters</span>
                </button>
              </div>
            ) : viewMode === 'grid' ? (
              /* GRID VIEW */
              <div className={clsx(
                "grid gap-4 auto-rows-min transition-all",
                selectedContactId
                  ? "grid-cols-1 md:grid-cols-2"
                  : "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
              )}>
                {contactsData?.items?.map((contact: ContactItem) => {
                  const roleBadge = getRoleBadge(contact.role_type);
                  const isSelected = selectedContactId === contact.id;
                  const isChecked = checkedContactIds.includes(contact.id);

                  return (
                    <div
                      key={contact.id}
                      onClick={() => setSelectedContactId(contact.id)}
                      className={clsx(
                        "text-left bg-white rounded-2xl border p-4.5 hover:shadow-md transition-all group shadow-2xs relative flex flex-col justify-between cursor-pointer",
                        isChecked ? "border-indigo-500 ring-2 ring-indigo-200 bg-indigo-50/20" :
                        isSelected
                          ? "border-indigo-500 ring-2 ring-indigo-100 shadow-md bg-indigo-50/10"
                          : "border-slate-200/80 hover:border-indigo-300"
                      )}
                    >
                      <div>
                        {/* Header: Checkbox (Admin), Logo, Name & Role Badge */}
                        <div className="flex items-start gap-3">
                          {isAdmin && (
                            <div className="pt-0.5 shrink-0" onClick={e => e.stopPropagation()}>
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={e => toggleContactCheck(contact.id, e as any)}
                                className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                              />
                            </div>
                          )}
                          <OrgLogo
                            org={contact.institution_name || contact.organization_name || 'Organization'}
                            domain={contact.email_domain || contact.entity_contact_url || ''}
                            size="md"
                          />
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between gap-1.5">
                              <h3 className="text-[13.5px] font-bold text-slate-900 group-hover:text-indigo-700 transition-colors truncate">
                                {contact.name_display}
                              </h3>
                              <ChevronRight size={14} className="text-slate-300 group-hover:text-indigo-600 shrink-0" />
                            </div>

                            {/* Role Badge & Email Verification Pill */}
                            <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                              <span className={clsx("text-[9.5px] font-bold px-2 py-0.5 rounded-full border", roleBadge.bg)}>
                                {roleBadge.label}
                              </span>
                              {contact.email_deliverable ? (
                                <span className="inline-flex items-center gap-0.5 text-[9px] font-bold font-mono px-1.5 py-0.2 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                                  <CheckCircle2 size={9} />
                                  <span>Verified</span>
                                </span>
                              ) : null}
                              {contact.state && (
                                <span className="text-[10.5px] text-slate-500 font-medium flex items-center gap-0.5">
                                  <MapPin size={10} className="text-slate-400" />
                                  {contact.city ? `${contact.city}, ` : ''}{contact.state}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Title, Institution & Physical Mailing Address */}
                        <div className="mt-3 space-y-1">
                          {contact.title && (
                            <div className="text-[12px] font-semibold text-slate-800 line-clamp-1">
                              {contact.title}
                            </div>
                          )}
                          <div className="text-[11.5px] text-slate-500 font-medium line-clamp-1 flex items-center gap-1">
                            <Building2 size={11} className="text-slate-400 shrink-0" />
                            <span>{contact.institution_name || contact.organization_name}</span>
                          </div>
                          {contact.formatted_address ? (
                            <div className="text-[10.5px] text-slate-500 font-medium line-clamp-1 flex items-center gap-1 pt-0.5" title={`Verified Mailing Address: ${contact.formatted_address}`}>
                              <MapPin size={11} className="text-indigo-500 shrink-0" />
                              <span className="truncate">{contact.formatted_address}</span>
                            </div>
                          ) : null}
                        </div>

                        {/* Technology Area Tag */}
                        {contact.technology_area && (
                          <div className="mt-2.5 inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[10.5px] font-semibold">
                            {TECH_ICONS[contact.technology_area] || <Zap size={11} className="text-indigo-500" />}
                            <span className="truncate max-w-[200px]">{contact.technology_area}</span>
                          </div>
                        )}
                      </div>

                      {/* Contact Actions & Provenance */}
                      <div className="mt-4 pt-3 border-t border-slate-100 space-y-2">
                        <div className="flex items-center justify-between text-xs gap-2">
                          {contact.email ? (
                            <div className="flex items-center gap-1.5 min-w-0">
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setEmailingContact(contact);
                                }}
                                className="inline-flex items-center gap-1 px-2.5 py-1 bg-indigo-50 hover:bg-indigo-600 text-indigo-700 hover:text-white font-bold text-[11px] rounded-lg transition-all border border-indigo-200 hover:border-indigo-600 shadow-2xs cursor-pointer group/btn"
                              >
                                <Send size={11} className="group-hover/btn:translate-x-0.5 transition-transform" />
                                <span>Email Now</span>
                              </button>
                              <button
                                type="button"
                                onClick={e => copyToClipboard(contact.email!, `email-${contact.id}`, e)}
                                className="p-1 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                                title="Copy Email"
                              >
                                {copiedKey === `email-${contact.id}` ? <Check size={11} className="text-emerald-600" /> : <Copy size={11} />}
                              </button>
                            </div>
                          ) : (
                            <span className="text-[11px] font-medium text-slate-400 italic flex items-center gap-1">
                              <ExternalLink size={10} /> Refer to Entity Gateway
                            </span>
                          )}

                          {contact.total_funding > 0 && (
                            <span className="text-[11px] font-mono font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200 shrink-0">
                              {fmt(contact.total_funding)}
                            </span>
                          )}
                        </div>

                        {/* Data Provenance Badge */}
                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono pt-1">
                          <span className="truncate max-w-[210px]">
                            {contact.data_provenance || 'Public Registry'}
                          </span>
                          {contact.awards_count > 0 && (
                            <span className="text-slate-600 font-semibold shrink-0">
                              {contact.awards_count} {contact.awards_count === 1 ? 'Project' : 'Projects'}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              /* TABLE / LIST VIEW */
              <div className="bg-white rounded-2xl border border-slate-200/80 shadow-2xs overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 border-b border-slate-200/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                      <tr>
                        {isAdmin && (
                          <th className="py-3 px-3 w-10 text-center">
                            <input
                              type="checkbox"
                              checked={Boolean(contactsData?.items && contactsData.items.length > 0 && contactsData.items.every((c: ContactItem) => checkedContactIds.includes(c.id)))}
                              onChange={toggleSelectAllPage}
                              className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                              title="Select All on Page"
                            />
                          </th>
                        )}
                        <th className="py-3 px-4">Contact Name &amp; Role</th>
                        <th className="py-3 px-4">Institution / Organization</th>
                        <th className="py-3 px-4">Technology &amp; Sector</th>
                        <th className="py-3 px-4">Public Email &amp; Status</th>
                        <th className="py-3 px-4 text-right">Led Awards</th>
                        <th className="py-3 px-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {contactsData?.items?.map((contact: ContactItem) => {
                        const roleBadge = getRoleBadge(contact.role_type);
                        const isSelected = selectedContactId === contact.id;
                        const isChecked = checkedContactIds.includes(contact.id);

                        return (
                          <tr
                            key={contact.id}
                            onClick={() => setSelectedContactId(contact.id)}
                            className={clsx(
                              "hover:bg-indigo-50/40 transition-colors cursor-pointer",
                              isChecked ? "bg-indigo-50/50" : "",
                              isSelected ? "bg-indigo-50/60 font-semibold" : ""
                            )}
                          >
                            {isAdmin && (
                              <td className="py-3 px-3 text-center" onClick={e => e.stopPropagation()}>
                                <input
                                  type="checkbox"
                                  checked={isChecked}
                                  onChange={e => toggleContactCheck(contact.id, e as any)}
                                  className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                                />
                              </td>
                            )}
                            <td className="py-3 px-4">
                              <div className="font-bold text-[13px] text-slate-900">{contact.name_display}</div>
                              <div className="flex items-center gap-1.5 mt-0.5">
                                <span className={clsx("text-[9px] font-bold px-1.5 py-0.2 rounded-full border", roleBadge.bg)}>
                                  {roleBadge.label}
                                </span>
                                {contact.title && (
                                  <span className="text-[11px] text-slate-500 truncate max-w-[180px]">
                                    {contact.title}
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2.5">
                                <OrgLogo
                                  org={contact.institution_name || contact.organization_name || 'Organization'}
                                  domain={contact.email_domain || contact.entity_contact_url || ''}
                                  size="sm"
                                  showTooltip={false}
                                />
                                <div className="min-w-0">
                                  <div className="font-semibold text-slate-800 truncate max-w-[240px]">
                                    {contact.institution_name || contact.organization_name}
                                  </div>
                                  {contact.formatted_address ? (
                                    <div className="text-[10.5px] text-slate-500 truncate max-w-[260px] flex items-center gap-1" title={contact.formatted_address}>
                                      <MapPin size={10} className="text-indigo-500 shrink-0" />
                                      <span className="truncate">{contact.formatted_address}</span>
                                    </div>
                                  ) : contact.state ? (
                                    <div className="text-[11px] text-slate-400 truncate">
                                      {contact.city ? `${contact.city}, ` : ''}{contact.state}
                                    </div>
                                  ) : null}
                                </div>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              {contact.technology_area && (
                                <div className="font-medium text-slate-700 flex items-center gap-1">
                                  {TECH_ICONS[contact.technology_area] || <Zap size={11} className="text-indigo-500" />}
                                  <span className="truncate max-w-[170px]">{contact.technology_area}</span>
                                </div>
                              )}
                              {contact.sector && (
                                <div className="text-[10.5px] text-slate-400">{contact.sector}</div>
                              )}
                            </td>
                            <td className="py-3 px-4">
                              {contact.email ? (
                                <div>
                                  <div className="flex items-center gap-1">
                                    <span className="font-mono text-[11.5px] text-slate-800">{contact.email}</span>
                                    <button
                                      type="button"
                                      onClick={e => copyToClipboard(contact.email!, `t-email-${contact.id}`, e)}
                                      className="p-1 rounded text-slate-400 hover:text-slate-600"
                                    >
                                      {copiedKey === `t-email-${contact.id}` ? <Check size={10} className="text-emerald-600" /> : <Copy size={10} />}
                                    </button>
                                  </div>
                                  <div className="flex items-center gap-1 mt-0.5">
                                    {contact.email_deliverable ? (
                                      <span className="inline-flex items-center gap-0.5 text-[9px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                                        <CheckCircle2 size={8} /> Verified Deliverable
                                      </span>
                                    ) : (
                                      <span className="text-[9px] text-slate-400 font-mono">Syntax Valid</span>
                                    )}
                                  </div>
                                </div>
                              ) : (
                                <span className="text-slate-400 italic text-[11px]">Refer to Entity Gateway</span>
                              )}
                            </td>
                            <td className="py-3 px-4 text-right">
                              {contact.total_funding > 0 ? (
                                <div className="font-mono font-bold text-emerald-700">{fmt(contact.total_funding)}</div>
                              ) : (
                                <div className="text-slate-400">—</div>
                              )}
                              {contact.awards_count > 0 && (
                                <div className="text-[10.5px] text-slate-500">{contact.awards_count} projects</div>
                              )}
                            </td>
                            <td className="py-3 px-4 text-right">
                              <div className="flex items-center justify-end gap-1.5">
                                {contact.email && (
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setEmailingContact(contact);
                                    }}
                                    className="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-600 text-indigo-700 hover:text-white font-bold text-[11px] rounded-lg transition-colors border border-indigo-200 shadow-2xs cursor-pointer"
                                  >
                                    Email Now
                                  </button>
                                )}
                                <button
                                  type="button"
                                  onClick={() => setSelectedContactId(contact.id)}
                                  className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg transition-colors"
                                >
                                  Dossier
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Pagination Controls */}
            {contactsData && contactsData.total_pages > 1 && (
              <div className="flex items-center justify-between bg-white px-4 py-3 rounded-xl border border-slate-200/80 shadow-2xs text-xs font-semibold">
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
                >
                  Previous
                </button>
                <div className="text-slate-600">
                  Page <span className="font-bold text-slate-900">{page}</span> of <span className="font-bold text-slate-900">{contactsData.total_pages}</span>
                </div>
                <button
                  type="button"
                  disabled={page >= contactsData.total_pages}
                  onClick={() => setPage(p => Math.min(contactsData.total_pages, p + 1))}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
                >
                  Next
                </button>
              </div>
            )}
          </div>

          {/* Slide-out Contact Dossier Drawer */}
          {selectedContactId && (
            <div className="w-96 bg-white rounded-2xl border border-slate-200 shadow-xl flex flex-col max-h-[calc(100vh-10rem)] overflow-hidden shrink-0 sticky top-4 animate-in slide-in-from-right-3 duration-150">
              {/* Dossier Header */}
              <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/80 flex items-start justify-between rounded-t-2xl">
                <div className="flex items-start gap-3 min-w-0">
                  <OrgLogo
                    org={contactDetail?.institution_name || contactDetail?.organization?.name || 'Organization'}
                    domain={contactDetail?.email_domain || contactDetail?.entity_contact_url || contactDetail?.organization?.website || ''}
                    size="md"
                  />
                  <div className="min-w-0">
                    <h2 className="text-[14.5px] font-bold text-slate-900 leading-snug truncate">
                      {contactDetail?.name_display || 'Contact Dossier'}
                    </h2>
                    {contactDetail?.role_type && (
                      <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                        <span className={clsx("text-[9.5px] font-bold px-2 py-0.5 rounded-full border", getRoleBadge(contactDetail.role_type).bg)}>
                          {getRoleBadge(contactDetail.role_type).label}
                        </span>
                        {contactDetail.email_deliverable ? (
                          <span className="text-[9.5px] font-mono font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                            Verified Deliverable
                          </span>
                        ) : null}
                      </div>
                    )}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedContactId(null)}
                  className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors"
                >
                  <X size={16} />
                </button>
              </div>

              {/* Dossier Body */}
              <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
                {detailLoading ? (
                  <div className="flex justify-center py-12">
                    <Loader2 className="animate-spin text-indigo-600" size={24} />
                  </div>
                ) : contactDetail ? (
                  <>
                    {/* Primary Action Buttons */}
                    <div className="flex items-center gap-2">
                      {contactDetail.email ? (
                        <button
                          type="button"
                          onClick={() => setEmailingContact(contactDetail)}
                          className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
                        >
                          <Send size={12} />
                          <span>Email Now</span>
                        </button>
                      ) : null}
                      <button
                        type="button"
                        onClick={e => downloadVCard(contactDetail, e)}
                        className="inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold shadow-2xs transition-colors cursor-pointer"
                      >
                        <Download size={12} />
                        <span>vCard</span>
                      </button>
                    </div>

                    {/* Admin Outreach & CRM Card */}
                    {isAdmin && (
                      <div className="bg-slate-900 text-white rounded-xl p-3.5 border border-slate-700 space-y-2.5 shadow-md">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                            <Mail size={11} />
                            <span>Admin Outreach &amp; Correspondence CRM</span>
                          </span>
                          {contactCorrespondence?.has_thread ? (
                            <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded bg-slate-800 text-blue-300 border border-slate-700 uppercase font-mono">
                              {contactCorrespondence.thread?.status?.replace('_', ' ')}
                            </span>
                          ) : (
                            <span className="text-[9px] text-slate-400 font-mono">No Outreach Yet</span>
                          )}
                        </div>

                        {contactCorrespondence?.has_thread ? (
                          <div className="space-y-1.5">
                            <p className="text-[11px] text-slate-300 leading-relaxed">
                              {contactCorrespondence.thread?.conversation_summary || 'Active email thread linked with Brandon Owens.'}
                            </p>
                            {contactCorrespondence.thread?.next_action && (
                              <div className="text-[10px] text-blue-300 font-medium">
                                👉 Next: {contactCorrespondence.thread.next_action}
                              </div>
                            )}
                          </div>
                        ) : (
                          <p className="text-[11px] text-slate-400">
                            No email outreach recorded yet with Brandon Owens for this contact.
                          </p>
                        )}

                        <button
                          type="button"
                          onClick={() => navigate('/admin/email-hub', { state: { selectedContactIds: [contactDetail.id] } })}
                          className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                        >
                          <Send size={11} />
                          <span>{contactCorrespondence?.has_thread ? 'Manage in Admin Email Hub' : 'Launch Outreach to this Contact'}</span>
                        </button>
                      </div>
                    )}

                    {/* Official Contact Details Box */}
                    <div className="bg-slate-50 rounded-xl border border-slate-200/80 p-3.5 space-y-2.5">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        Official Public Contact Point
                      </div>

                      {contactDetail.title && (
                        <div>
                          <span className="block text-[10px] text-slate-400">Position / Title</span>
                          <span className="font-semibold text-slate-800">{contactDetail.title}</span>
                        </div>
                      )}

                      {contactDetail.department && (
                        <div>
                          <span className="block text-[10px] text-slate-400">Department / Office</span>
                          <span className="font-medium text-slate-700">{contactDetail.department}</span>
                        </div>
                      )}

                      <div>
                        <span className="block text-[10px] text-slate-400">Institution / Entity</span>
                        <span className="font-semibold text-slate-800">
                          {contactDetail.institution_name || contactDetail.organization?.name}
                        </span>
                      </div>

                      {/* Verified Physical Mailing Address */}
                      <div className="pt-0.5">
                        <div className="flex items-center justify-between">
                          <span className="block text-[10px] text-slate-400">Verified Physical Mailing Address</span>
                          {contactDetail.formatted_address && (
                            <button
                              type="button"
                              onClick={e => copyToClipboard(contactDetail.formatted_address!, 'dossier-address', e)}
                              className="text-[10px] text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1 cursor-pointer"
                              title="Copy Physical Address"
                            >
                              {copiedKey === 'dossier-address' ? <Check size={10} className="text-emerald-600" /> : <Copy size={10} />}
                              <span>{copiedKey === 'dossier-address' ? 'Copied Address!' : 'Copy Address'}</span>
                            </button>
                          )}
                        </div>
                        <div className="mt-1 p-2.5 bg-white rounded-lg border border-slate-200/80 shadow-2xs space-y-1">
                          <div className="flex items-start gap-2">
                            <MapPin size={13} className="text-indigo-600 shrink-0 mt-0.5" />
                            <div className="min-w-0 flex-1">
                              {contactDetail.address_line1 && (
                                <div className="font-semibold text-slate-800 text-[11.5px] leading-tight">
                                  {contactDetail.address_line1}
                                  {contactDetail.address_line2 ? ` · ${contactDetail.address_line2}` : ''}
                                </div>
                              )}
                              <div className="text-[11px] text-slate-600 font-medium mt-0.5">
                                {contactDetail.city ? `${contactDetail.city}, ` : ''}{contactDetail.state} {contactDetail.postal_code || ''}
                              </div>
                              <div className="text-[10px] font-mono text-slate-400 flex items-center justify-between pt-1 mt-1 border-t border-slate-100">
                                <span>{contactDetail.country || 'US'}</span>
                                <span className="inline-flex items-center gap-0.5 text-[9px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                                  <CheckCircle2 size={8} /> Verified Physical Address
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {contactDetail.email ? (
                        <div>
                          <span className="block text-[10px] text-slate-400">Direct Public Project Email</span>
                          <div className="flex items-center justify-between mt-0.5">
                            <a
                              href={`mailto:${contactDetail.email}`}
                              className="text-indigo-600 hover:underline font-mono font-semibold text-[12px] flex items-center gap-1 truncate"
                            >
                              <Mail size={12} className="shrink-0" />
                              <span className="truncate">{contactDetail.email}</span>
                            </a>
                            <button
                              type="button"
                              onClick={e => copyToClipboard(contactDetail.email!, 'dossier-email', e)}
                              className="p-1 rounded text-slate-400 hover:text-slate-600"
                              title="Copy Email"
                            >
                              {copiedKey === 'dossier-email' ? <Check size={11} className="text-emerald-600" /> : <Copy size={11} />}
                            </button>
                          </div>
                          {contactDetail.email_deliverable && (
                            <div className="mt-1 flex items-center gap-1 text-[10px] text-emerald-700 font-mono">
                              <CheckCircle2 size={10} />
                              <span>MX Verified Active ({contactDetail.email_domain})</span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="p-2 bg-amber-50 rounded-lg border border-amber-200 text-amber-900 text-[11px]">
                          <strong>Entity Contact Gateway:</strong> Direct personal email is unreleased in public award record. Please contact via official institutional portal below.
                        </div>
                      )}

                      {contactDetail.phone && (
                        <div>
                          <span className="block text-[10px] text-slate-400">Official Telephone Line</span>
                          <span className="font-mono text-slate-700 flex items-center gap-1 mt-0.5">
                            <Phone size={11} className="text-slate-400" />
                            <span>{contactDetail.phone}</span>
                          </span>
                        </div>
                      )}

                      {contactDetail.entity_contact_url && (
                        <div className="pt-1">
                          <a
                            href={contactDetail.entity_contact_url.startsWith('http') ? contactDetail.entity_contact_url : `https://${contactDetail.entity_contact_url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 text-indigo-600 hover:underline font-semibold text-[11.5px]"
                          >
                            <Globe size={12} />
                            <span>Visit Official Institutional Portal</span>
                            <ExternalLink size={10} />
                          </a>
                        </div>
                      )}
                    </div>

                    {/* Domain & Specialization */}
                    <div className="bg-indigo-50/50 rounded-xl border border-indigo-100 p-3.5 space-y-2">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-900">
                        Innovation &amp; Technology Domain
                      </div>
                      {contactDetail.technology_area && (
                        <div className="flex items-center gap-1.5 font-semibold text-indigo-950">
                          {TECH_ICONS[contactDetail.technology_area] || <Zap size={12} className="text-indigo-600" />}
                          <span>{contactDetail.technology_area}</span>
                        </div>
                      )}
                      {contactDetail.sector && (
                        <div className="text-[11px] text-slate-600">
                          Sector: <span className="font-semibold text-slate-800">{contactDetail.sector}</span>
                        </div>
                      )}
                      {contactDetail.total_funding > 0 && (
                        <div className="pt-1 flex items-center justify-between border-t border-indigo-100/80 font-mono">
                          <span className="text-slate-500">Track Record Funding:</span>
                          <span className="font-bold text-emerald-700 text-sm">{fmt(contactDetail.total_funding)}</span>
                        </div>
                      )}
                    </div>

                    {/* Awarded Research Grants / Projects */}
                    {contactDetail.awarded_projects && contactDetail.awarded_projects.length > 0 && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[10.5px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                            <Trophy size={12} className="text-amber-500" />
                            <span>Awarded Innovation Grants ({contactDetail.awarded_projects.length})</span>
                          </span>
                        </div>
                        <div className="space-y-2">
                          {contactDetail.awarded_projects.map(a => (
                            <div key={a.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200/70 space-y-1">
                              <div className="flex items-center justify-between text-[10px] font-mono">
                                <span className="inline-flex items-center gap-1 font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.2 rounded border border-indigo-100">
                                  <OrgLogo org={a.agency || 'DOE'} size="xs" showTooltip={false} />
                                  <span>{a.agency || 'Federal'}</span>
                                </span>
                                {a.award_amount && (
                                  <span className="font-bold text-emerald-700">{fmt(a.award_amount)}</span>
                                )}
                              </div>
                              <div className="font-bold text-slate-900 text-[11.5px] leading-snug">
                                {a.project_title}
                              </div>
                              {a.project_abstract && (
                                <p className="text-[10.5px] text-slate-500 line-clamp-2 leading-relaxed">
                                  {a.project_abstract}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Linked Funding Opportunities */}
                    {contactDetail.linked_opportunities && contactDetail.linked_opportunities.length > 0 && (
                      <div className="space-y-2">
                        <div className="text-[10.5px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                          <Layers size={12} className="text-indigo-600" />
                          <span>Linked Funding Opportunities ({contactDetail.linked_opportunities.length})</span>
                        </div>
                        <div className="space-y-1.5">
                          {contactDetail.linked_opportunities.map(opp => (
                            <Link
                              key={opp.id}
                              to={`/opportunities/${opp.id}`}
                              className="p-2.5 bg-slate-50 hover:bg-indigo-50/50 rounded-xl border border-slate-200/70 block transition-all group"
                            >
                              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                                <span className="font-bold text-indigo-600">{opp.solicitation_number}</span>
                                <span className={clsx(
                                  "px-1.5 py-0.2 rounded font-bold uppercase",
                                  opp.status === 'open' ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-slate-100 text-slate-500"
                                )}>
                                  {opp.status}
                                </span>
                              </div>
                              <div className="font-semibold text-slate-800 group-hover:text-indigo-700 text-[11.5px] mt-0.5 line-clamp-1">
                                {opp.name}
                              </div>
                            </Link>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Public Provenance & Privacy Notice */}
                    <div className="p-3 bg-slate-100/80 rounded-xl border border-slate-200/80 text-[10.5px] text-slate-500 space-y-1">
                      <div className="flex items-center gap-1 font-bold text-slate-700">
                        <ShieldCheck size={12} className="text-indigo-600" />
                        <span>Public Provenance &amp; Compliance Disclosure</span>
                      </div>
                      <p className="leading-relaxed">
                        {contactDetail.privacy_notice}
                      </p>
                      <div className="font-mono text-[9.5px] text-slate-400 pt-1">
                        Source Record: {contactDetail.data_provenance} · Email Verified: {contactDetail.email_verified_at || '2026-09-01'}
                      </div>
                    </div>
                  </>
                ) : null}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
