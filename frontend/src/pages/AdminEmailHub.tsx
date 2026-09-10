import React, { useState, useMemo, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  api,
  AdminEmailCampaign,
  AdminEmailLog,
  ContactEmailThread,
  ContactEmailMessage,
  ContactItem,
  EmailTemplate,
  SendEmailRequestPayload
} from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  Mail, Send, Inbox, RefreshCw, CheckCircle2, AlertCircle,
  Paperclip, FileText, Users, Search, ShieldCheck,
  ChevronRight, X, Loader2, ArrowRight, Eye, Trash2, Clock,
  MessageSquare, UserCheck, Check, CornerDownRight, Tag,
  Globe, Building2, MapPin, ExternalLink, Sliders, Zap
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';

export default function AdminEmailHub() {
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Active tab: 'compose' | 'inbox' | 'campaigns' | 'diagnostics'
  const [activeTab, setActiveTab] = useState<'compose' | 'inbox' | 'campaigns' | 'diagnostics'>('compose');

  // Preloaded contact IDs if navigated from KeyContacts
  const stateContactIds: number[] = location.state?.selectedContactIds || [];
  const [recipientMode, setRecipientMode] = useState<'ids' | 'category' | 'technology' | 'state' | 'all'>(
    stateContactIds.length > 0 ? 'ids' : 'category'
  );
  const [selectedContactIds, setSelectedContactIds] = useState<number[]>(stateContactIds);
  const [filterCategory, setFilterCategory] = useState<string>('funder_officers');
  const [filterTech, setFilterTech] = useState<string>('Energy Storage & Advanced Batteries');
  const [filterState, setFilterState] = useState<string>('NY');
  const [deliverableOnly, setDeliverableOnly] = useState<boolean>(true);

  // Compose State
  const [campaignName, setCampaignName] = useState('Energy Innovation Application Invitation');
  const [selectedTemplateId, setSelectedTemplateId] = useState('application_invitation');
  const [subject, setSubject] = useState('Invitation: Access the National Energy Innovation Innovation Intelligence Terminal — {{name}}');
  const [bodyText, setBodyText] = useState('');
  const [customFooter, setCustomFooter] = useState('');
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [sendSuccessMessage, setSendSuccessMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Inbox / Thread State
  const [threadSearch, setThreadSearch] = useState('');
  const [threadStatusFilter, setThreadStatusFilter] = useState('all');
  const [selectedThreadId, setSelectedThreadId] = useState<number | null>(null);
  const [quickReplyText, setQuickReplyText] = useState('');
  const [quickReplySubject, setQuickReplySubject] = useState('');
  const [isSyncing, setIsSyncing] = useState(false);
  const [selectedCampaignId, setSelectedCampaignId] = useState<number | null>(null);

  // Query: Admin Status
  const { data: statusData, refetch: refetchStatus } = useQuery({
    queryKey: ['admin-email-status'],
    queryFn: () => api.getAdminEmailStatus(),
  });

  // Query: Templates
  const { data: templatesData } = useQuery({
    queryKey: ['admin-email-templates'],
    queryFn: () => api.getAdminEmailTemplates(),
  });

  // Query: Target Contacts preview
  const { data: targetContactsData, isLoading: contactsLoading } = useQuery({
    queryKey: ['admin-target-contacts', recipientMode, selectedContactIds, filterCategory, filterTech, filterState, deliverableOnly],
    queryFn: () => {
      if (recipientMode === 'ids') {
        if (selectedContactIds.length === 0) return { items: [], total: 0 };
        return api.getContacts({ page: 1, page_size: 100 }); // We'll filter or query
      }
      return api.getContacts({
        category: recipientMode === 'category' ? filterCategory : undefined,
        technology: recipientMode === 'technology' ? filterTech : undefined,
        state: recipientMode === 'state' ? filterState : undefined,
        email_status: deliverableOnly ? 'verified_valid' : undefined,
        page: 1,
        page_size: 50,
      });
    },
  });

  // Query: Threads
  const { data: threadsData, refetch: refetchThreads, isLoading: threadsLoading } = useQuery({
    queryKey: ['admin-email-threads', threadSearch, threadStatusFilter],
    queryFn: () => api.getAdminEmailThreads({
      search: threadSearch.trim() || undefined,
      status_filter: threadStatusFilter !== 'all' ? threadStatusFilter : undefined,
      page: 1,
      page_size: 50,
    }),
  });

  // Query: Selected Thread Detail
  const { data: threadDetail, refetch: refetchThreadDetail } = useQuery({
    queryKey: ['admin-email-thread-detail', selectedThreadId],
    queryFn: () => api.getAdminEmailThread(selectedThreadId!),
    enabled: !!selectedThreadId,
  });

  // Query: Campaigns
  const { data: campaignsData, refetch: refetchCampaigns } = useQuery({
    queryKey: ['admin-email-campaigns'],
    queryFn: () => api.getAdminEmailCampaigns({ page: 1, page_size: 20 }),
  });

  // Query: Selected Campaign Detail
  const { data: campaignDetail } = useQuery({
    queryKey: ['admin-email-campaign-detail', selectedCampaignId],
    queryFn: () => api.getAdminEmailCampaign(selectedCampaignId!),
    enabled: !!selectedCampaignId,
  });

  // Initialize body with default template if empty
  React.useEffect(() => {
    if (templatesData?.templates && !bodyText) {
      const t = templatesData.templates.find(x => x.id === selectedTemplateId) || templatesData.templates[0];
      if (t) {
        setSubject(t.default_subject);
        setBodyText(t.default_body);
      }
    }
  }, [templatesData]);

  // When template changes
  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplateId(templateId);
    const t = templatesData?.templates.find(x => x.id === templateId);
    if (t) {
      setSubject(t.default_subject);
      setBodyText(t.default_body);
      setCampaignName(t.name.replace(/^[^\w\s]+/, '').trim());
    }
  };

  // Insert Variable Tag Helper
  const insertTag = (tag: string) => {
    setBodyText(prev => prev + ' ' + tag + ' ');
  };

  // Handle File Uploads
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachedFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Sync Gmail Handler
  const handleSyncGmail = async () => {
    setIsSyncing(true);
    try {
      const res = await api.syncAdminEmail(30);
      await Promise.all([refetchThreads(), refetchStatus()]);
      alert(`Gmail Sync Complete: ${res.messages_synced} messages synchronized across ${res.threads_updated} contact threads.`);
    } catch (err: any) {
      alert(`Sync failed: ${err.message}`);
    } finally {
      setIsSyncing(false);
    }
  };

  // Send Campaign Handler
  const handleSendCampaign = async () => {
    if (!subject.trim() || !bodyText.trim()) {
      alert('Please provide both an email subject and body.');
      return;
    }

    setIsSending(true);
    try {
      const payload: SendEmailRequestPayload = {
        name: campaignName.trim() || 'Admin Outreach',
        template_type: selectedTemplateId,
        subject: subject.trim(),
        body_text: bodyText.trim(),
        footer_text: customFooter.trim() || undefined,
        recipient_mode: recipientMode === 'ids' ? 'ids' : (recipientMode === 'all' ? 'all' : 'filter'),
        contact_ids: recipientMode === 'ids' ? selectedContactIds : undefined,
        filter_criteria: {
          category: recipientMode === 'category' ? filterCategory : undefined,
          technology: recipientMode === 'technology' ? filterTech : undefined,
          sector: undefined,
          state: recipientMode === 'state' ? filterState : undefined,
          deliverable_only: deliverableOnly,
        },
      };

      const res = await api.sendAdminEmailCampaign(payload, attachedFiles);
      setSendSuccessMessage(`Campaign "${payload.name}" sent successfully to ${res.result.sent} contacts!`);
      setShowPreviewModal(false);
      setAttachedFiles([]);
      refetchCampaigns();
      refetchThreads();
      refetchStatus();
    } catch (err: any) {
      alert(`Failed to send campaign: ${err.message}`);
    } finally {
      setIsSending(false);
    }
  };

  // Quick Reply Handler
  const handleSendReply = async () => {
    if (!selectedThreadId || !quickReplyText.trim()) return;
    try {
      await api.quickReplyAdminEmailThread(selectedThreadId, {
        subject: quickReplySubject || `Re: ${threadDetail?.thread.contact_name || 'Inquiry'}`,
        body_text: quickReplyText.trim(),
      });
      setQuickReplyText('');
      refetchThreadDetail();
      refetchThreads();
      alert('Reply sent successfully!');
    } catch (err: any) {
      alert(`Reply error: ${err.message}`);
    }
  };

  // Sample Preview contact
  const sampleContact = targetContactsData?.items?.[0] || {
    id: 9999,
    name_display: 'Dr. Pamela Miller',
    name_first: 'Pamela',
    name_last: 'Miller',
    institution_name: 'State Clean Transportation & Storage Office',
    technology_area: 'Energy Storage & Advanced Batteries',
    sector: 'Electric Grid & Utility',
    title: 'Senior Program Manager',
    email: 'pamela.miller@energyagency.state.gov',
    awards_count: 4,
    total_funding: 8500000,
  };

  // Interpolated Preview Text
  const previewSubject = useMemo(() => {
    return subject
      .replace(/{{name}}|{name}/g, sampleContact.name_display)
      .replace(/{{first_name}}|{first_name}/g, sampleContact.name_first || 'Colleague')
      .replace(/{{institution}}|{institution}/g, sampleContact.institution_name || 'your institution')
      .replace(/{{technology_area}}|{technology_area}/g, sampleContact.technology_area || 'Energy Innovation')
      .replace(/{{sector}}|{sector}/g, sampleContact.sector || 'Energy');
  }, [subject, sampleContact]);

  const previewBody = useMemo(() => {
    return bodyText
      .replace(/{{name}}|{name}/g, sampleContact.name_display)
      .replace(/{{first_name}}|{first_name}/g, sampleContact.name_first || 'Colleague')
      .replace(/{{last_name}}|{last_name}/g, sampleContact.name_last || '')
      .replace(/{{institution}}|{institution}/g, sampleContact.institution_name || 'your institution')
      .replace(/{{technology_area}}|{technology_area}/g, sampleContact.technology_area || 'Energy Innovation')
      .replace(/{{sector}}|{sector}/g, sampleContact.sector || 'Energy')
      .replace(/{{title}}|{title}/g, sampleContact.title || 'Innovator')
      .replace(/{{awards_count}}|{awards_count}/g, String(sampleContact.awards_count || 3))
      .replace(/{{total_funding}}|{total_funding}/g, '$8.5M')
      .replace(/{{app_link}}|{app_link}/g, 'https://terminal.aixenergy.io');
  }, [bodyText, sampleContact]);

  // Open preview mode active: everyone can access the Admin Email Hub and outreach console
  const isPreviewMode = !isAuthenticated || (user?.role !== 'admin' && user?.email?.toLowerCase() !== 'bowens@aixenergy.io');

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-16">
      {isPreviewMode && (
        <div className="bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-purple-900/40 border border-blue-500/30 rounded-xl p-3.5 flex items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2.5 text-blue-200">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>
              <strong>Open Admin Preview Active:</strong> The Outreach Console, Gmail CRM sync, and Campaign Dispatcher are open for live evaluation.
            </span>
          </div>
          <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-mono text-[10.5px] border border-blue-400/20 shrink-0">
            System Admin Demo
          </span>
        </div>
      )}
      {/* Top Header & Telemetry Banner */}
      <div className="bg-slate-900 text-white p-6 rounded-xl border border-slate-800 shadow-md flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-1.5 min-w-0">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10.5px] font-semibold bg-slate-800 text-slate-200 border border-slate-700">
              <ShieldCheck size={12} />
              <span>Primary System Admin: Brandon Owens</span>
            </span>
            <span className="text-slate-600">|</span>
            <span className="inline-flex items-center gap-1.5 text-[11px] font-mono text-slate-300 bg-slate-800 px-2.5 py-0.5 rounded-md border border-slate-700">
              <Mail size={12} className="text-slate-400" />
              <span>bowens@aixenergy.io</span>
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-[11px] font-mono text-cyan-400 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              <span>In-Terminal CRM Mode Active</span>
            </span>
          </div>

          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            Executive Contact Intelligence &amp; CRM Hub
          </h1>
          <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
            Manage energy innovation contacts and institutions, review communication histories, draft AI correspondence, and maintain stakeholder records directly inside the terminal database ledger.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            type="button"
            disabled={isSyncing}
            onClick={handleSyncGmail}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/20 shadow-sm transition-all cursor-pointer disabled:opacity-50"
          >
            <RefreshCw size={13} className={isSyncing ? "animate-spin text-cyan-300" : "text-cyan-300"} />
            <span>{isSyncing ? 'Syncing Gmail...' : 'Sync Inbox & Sent'}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('compose')}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-extrabold shadow-md shadow-cyan-500/20 transition-all cursor-pointer"
          >
            <Send size={13} />
            <span>Compose Email</span>
          </button>
        </div>
      </div>

      {/* Metric Tiles */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5">Contacts With Email</div>
          <div className="text-xl font-bold font-mono text-slate-900">
            {statusData?.telemetry?.contacts_with_direct_email?.toLocaleString() || '2,946'}
          </div>
          <div className="text-[10.5px] text-slate-500 mt-0.5">Energy Innovation Database</div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5">Total Campaigns</div>
          <div className="text-xl font-bold font-mono text-indigo-600">
            {statusData?.telemetry?.total_campaigns_dispatched || campaignsData?.total || 0}
          </div>
          <div className="text-[10.5px] text-slate-500 mt-0.5">Dispatched Outreach</div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5">Tracked Conversations</div>
          <div className="text-xl font-bold font-mono text-slate-900">
            {statusData?.telemetry?.tracked_threads || threadsData?.total || 0}
          </div>
          <div className="text-[10.5px] text-slate-500 mt-0.5">Gmail Linked Threads</div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5">Unread Inbound Replies</div>
          <div className="text-xl font-bold font-mono text-emerald-600">
            {statusData?.telemetry?.unread_inbound_messages || 0}
          </div>
          <div className="text-[10.5px] text-emerald-600 font-semibold mt-0.5">Awaiting Review</div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs col-span-2 sm:col-span-1">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-0.5">Active Engagement</div>
          <div className="text-xl font-bold font-mono text-purple-600">
            {statusData?.telemetry?.active_engaged_conversations || 0}
          </div>
          <div className="text-[10.5px] text-purple-600 font-medium mt-0.5">Interested / In Dialogue</div>
        </div>
      </div>

      {/* Success Notification Banner */}
      {sendSuccessMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-900 rounded-2xl flex items-center justify-between text-xs font-semibold shadow-xs animate-in fade-in duration-200">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
            <span>{sendSuccessMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setSendSuccessMessage(null)}
            className="text-emerald-700 hover:text-emerald-900"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Main Tab Navigation */}
      <div className="flex items-center gap-1 border-b border-slate-200 pb-2 overflow-x-auto no-scrollbar">
        {[
          { id: 'compose', label: 'Compose & Bulk Dispatch', badge: selectedContactIds.length > 0 ? `${selectedContactIds.length} Selected` : undefined },
          { id: 'inbox', label: 'Inbox & Correspondence CRM', badge: statusData?.telemetry?.unread_inbound_messages ? `${statusData.telemetry.unread_inbound_messages} New` : undefined },
          { id: 'campaigns', label: 'Campaign History & Logs' },
          { id: 'diagnostics', label: 'Gmail Settings & Connection' },
        ].map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id as any)}
            className={clsx(
              "px-4 py-2 rounded-xl text-xs font-bold transition-all shrink-0 flex items-center gap-2 cursor-pointer",
              activeTab === tab.id
                ? "bg-slate-900 text-white shadow-2xs"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            )}
          >
            <span>{tab.label}</span>
            {tab.badge && (
              <span className={clsx(
                "text-[10px] font-mono px-1.5 py-0.2 rounded-full font-bold",
                activeTab === tab.id ? "bg-white/20 text-white" : "bg-indigo-100 text-indigo-700"
              )}>
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* ========================================================= */}
      {/* TAB 1: COMPOSE & CAMPAIGN DISPATCHER                      */}
      {/* ========================================================= */}
      {activeTab === 'compose' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: Form */}
          <div className="lg:col-span-2 space-y-4">
            {/* Template Selector Cards */}
            <div className="bg-white p-4.5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  Select Email Purpose &amp; Template
                </label>
                <span className="text-[10.5px] text-indigo-600 font-semibold font-mono">
                  Auto-interpolates recipient records
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {templatesData?.templates?.map(t => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => handleTemplateSelect(t.id)}
                    className={clsx(
                      "p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between",
                      selectedTemplateId === t.id
                        ? "bg-indigo-50/50 border-indigo-500 ring-2 ring-indigo-100 shadow-2xs"
                        : "bg-slate-50/60 hover:bg-slate-100/80 border-slate-200 text-slate-700"
                    )}
                  >
                    <div className="font-bold text-xs text-slate-900 leading-snug">
                      {t.name}
                    </div>
                    <div className="text-[11px] text-slate-500 line-clamp-1 mt-1 font-mono">
                      {t.default_subject}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Campaign Name & Subject */}
            <div className="bg-white p-4.5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="sm:col-span-1">
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                    Campaign / Activity Name
                  </label>
                  <input
                    type="text"
                    value={campaignName}
                    onChange={e => setCampaignName(e.target.value)}
                    placeholder="e.g. National Storage PI Outreach"
                    className="w-full px-3 py-2 bg-slate-50 focus:bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-2xs"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                    Subject Line
                  </label>
                  <input
                    type="text"
                    value={subject}
                    onChange={e => setSubject(e.target.value)}
                    placeholder="Subject with {{name}}, {{technology_area}}, etc."
                    className="w-full px-3 py-2 bg-slate-50 focus:bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-2xs"
                  />
                </div>
              </div>

              {/* Dynamic Variables Pill Bar */}
              <div>
                <div className="text-[10.5px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1">
                  <Tag size={11} />
                  <span>Insert Variable Tags into Subject / Body:</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    { tag: '{{name}}', desc: 'Full Name' },
                    { tag: '{{first_name}}', desc: 'First Name' },
                    { tag: '{{institution}}', desc: 'Institution / Entity' },
                    { tag: '{{technology_area}}', desc: 'Technology Domain' },
                    { tag: '{{sector}}', desc: 'Sector' },
                    { tag: '{{title}}', desc: 'Job Title' },
                    { tag: '{{awards_count}}', desc: 'Projects Count' },
                    { tag: '{{total_funding}}', desc: 'Total Grant $' },
                    { tag: '{{app_link}}', desc: 'Platform URL' },
                  ].map(chip => (
                    <button
                      key={chip.tag}
                      type="button"
                      onClick={() => insertTag(chip.tag)}
                      className="px-2 py-0.5 rounded-lg bg-slate-100 hover:bg-indigo-50 text-slate-700 hover:text-indigo-700 border border-slate-200 text-[10.5px] font-mono font-semibold transition-colors cursor-pointer"
                      title={chip.desc}
                    >
                      {chip.tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Email Body Message */}
            <div className="bg-white p-4.5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-2">
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Email Body Message (Plain Text + Markdown/HTML Supported)
              </label>
              <textarea
                rows={11}
                value={bodyText}
                onChange={e => setBodyText(e.target.value)}
                placeholder="Compose your outreach message here..."
                className="w-full px-3.5 py-2.5 bg-slate-50 focus:bg-white border border-slate-200 rounded-xl text-xs text-slate-800 leading-relaxed font-sans outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-2xs"
              />
            </div>

            {/* Email Footer / Signature */}
            <div className="bg-white p-4.5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-2">
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Email Footer &amp; Signature (Included at bottom of every message)
              </label>
              <textarea
                rows={4}
                value={customFooter || statusData?.default_footer || ''}
                onChange={e => setCustomFooter(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 focus:bg-white border border-slate-200 rounded-xl text-[11.5px] font-mono text-slate-600 leading-relaxed outline-none focus:ring-2 focus:ring-indigo-500/20 shadow-2xs"
              />
            </div>

            {/* Multi-File Attachments */}
            <div className="bg-white p-4.5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Paperclip size={13} className="text-indigo-600" />
                  <span>Attach 1 or More Files (PDF, Docs, Sheets, Presentations)</span>
                </label>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-3 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs rounded-lg transition-colors cursor-pointer"
                >
                  + Add File(s)
                </button>
                <input
                  type="file"
                  multiple
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>

              {attachedFiles.length === 0 ? (
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="p-4 border-2 border-dashed border-slate-200 hover:border-indigo-300 rounded-xl text-center text-xs text-slate-500 cursor-pointer bg-slate-50/50 hover:bg-slate-50 transition-colors"
                >
                  No attachments selected. Click here or drag files to attach.
                </div>
              ) : (
                <div className="space-y-1.5">
                  {attachedFiles.map((file, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-xs"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <FileText size={14} className="text-indigo-600 shrink-0" />
                        <span className="font-semibold text-slate-800 truncate">{file.name}</span>
                        <span className="text-[10px] font-mono text-slate-400">
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile(idx)}
                        className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right 1 Col: Audience, Filter, Preview & Dispatch */}
          <div className="space-y-4">
            {/* Target Audience Picker */}
            <div className="bg-white p-4.5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  Target Recipient List
                </label>
                <span className="text-[11px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md font-mono">
                  {targetContactsData?.total || 0} Contacts
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <label className="block text-[10.5px] font-medium text-slate-500 mb-1">Audience Scope</label>
                  <select
                    value={recipientMode}
                    onChange={e => setRecipientMode(e.target.value as any)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20 cursor-pointer"
                  >
                    {stateContactIds.length > 0 && (
                      <option value="ids">Selected Contacts from Directory ({stateContactIds.length})</option>
                    )}
                    <option value="category">Target by Role Category</option>
                    <option value="technology">Target by Technology Domain</option>
                    <option value="state">Target by State / Geography</option>
                    <option value="all">Entire National Directory (All Contacts)</option>
                  </select>
                </div>

                {recipientMode === 'category' && (
                  <div>
                    <label className="block text-[10.5px] font-medium text-slate-500 mb-1">Select Role Category</label>
                    <select
                      value={filterCategory}
                      onChange={e => setFilterCategory(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20 cursor-pointer"
                    >
                      <option value="funder_officers">Agency Program Officers (DOE, CEC, MassCEC, State Energy Offices)</option>
                      <option value="domain_experts">Technology &amp; Sector Domain Experts (PIs)</option>
                      <option value="institutional_gateways">National Lab &amp; Institutional Partner Desks</option>
                      <option value="utilities">Utility Energy Innovation POCs</option>
                    </select>
                  </div>
                )}

                {recipientMode === 'technology' && (
                  <div>
                    <label className="block text-[10.5px] font-medium text-slate-500 mb-1">Select Technology Domain</label>
                    <select
                      value={filterTech}
                      onChange={e => setFilterTech(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20 cursor-pointer"
                    >
                      <option value="Energy Storage & Advanced Batteries">Energy Storage &amp; Batteries</option>
                      <option value="Solar">Solar &amp; Photovoltaics</option>
                      <option value="Wind">Wind &amp; Offshore Wind</option>
                      <option value="Hydrogen">Hydrogen &amp; Clean Fuels</option>
                      <option value="Grid Modernization">Grid Modernization</option>
                      <option value="Carbon Capture">Carbon Capture &amp; CCUS</option>
                      <option value="Building Decarbonization">Building Decarb &amp; Heat</option>
                      <option value="Electric Mobility">Electric Mobility &amp; EVs</option>
                      <option value="Nuclear">Advanced Nuclear &amp; Fusion</option>
                    </select>
                  </div>
                )}

                {recipientMode === 'state' && (
                  <div>
                    <label className="block text-[10.5px] font-medium text-slate-500 mb-1">Select Target State</label>
                    <select
                      value={filterState}
                      onChange={e => setFilterState(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 outline-none focus:ring-2 focus:ring-indigo-500/20 cursor-pointer"
                    >
                      <option value="NY">New York (NY)</option>
                      <option value="CA">California (CA)</option>
                      <option value="MA">Massachusetts (MA)</option>
                      <option value="DC">Washington, DC</option>
                      <option value="CO">Colorado (CO)</option>
                      <option value="TX">Texas (TX)</option>
                      <option value="WA">Washington (WA)</option>
                    </select>
                  </div>
                )}

                {/* Deliverable Checkbox */}
                <label className="flex items-center gap-2 pt-1 text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={deliverableOnly}
                    onChange={e => setDeliverableOnly(e.target.checked)}
                    className="rounded text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="font-semibold text-[11.5px]">Filter only verified deliverable emails</span>
                </label>
              </div>
            </div>

            {/* Live Rendered Sample Preview Card */}
            <div className="bg-white p-4.5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Eye size={13} className="text-indigo-600" />
                  <span>Sample Contact Preview</span>
                </label>
                <span className="text-[10px] text-slate-400 font-mono">Live Interpolation</span>
              </div>

              <div className="bg-slate-50 rounded-xl border border-slate-200 p-3.5 space-y-2 text-xs">
                <div className="border-b border-slate-200 pb-2">
                  <div className="text-[10.5px] text-slate-400 font-mono">
                    <strong>To:</strong> {sampleContact.name_display} &lt;{sampleContact.email || 'contact@institution.edu'}&gt;
                  </div>
                  <div className="text-[10.5px] text-slate-400 font-mono mt-0.5">
                    <strong>From:</strong> Brandon Owens &lt;bowens@aixenergy.io&gt;
                  </div>
                  <div className="text-xs font-bold text-slate-900 mt-1">
                    {previewSubject}
                  </div>
                </div>

                <div className="text-slate-700 text-[11px] leading-relaxed whitespace-pre-wrap max-h-56 overflow-y-auto font-sans">
                  {previewBody}
                </div>

                {attachedFiles.length > 0 && (
                  <div className="pt-2 border-t border-slate-200 flex items-center gap-1.5 flex-wrap">
                    <span className="text-[10px] font-bold text-slate-500">Attachments:</span>
                    {attachedFiles.map((f, i) => (
                      <span key={i} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 inline-flex items-center gap-1">
                        <Paperclip size={10} /> {f.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Dispatch Button */}
            <div className="bg-slate-900 text-white p-4.5 rounded-xl border border-slate-800 shadow-md space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400 font-medium">Ready to Dispatch:</span>
                <span className="font-mono font-semibold text-emerald-400">
                  {targetContactsData?.total || 0} Recipients
                </span>
              </div>

              <button
                type="button"
                disabled={isSending || (targetContactsData?.total || 0) === 0}
                onClick={handleSendCampaign}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs rounded-lg shadow-sm transition-colors flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSending ? (
                  <>
                    <Loader2 size={15} className="animate-spin text-white" />
                    <span>Transmitting via Gmail SMTP...</span>
                  </>
                ) : (
                  <>
                    <Send size={15} />
                    <span>Send Email Outreach Now</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 2: INBOX & CORRESPONDENCE CRM                         */}
      {/* ========================================================= */}
      {activeTab === 'inbox' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Thread List */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden flex flex-col h-[750px]">
            {/* Search & Filter */}
            <div className="p-3.5 border-b border-slate-100 bg-slate-50 space-y-2">
              <div className="relative">
                <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search threads by contact or summary..."
                  value={threadSearch}
                  onChange={e => setThreadSearch(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs outline-none focus:ring-2 focus:ring-indigo-500/20"
                />
              </div>

              <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar text-[10.5px]">
                {[
                  { id: 'all', label: 'All' },
                  { id: 'pending_reply', label: 'Pending Reply' },
                  { id: 'replied', label: 'Replied' },
                  { id: 'interested', label: 'Interested' },
                  { id: 'joined', label: 'Joined' },
                ].map(f => (
                  <button
                    key={f.id}
                    type="button"
                    onClick={() => setThreadStatusFilter(f.id)}
                    className={clsx(
                      "px-2.5 py-1 rounded-lg font-semibold transition-colors cursor-pointer shrink-0",
                      threadStatusFilter === f.id
                        ? "bg-slate-900 text-white"
                        : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
                    )}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Threads List */}
            <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
              {threadsLoading ? (
                <div className="flex items-center justify-center h-48">
                  <Loader2 className="animate-spin text-indigo-600" size={24} />
                </div>
              ) : threadsData?.items?.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400 space-y-2">
                  <Inbox size={24} className="mx-auto text-slate-300" />
                  <p>No correspondence threads found.</p>
                  <button
                    type="button"
                    onClick={handleSyncGmail}
                    className="text-indigo-600 font-bold hover:underline"
                  >
                    Sync Gmail Inbox Now
                  </button>
                </div>
              ) : (
                threadsData?.items?.map(thread => {
                  const isSelected = selectedThreadId === thread.id;
                  const isUnread = thread.unread_inbound_count > 0;

                  return (
                    <div
                      key={thread.id}
                      onClick={() => setSelectedThreadId(thread.id)}
                      className={clsx(
                        "p-3.5 hover:bg-indigo-50/40 transition-all cursor-pointer text-xs space-y-1 relative",
                        isSelected ? "bg-indigo-50/70 border-l-4 border-indigo-600" : "",
                        isUnread ? "font-bold" : ""
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900 truncate max-w-[160px]">
                          {thread.contact_name}
                        </span>
                        <span className="text-[10px] font-mono text-slate-400">
                          {thread.last_activity_at ? new Date(thread.last_activity_at).toLocaleDateString() : ''}
                        </span>
                      </div>

                      <div className="text-[11px] text-slate-500 line-clamp-1">
                        {thread.institution_name || thread.contact_email}
                      </div>

                      {thread.conversation_summary && (
                        <p className="text-[10.5px] text-slate-600 line-clamp-2 leading-relaxed bg-slate-50/80 p-1.5 rounded-md border border-slate-100">
                          {thread.conversation_summary}
                        </p>
                      )}

                      <div className="flex items-center justify-between pt-1">
                        <span className={clsx(
                          "text-[9px] font-bold px-1.5 py-0.2 rounded border uppercase",
                          thread.status === 'interested' ? "bg-purple-50 text-purple-700 border-purple-200" :
                          thread.status === 'replied' ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                          thread.status === 'joined' ? "bg-cyan-50 text-cyan-700 border-cyan-200" :
                          "bg-slate-100 text-slate-600 border-slate-200"
                        )}>
                          {thread.status.replace('_', ' ')}
                        </span>

                        {isUnread && (
                          <span className="text-[9px] font-bold bg-indigo-600 text-white px-1.5 py-0.2 rounded-full">
                            {thread.unread_inbound_count} New
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right 2 Columns: Selected Thread Conversation Stream */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden flex flex-col h-[750px]">
            {!selectedThreadId ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-400 space-y-3">
                <MessageSquare size={36} className="text-slate-300" />
                <h3 className="text-base font-bold text-slate-800">Select a Contact Conversation Thread</h3>
                <p className="text-xs max-w-sm text-slate-500">
                  Select a contact on the left to view the full chronological email exchange with Brandon Owens and AI conversation summary.
                </p>
              </div>
            ) : (
              <>
                {/* Thread Header & AI Summary */}
                <div className="p-4 border-b border-slate-100 bg-slate-50/80 flex flex-col gap-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h2 className="text-base font-bold text-slate-900">
                        {threadDetail?.thread.contact_name}
                      </h2>
                      <div className="text-xs text-slate-500 font-mono mt-0.5">
                        {threadDetail?.thread.contact_email} · {threadDetail?.thread.institution_name}
                      </div>
                    </div>

                    {/* Status update dropdown */}
                    <select
                      value={threadDetail?.thread.status || 'pending_reply'}
                      onChange={async (e) => {
                        await api.updateAdminEmailThreadStatus(selectedThreadId!, { status: e.target.value });
                        refetchThreadDetail();
                        refetchThreads();
                      }}
                      className="px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-700 outline-none"
                    >
                      <option value="pending_reply">Pending Reply</option>
                      <option value="replied">Replied</option>
                      <option value="interested">Interested / Warm</option>
                      <option value="meeting_scheduled">Meeting Scheduled</option>
                      <option value="joined">Joined Platform</option>
                      <option value="opted_out">Opted Out</option>
                    </select>
                  </div>

                  {/* Executive Conversation Summary Box */}
                  {threadDetail?.thread.conversation_summary && (
                    <div className="p-3 bg-indigo-50/60 rounded-xl border border-indigo-100 text-xs space-y-1">
                      <div className="flex items-center gap-1.5 font-bold text-indigo-900 text-[10.5px] uppercase tracking-wider">
                        <FileText size={12} className="text-indigo-600" />
                        <span>Executive Conversation Summary</span>
                      </div>
                      <p className="text-slate-700 leading-relaxed text-[11.5px]">
                        {threadDetail.thread.conversation_summary}
                      </p>
                      {threadDetail.thread.next_action && (
                        <div className="text-[10.5px] text-indigo-800 font-semibold pt-1">
                          Suggested Next Step: {threadDetail.thread.next_action}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Message Stream */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/30">
                  {threadDetail?.messages?.map(msg => {
                    const isOutbound = msg.direction === 'outbound';

                    return (
                      <div
                        key={msg.id}
                        className={clsx(
                          "flex flex-col max-w-xl text-xs space-y-1",
                          isOutbound ? "ml-auto items-end" : "mr-auto items-start"
                        )}
                      >
                        <div className="flex items-center gap-1.5 text-[10.5px] text-slate-400 font-mono">
                          <span>{isOutbound ? 'Brandon Owens (Admin)' : msg.from_name || threadDetail.thread.contact_name}</span>
                          <span>·</span>
                          <span>{msg.sent_at ? new Date(msg.sent_at).toLocaleString() : ''}</span>
                        </div>

                        <div className={clsx(
                          "p-3.5 rounded-2xl shadow-2xs space-y-1.5 text-left",
                          isOutbound
                            ? "bg-slate-900 text-white rounded-br-xs"
                            : "bg-white text-slate-800 border border-slate-200 rounded-bl-xs"
                        )}>
                          <div className="font-bold text-[11.5px] border-b border-white/10 pb-1">
                            {msg.subject}
                          </div>
                          <div className="whitespace-pre-wrap leading-relaxed text-[11px] font-sans">
                            {msg.body_text}
                          </div>

                          {msg.has_attachments && msg.attachments?.length > 0 && (
                            <div className="pt-1.5 flex items-center gap-1.5 flex-wrap border-t border-white/10">
                              <span className="text-[9.5px] font-bold text-slate-400">Attachments:</span>
                              {msg.attachments.map((a: any, i) => (
                                <span key={i} className="text-[9.5px] font-mono px-1.5 py-0.2 rounded bg-white/20 text-white inline-flex items-center gap-1">
                                  <Paperclip size={9} /> {typeof a === 'string' ? a : a.filename}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Quick Reply Composer at bottom */}
                <div className="p-3.5 border-t border-slate-100 bg-white space-y-2">
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="Subject (e.g. Re: Project Collaboration)"
                      value={quickReplySubject}
                      onChange={e => setQuickReplySubject(e.target.value)}
                      className="flex-1 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-semibold"
                    />
                  </div>
                  <div className="flex items-end gap-2">
                    <textarea
                      rows={2}
                      placeholder={`Reply directly to ${threadDetail?.thread.contact_name}...`}
                      value={quickReplyText}
                      onChange={e => setQuickReplyText(e.target.value)}
                      className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs outline-none focus:ring-2 focus:ring-indigo-500/20"
                    />
                    <button
                      type="button"
                      onClick={handleSendReply}
                      disabled={!quickReplyText.trim()}
                      className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-colors disabled:opacity-40 flex items-center gap-1.5 cursor-pointer"
                    >
                      <Send size={12} />
                      <span>Reply</span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 3: CAMPAIGN HISTORY & AUDIT LOGS                      */}
      {/* ========================================================= */}
      {activeTab === 'campaigns' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden space-y-4 p-5">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">Historical Email Campaigns &amp; Delivery Audits</h3>
            <span className="text-xs text-slate-500 font-mono">{campaignsData?.total || 0} Campaigns Logged</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="py-3 px-4">Campaign Name &amp; Subject</th>
                  <th className="py-3 px-4">Template</th>
                  <th className="py-3 px-4 text-center">Recipients</th>
                  <th className="py-3 px-4 text-center">Delivered</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4">Dispatched At</th>
                  <th className="py-3 px-4 text-right">Audit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {campaignsData?.items?.map(c => (
                  <tr key={c.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-900">{c.name}</div>
                      <div className="text-[11px] text-slate-500 font-mono truncate max-w-sm">{c.subject}</div>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-600">{c.template_type}</td>
                    <td className="py-3 px-4 text-center font-mono font-bold text-slate-800">{c.total_recipients}</td>
                    <td className="py-3 px-4 text-center font-mono font-bold text-emerald-600">{c.sent_count}</td>
                    <td className="py-3 px-4 text-center">
                      <span className={clsx(
                        "text-[9.5px] font-bold px-2 py-0.5 rounded-full border uppercase",
                        c.status === 'completed' ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                        c.status === 'partial_failure' ? "bg-amber-50 text-amber-700 border-amber-200" :
                        "bg-slate-100 text-slate-700 border-slate-200"
                      )}>
                        {c.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                      {c.started_at ? new Date(c.started_at).toLocaleString() : c.created_at}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        type="button"
                        onClick={() => setSelectedCampaignId(c.id)}
                        className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-semibold text-[11px] transition-colors"
                      >
                        View Logs
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Campaign Log Modal */}
          {selectedCampaignId && campaignDetail && (
            <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
              <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[85vh]">
                <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">{campaignDetail.campaign.name}</h3>
                    <div className="text-xs text-slate-500 font-mono mt-0.5">
                      {campaignDetail.campaign.sent_count} sent / {campaignDetail.campaign.failed_count} failed
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedCampaignId(null)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600"
                  >
                    <X size={16} />
                  </button>
                </div>

                <div className="p-6 overflow-y-auto flex-1">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 border-b border-slate-200 text-[10.5px] font-bold uppercase text-slate-500">
                      <tr>
                        <th className="py-2 px-3">Recipient</th>
                        <th className="py-2 px-3">Email Address</th>
                        <th className="py-2 px-3 text-center">Status</th>
                        <th className="py-2 px-3">Sent Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                      {campaignDetail.logs?.map(log => (
                        <tr key={log.id}>
                          <td className="py-2 px-3 font-sans font-semibold text-slate-900">{log.recipient_name}</td>
                          <td className="py-2 px-3 text-slate-600">{log.recipient_email}</td>
                          <td className="py-2 px-3 text-center">
                            <span className={clsx(
                              "text-[9px] font-bold px-1.5 py-0.2 rounded uppercase",
                              log.status === 'sent' ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
                            )}>
                              {log.status}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-slate-400">{log.sent_at ? new Date(log.sent_at).toLocaleTimeString() : 'N/A'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 4: SETTINGS & DIAGNOSTICS                             */}
      {/* ========================================================= */}
      {activeTab === 'diagnostics' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sliders size={18} className="text-indigo-600" />
              <span>Gmail Server Configuration</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="font-bold text-slate-700">Primary Admin Account</span>
                <span className="font-mono text-indigo-700 font-semibold">{statusData?.admin_email}</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="font-bold text-slate-700">SMTP Host (Outbound)</span>
                <span className="font-mono text-slate-700">{statusData?.smtp_host}:{statusData?.smtp_port} (STARTTLS)</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="font-bold text-slate-700">IMAP Host (Inbound/Sent Sync)</span>
                <span className="font-mono text-slate-700">{statusData?.imap_host}:{statusData?.imap_port} (SSL)</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="font-bold text-slate-700">Sender Display Name</span>
                <span className="font-semibold text-slate-800">{statusData?.display_name}</span>
              </div>
            </div>

            <button
              type="button"
              onClick={async () => {
                const res = await api.testAdminEmailConnection();
                alert(`SMTP Handshake: ${res.smtp.success ? 'PASS' : 'FAIL'} (${res.smtp.message})\nIMAP Handshake: ${res.imap.success ? 'PASS' : 'FAIL'} (${res.imap.message})`);
              }}
              className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer"
            >
              Test Live Connection Handshake
            </button>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck size={18} className="text-emerald-600" />
              <span>Security &amp; Deliverability Guidelines</span>
            </h3>

            <div className="text-xs text-slate-600 space-y-2.5 leading-relaxed">
              <p>
                • <strong>Public Domain Compliance:</strong> All outreach is mapped strictly to public research PIs, state program officers, and official institutional gateway contacts indexed from government grant registries.
              </p>
              <p>
                • <strong>Google App Password:</strong> If 2-Factor Authentication is enabled on <code>bowens@aixenergy.io</code>, please ensure a 16-character Google App Password is configured.
              </p>
              <p>
                • <strong>Automated Dialogue Sync:</strong> Background sync periodically reads sent items and inbound replies from Gmail to automatically maintain the AI dialogue summary and response status for each contact.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
