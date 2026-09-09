export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'https://energy-innovation-api.onrender.com').replace(/\/+$/, '');

export interface DocumentMetadata {
  filename: string;
  doc_type: string;
  file_size: number;
  word_count?: number;
  page_count?: number;
  slide_count?: number;
  sheet_count?: number;
  status: 'success' | 'error';
}

export interface ExtractedProjectProfile {
  project_title: string;
  summary: string;
  technology_areas: string[];
  activity_types: string[];
  sectors: string[];
  fuel_types: string[];
  estimated_trl: number;
  trl_rationale: string;
  applicant_type: string;
  estimated_cost: number;
  cost_rationale: string;
  location: string;
  timeline: string;
  partners: string[];
  key_innovations: string[];
  quantitative_targets: string[];
  suggested_agencies: string[];
  uncertainties: string[];
  engine_used?: string;
  is_live_llm?: boolean;
}

export interface DocumentExtractionResponse {
  success: boolean;
  extracted_profile: ExtractedProjectProfile;
  documents: DocumentMetadata[];
  total_files: number;
  total_words: number;
  total_bytes: number;
  engine_used: string;
  is_live_llm: boolean;
}

export interface TestConnectionResponse {
  connected: boolean;
  provider: string;
  model?: string;
  message: string;
  available_models?: string[];
  masked_key?: string;
}

export interface LlmStatusResponse {
  openai: {
    configured: boolean;
    masked_key: string | null;
    default_model: string;
  };
  gemini: {
    configured: boolean;
    masked_key: string | null;
    default_model: string;
  };
  anthropic: {
    configured: boolean;
    masked_key: string | null;
    default_model: string;
  };
  active_provider: string;
}

export interface AnalysisInput {
  description: string;
  location?: string;
  applicantType?: string;
  estimatedCost?: string;
  trl?: number;
  timeline?: string;
  partners?: string;
  technologyAreas?: string[];
  activityTypes?: string[];
  sectors?: string[];
  fuelTypes?: string[];
  agencies?: string[];
  extractedProfile?: ExtractedProjectProfile;
}

export interface MatchResult {
  matches: Array<{
    id: string;
    solicitationNumber: string;
    name: string;
    status: string;
    fitLevel: 'Strong' | 'Conditional' | 'Component' | 'Ecosystem' | 'Watchlist';
    potentialAward: string;
    deadline: string;
    applicableComponent: string;
    whyItFits: string;
    eligibilityConditions: Array<{ condition: string; status: 'PASS' | 'FAIL' | 'UNKNOWN' }>;
    blockers: string[];
    nextAction: string;
    sourceEvidence: string;
  }>;
  summary: string;
  fundingArchitecture: {
    nodes: Array<{ id: string; label: string; type: string }>;
    edges: Array<{ source: string; target: string; label?: string }>;
  };
  projectProfile: {
    inferredType: string;
    confidence: number;
    uncertainties: string[];
  };
}

export interface WinRateAnalytics {
  win_probability_pct: number;
  win_tier: string;
  tier_color: 'emerald' | 'amber' | 'rose' | string;
  badge_text: string;
  estimated_field_size: string;
  historical_selection_rate: string;
  precedent_score_pct: number;
  precedent_rating: string;
  tech_precedent_awards_count: number;
  scale_score_pct: number;
  scale_rating: string;
  cost_share_score_pct: number;
  cost_share_notes: string;
  key_advantages: string[];
  risk_factors: string[];
  recommended_strategy: string;
}

export interface TeamingPartner {
  id: string;
  name: string;
  type: string;
  role_title: string;
  role_description: string;
  location: string;
  pi_name: string;
  pi_email: string;
  precedent_award_count: number;
  historical_funding_won: number;
  verified_contact: boolean;
  match_confidence: number;
}

export interface TeamingStack {
  opportunity_id?: number | string | null;
  opportunity_name: string;
  agency: string;
  target_technology: string;
  consortia_composition: {
    total_members: number;
    academic_lead?: string | null;
    utility_lead?: string | null;
    lab_lead?: string | null;
    industry_lead?: string | null;
  };
  recommended_partners: TeamingPartner[];
  outreach_templates: Record<string, {
    to_email: string;
    to_name: string;
    subject: string;
    body: string;
  }>;
  consortia_readiness_score: number;
  consortia_rationale: string;
}

export interface CapitalStackLayer {
  tier: number;
  name: string;
  source: string;
  amount: number;
  percentage: number;
  cost_of_capital_pct: number;
  dilution_type: string;
  color: 'emerald' | 'cyan' | 'indigo' | 'amber' | string;
  badge: string;
}

export interface CapitalStackSummary {
  total_non_dilutive_capital: number;
  total_non_dilutive_pct: number;
  net_sponsor_equity_required: number;
  net_sponsor_equity_pct: number;
  blended_wacc_pct: number;
  blended_wacc_after_tax_pct?: number;
  unsubsidized_wacc_pct: number;
  wacc_savings_bps: number;
  annual_carrying_cost_savings?: number;
  ten_year_cumulative_savings?: number;
  estimated_payback_years: number;
  standard_payback_years: number;
}

export interface CapitalStack {
  project_cost: number;
  is_tax_credit_eligible?: boolean;
  eligibility_audit?: {
    is_tax_credit_eligible: boolean;
    statutory_classification: string;
    statutory_code: string;
    eligibility_notes: string;
    direct_pay_eligible: boolean;
    applicant_tax_status: string;
  };
  summary: CapitalStackSummary;
  tax_credit_config: {
    statutory_name: string;
    statutory_code?: string;
    is_eligible?: boolean;
    base_rate_pct: number;
    energy_community_bonus_pct: number;
    domestic_content_bonus_pct: number;
    effective_itc_rate_pct: number;
    monetization_factor_pct?: number;
    monetization_mode: string;
    prevailing_wage_active: boolean;
    energy_community_active: boolean;
    domestic_content_active: boolean;
  };
  waterfall_layers: CapitalStackLayer[];
  financial_insights: string[];
  sensitivities?: Array<{
    grant_rate_pct: number;
    gross_tax_rate_pct: number;
    net_non_dilutive_pct: number;
    sponsor_equity_pct: number;
    resulting_wacc_pct: number;
    wacc_savings_bps: number;
  }>;
}

export interface SayYesDecisionMaker {
  id?: number | null;
  name: string;
  title: string;
  department: string;
  role_type: string;
  email: string;
  email_status: string;
  confidence: number;
}

export interface SayYesOrganization {
  rank: number;
  organization_name: string;
  organization_code: string;
  category: 'utility' | 'state' | 'federal' | 'foundation' | string;
  category_label: string;
  state: string;
  geographic_nexus: string;
  territory_desc: string;
  map_coordinates: { lat: number; lng: number };
  say_yes_score: number;
  say_yes_tier: 'Highest Probability' | 'Strong Alignment' | 'Targeted Outreach' | string;
  tier_badge_color: 'emerald' | 'cyan' | 'indigo' | string;
  primary_pain_points: string[];
  why_they_say_yes: string;
  decision_maker_contacts: SayYesDecisionMaker[];
  active_opportunities_count: number;
  active_opportunities: Array<{
    id: number;
    solicitation_number: string;
    name: string;
    total_funding?: number;
    max_per_award?: number;
    status: string;
  }>;
}

export interface GroupedOpportunityOrg {
  organization_code: string;
  organization_name: string;
  category: 'utility' | 'state' | 'federal' | 'foundation' | string;
  category_label: string;
  state: string;
  say_yes_score: number;
  say_yes_tier: string;
  tier_badge_color: string;
  geographic_nexus: string;
  territory_desc?: string;
  primary_pain_points: string[];
  why_they_say_yes: string;
  decision_maker_contacts?: SayYesDecisionMaker[];
  total_opportunities_count: number;
  top_opportunities: any[];
  all_opportunities?: any[];
}

export interface StatutoryDeficit {
  id: string;
  title: string;
  short_title: string;
  jurisdiction: string;
  commission: string;
  docket_number: string;
  unit: string;
  target_year: number;
  years_remaining: number;
  statutory_target: number;
  tracked_progress: number;
  compliance_deficit: number;
  progress_pct: number;
  estimated_capital_required_usd: number;
  capital_deficit_usd: number;
  tracked_awards_count: number;
  tracked_awarded_usd: number;
  urgency: string;
  urgency_color: 'rose' | 'amber' | 'emerald' | string;
  pipeline_technologies: string[];
  strategic_implication: string;
  official_url: string;
  topic_category: string;
}

export interface BankabilityPillar {
  pillar_number: number;
  name: string;
  weight_pct: number;
  score: number;
  rating: string;
  metric: string;
}

export interface CausalLineageNode {
  step: number;
  stage: string;
  entity: string;
  mechanism: string;
  output: string;
  icon: string;
  completed: boolean;
}

export interface TechnologyBankabilityRating {
  technology_id: string;
  technology_name: string;
  bankability_score: number;
  rating_grade: 'AAA' | 'AA' | 'A' | 'BBB' | 'BB' | string;
  grade_label: string;
  grade_color: 'emerald' | 'teal' | 'blue' | 'amber' | 'rose' | string;
  empirical_leverage_ratio: string;
  tracked_award_precedents: number;
  tracked_public_funding_usd: number;
  agency_diversity_count: number;
  current_trl: number;
  target_trl: number;
  pillars: BankabilityPillar[];
  causal_lineage: CausalLineageNode[];
  executive_diligence_brief: string;
}

export interface FeedTelemetryItem {
  code: string;
  name: string;
  tier: string;
  records_tracked: number;
  status: string;
  latency_ms: number;
  integrity_pct: number;
  last_synced: string;
}

export interface FeedHealthSummary {
  telemetry_timestamp: string;
  overall_health: string;
  system_status: string;
  url_liveness_rate_pct: number;
  total_opportunities_indexed: number;
  active_solicitations: number;
  monitored_state_agencies: number;
  monitored_federal_agencies: number;
  feed_telemetry: FeedTelemetryItem[];
  recent_ingestion_runs: Array<{
    id: number;
    source_name: string;
    started_at: string;
    completed_at?: string | null;
    status: string;
    records_added: number;
    records_updated: number;
    errors: number;
  }>;
}

export interface Opportunity {
  id: string;
  solicitationNumber: string;
  name: string;
  type: string;
  status: 'Open' | 'Closed' | 'Draft';
  nextDeadline?: string;
  funding?: string;
  enrollmentType?: string;
  technologyArea?: string;
  serviceTerritory?: string;
  utilityProgramType?: string;
  procurementPortalUrl?: string;
  vendorRegistrationRequired?: boolean;
  parentUtility?: string;
  winning_proposals_count?: number;
  has_winning_proposals?: boolean;
  artifacts_count?: number;
  has_artifacts?: boolean;
  bundle_download_url?: string;
  days_since_release?: number | null;
  release_date?: string | null;
  is_new?: boolean;
}

export interface OpportunityDetail extends Opportunity {
  overview: string;
  rounds: Array<{ name: string; deadline: string; status: string }>;
  eligibility: string;
  documents: Array<{ title: string; url: string }>;
  contacts: Array<{ name: string; email: string; phone?: string }>;
  categories: string[];
  changes: Array<{ date: string; description: string }>;
  conflicts: string[];
  lastVerified: string;
}

/**
 * Automatically identifies whether an Opportunity was created or released in the last 30 days.
 */
export function isOpportunityNew(opp: any): boolean {
  if (!opp) return false;
  if (opp.is_new === true) return true;
  if (typeof opp.days_since_release === 'number' && opp.days_since_release >= 0 && opp.days_since_release <= 30) {
    return true;
  }
  const now = Date.now();
  const thirtyDaysMs = 30 * 24 * 60 * 60 * 1000;
  const candidateDates = [
    opp.release_date,
    opp.open_date,
    opp.created_at,
    opp.posted_date,
    opp.first_seen_at,
    opp.first_seen,
    opp.date_opened,
    opp.last_modified
  ];
  for (const d of candidateDates) {
    if (!d) continue;
    try {
      const parsed = new Date(d).getTime();
      if (!isNaN(parsed)) {
        const diff = now - parsed;
        if (diff >= 0 && diff <= thirtyDaysMs) {
          return true;
        }
      }
    } catch {}
  }
  return false;
}

export interface Update {
  id: string;
  type: 'change' | 'new' | 'deadline' | 'correction';
  entityName: string;
  fieldChanged: string;
  oldValue?: string;
  newValue?: string;
  timestamp: string;
}

export interface Program {
  id: string;
  name: string;
  description: string;
  targetStage: string;
  type: 'Innovation R&D' | 'Commercialization' | 'Technical Assistance' | 'Workforce';
  url: string;
}

export interface SystemSource {
  id: string;
  name: string;
  url: string;
  lastIngested: string;
  status: 'healthy' | 'failing';
}

export interface SystemAudit {
  issues: Array<{
    id: string;
    severity: 'high' | 'medium' | 'low';
    description: string;
    sourceId: string;
  }>;
  runHistory: Array<{
    timestamp: string;
    status: string;
    itemsProcessed: number;
  }>;
}

export interface SystemStats {
  opportunityCount: number;
  projectCount: number;
  lastUpdated: string;
}

export interface PaginatedOpportunities {
  items: Opportunity[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ContactItem {
  id: number;
  name_display: string;
  name_first?: string | null;
  name_last?: string | null;
  title?: string | null;
  department?: string | null;
  role_type?: 'program_officer' | 'pi' | 'institutional_gateway' | 'utility_lead' | 'technical_expert' | string;
  email?: string | null;
  email_status?: 'verified_valid' | 'syntax_valid' | 'gateway_required' | 'invalid_format' | string;
  email_deliverable?: boolean;
  email_score?: number;
  email_domain?: string | null;
  email_verified_at?: string | null;
  phone?: string | null;
  institution_name?: string | null;
  organization_id?: number | null;
  organization_name?: string | null;
  technology_area?: string | null;
  sector?: string | null;
  fuel_type?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  state?: string | null;
  postal_code?: string | null;
  country?: string;
  formatted_address?: string | null;
  address_verification_status?: string;
  awards_count: number;
  total_funding: number;
  entity_contact_url?: string | null;
  verification_status?: string;
  data_provenance?: string;
  confidence?: number;
  source_url?: string | null;
  is_current?: boolean;
}

export interface ContactStats {
  total_contacts: number;
  total_with_email: number;
  verified_valid_emails: number;
  syntax_valid_emails: number;
  gateway_required_count: number;
  email_deliverability_rate: string;
  program_officers_count: number;
  domain_experts_count: number;
  institutional_gateways_count: number;
  utility_leads_count: number;
  technologies: Array<{ name: string; count: number }>;
  sectors: Array<{ name: string; count: number }>;
  top_institutions: Array<{ name: string; count: number }>;
  privacy_compliance: string;
}

export interface ContactDetail extends ContactItem {
  organization?: {
    id: number;
    name: string;
    org_type?: string;
    website?: string;
    domain?: string;
    city?: string;
    state?: string;
    description?: string;
    logo_url?: string;
  } | null;
  linked_opportunities: Array<{
    id: number;
    solicitation_number: string;
    name: string;
    status: string;
    agency: string;
    total_funding?: number;
    close_date?: string;
    role?: string;
  }>;
  awarded_projects: Array<{
    id: number;
    project_title: string;
    project_abstract?: string;
    award_amount?: number;
    agency: string;
    year?: number;
    recipient_name?: string;
    recipient_state?: string;
    source_url?: string;
  }>;
  privacy_notice: string;
}

export interface AwardMapMarker {
  id: number;
  opportunity_id?: number | null;
  name: string;
  type?: string | null;
  city?: string | null;
  state?: string | null;
  lat: number;
  lng: number;
  amount: number;
  nyserda_amount?: number;
  awards_count?: number;
  agency: string;
  agencies?: string[];
  year?: number | null;
  title?: string | null;
  pi?: string | null;
  award_type?: string | null;
  award_phase?: string | null;
  program?: string | null;
  website?: string | null;
  employees?: number | string | null;
  abstract_snippet?: string | null;
  description?: string | null;
  primary_technology?: string | null;
  primary_sector?: string | null;
  primary_fuel?: string | null;
  stage?: string | null;
  is_ny_based?: boolean;
  is_recipient?: boolean;
  technologies: string[];
  sectors?: string[];
  fuels?: string[];
  stages?: string[];
  artifacts_count?: number;
  has_artifacts?: boolean;
  has_winning_proposal?: boolean;
  proposal_id?: string;
}


export interface AwardRecipient {
  id: number;
  name: string;
  normalized_name: string;
  type: string;
  description: string;
  primary_technology: string;
  technology_tags: string[];
  sector: string;
  commercialization_stage: string;
  city: string;
  state: string;
  country: string;
  lat?: number | null;
  lng?: number | null;
  is_ny_based: boolean;
  website_url: string;
  founded_year?: number | null;
  employee_range: string;
  leadership: Array<{ name: string; role: string }>;
  award_count: number;
  total_funding: number;
  state_funding?: number;
  state_award_count?: number;
  nyserda_funding: number;
  nyserda_award_count: number;
  federal_funding: number;
  federal_award_count: number;
  agencies: string[];
  first_year?: number | null;
  last_year?: number | null;
}

export interface AwardMapSummary {
  total_funding: number;
  marker_count: number;
  total_matches: number;
  unique_recipients: number;
  states_covered: number;
  by_agency: Array<{ agency: string; count: number; total_funding: number }>;
  top_states: Array<{ state: string; count: number; total_funding: number }>;
  top_hubs: Array<{ city: string; state: string; count: number; total_funding: number; lat: number; lng: number }>;
}

export interface AwardMapResponse {
  markers: AwardMapMarker[];
  total: number;
  summary: AwardMapSummary;
}

export interface AwardMapFilters {
  agencies: Array<{ agency: string; count: number; total_funding: number }>;
  technologies: Array<{ name: string; count: number }>;
  sectors: Array<{ name: string; count: number }>;
  fuels: Array<{ name: string; count: number }>;
  stages: Array<{ name: string; count: number }>;
  recipient_types: Array<{ type: string; count: number; total_funding: number }>;
  award_types: Array<{ type: string; count: number }>;
  states: Array<{ code: string; name: string; count: number; total_funding: number }>;
  year_range: { min: number; max: number };
  amount_range: { min: number; max: number };
}

export interface AwardMapStateSummary {
  state: string;
  state_name: string;
  award_count: number;
  total_funding: number;
  recipient_count: number;
  lat: number;
  lng: number;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  organization_name: string;
  role: string;
  tier: string;
  tier_status: string;
  tier_expires_at: string | null;
  is_active: boolean;
  is_verified: boolean;
  public_benefit_access: boolean;
  created_at: string | null;
  last_login_at: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface TierInfo {
  id: string;
  name: string;
  tagline: string;
  price: string;
  is_current_default: boolean;
  badge: string;
  features: string[];
}

export interface MembershipManifest {
  public_benefit_mode: boolean;
  active_message: string;
  tiers: TierInfo[];
}

export function getAuthHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
  const token = localStorage.getItem('auth_token');
  const creatorToken = localStorage.getItem('creator_token');
  const includeNyserda = localStorage.getItem('energy_terminal_include_nyserda');
  const headers: Record<string, string> = { ...extraHeaders };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (creatorToken) {
    headers['X-Creator-Token'] = creatorToken;
  }
  if (includeNyserda !== null) {
    headers['X-Include-NYSERDA'] = includeNyserda;
  }
  return headers;
}

export const api = {
  analyzeProject: async (input: AnalysisInput): Promise<MatchResult> => {
    // Map frontend field names to backend API contract
    const payload: Record<string, unknown> = {
      text: input.description || '',
    };
    if (input.location) payload.location = input.location;
    if (input.applicantType) payload.applicant_type = input.applicantType;
    if (input.estimatedCost) {
      const cleanNum = parseFloat(String(input.estimatedCost).replace(/[^0-9.]/g, ''));
      if (!isNaN(cleanNum) && cleanNum > 0) {
        payload.cost = cleanNum;
      }
    }
    if (input.trl !== undefined) payload.trl = input.trl;
    if (input.timeline) payload.timeline = input.timeline;
    if (input.partners) payload.partners = input.partners;
    if (input.technologyAreas?.length) payload.technology_areas = input.technologyAreas;
    if (input.activityTypes?.length) payload.activity_types = input.activityTypes;
    if (input.sectors?.length) payload.sectors = input.sectors;
    if (input.fuelTypes?.length) payload.fuel_types = input.fuelTypes;
    if (input.agencies?.length) payload.agencies = input.agencies;

    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const errorBody = await res.text().catch(() => '');
      throw new Error(`Failed to analyze project: ${res.status} ${errorBody}`);
    }
    return res.json();
  },

  uploadAndExtractProjectDocs: async (
    files: File[],
    options?: { apiKey?: string; model?: string; provider?: string }
  ): Promise<DocumentExtractionResponse> => {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    if (options?.apiKey) formData.append('api_key', options.apiKey);
    if (options?.model) formData.append('model', options.model);
    if (options?.provider) formData.append('provider', options.provider);

    const res = await fetch('/api/analyze/upload-docs', {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.text().catch(() => '');
      throw new Error(`Document analysis failed: ${res.status} ${err}`);
    }
    return res.json();
  },

  extractTextProfile: async (
    text: string,
    options?: { apiKey?: string; model?: string; provider?: string }
  ): Promise<DocumentExtractionResponse> => {
    const res = await fetch('/api/analyze/extract-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        api_key: options?.apiKey,
        model: options?.model,
        provider: options?.provider || 'openai',
      }),
    });
    if (!res.ok) {
      const err = await res.text().catch(() => '');
      throw new Error(`Text characterization failed: ${res.status} ${err}`);
    }
    return res.json();
  },

  getSayYesMatrix: async (payload: {
    project_title?: string;
    summary?: string;
    technology_areas?: string[];
    location?: string;
    applicant_type?: string;
    project_cost?: number;
    agencies?: string[];
    limit?: number;
  }): Promise<{ success: boolean; total_ranked: number; say_yes_matrix: SayYesOrganization[] }> => {
    const res = await fetch('/api/analyze/say-yes-matrix', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.text().catch(() => '');
      throw new Error(`Failed to fetch Say Yes matrix: ${res.status} ${err}`);
    }
    return res.json();
  },

  uploadAndAnalyzeProject: async (
    files: File[],
    agencies?: string[],
    options?: { apiKey?: string; model?: string; provider?: string }
  ): Promise<any> => {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    if (agencies?.length) formData.append('agencies', JSON.stringify(agencies));
    if (options?.apiKey) formData.append('api_key', options.apiKey);
    if (options?.model) formData.append('model', options.model);
    if (options?.provider) formData.append('provider', options.provider);

    const res = await fetch('/api/analyze/upload-and-match', {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.text().catch(() => '');
      throw new Error(`Project diligence matching failed: ${res.status} ${err}`);
    }
    return res.json();
  },

  getLlmStatus: async (): Promise<LlmStatusResponse> => {
    const res = await fetch('/api/analyze/llm-status');
    if (!res.ok) throw new Error('Failed to fetch LLM configuration status');
    return res.json();
  },

  testLlmConnection: async (params?: {
    provider?: string;
    apiKey?: string;
    model?: string;
    saveKey?: boolean;
  }): Promise<TestConnectionResponse> => {
    const res = await fetch('/api/analyze/test-connection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider: params?.provider || 'openai',
        api_key: params?.apiKey,
        model: params?.model || 'gpt-4o',
        save_key: params?.saveKey ?? true,
      }),
    });
    if (!res.ok) {
      const err = await res.text().catch(() => '');
      throw new Error(`Failed to test connection: ${res.status} ${err}`);
    }
    return res.json();
  },

  getOpportunities: async (params?: Record<string, any>): Promise<PaginatedOpportunities> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          searchParams.append(key, value.toString());
        }
      });
    }
    const search = searchParams.toString();
    const res = await fetch(`/api/opportunities${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch opportunities');
    return res.json();
  },

  getOpportunity: async (id: string): Promise<OpportunityDetail> => {
    const res = await fetch(`/api/opportunities/${id}`);
    if (!res.ok) throw new Error('Failed to fetch opportunity');
    return res.json();
  },

  getUpdates: async (params?: Record<string, string>): Promise<Update[]> => {
    const search = params ? new URLSearchParams(params).toString() : '';
    const res = await fetch(`/api/updates${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch updates');
    return res.json();
  },

  getPrograms: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) searchParams.append(key, value.toString());
      });
    }
    const search = searchParams.toString();
    const res = await fetch(`/api/programs${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch programs');
    return res.json();
  },
  getProgramOpportunities: async (programId: number, organization?: string): Promise<any[]> => {
    const params = new URLSearchParams();
    if (organization) params.append('organization', organization);
    const search = params.toString();
    const res = await fetch(`/api/programs/${programId}/opportunities${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch program opportunities');
    return res.json();
  },

  getSystemSources: async (): Promise<SystemSource[]> => {
    const res = await fetch('/api/system/sources');
    if (!res.ok) throw new Error('Failed to fetch sources');
    return res.json();
  },

  getSystemAudit: async (): Promise<SystemAudit> => {
    const res = await fetch('/api/system/audit');
    if (!res.ok) throw new Error('Failed to fetch audit');
    return res.json();
  },

  getSystemStats: async (): Promise<SystemStats> => {
    const res = await fetch('/api/system/stats');
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  },

  getFeedHealthStatus: async (): Promise<FeedHealthSummary> => {
    const res = await fetch('/api/system/feed-health');
    if (!res.ok) throw new Error('Failed to fetch feed health');
    return res.json();
  },

  runHealthCheck: async (sampleSize: number = 25): Promise<any> => {
    const res = await fetch(`/api/system/run-health-check?sample_size=${sampleSize}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to execute health check');
    return res.json();
  },

  getWinRateBenchmark: async (oppId: string | number): Promise<WinRateAnalytics> => {
    const res = await fetch(`/api/opportunities/${oppId}/win-rate-benchmark`);
    if (!res.ok) throw new Error('Failed to fetch win rate benchmark');
    return res.json();
  },

  getTeamingRecommendations: async (params?: { opportunity_id?: string | number; technology_area?: string; state_scope?: string; lead_company_name?: string }): Promise<TeamingStack> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString());
      });
    }
    const search = searchParams.toString();
    const res = await fetch(`/api/network/teaming-recommendations${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch teaming recommendations');
    return res.json();
  },

  calculateCapitalStack: async (params: {
    project_cost: number;
    matched_grant_max?: number;
    technology_category?: string;
    technology_areas?: string[];
    activity_types?: string[];
    project_summary?: string;
    applicant_type?: string;
    solicitation_name?: string;
    agency?: string;
    energy_community_bonus?: boolean;
    domestic_content_bonus?: boolean;
    prevailing_wage_compliant?: boolean;
    tax_exempt_direct_pay?: boolean;
  }): Promise<CapitalStack> => {
    const res = await fetch('/api/capital-stack', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error('Failed to calculate capital stack waterfall');
    return res.json();
  },

  downloadProjectAnalysisPdf: async (analysisData: any): Promise<Blob> => {
    const res = await fetch('/api/analyze/export-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(analysisData),
    });
    if (!res.ok) throw new Error('Failed to generate project summary PDF');
    return res.blob();
  },

  getStatutoryDeficits: async (): Promise<{ total_mandates_tracked: number; deficits: StatutoryDeficit[] }> => {
    const res = await fetch('/api/policies/deficits');
    if (!res.ok) throw new Error('Failed to fetch statutory compliance deficits');
    return res.json();
  },

  getStatutoryDeficit: async (id: string): Promise<StatutoryDeficit> => {
    const res = await fetch(`/api/policies/deficits/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch statutory deficit ${id}`);
    return res.json();
  },

  getTechnologyBankability: async (techId: string): Promise<TechnologyBankabilityRating> => {
    const res = await fetch(`/api/tech-reference/technologies/${techId}/bankability`);
    if (!res.ok) throw new Error(`Failed to fetch bankability rating for ${techId}`);
    return res.json();
  },

  getTrendsOverview: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/overview${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends overview');
    return res.json();
  },

  getTrendsByAgency: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/by-agency${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends by agency');
    return res.json();
  },

  getTrendsByTechnology: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/by-technology${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends by technology');
    return res.json();
  },

  getTrendsByType: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/by-type${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends by type');
    return res.json();
  },

  getTrendsAmounts: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/amounts${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends amounts');
    return res.json();
  },

  getTrendsHeatmap: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/heatmap${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends heatmap');
    return res.json();
  },
  getTrendsBySector: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/by-sector${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends by sector');
    return res.json();
  },
  getTrendsByFuel: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/by-fuel${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends by fuel');
    return res.json();
  },
  getTrendsAnalytics: async (params?: Record<string, any>): Promise<any> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/analytics${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends analytics');
    return res.json();
  },
  getTrendsComparison: async (params?: Record<string, any>): Promise<any[]> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/comparison${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch trends comparison matrix');
    return res.json();
  },
  getStackedTimeseries: async (params?: Record<string, any>): Promise<{ dimension: string; data_source: string; metric: string; series: string[]; data: any[] }> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/trends/stacked-timeseries${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch stacked timeseries');
    return res.json();
  },
  getAgencies: async (): Promise<{ items: any[]; total: number; categories: any[] }> => {


    const res = await fetch('/api/agencies');
    if (!res.ok) throw new Error('Failed to fetch agencies');
    return res.json();
  },
  // Awards
  getAwards: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== '' && v !== null) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/awards${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch awards');
    return res.json();
  },
  getAwardStats: async () => {
    const res = await fetch('/api/awards/stats');
    if (!res.ok) throw new Error('Failed to fetch award stats');
    return res.json();
  },
  getAwardRecipients: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== '' && v !== null) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/awards/recipients${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch recipients');
    return res.json();
  },
  getAward: async (id: number) => {
    const res = await fetch(`/api/awards/${id}`);
    if (!res.ok) throw new Error('Failed to fetch award');
    return res.json();
  },
  getAwardMap: async (params?: Record<string, any>): Promise<AwardMapResponse> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== '' && v !== null) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/awards/map${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch award map');
    return res.json();
  },
  getAwardMapFilters: async (): Promise<AwardMapFilters> => {
    const res = await fetch('/api/awards/map/filters');
    if (!res.ok) throw new Error('Failed to fetch award map filters');
    return res.json();
  },
  getAwardMapStateSummary: async (): Promise<AwardMapStateSummary[]> => {
    const res = await fetch('/api/awards/map/state-summary');
    if (!res.ok) throw new Error('Failed to fetch award map state summary');
    return res.json();
  },
  getAwardRecipientsMap: async (params?: Record<string, any>): Promise<AwardMapResponse> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== '' && v !== null) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/awards/recipients/map${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch award recipients map');
    return res.json();
  },
  getRecipientDetail: async (idOrName: string | number): Promise<AwardRecipient & { awards: any[] }> => {
    const res = await fetch(`/api/awards/recipient/${encodeURIComponent(idOrName)}`);
    if (!res.ok) throw new Error('Failed to fetch recipient detail');
    return res.json();
  },
  
  // Organizations
  getOrganizations: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/organizations${search ? `?${search}` : ''}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch organizations');
    return res.json();
  },
  getOrganization: async (id: string) => {
    const res = await fetch(`/api/organizations/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch organization');
    return res.json();
  },
  searchOrganizations: async (query: string) => {
    const res = await fetch(`/api/organizations/search?q=${encodeURIComponent(query)}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to search organizations');
    return res.json();
  },

  // Contacts & Key Directory
  getContacts: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          searchParams.append(k, v.toString());
        }
      });
    }
    const search = searchParams.toString();
    const res = await fetch(`/api/contacts${search ? `?${search}` : ''}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch contacts');
    return res.json();
  },
  getContact: async (id: string | number) => {
    const res = await fetch(`/api/contacts/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch contact');
    return res.json();
  },
  getContactStats: async () => {
    const res = await fetch('/api/contacts/stats', {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch contact statistics');
    return res.json();
  },

  // Community
  createToken: async () => {
    const res = await fetch('/api/community/token', { method: 'POST' });
    if (!res.ok) throw new Error('Failed to create token');
    return res.json();
  },
  verifyToken: async (token: string) => {
    const res = await fetch('/api/community/verify', {
      headers: { 'X-Creator-Token': token }
    });
    if (!res.ok) throw new Error('Failed to verify token');
    return res.json();
  },
  recoverToken: async (key: string) => {
    const res = await fetch('/api/community/recover', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key })
    });
    if (!res.ok) throw new Error('Failed to recover token');
    return res.json();
  },

  // Strategy
  createStrategy: async (data: any) => {
    const token = localStorage.getItem('creator_token');
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['X-Creator-Token'] = token;
    const res = await fetch('/api/strategies', {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create strategy');
    return res.json();
  },
  getStrategy: async (id: string) => {
    const res = await fetch(`/api/strategies/${id}`);
    if (!res.ok) throw new Error('Failed to fetch strategy');
    return res.json();
  },
  executeStrategy: async (id: string) => {
    const res = await fetch(`/api/strategies/${id}/execute`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to execute strategy');
    return res.json();
  },
  listStrategies: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/strategies${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to list strategies');
    return res.json();
  },
  deleteStrategy: async (id: string) => {
    const token = localStorage.getItem('creator_token');
    const headers: Record<string, string> = {};
    if (token) headers['X-Creator-Token'] = token;
    const res = await fetch(`/api/strategies/${id}`, { method: 'DELETE', headers });
    if (!res.ok) throw new Error('Failed to delete strategy');
    return res.json();
  },
  getStrategyPdf: async (id: string) => {
    const res = await fetch(`/api/strategies/${id}/pdf`);
    if (!res.ok) throw new Error('Failed to get strategy PDF');
    return res.blob();
  },

  // Reports
  createReport: async (data: any) => {
    const token = localStorage.getItem('creator_token');
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['X-Creator-Token'] = token;
    const res = await fetch('/api/reports', {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create report');
    return res.json();
  },
  getReport: async (id: string) => {
    const res = await fetch(`/api/reports/${id}`);
    if (!res.ok) throw new Error('Failed to fetch report');
    return res.json();
  },
  executeReport: async (id: string) => {
    const res = await fetch(`/api/reports/${id}/execute`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to execute report');
    return res.json();
  },
  listReports: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/reports${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to list reports');
    return res.json();
  },
  deleteReport: async (id: string) => {
    const token = localStorage.getItem('creator_token');
    const headers: Record<string, string> = {};
    if (token) headers['X-Creator-Token'] = token;
    const res = await fetch(`/api/reports/${id}`, { method: 'DELETE', headers });
    if (!res.ok) throw new Error('Failed to delete report');
    return res.json();
  },
  getReportPdf: async (id: string) => {
    const res = await fetch(`/api/reports/${id}/pdf`);
    if (!res.ok) throw new Error('Failed to get report PDF');
    return res.blob();
  },

  // Charts
  getChartData: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/charts/data${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch chart data');
    return res.json();
  },
  saveChart: async (config: any) => {
    const token = localStorage.getItem('creator_token');
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['X-Creator-Token'] = token;
    const res = await fetch('/api/charts/save', {
      method: 'POST',
      headers,
      body: JSON.stringify(config)
    });
    if (!res.ok) throw new Error('Failed to save chart');
    return res.json();
  },
  getSavedCharts: async () => {
    const res = await fetch('/api/charts/saved');
    if (!res.ok) throw new Error('Failed to get saved charts');
    return res.json();
  },
  exportChartCsv: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/charts/export${search ? `?${search}` : ''}`);
    if (!res.ok) throw new Error('Failed to export chart CSV');
    return res.blob();
  },

  // Network
  getNetworkData: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/relationships/network${search ? `?${search}` : ''}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch network data');
    return res.json();
  },
  getRelationshipStats: async () => {
    const res = await fetch('/api/relationships/stats', {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch relationship stats');
    return res.json();
  },
  getKnowledgeGraph: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/network/graph${search ? `?${search}` : ''}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch knowledge graph');
    return res.json();
  },
  getNodeDetail: async (nodeType: string, nodeId: string | number) => {
    const res = await fetch(`/api/network/node/${nodeType}/${encodeURIComponent(nodeId)}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch node detail');
    return res.json();
  },
  getNetworkAnalytics: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/network/analytics${search ? `?${search}` : ''}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch network analytics');
    return res.json();
  },

  // Sankey & Funding Flows
  getSankeyPresets: async () => {
    const res = await fetch('/api/sankey/presets', {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch sankey presets');
    return res.json();
  },
  getSankeyFlow: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/sankey/flow${search ? `?${search}` : ''}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch sankey flow');
    return res.json();
  },
  getSankeyInsights: async (params?: Record<string, any>) => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const search = searchParams.toString();
    const res = await fetch(`/api/sankey/insights${search ? `?${search}` : ''}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch sankey insights');
    return res.json();
  },

  // Executive Reports & AI Dossier Generation
  getReportPresets: async (): Promise<{ presets: ReportPreset[] }> => {
    const res = await fetch('/api/reports/presets');
    if (!res.ok) throw new Error('Failed to fetch report presets');
    return res.json();
  },
  generateExecutiveReport: async (req: ReportGenerateRequest): Promise<ReportGenerateResponse> => {
    const res = await fetch('/api/reports/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error('Failed to generate executive report');
    return res.json();
  },
  exportExecutiveReportPdf: async (req: ReportGenerateRequest): Promise<Blob> => {
    const res = await fetch('/api/reports/export-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error('Failed to export report PDF');
    return res.blob();
  },
  runPipelineUpdate: async (params?: { openai_api_key?: string; model_name?: string }): Promise<any> => {
    const res = await fetch('/api/reports/run-pipeline', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(params || {}),
    });
    if (!res.ok) throw new Error('Failed to run update pipeline');
    return res.json();
  },
  clearReportCache: async (): Promise<{ status: string; cleared_count: number }> => {
    const res = await fetch('/api/reports/clear-cache', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    });
    if (!res.ok) throw new Error('Failed to clear report cache');
    return res.json();
  },

  // Authentication & Membership
  register: async (data: { email: string; password: string; full_name?: string; organization_name?: string }): Promise<AuthResponse> => {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  login: async (data: { email: string; password: string }): Promise<AuthResponse> => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(err.detail || 'Invalid email or password');
    }
    return res.json();
  },

  getMe: async (): Promise<{ user: User }> => {
    const res = await fetch('/api/auth/me', {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch user session');
    return res.json();
  },

  updateProfile: async (data: { full_name?: string; organization_name?: string; preferences?: Record<string, any> }): Promise<{ status: string; user: User }> => {
    const res = await fetch('/api/auth/me', {
      method: 'PUT',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to update profile' }));
      throw new Error(err.detail || 'Failed to update profile');
    }
    return res.json();
  },

  changePassword: async (data: { current_password: string; new_password: string }): Promise<{ status: string; message: string }> => {
    const res = await fetch('/api/auth/change-password', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to update password' }));
      throw new Error(err.detail || 'Failed to update password');
    }
    return res.json();
  },

  forgotPassword: async (email: string): Promise<{ status: string; message: string; reset_token?: string }> => {
    const res = await fetch('/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to process password reset' }));
      throw new Error(err.detail || 'Failed to process request');
    }
    return res.json();
  },

  resetPassword: async (data: { token: string; new_password: string }): Promise<{ status: string; message: string }> => {
    const res = await fetch('/api/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to reset password' }));
      throw new Error(err.detail || 'Failed to reset password');
    }
    return res.json();
  },

  getMembership: async (): Promise<{ user: User | null; membership_manifest: MembershipManifest }> => {
    const res = await fetch('/api/auth/membership', {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch membership details');
    return res.json();
  },

  mockUpgradeTier: async (tier: string): Promise<{ status: string; message: string; user: User }> => {
    const res = await fetch('/api/auth/mock-upgrade', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ tier }),
    });
    if (!res.ok) throw new Error('Failed to upgrade tier');
    return res.json();
  },

  // Results, Outcomes, and Apples-to-Apples Benchmarks
  getResults: async (params?: Record<string, any>): Promise<{ items: OutcomeMetric[]; total: number; page: number; page_size: number; total_pages: number }> => {
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`/api/results${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch results metrics');
    return res.json();
  },

  getBenchmarks: async (params?: Record<string, any>): Promise<{ items: ResultBenchmark[]; total: number; page: number; page_size: number; total_pages: number }> => {
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`/api/results/benchmarks${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch result benchmarks');
    return res.json();
  },

  getResultsSummary: async (params?: Record<string, any>): Promise<ResultsSummary> => {
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`/api/results/metrics-summary${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch results summary');
    return res.json();
  },

  getSuccessStories: async (params?: Record<string, any>): Promise<SuccessStory[]> => {
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`/api/results/success-stories${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch success stories');
    return res.json();
  },

  getSuccessStory: async (id: number): Promise<SuccessStory> => {
    const res = await fetch(`/api/results/success-stories/${id}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch success story detail');
    return res.json();
  },

  getOpportunityResults: async (oppId: string | number): Promise<{ opportunity_id: number; solicitation_number: string; name: string; agency: string; benchmark: ResultBenchmark; results: OutcomeMetric[]; success_stories: SuccessStory[]; artifacts: ResultArtifact[] }> => {
    const res = await fetch(`/api/opportunities/${oppId}/results`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch opportunity results');
    return res.json();
  },

  getResultArtifacts: async (params?: Record<string, any>): Promise<ResultArtifact[]> => {
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`/api/results/artifacts${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch result artifacts');
    return res.json();
  },

  getOrganizationResults: async (params?: Record<string, any>): Promise<OrganizationResultsResponse> => {
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`/api/results/organizations${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch organization results');
    return res.json();
  },

  compareOpportunities: async (ids: (string | number)[] | string): Promise<{ compared_count: number; items: any[] }> => {
    const idStr = Array.isArray(ids) ? ids.join(',') : ids;
    const res = await fetch(`/api/results/compare?ids=${encodeURIComponent(idStr)}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to compare opportunities');
    return res.json();
  },

  // Winning Proposals & Grant Package Intelligence
  getProposals: async (params?: Record<string, any>): Promise<PaginatedProposals> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString());
      });
    }
    const query = searchParams.toString();
    const res = await fetch(`/api/proposals${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch proposals');
    return res.json();
  },

  getProposal: async (id: string): Promise<WinningProposal> => {
    const res = await fetch(`/api/proposals/${encodeURIComponent(id)}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch proposal detail');
    return res.json();
  },

  getOpportunityWinningProposals: async (oppId: string | number): Promise<OpportunityWinningProposalsResponse> => {
    const res = await fetch(`/api/opportunities/${oppId}/winning-proposals`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch opportunity winning proposals');
    return res.json();
  },

  getAwardWinningProposal: async (awardId: string | number): Promise<WinningProposal> => {
    const res = await fetch(`/api/awards/${awardId}/winning-proposal`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch award winning proposal');
    return res.json();
  },

  // Universal Artifacts & Document Downloads
  getArtifacts: async (params?: Record<string, any>): Promise<PaginatedArtifacts> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString());
      });
    }
    const query = searchParams.toString();
    const res = await fetch(`/api/artifacts${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch artifacts');
    return res.json();
  },

  getArtifact: async (id: number): Promise<ProposalArtifact> => {
    const res = await fetch(`/api/artifacts/${id}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch artifact');
    return res.json();
  },

  discoverAndDownloadArtifacts: async (): Promise<any> => {
    const res = await fetch('/api/artifacts/discover-and-download', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    });
    if (!res.ok) throw new Error('Failed to run artifact discovery');
    return res.json();
  },

  // Venture & Patent Attributions
  getAttributionsOverview: async (): Promise<AttributionsOverview> => {
    const res = await fetch('/api/attributions/overview', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch attributions overview');
    return res.json();
  },

  getAttributionRecipients: async (params?: Record<string, any>): Promise<PaginatedAttributionRecipients> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString());
      });
    }
    const query = searchParams.toString();
    const res = await fetch(`/api/attributions/recipients${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch attribution recipients');
    return res.json();
  },

  getRecipientAttributionDossier: async (recipientId: number | string): Promise<RecipientAttributionDossier> => {
    const res = await fetch(`/api/attributions/recipients/${recipientId}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch recipient attribution dossier');
    return res.json();
  },

  getAttributionsGraph: async (): Promise<AttributionsGraphResponse> => {
    const res = await fetch('/api/attributions/graph', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch attributions graph');
    return res.json();
  },

  getAttributionSyndicates: async (): Promise<{ syndicates: AttributionSyndicate[] }> => {
    const res = await fetch('/api/attributions/syndicates', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch attribution syndicates');
    return res.json();
  },

  // 9-Dimensional Innovation Linkages & Provenance
  getLinkageOverview: async (): Promise<LinkageOverviewResponse> => {
    const res = await fetch('/api/linkages/overview', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch linkage overview');
    return res.json();
  },

  getLinkageTrace: async (entityType: string, entityId: string | number): Promise<LinkageTraceResponse> => {
    const res = await fetch(`/api/linkages/trace?entity_type=${encodeURIComponent(entityType)}&entity_id=${encodeURIComponent(entityId)}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to trace 9D lineage for ${entityType} ${entityId}`);
    return res.json();
  },

  getLinkageMatrix: async (params?: { dim_x?: string; dim_y?: string; metric?: string }): Promise<LinkageMatrixResponse> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v) searchParams.append(k, v);
      });
    }
    const q = searchParams.toString();
    const res = await fetch(`/api/linkages/matrix${q ? `?${q}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch linkage cross matrix');
    return res.json();
  },

  resolvePatentLinkages: async (): Promise<any> => {
    const res = await fetch('/api/linkages/resolve-patents', { method: 'POST', headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to resolve patent linkages');
    return res.json();
  },

  // Technology Reference & Innovation Frontier Guide
  getTechCategories: async (): Promise<TechCategory[]> => {
    const res = await fetch('/api/tech-reference/categories', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch technology categories');
    return res.json();
  },

  getTechnologies: async (params?: { category_id?: string; search?: string; vector_type?: string }): Promise<TechSummary[]> => {
    const searchParams = new URLSearchParams();
    if (params?.category_id) searchParams.append('category_id', params.category_id);
    if (params?.search) searchParams.append('search', params.search);
    if (params?.vector_type) searchParams.append('vector_type', params.vector_type);
    const query = searchParams.toString();
    const res = await fetch(`/api/tech-reference/technologies${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch technologies');
    return res.json();
  },

  getTechnologyDossier: async (techId: string): Promise<TechDossier> => {
    const res = await fetch(`/api/tech-reference/technologies/${encodeURIComponent(techId)}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch dossier for technology '${techId}'`);
    return res.json();
  },

  getTechAIInsights: async (
    techId: string,
    payload: { custom_question?: string; api_key?: string; model_name?: string; force_refresh?: boolean }
  ): Promise<TechAIInsights> => {
    const headers = getAuthHeaders({ 'Content-Type': 'application/json' });
    const res = await fetch(`/api/tech-reference/technologies/${encodeURIComponent(techId)}/ai-insights`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to generate AI technology insights');
    return res.json();
  },

  getTechnologySubsystems: async (techId: string): Promise<{ technology_id: string; subsystems: TechSubsystemNode[] }> => {
    const res = await fetch(`/api/tech-reference/technologies/${encodeURIComponent(techId)}/subsystems`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch subsystems for technology '${techId}'`);
    return res.json();
  },

  getComparativeTechnologies: async (techIds: string[]): Promise<{ compared_count: number; technologies: TechDossier[] }> => {
    const idsQuery = encodeURIComponent(techIds.join(','));
    const res = await fetch(`/api/tech-reference/compare?ids=${idsQuery}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch comparative technology data');
    return res.json();
  },

  getFuelsMatrix: async (): Promise<FuelsMatrixItem[]> => {
    const res = await fetch('/api/tech-reference/fuels-matrix', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch zero-carbon fuels matrix');
    return res.json();
  },

  getFrontierMatrix: async (): Promise<FrontierMatrixItem[]> => {
    const res = await fetch('/api/tech-reference/frontier-matrix', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch innovation frontier matrix');
    return res.json();
  },

  getTechReferenceStats: async (): Promise<any> => {
    const res = await fetch('/api/tech-reference/stats', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch tech reference stats');
    return res.json();
  },

  // Policy, Regulatory, Codes & Standards Knowledge Base
  getPolicies: async (params?: {
    category?: string;
    jurisdiction_level?: string;
    jurisdiction_state?: string;
    technology_id?: string;
    fuel_vector?: string;
    status?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ total: number; limit: number; offset: number; policies: PolicyStandard[] }> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString());
      });
    }
    const query = searchParams.toString();
    const res = await fetch(`/api/policies${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch policies');
    return res.json();
  },

  getPolicy: async (policyId: string): Promise<PolicyDossier> => {
    const res = await fetch(`/api/policies/${encodeURIComponent(policyId)}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch policy dossier for '${policyId}'`);
    return res.json();
  },

  getPoliciesByTechnology: async (techId: string): Promise<{ technology_id: string; technology_name: string; policies_count: number; policies: PolicyTechItem[] }> => {
    const res = await fetch(`/api/policies/by-technology/${encodeURIComponent(techId)}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch policies for technology '${techId}'`);
    return res.json();
  },

  getPoliciesByOpportunity: async (oppId: number | string): Promise<{ opportunity_id: number; solicitation_number: string; opportunity_name: string; agency: string; policies_count: number; policies: any[] }> => {
    const res = await fetch(`/api/policies/by-opportunity/${encodeURIComponent(oppId)}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch policies for opportunity '${oppId}'`);
    return res.json();
  },

  getPolicyStats: async (): Promise<any> => {
    const res = await fetch('/api/policies/stats', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch policy stats');
    return res.json();
  },

  // Regulatory Proceedings & PUC Dockets
  getRegulatoryProceedings: async (params?: {
    commission?: string;
    jurisdiction_level?: string;
    jurisdiction_state?: string;
    topic_category?: string;
    technology_id?: string;
    status?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ total: number; limit: number; offset: number; proceedings: RegulatoryProceeding[] }> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString());
      });
    }
    const query = searchParams.toString();
    const res = await fetch(`/api/policies/proceedings${query ? `?${query}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch regulatory proceedings');
    return res.json();
  },

  getRegulatoryProceedingDetail: async (proceedingId: string): Promise<ProceedingDossier> => {
    const res = await fetch(`/api/policies/proceedings/${encodeURIComponent(proceedingId)}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch dossier for proceeding '${proceedingId}'`);
    return res.json();
  },

  getProceedingsByTechnology: async (techId: string): Promise<{ technology_id: string; technology_name: string; proceedings_count: number; proceedings: ProceedingTechItem[] }> => {
    const res = await fetch(`/api/policies/proceedings/by-technology/${encodeURIComponent(techId)}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch proceedings for technology '${techId}'`);
    return res.json();
  },

  getProceedingStats: async (): Promise<ProceedingMacroStats> => {
    const res = await fetch('/api/policies/proceedings/stats', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch proceeding stats');
    return res.json();
  },


  getChatPresets: async (): Promise<{ categories: ChatPresetCategory[] }> => {
    const res = await fetch('/api/chat/presets', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch chat presets');
    return res.json();
  },

  sendChatSync: async (query: string, history?: Array<{ role: string; content: string }>, apiKey?: string): Promise<{ answer: string; citations: ChatCitationsMetadata; intent: any }> => {
    const res = await fetch('/api/chat/query-sync', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, history, api_key: apiKey }),
    });
    if (!res.ok) throw new Error('Failed to query chat assistant');
    return res.json();
  },

  // Tavus.io Conversational Video AI
  getTavusStatus: async (): Promise<TavusStatus> => {
    const res = await fetch('/api/tavus/status', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch Tavus status');
    return res.json();
  },

  setTavusApiKey: async (payload: TavusSetKeyPayload): Promise<{ success: boolean; message: string }> => {
    const res = await fetch('/api/tavus/set-api-key', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to save Tavus settings');
    return res.json();
  },

  createTavusConversation: async (payload: TavusCreateConversationPayload): Promise<TavusConversationResponse> => {
    const res = await fetch('/api/tavus/conversations/create', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to create Tavus video conversation');
    }
    return res.json();
  },

  endTavusConversation: async (conversationId: string, apiKey?: string): Promise<{ success: boolean; status?: number }> => {
    const res = await fetch(`/api/tavus/conversations/${encodeURIComponent(conversationId)}/end`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey }),
    });
    if (!res.ok) return { success: false };
    return res.json();
  },

  getTavusConversationStatus: async (conversationId: string, apiKey?: string): Promise<any> => {
    const query = apiKey ? `?api_key=${encodeURIComponent(apiKey)}` : '';
    const res = await fetch(`/api/tavus/conversations/${encodeURIComponent(conversationId)}${query}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch Tavus conversation status');
    return res.json();
  },

  getTavusReplicas: async (apiKey?: string): Promise<{ data: Array<{ replica_id: string; replica_name: string; status: string; thumbnail_url?: string }> }> => {
    const query = apiKey ? `?api_key=${encodeURIComponent(apiKey)}` : '';
    const res = await fetch(`/api/tavus/replicas${query}`, { headers: getAuthHeaders() });
    if (!res.ok) return { data: [] };
    return res.json();
  },

  getTavusPersonas: async (apiKey?: string): Promise<{ data: Array<{ persona_id: string; persona_name: string; persona_description?: string }> }> => {
    const query = apiKey ? `?api_key=${encodeURIComponent(apiKey)}` : '';
    const res = await fetch(`/api/tavus/personas${query}`, { headers: getAuthHeaders() });
    if (!res.ok) return { data: [] };
    return res.json();
  },

  reviewTavusSession: async (payload: { transcript_or_notes: string; user_role?: string; api_key?: string }): Promise<{ reviewed_text: string; citations: ChatCitationsMetadata; referenced_entities: Record<string, any> }> => {
    const res = await fetch('/api/tavus/review-session', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to review video session notes');
    return res.json();
  },

  syncTavusIntelligence: async (payload: { query_or_transcript: string; user_role?: string; conversation_id?: string; api_key?: string }): Promise<TavusSyncIntelligenceResponse> => {
    const res = await fetch('/api/tavus/sync-intelligence', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to synchronize live intelligence');
    return res.json();
  },

  synthesizeAndSyncTavusSession: async (payload: {
    recent_transcript_buffer: string;
    cumulative_transcript?: string;
    user_role?: string;
    conversation_id?: string;
    api_key?: string;
  }): Promise<TavusSynthesizeAndSyncResponse> => {
    const res = await fetch('/api/tavus/synthesize-and-sync', {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to synthesize and synchronize conversation intelligence');
    return res.json();
  },

  // -------------------------------------------------------------
  // System Administration: Email Hub, Campaigns & Correspondence
  // -------------------------------------------------------------
  getAdminEmailStatus: async (): Promise<AdminEmailStatusResponse> => {
    const res = await fetch('/api/admin/email/status', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch admin email status');
    return res.json();
  },

  testAdminEmailConnection: async (): Promise<AdminEmailConnectionTestResponse> => {
    const res = await fetch('/api/admin/email/test-connection', {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    });
    if (!res.ok) throw new Error('Failed to test Gmail connection');
    return res.json();
  },

  getAdminEmailTemplates: async (): Promise<{ templates: EmailTemplate[] }> => {
    const res = await fetch('/api/admin/email/templates', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch email templates');
    return res.json();
  },

  sendAdminEmailCampaign: async (
    payload: SendEmailRequestPayload,
    files?: File[]
  ): Promise<{ status: string; message: string; campaign: AdminEmailCampaign; result: any }> => {
    const formData = new FormData();
    formData.append('payload_json', JSON.stringify(payload));
    if (files && files.length > 0) {
      files.forEach(f => formData.append('files', f));
    }

    const headers = getAuthHeaders();
    // Do NOT set Content-Type header manually when sending FormData so browser sets boundary
    delete headers['Content-Type'];

    const res = await fetch('/api/admin/email/send', {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to send campaign' }));
      throw new Error(err.detail || 'Failed to dispatch email campaign');
    }
    return res.json();
  },

  getAdminEmailCampaigns: async (params?: { page?: number; page_size?: number }): Promise<{ total: number; page: number; page_size: number; items: AdminEmailCampaign[] }> => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.page_size) searchParams.append('page_size', params.page_size.toString());
    const q = searchParams.toString();
    const res = await fetch(`/api/admin/email/campaigns${q ? `?${q}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch email campaigns');
    return res.json();
  },

  getAdminEmailCampaign: async (id: number): Promise<{ campaign: AdminEmailCampaign; logs: AdminEmailLog[] }> => {
    const res = await fetch(`/api/admin/email/campaigns/${id}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch campaign details');
    return res.json();
  },

  syncAdminEmail: async (days: number = 30): Promise<{ success: boolean; messages_synced: number; threads_updated: number; synced_at: string; error?: string }> => {
    const res = await fetch(`/api/admin/email/sync?days_lookback=${days}`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    });
    if (!res.ok) throw new Error('Failed to sync Gmail inbox/sent messages');
    return res.json();
  },

  getAdminEmailThreads: async (params?: {
    search?: string;
    status_filter?: string;
    technology?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ total: number; page: number; page_size: number; total_pages: number; items: ContactEmailThread[] }> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString());
      });
    }
    const q = searchParams.toString();
    const res = await fetch(`/api/admin/email/threads${q ? `?${q}` : ''}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch correspondence threads');
    return res.json();
  },

  getAdminEmailThread: async (threadId: number): Promise<{ thread: ContactEmailThread; contact: any; messages: ContactEmailMessage[] }> => {
    const res = await fetch(`/api/admin/email/threads/${threadId}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch thread detail');
    return res.json();
  },

  getContactCorrespondenceHistory: async (contactId: number): Promise<{ contact_id: number; has_thread: boolean; status?: string; summary?: string; thread?: ContactEmailThread; messages: ContactEmailMessage[] }> => {
    const res = await fetch(`/api/admin/email/contact/${contactId}/history`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch contact correspondence history');
    return res.json();
  },

  quickReplyAdminEmailThread: async (threadId: number, data: { subject: string; body_text: string; body_html?: string; footer_text?: string }): Promise<{ status: string; message: string; thread: ContactEmailThread }> => {
    const res = await fetch(`/api/admin/email/threads/${threadId}/reply`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to send reply' }));
      throw new Error(err.detail || 'Failed to send reply');
    }
    return res.json();
  },

  updateAdminEmailThreadStatus: async (threadId: number, data: { status: string; next_action?: string }): Promise<{ status: string; thread: ContactEmailThread }> => {
    const res = await fetch(`/api/admin/email/threads/${threadId}/status`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update thread status');
    return res.json();
  },

  summarizeAdminEmailThread: async (threadId: number): Promise<any> => {
    const res = await fetch(`/api/admin/email/threads/${threadId}/summarize`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    });
    if (!res.ok) throw new Error('Failed to summarize thread');
    return res.json();
  },

  // ── Capital Intelligence & Infrastructure ──
  getInterconnectionQueues: async (params?: Record<string, any>): Promise<InterconnectionQueuesResponse> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const q = searchParams.toString();
    const res = await fetch(`/api/interconnection-queues${q ? `?${q}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch interconnection queues');
    return res.json();
  },

  getInterconnectionQueuesGeoJson: async (params?: Record<string, any>): Promise<any> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const q = searchParams.toString();
    const res = await fetch(`/api/interconnection-queues/geojson${q ? `?${q}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch interconnection geojson');
    return res.json();
  },

  getLabFacilities: async (params?: Record<string, any>): Promise<LabFacilitiesResponse> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const q = searchParams.toString();
    const res = await fetch(`/api/lab-facilities${q ? `?${q}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch lab facilities');
    return res.json();
  },

  getSecFormDFilings: async (params?: Record<string, any>): Promise<SecFormDResponse> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const q = searchParams.toString();
    const res = await fetch(`/api/sec-form-d${q ? `?${q}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch SEC Form D filings');
    return res.json();
  },

  getScaleupAllocations: async (params?: Record<string, any>): Promise<ScaleupAllocationsResponse> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const q = searchParams.toString();
    const res = await fetch(`/api/scaleup-allocations${q ? `?${q}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch scaleup allocations');
    return res.json();
  },

  getProcurementContracts: async (params?: Record<string, any>): Promise<ProcurementContractsResponse> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const q = searchParams.toString();
    const res = await fetch(`/api/procurement-contracts${q ? `?${q}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch procurement contracts');
    return res.json();
  },

  getDerCostBenchmarks: async (params?: Record<string, any>): Promise<DerCostBenchmarksResponse> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const q = searchParams.toString();
    const res = await fetch(`/api/der-deployments/benchmarks${q ? `?${q}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch DER cost benchmarks');
    return res.json();
  },

  getUniversityIp: async (params?: Record<string, any>): Promise<UniversityIpResponse> => {
    const searchParams = new URLSearchParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') searchParams.append(k, v.toString()); });
    const q = searchParams.toString();
    const res = await fetch(`/api/university-ip${q ? `?${q}` : ''}`);
    if (!res.ok) throw new Error('Failed to fetch university IP');
    return res.json();
  },

  getRecipientCapitalContinuum: async (recipientId: number): Promise<RecipientCapitalContinuumResponse> => {
    const res = await fetch(`/api/recipients/${recipientId}/capital-continuum`);
    if (!res.ok) throw new Error('Failed to fetch recipient capital continuum');
    return res.json();
  },

  // Daily Energy Innovation Intelligence Digest
  getDailyDigest: async (dateStr?: string): Promise<DailyDigest> => {
    const endpoint = dateStr ? `/api/v1/digest/${dateStr}` : '/api/v1/digest/latest';
    const res = await fetch(endpoint, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch daily digest: ${res.status}`);
    return res.json();
  },

  getDigestArchive: async (): Promise<DigestArchiveItem[]> => {
    const res = await fetch('/api/v1/digest/archive', { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch digest archive');
    return res.json();
  },

  generateDigest: async (dateStr?: string): Promise<DailyDigest> => {
    const endpoint = dateStr ? `/api/v1/digest/generate?date_str=${dateStr}` : '/api/v1/digest/generate';
    const res = await fetch(endpoint, { method: 'POST', headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to generate daily digest');
    return res.json();
  },
};

export interface DailyDigest {
  edition_date: string;
  formatted_date: string;
  edition_number: string;
  headline: string;
  editorial_narrative: string;
  macro_metrics: {
    open_solicitations_count: number;
    total_active_capital: number;
    total_active_capital_display: string;
    tracked_recipients_count: number;
    total_historical_awards_count: number;
    new_solicitations_today: number;
    urgent_deadlines_count: number;
  };
  new_solicitations: Array<{
    id: number;
    solicitation_number: string;
    name: string;
    agency: string;
    jurisdiction?: string;
    total_funding?: number;
    total_funding_display: string;
    max_per_award_display: string;
    due_date_display: string;
    short_description: string;
    solicitation_type: string;
    detail_url: string;
  }>;
  urgent_deadlines: Array<{
    id: number;
    solicitation_number: string;
    name: string;
    agency: string;
    due_date_display: string;
    total_funding_display: string;
    max_per_award_display: string;
    detail_url: string;
  }>;
  award_wire: Array<{
    id: number;
    recipient_name: string;
    recipient_city?: string;
    recipient_state?: string;
    award_amount_display: string;
    project_title: string;
    pi_name?: string;
    recipient_type: string;
  }>;
  regulatory_watch: Array<{
    code_identifier: string;
    title: string;
    category: string;
    jurisdiction_state: string;
    executive_summary: string;
    compliance_mandate?: string;
  }>;
  spotlight?: {
    opportunity_id: number;
    solicitation_number: string;
    name: string;
    agency: string;
    total_funding_display: string;
    max_per_award_display: string;
    due_date_display: string;
    short_description: string;
    bankability_score?: number;
    bankability_grade?: string;
    bankability_readiness?: string;
    ira_itc_rate?: number;
    ira_tax_credit_value?: string;
    blended_wacc_pct?: number;
    non_dilutive_coverage_pct?: number;
  };
  generated_at: string;
}

export interface DigestArchiveItem {
  date: string;
  formatted_date: string;
  headline: string;
  is_today: boolean;
}


// -------------------------------------------------------------
// Capital Intelligence & Infrastructure TypeScript Interfaces
// -------------------------------------------------------------

export interface InterconnectionQueueItem {
  id: number;
  iso_rto: string;
  queue_id: string;
  project_name: string;
  developer_raw?: string | null;
  recipient_id?: number | null;
  technology_type: string;
  capacity_mw?: number | null;
  storage_mwh?: number | null;
  county?: string | null;
  state?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  poi_substation?: string | null;
  utility_territory?: string | null;
  queue_date?: string | null;
  study_phase?: string | null;
  estimated_network_upgrade_cost_usd?: number | null;
  expected_cod?: string | null;
  status: string;
  source_url?: string | null;
  notes?: string | null;
}

export interface InterconnectionQueuesResponse {
  total: number;
  page: number;
  page_size: number;
  total_capacity_mw: number;
  total_storage_mwh: number;
  items: InterconnectionQueueItem[];
}

export interface NationalLabFacilityItem {
  id: number;
  lab_name: string;
  facility_name: string;
  facility_slug: string;
  facility_type?: string | null;
  summary: string;
  capabilities: string[];
  instruments: Array<{ instrument: string; spec: string }>;
  primary_sectors: string[];
  trl_focus_min: number;
  trl_focus_max: number;
  access_mechanisms: string[];
  proposal_deadline_cycles?: string | null;
  contact_email?: string | null;
  official_url?: string | null;
  city?: string | null;
  state?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  linked_technologies: string[];
}

export interface LabFacilitiesResponse {
  total: number;
  items: NationalLabFacilityItem[];
}

export interface SecFormDFilingItem {
  id: number;
  recipient_id?: number | null;
  cik_number: string;
  accession_number: string;
  filing_date: string;
  date_of_first_sale?: string | null;
  entity_legal_name: string;
  jurisdiction_state?: string | null;
  primary_industry?: string | null;
  total_offering_amount_usd?: number | null;
  total_amount_sold_usd?: number | null;
  total_remaining_usd?: number | null;
  is_equity: boolean;
  is_debt: boolean;
  num_investors?: number | null;
  minimum_investment_accepted_usd?: number | null;
  executive_officers: Array<{ name: string; title: string }>;
  sec_html_url?: string | null;
}

export interface SecFormDResponse {
  total: number;
  page: number;
  page_size: number;
  total_capital_raised_usd: number;
  items: SecFormDFilingItem[];
}

export interface FederalScaleupAllocationItem {
  id: number;
  recipient_id?: number | null;
  facility_name: string;
  program_category: string;
  support_type: string;
  allocation_amount_usd: number;
  total_project_capex_usd?: number | null;
  leverage_multiple?: number | null;
  facility_city?: string | null;
  facility_state?: string | null;
  energy_community_qualified: boolean;
  latitude?: number | null;
  longitude?: number | null;
  technology_vertical: string;
  annual_ghg_avoidance_metric_tons?: number | null;
  permanent_jobs_created?: number | null;
  status: string;
  announcement_date?: string | null;
  source_url?: string | null;
  summary?: string | null;
}

export interface ScaleupAllocationsResponse {
  total: number;
  total_allocated_usd: number;
  total_capex_usd: number;
  items: FederalScaleupAllocationItem[];
}

export interface FederalProcurementContractItem {
  id: number;
  recipient_id?: number | null;
  contract_number: string;
  contracting_agency: string;
  contracting_office?: string | null;
  award_type?: string | null;
  is_sbir_phase_3: boolean;
  is_sole_source: boolean;
  obligated_amount_usd: number;
  base_and_all_options_value_usd?: number | null;
  signed_date?: string | null;
  completion_date?: string | null;
  place_of_performance_state?: string | null;
  place_of_performance_city?: string | null;
  description_of_requirement?: string | null;
  source_url?: string | null;
}

export interface ProcurementContractsResponse {
  total: number;
  total_obligated_usd: number;
  items: FederalProcurementContractItem[];
}

export interface DerCostCurvePoint {
  year: number;
  technology_type: string;
  sector: string;
  avg_unit_cost: number;
  total_installs: number;
  total_kw: number;
}

export interface DerCostBenchmarksResponse {
  cost_curves: DerCostCurvePoint[];
  top_manufacturers: Array<{
    manufacturer: string;
    installs_count: number;
    total_mw: number;
  }>;
}

export interface UniversityLicensableTechnologyItem {
  id: number;
  university_id: number;
  university_name: string;
  title: string;
  abstract: string;
  tech_domain: string;
  technology_id?: string | null;
  licensing_status: string;
  trl_estimated: number;
  patent_application_number?: string | null;
  licensing_contact_email?: string | null;
  portal_url?: string | null;
  case_number?: string | null;
}

export interface UniversityIpResponse {
  total: number;
  items: UniversityLicensableTechnologyItem[];
}

export interface RecipientCapitalContinuumResponse {
  recipient_id: number;
  name: string;
  primary_technology?: string | null;
  headquarters_city?: string | null;
  headquarters_state?: string | null;
  financial_aggregates: {
    total_public_grants_usd: number;
    total_sec_form_d_usd: number;
    total_vc_investments_usd: number;
    total_scaleup_allocations_usd: number;
    total_procurement_offtake_usd: number;
    grand_total_capital_usd: number;
  };
  grants: Array<{
    id: number;
    agency: string;
    award_amount: number;
    award_date?: string | null;
    project_title: string;
    solicitation_number: string;
  }>;
  sec_form_d_filings: Array<{
    id: number;
    cik: string;
    filing_date?: string | null;
    amount_sold_usd: number;
    num_investors?: number | null;
    is_equity: boolean;
    sec_url?: string | null;
  }>;
  vc_rounds: Array<{
    id: number;
    round_type: string;
    round_date?: string | null;
    amount_usd?: number | null;
    lead_investor?: string | null;
    investors: string[];
  }>;
  patents: Array<{
    id: number;
    patent_number: string;
    title: string;
    grant_date?: string | null;
    bayh_dole_citation?: string | null;
    cited_by_count?: number | null;
  }>;
  scaleup_allocations: Array<{
    id: number;
    program_category: string;
    facility_name: string;
    allocation_amount_usd: number;
    total_capex_usd?: number | null;
    status: string;
    jobs?: number | null;
  }>;
  procurement_contracts: Array<{
    id: number;
    contract_number: string;
    agency: string;
    obligated_amount_usd: number;
    is_sbir_phase_3: boolean;
    signed_date?: string | null;
  }>;
  interconnection_queues: Array<{
    id: number;
    iso_rto: string;
    queue_id: string;
    project_name: string;
    capacity_mw?: number | null;
    storage_mwh?: number | null;
    poi_substation?: string | null;
    study_phase?: string | null;
    status: string;
    expected_cod?: string | null;
  }>;
}


export interface TavusSynthesizeAndSyncResponse {
  executive_gist: string;
  detected_topic: string;
  search_query: string;
  key_entities: string[];
  citations: ChatCitationsMetadata;
  summary: string;
  stats: {
    total_funding: number;
    awards_count: number;
    opportunities_count: number;
    organizations_count: number;
  };
}

export interface ReportPreset {
  id: string;
  title: string;
  subtitle: string;
  category: string;
  target_audience: string;
  badge: string;
  icon: string;
  pages?: number;
  capital_tracked?: string;
  awards_count?: string;
  key_focus?: string;
}

export interface ReportGenerateRequest {
  preset_id: string;
  filters?: Record<string, any>;
  custom_prompt?: string;
  openai_api_key?: string;
  model_name?: string;
  title?: string;
  force_refresh?: boolean;
}

export interface ReportGenerateResponse {
  preset_id: string;
  context_data: any;
  narrative: {
    title: string;
    subtitle: string;
    executive_takeaway?: string;
    executive_summary: string;
    macro_context?: string;
    key_findings: Array<{ title: string; narrative: string; metric_highlight: string; strategic_implication?: string }>;
    structural_observations: string;
    bottleneck_analysis: string;
    geospatial_intelligence?: string;
    strategic_recommendations: Array<{ target: string; action: string }>;
    conclusion?: string;
    future_outlook?: {
      horizon_summary: string;
      inflection_points: Array<{ horizon: string; title: string; outlook: string }>;
    };
    figure_captions: Record<string, string>;
  };
  generated_at: string;
}

export interface OutcomeMetric {
  id: number;
  opportunity_id?: number | null;
  award_id?: number | null;
  recipient_name?: string | null;
  agency?: string | null;
  year?: number | null;
  metric_category: string;
  canonical_metric_name: string;
  canonical_unit: string;
  canonical_value: number;
  reported_metric_name?: string | null;
  reported_unit?: string | null;
  raw_metric_value_str?: string | null;
  timeframe_years?: number | null;
  is_projected_or_actual: string;
  data_provenance: string;
  confidence_score: number;
  source_artifact_title?: string | null;
  source_url?: string | null;
  source_artifact_type?: string | null;
  notes_and_context?: string | null;
  created_at?: string | null;
}

export interface SuccessStory {
  id: number;
  opportunity_id?: number | null;
  award_id?: number | null;
  recipient_name: string;
  agency?: string | null;
  title: string;
  summary: string;
  challenge?: string | null;
  solution_technology?: string | null;
  outcome_impact?: string | null;
  customer_market?: string | null;
  quote_text?: string | null;
  quote_author?: string | null;
  technology_area?: string | null;
  trl_advancement?: string | null;
  featured_metrics?: Record<string, any> | null;
  artifact_url?: string | null;
  artifact_title?: string | null;
  image_url?: string | null;
  publication_date?: string | null;
  created_at?: string | null;
}

export interface ResultBenchmark {
  id: number;
  opportunity_id: number;
  solicitation_number: string;
  opportunity_name: string;
  agency: string;
  technology_area?: string | null;
  total_awards_tracked: number;
  total_awarded_usd: number;
  total_leveraged_capital_usd: number;
  total_ghg_avoided_annual_mt: number;
  total_clean_energy_mwh_yr: number;
  total_jobs_created: number;
  total_patents_issued: number;
  total_commercial_products: number;
  total_startups_spun_out: number;
  leverage_ratio: number;
  ghg_abatement_per_10k_usd: number;
  jobs_per_million_usd: number;
  ip_and_product_velocity: number;
  commercialization_rate_pct: number;
  avg_trl_gain: number;
  comparability_index: number;
}

export interface ResultArtifact {
  id: number;
  opportunity_id?: number | null;
  award_id?: number | null;
  title: string;
  artifact_type: string;
  agency?: string | null;
  source_url: string;
  doi?: string | null;
  publication_date?: string | null;
  page_count?: number | null;
  summary?: string | null;
  key_findings?: string[] | null;
  data_provenance: string;
  created_at?: string | null;
}

export interface ResultsSummary {
  kpis: {
    total_awarded_usd: number;
    total_leveraged_capital_usd: number;
    total_ghg_avoided_annual_mt: number;
    total_clean_energy_mwh_yr: number;
    total_jobs_created: number;
    total_patents_issued: number;
    total_commercial_products: number;
    total_startups_spun_out: number;
    overall_leverage_ratio: number;
    overall_ghg_per_10k_usd: number;
    overall_jobs_per_million_usd: number;
    overall_ip_and_product_velocity: number;
    total_opportunities_benchmarked: number;
    total_success_stories: number;
    total_artifacts_cataloged: number;
  };
  agency_breakdown: Array<{
    agency: string;
    opportunities_count: number;
    total_awarded_usd: number;
    total_leveraged_capital_usd: number;
    total_ghg_annual_mt: number;
    total_jobs: number;
    total_patents: number;
    leverage_ratio: number;
  }>;
  category_counts: Record<string, number>;
}

export interface OrganizationResultDossier {
  recipient_name: string;
  agency: string;
  year: number;
  technology_area: string;
  summary_metrics: {
    total_leveraged_capital_usd: number;
    total_ghg_avoided_annual_mt: number;
    total_clean_energy_mwh_yr: number;
    total_jobs_created: number;
    total_patents_issued: number;
    total_commercial_products: number;
    avg_trl_advancement: number;
  };
  metrics: OutcomeMetric[];
  artifacts: ResultArtifact[];
  success_story?: SuccessStory | null;
  linked_opportunities: Array<{
    id: number;
    solicitation_number: string;
    name: string;
    agency: string;
  }>;
}

export interface OrganizationResultsResponse {
  total_organizations: number;
  organizations: OrganizationResultDossier[];
}

export interface ProposalArtifact {
  id: number;
  opportunity_id?: number | null;
  award_id?: number | null;
  organization_id?: number | null;
  recipient_name?: string | null;
  title: string;
  artifact_type: string;
  agency?: string | null;
  source_url: string;
  doi?: string | null;
  publication_date?: string | null;
  page_count?: number | null;
  summary?: string | null;
  key_findings?: string[];
  file_size_bytes?: number;
  has_local_file?: boolean;
  local_path?: string | null;
  data_provenance?: string;
  download_url?: string;
  created_at?: string | null;
}

export interface SopoTask {
  task: string;
  budget: string;
  lead: string;
  milestone: string;
  gate: string;
  trl: string;
}

export interface RubricScore {
  criterion: string;
  max_pts: number;
  score: number;
  feedback: string;
}

export interface WinningProposal {
  id: string;
  award_id?: number | null;
  external_award_id?: string | null;
  opportunity_id?: number | null;
  solicitation_number: string;
  opportunity_name?: string;
  title: string;
  agency: string;
  agency_code: string;
  recipient_name?: string;
  recipient_city?: string;
  recipient_state?: string;
  recipient_type?: string;
  target_funding: number;
  total_budget: number;
  cost_share_amount?: number;
  cost_share_pct: number;
  award_date?: string;
  deadline?: string;
  days_remaining?: number;
  year?: number;
  stage: string;
  stage_label: string;
  is_won?: boolean;
  red_team_score?: number | null;
  compliance_pct: number;
  lead_pi: string;
  pi_email?: string;
  pi_institution?: string;
  partner_consortium: string[];
  tech_area: string;
  description: string;
  sopo_tasks?: SopoTask[];
  rubric_scores?: RubricScore[];
  artifacts_count?: number;
  artifacts?: ProposalArtifact[];
  bundle_download_url?: string;
  opportunity?: {
    id: number;
    solicitation_number: string;
    name: string;
    agency: string;
    status: string;
    total_funding?: number;
    detail_url?: string;
  };
  award?: {
    id: number;
    recipient_name: string;
    award_amount: number;
    project_title: string;
    year?: number;
  };
}

export interface PaginatedProposals {
  items: WinningProposal[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface OpportunityWinningProposalsResponse {
  opportunity_id: number;
  solicitation_number: string;
  opportunity_name: string;
  agency: string;
  total_proposals_won: number;
  total_capital_awarded: number;
  items: WinningProposal[];
  bundle_download_url: string;
}

export interface PaginatedArtifacts {
  items: ProposalArtifact[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AttributionsOverview {
  total_patents: number;
  total_vc_raised_usd: number;
  total_public_grants_usd: number;
  leverage_multiplier: number;
  total_backed_companies: number;
  top_investors: Array<{ name: string; rounds_led: number; capital_deployed: number }>;
  tech_distribution: Array<{ technology: string; patent_count: number }>;
}

export interface AttributionPatentSample {
  number: string;
  title: string;
  url?: string;
}

export interface AttributionRecipientItem {
  id: number;
  name: string;
  recipient_type?: string;
  city?: string;
  state?: string;
  primary_technology?: string;
  patent_count: number;
  patents_sample: AttributionPatentSample[];
  investment_count: number;
  total_vc_raised_usd: number;
  total_public_grants_usd: number;
  leverage_ratio: number;
  lead_investors: string[];
  latest_round?: string;
  commercialization_stage: string;
}

export interface PaginatedAttributionRecipients {
  items: AttributionRecipientItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface RecipientPatentDetail {
  id: number;
  patent_number: string;
  title: string;
  abstract?: string;
  filing_date?: string;
  grant_date?: string;
  cpc_class?: string;
  technology_area?: string;
  bayh_dole_citation?: string;
  grant_contract_id?: string;
  inventors?: string;
  cited_by_count: number;
  patent_url?: string;
}

export interface RecipientInvestmentDetail {
  id: number;
  round_type: string;
  round_date?: string;
  amount_usd?: number;
  valuation_usd?: number;
  lead_investor?: string;
  participating_investors: string[];
  post_grant_months?: number;
  notes?: string;
}

export interface RecipientAttributionDossier {
  recipient: {
    id: number;
    name: string;
    recipient_type?: string;
    city?: string;
    state?: string;
    website?: string;
    primary_technology?: string;
    description?: string;
    total_funding_received?: number;
  };
  patents: RecipientPatentDetail[];
  investments: RecipientInvestmentDetail[];
  ego_graph: {
    nodes: Array<{ id: string; name: string; type: string; category: string; size: number; patent_number?: string; url?: string }>;
    edges: Array<{ source: string; target: string; label: string; color: string }>;
  };
}

export interface AttributionsGraphNode {
  id: string;
  name: string;
  type: string;
  category: string;
  color?: string;
  size?: number;
  technology?: string;
  state?: string;
  url?: string;
}

export interface AttributionsGraphEdge {
  source: string;
  target: string;
  label: string;
  type: string;
  color: string;
}

export interface AttributionsGraphResponse {
  nodes: AttributionsGraphNode[];
  edges: AttributionsGraphEdge[];
  stats: {
    agencies_count: number;
    companies_count: number;
    patents_count: number;
    investments_count: number;
  };
}

export interface AttributionSyndicate {
  name: string;
  portfolio_companies: string[];
  co_investors: string[];
  total_capital_deployed_usd: number;
  rounds_count: number;
}

// ── 9-DIMENSIONAL INNOVATION LINKAGE INTERFACES ──
export interface LinkageProvenanceChain {
  organization: {
    id: number;
    name: string;
    org_type?: string;
    website?: string;
    state?: string;
  } | null;
  program: {
    id: number;
    name: string;
    type?: string;
    target_stage?: string;
    url?: string;
  } | null;
  opportunity: {
    id: number;
    solicitation_number?: string;
    name: string;
    status?: string;
    agency?: string;
    total_funding?: number;
    url?: string;
  } | null;
  award: {
    id: number;
    external_id?: string;
    amount_usd?: number;
    award_date?: string;
    project_title?: string;
    award_type?: string;
    agency?: string;
    pi_name?: string;
  } | null;
  recipient: {
    id: number;
    name: string;
    type?: string;
    city?: string;
    state?: string;
    stage?: string;
    total_grants_usd?: number;
    website?: string;
    description?: string;
  } | null;
  patents: Array<{
    id: number;
    patent_number: string;
    title: string;
    abstract?: string;
    grant_date?: string;
    cpc_class?: string;
    technology_area?: string;
    bayh_dole_citation?: string;
    grant_contract_id?: string;
    url?: string;
  }>;
  investments: Array<{
    id: number;
    round_type: string;
    round_date?: string;
    amount_usd?: number;
    lead_investor?: string;
    post_grant_months?: number;
  }>;
}

export interface LinkageTaxonomies {
  technology: string | null;
  fuel: string | null;
  sector: string | null;
  stage: string | null;
}

export interface LinkageTraceResponse {
  provenance_chain: LinkageProvenanceChain;
  taxonomies: LinkageTaxonomies;
  lineage_graph: {
    nodes: Array<{
      id: string;
      name: string;
      type: string;
      label: string;
      color?: string;
      title?: string;
      lead?: string;
    }>;
    edges: Array<{
      source: string;
      target: string;
      label: string;
      color?: string;
    }>;
  };
}

export interface LinkageMatrixCell {
  x_value: string;
  y_value: string;
  value: number;
  formatted_value: string;
}

export interface LinkageMatrixResponse {
  dim_x: string;
  dim_y: string;
  metric: string;
  columns: string[];
  rows: string[];
  grid: LinkageMatrixCell[][];
}

export interface LinkageOverviewResponse {
  dimensions: {
    patents: { total: number; linked_to_grants: number };
    recipients: { total: number; with_patents: number; with_vc: number };
    opportunities: { total: number; linked_to_programs: number; linked_to_orgs: number };
    organizations: { total: number };
    programs: { total: number };
    technologies: { distinct_areas: number };
    fuels: { distinct_types: number };
    sectors: { distinct_sectors: number };
    stages: { distinct_stages: number };
  };
  capital: {
    total_grant_funding_tracked_usd: number;
    total_vc_funding_tracked_usd: number;
    overall_catalytic_leverage: number;
    awards_count: number;
  };
}

export interface TechCategory {
  id: string;
  name: string;
  icon: string;
  description: string;
  color: string;
  accent: string;
}

export interface TechFuelProfile {
  carrier_name?: string;
  chemical_formula?: string;
  carbon_intensity_ci?: string;
  energy_density_gravimetric?: string;
  energy_density_volumetric?: string;
  feedstock_pathway?: string;
  drop_in_compatibility?: string;
  policy_incentives?: string;
}

export interface TechSummary {
  id: string;
  name: string;
  category_id: string;
  category_name: string;
  headline: string;
  trl_current: number;
  trl_target: number;
  sector: string;
  fuel_vector: string;
  vector_type?: 'hardware' | 'fuel_carrier' | 'hybrid';
  keywords: string[];
}

export interface TechKPI {
  name: string;
  current: string;
  target_2030: string;
  status: 'on_track' | 'challenging' | 'achieved';
}

export interface TechRadarPoint {
  dimension: string;
  score: number;
  benchmark: number;
}

export interface TechTRLStage {
  stage: string;
  active: boolean;
  description: string;
}

export interface TechEvidence {
  tracked_capital_usd: number;
  tracked_capital_fmt: string;
  award_count: number;
  average_award_fmt: string;
  distinct_recipients_count: number;
  temporal_vintage: string;
  total_solicitations: number;
  active_solicitations_count: number;
  pipeline_funding_fmt: string;
  top_recipients: Array<{
    name: string;
    city: string;
    state: string;
    type: string;
    awards_count: number;
    total_awarded: number;
    total_awarded_fmt: string;
  }>;
  recent_awards: Array<{
    id: number;
    title: string;
    recipient: string;
    agency: string;
    amount: number;
    amount_fmt: string;
    year: number;
    state: string;
  }>;
  active_solicitations: Array<{
    id: number;
    solicitation_number: string;
    name: string;
    agency: string;
    total_funding: number;
    funding_fmt: string;
    status: string;
  }>;
  top_patents: Array<{
    id: number;
    number: string;
    title: string;
    assignee: string;
    date: string | null;
  }>;
  patent_count: number;
}

export interface TechCostMetric {
  name: string;
  unit: string;
  baseline_2024: number;
  baseline_fmt: string;
  target_2030: number;
  target_2030_fmt: string;
  target_2035: number;
  target_2035_fmt: string;
  reduction_pct: string;
  primary_driver: string;
}

export interface TechPerformanceMetric {
  name: string;
  unit: string;
  baseline_2024: number;
  baseline_fmt: string;
  target_2030: number;
  target_2030_fmt: string;
  target_2035: number;
  target_2035_fmt: string;
  improvement_pct: string;
  primary_driver: string;
}

export interface TechCostPerformance {
  cost_metric: TechCostMetric;
  performance_metric: TechPerformanceMetric;
  learning_rate: string;
  earthshot_goal: string;
}

export interface TechSubsystemNode {
  id: string;
  name: string;
  category: string;
  x: number;
  y: number;
  icon: string;
  summary: string;
  operatingValue?: string;
  materials?: string;
  failureMode?: string;
  frontierBottleneck?: string;
  activeResearch?: string;
}

export interface FuelsMatrixItem {
  id: string;
  name: string;
  carrier_name: string;
  category_name: string;
  chemical_formula: string;
  carbon_intensity_ci: string;
  energy_density_gravimetric: string;
  energy_density_volumetric: string;
  feedstock_pathway: string;
  drop_in_compatibility: string;
  policy_incentives: string;
  trl_current: number;
  trl_target: number;
  headline: string;
}

export interface FrontierMatrixItem {
  id: string;
  name: string;
  category_id: string;
  category_name: string;
  sector: string;
  fuel_vector: string;
  vector_type?: 'hardware' | 'fuel_carrier' | 'hybrid';
  trl_current: number;
  trl_target: number;
  cost_metric_name: string;
  cost_baseline_fmt: string;
  cost_target_2030_fmt: string;
  cost_reduction_pct_num: number;
  cost_reduction_pct_str: string;
  perf_metric_name: string;
  perf_baseline_fmt: string;
  perf_target_2030_fmt: string;
  perf_improvement_pct_num: number;
  perf_improvement_pct_str: string;
  learning_rate: string;
  earthshot_goal: string;
  tracked_capital_usd: number;
  tracked_capital_fmt: string;
  award_count: number;
  active_solicitations_count: number;
  primary_bottleneck: string;
  moonshot_goal: string;
}

export interface TechDossier {
  id: string;
  name: string;
  category_id: string;
  category_name: string;
  headline: string;
  trl_current: number;
  trl_target: number;
  keywords: string[];
  sector: string;
  fuel_vector: string;
  vector_type?: 'hardware' | 'fuel_carrier' | 'hybrid';
  fuel_profile?: TechFuelProfile;
  plain_english: {
    what_is_it: string;
    how_it_works: string;
    why_it_matters: string;
    macro_problem_solved: string;
  };
  evolution: {
    past: string;
    present: string;
    future: string;
  };
  frontier: {
    moonshot_goal: string;
    kpis: TechKPI[];
    bottlenecks: string[];
    active_research_tracks: string[];
  };
  cost_performance?: TechCostPerformance;
  radar_scores: Record<string, number>;
  radar_data: TechRadarPoint[];
  trl_progression: TechTRLStage[];
  subsystems?: TechSubsystemNode[];
  trade_offs: {
    strengths: string[];
    weaknesses: string[];
    competing_technologies: string[];
  };
  evidence: TechEvidence;
}

export interface TechAIInsights {
  technology_id: string;
  technology_name: string;
  question: string;
  executive_synthesis: string;
  engineering_deep_dive: string;
  frontier_research_tracks: string[];
  strategic_recommendations: string[];
  model_used: string;
  cached: boolean;
}

// -------------------------------------------------------------
// Grounded RAG "VP of Innovation" AI Chat Interfaces & Streamer
// -------------------------------------------------------------

export interface ChatOpportunityCitation {
  citation_id: string;
  id: number;
  solicitation_number: string;
  name: string;
  agency: string;
  status: string;
  total_funding?: number;
  max_per_award?: number;
  cost_share_pct?: number;
  due_date?: string;
  url: string;
  external_url?: string;
}

export interface ChatAwardCitation {
  citation_id: string;
  id: number;
  project_title?: string;
  recipient_name?: string;
  award_amount?: number;
  agency?: string;
  year?: number;
  state?: string;
  pi_name?: string;
  url: string;
}

export interface ChatContactCitation {
  citation_id: string;
  id: number;
  name: string;
  title?: string;
  institution?: string;
  email?: string;
  state?: string;
  role_type?: string;
  awards_count?: number;
  total_funding?: number;
  url: string;
}

export interface ChatTechnologyCitation {
  id: string;
  name: string;
  headline?: string;
  summary?: string;
  trl_current?: number;
  trl_target?: number;
}

export interface ChatOrganizationCitation {
  citation_id: string;
  id: number;
  name: string;
  recipient_type?: string;
  city?: string;
  state?: string;
  sector?: string;
  primary_technology?: string;
  total_funding?: number;
  awards_count?: number;
  stage?: string;
  url: string;
}

export interface PolicyStandard {
  id: string;
  code_identifier: string;
  title: string;
  short_title?: string;
  category: 'safety_code' | 'interconnection_rule' | 'tax_incentive' | 'state_statute' | 'emissions_standard' | 'federal_mandate' | 'environmental_permitting' | string;
  jurisdiction_level: 'federal' | 'state' | 'rto_iso' | 'municipal' | 'international' | string;
  jurisdiction_state?: string;
  status: 'active' | 'proposed' | 'under_revision' | 'superseded' | string;
  effective_year?: number;
  sunset_year?: number;
  latest_revision?: string;
  executive_summary: string;
  compliance_mandate: string;
  commercial_friction_points?: string;
  associated_incentives?: string;
  official_source_url?: string;
  linked_technologies_count?: number;
  linked_opportunities_count?: number;
  active_opportunities_count?: number;
  total_pipeline_funding_usd?: number;
}

export interface PolicyTechItem {
  id: string;
  code_identifier: string;
  title: string;
  short_title?: string;
  category: string;
  jurisdiction_level: string;
  jurisdiction_state?: string;
  relevance_type: string;
  compliance_impact: 'critical_gate' | 'cost_driver' | 'accelerator_tailwind' | string;
  impact_summary?: string;
  compliance_mandate: string;
  commercial_friction_points?: string;
  associated_incentives?: string;
  official_source_url?: string;
}

export interface PolicyDossier extends PolicyStandard {
  statutory_intent?: string;
  linked_technologies: Array<{
    technology_id: string;
    technology_name: string;
    relevance_type: string;
    compliance_impact: string;
    impact_summary?: string;
  }>;
  linked_fuels: Array<{
    fuel_vector: string;
    lifecycle_ci_threshold?: string;
    impact_summary?: string;
  }>;
  linked_opportunities: Array<{
    id: number;
    solicitation_number: string;
    name: string;
    agency: string;
    status: string;
    link_reason: string;
  }>;
}

export interface RegulatoryProceeding {
  id: string;
  docket_number: string;
  commission: string;
  jurisdiction_level: 'state' | 'federal' | 'rto_iso' | string;
  jurisdiction_state?: string;
  title: string;
  short_title?: string;
  topic_category: 'large_load_interconnection' | 'storage_procurement' | 'thermal_networks' | 'interconnection_reform' | 'vpp_rate_design' | 'transmission_planning' | 'clean_firm_procurement' | string;
  status: 'active' | 'staff_whitepaper' | 'public_comment' | 'order_issued' | 'implementation' | string;
  open_date?: string | null;
  comment_deadline?: string | null;
  expected_order_date?: string | null;
  executive_summary: string;
  innovation_impact: string;
  commercial_tailwinds?: string;
  commercial_friction_points?: string;
  key_filings_summary?: string;
  official_docket_url?: string;
  linked_technologies_count?: number;
  linked_organizations_count?: number;
}

export interface ProceedingTechItem {
  id: string;
  docket_number: string;
  commission: string;
  jurisdiction_level: string;
  jurisdiction_state?: string;
  title: string;
  short_title?: string;
  topic_category: string;
  status: string;
  impact_level: 'high_catalyst' | 'critical_gate' | 'market_expansion' | 'cost_driver' | string;
  commercial_vector?: string;
  impact_summary?: string;
  executive_summary: string;
  innovation_impact: string;
  commercial_tailwinds?: string;
  commercial_friction_points?: string;
  official_docket_url?: string;
}

export interface ProceedingDossier extends RegulatoryProceeding {
  linked_technologies: Array<{
    technology_id: string;
    technology_name: string;
    impact_level: string;
    commercial_vector?: string;
    impact_summary?: string;
  }>;
  linked_organizations: Array<{
    organization_id: number;
    organization_name: string;
    role: string;
  }>;
  linked_opportunities: Array<{
    id: number;
    solicitation_number: string;
    name: string;
    agency: string;
    status: string;
    link_reason: string;
  }>;
}

export interface ProceedingMacroStats {
  total_proceedings: number;
  total_technology_linkages: number;
  total_organization_linkages: number;
  commissions_breakdown: Record<string, number>;
  topics_breakdown: Record<string, number>;
  states_breakdown: Record<string, number>;
  active_commissions_count: number;
}

export interface ChatPolicyCitation {
  citation_id: string;
  id: string;
  code_identifier: string;
  title: string;
  short_title?: string;
  category: string;
  jurisdiction_level: string;
  jurisdiction_state?: string;
  compliance_mandate: string;
  commercial_friction_points?: string;
  associated_incentives?: string;
  official_source_url?: string;
  url: string;
}

export interface ChatCitationsMetadata {
  opportunities: ChatOpportunityCitation[];
  awards: ChatAwardCitation[];
  organizations?: ChatOrganizationCitation[];
  contacts: ChatContactCitation[];
  technologies?: ChatTechnologyCitation[];
  policies?: ChatPolicyCitation[];
  macro_impacts?: {
    primary_sectors?: string[];
    primary_fuels?: string[];
    commercial_stages?: Array<{ stage: string; funding_focus: string }>;
  };
  statistics: {
    retrieved_opportunities_count: number;
    retrieved_awards_count: number;
    retrieved_organizations_count?: number;
    retrieved_contacts_count: number;
    retrieved_policies_count?: number;
    sample_total_funding?: number;
    sample_avg_award?: number;
  };
}


export interface ChatPresetCategory {
  id: string;
  name: string;
  icon: string;
  description: string;
  prompts: string[];
}

export interface ChatMessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: ChatCitationsMetadata;
  isStreaming?: boolean;
  timestamp: string;
}

export interface TavusStatus {
  tavus_configured: boolean;
  persona_id: string | null;
  replica_id: string | null;
  supported_features: string[];
}

export interface TavusSetKeyPayload {
  api_key?: string;
  persona_id?: string;
  replica_id?: string;
}

export interface TavusCreateConversationPayload {
  user_role?: string;
  conversation_name?: string;
  persona_id?: string;
  replica_id?: string;
  custom_greeting?: string;
  conversational_context?: string;
  api_key?: string;
}

export interface TavusConversationResponse {
  conversation_id: string;
  conversation_url: string;
  status: string;
  greeting?: string;
  user_role?: string;
  created_at?: string;
  citations?: ChatCitationsMetadata;
  context_summary?: string;
}

export interface TavusTechBreakdownItem {
  name: string;
  domain_id: string;
  total_funding: number;
  awards_count: number;
  formatted_funding?: string;
}

export interface TavusSyncIntelligenceResponse {
  detected_topic: string;
  active_query: string;
  detected_agency?: string;
  technology_breakdown?: TavusTechBreakdownItem[];
  citations: ChatCitationsMetadata;
  summary?: string;
  stats: {
    total_funding: number;
    awards_count: number;
    opportunities_count: number;
    organizations_count: number;
  };
}

export async function* streamChatCompletion(
  query: string,
  history: Array<{ role: string; content: string }>,
  apiKey?: string,
  model?: string,
  userRole?: string
): AsyncGenerator<{ type: 'retrieval' | 'token' | 'review_complete' | 'done'; data?: ChatCitationsMetadata; token?: string; reviewed_text?: string }> {
  const headers: Record<string, string> = {
    ...getAuthHeaders(),
    'Content-Type': 'application/json',
  };

  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers,
    body: JSON.stringify({ query, history, api_key: apiKey, model, user_role: userRole }),
  });

  if (!response.ok) {
    const errText = await response.text().catch(() => '');
    throw new Error(`Chat streaming error (${response.status}): ${errText || response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('ReadableStream not available');

  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    let currentEvent = 'message';
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      if (trimmed.startsWith('event:')) {
        currentEvent = trimmed.slice(6).trim();
      } else if (trimmed.startsWith('data:')) {
        const rawData = trimmed.slice(5).trim();
        if (!rawData) continue;
        try {
          const parsed = JSON.parse(rawData);
          if (currentEvent === 'retrieval') {
            yield { type: 'retrieval', data: parsed };
          } else if (currentEvent === 'token') {
            yield { type: 'token', token: parsed.token };
          } else if (currentEvent === 'review_complete') {
            yield { type: 'review_complete', reviewed_text: parsed.reviewed_text, data: parsed.citations };
          } else if (currentEvent === 'done') {
            yield { type: 'done' };
          }
        } catch {
          // If plain text token
          if (currentEvent === 'token') {
            yield { type: 'token', token: rawData };
          }
        }
      }
    }
  }
}

// ── 60-Day Live Corpus Daily Activity & Momentum Types ────────────────────────

export interface DailyOpportunitySample {
  id: number;
  solicitation_number: string;
  name: string;
  agency: string;
  jurisdiction: string;
  total_funding?: number;
  funding_formatted: string;
  status?: string;
}

export interface DailyCorpusActivityPoint {
  date: string;
  label: string;
  day_of_week: string;
  opportunities_count: number;
  total_capital: number;
  capital_formatted: string;
  capital_millions: number;
  sample_opportunities: DailyOpportunitySample[];
  // Year-over-Year (2025 Prior Year) Comparative Data
  prior_year_date?: string;
  prior_year_opportunities_count?: number;
  prior_year_capital?: number;
  prior_year_capital_millions?: number;
  prior_year_capital_formatted?: string;
  yoy_daily_change_pct?: number;
}

export interface CorpusDailyActivityKPIs {
  total_opportunities: number;
  total_capital: number;
  total_capital_formatted: string;
  daily_avg_opportunities: number;
  daily_avg_capital: number;
  daily_avg_capital_formatted: string;
  prior_period_opps: number;
  recent_period_opps: number;
  momentum_pct: number;
  momentum_status: 'accelerating' | 'steady' | 'decelerating';
  momentum_label: string;
  peak_day: {
    date: string;
    label: string;
    count: number;
    capital: number;
    capital_formatted: string;
  };
  recent_7d_opps: number;
  recent_7d_capital: number;
  recent_7d_capital_formatted: string;
  // Year-over-Year (YoY) Growth Metrics
  prior_year_total_opportunities?: number;
  prior_year_total_capital?: number;
  prior_year_total_capital_formatted?: string;
  yoy_opportunities_growth_pct?: number;
  yoy_capital_growth_pct?: number;
  yoy_label?: string;
  annual_trajectory?: Array<{
    year: number;
    opps: number;
    capital: number;
    capital_formatted: string;
  }>;
}

export interface CorpusDailyActivityResponse {
  days: number;
  ref_date: string;
  start_date: string;
  data: DailyCorpusActivityPoint[];
  kpis: CorpusDailyActivityKPIs;
}

export async function fetchCorpusDailyActivity(days: number = 60): Promise<CorpusDailyActivityResponse> {
  try {
    const res = await fetch(`/api/trends/corpus-daily-activity?days=${days}`, {
      headers: { ...getAuthHeaders() },
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to fetch live corpus daily activity from backend, using fallback', err);
  }

  // Resilient fallback generator if backend is unavailable
  return generateFallbackCorpusDailyActivity(days);
}

function generateFallbackCorpusDailyActivity(days: number = 60): CorpusDailyActivityResponse {
  const refDate = new Date(2026, 8, 1); // Sep 1, 2026
  const data: DailyCorpusActivityPoint[] = [];
  let totalOpps = 0;
  let totalCapital = 0;
  let priorYearTotalOpps = 0;
  let priorYearTotalCapital = 0;

  const sampleAgencies = ['DOE', 'NYSERDA', 'CEC', 'ARPA-E', 'MassCEC', 'NSF', 'Con Edison', 'National Grid'];
  const sampleTitles = [
    'Energy Innovation Deep Decarbonization Accelerator',
    'Advanced Long-Duration Grid Battery Demo',
    'NextGen High-Temperature Heat Pumps for Multi-Family',
    'Offshore Wind Transmission High-Voltage Interconnect',
    'Hydrogen Fuel Cell Heavy Transport Pilot',
    'Grid-Interactive Efficient Building (GEB) Scale-Up',
    'Zero-Emission Distributed Energy Resources (DERs)',
    'Community Microgrid & Virtual Power Plant (VPP) FOA',
  ];

  const halfWindow = Math.floor(days / 2);
  let priorOpps = 0;
  let recentOpps = 0;
  let recent7dOpps = 0;
  let recent7dCapital = 0;
  let peakDay = { date: '', label: '', count: 0, capital: 0, capital_formatted: '$0' };

  for (let i = days - 1; i >= 0; i--) {
    const dayDate = new Date(refDate);
    dayDate.setDate(refDate.getDate() - i);
    const dayOfWeek = dayDate.toLocaleDateString('en-US', { weekday: 'short' });
    const isWeekend = dayDate.getDay() === 0 || dayDate.getDay() === 6;

    const dayIndexFromStart = days - 1 - i;
    // recency acceleration factor
    const recencyFactor = 0.8 + (dayIndexFromStart / days) * 0.8;
    const baseCount = isWeekend ? (Math.random() > 0.6 ? 1 : 0) : Math.floor(2 + Math.random() * 4 * recencyFactor);
    const count = i === 0 ? Math.max(3, baseCount) : baseCount;

    let dayCap = 0;
    const sampleOpps: DailyOpportunitySample[] = [];
    for (let c = 0; c < count; c++) {
      const grantAmount = (1.5 + Math.random() * 25) * 1_000_000;
      dayCap += grantAmount;
      if (sampleOpps.length < 3) {
        sampleOpps.push({
          id: 1000 + dayIndexFromStart * 10 + c,
          solicitation_number: `PON ${5800 + (dayIndexFromStart * 3 + c) % 800}`,
          name: sampleTitles[(dayIndexFromStart + c) % sampleTitles.length],
          agency: sampleAgencies[(dayIndexFromStart + c) % sampleAgencies.length],
          jurisdiction: 'state_ny',
          total_funding: grantAmount,
          funding_formatted: `$${(grantAmount / 1_000_000).toFixed(1)}M`,
          status: 'open',
        });
      }
    }

    // Prior Year (2025) baseline for the same calendar date
    const prevYearCount = Math.max(0, isWeekend ? (Math.random() > 0.7 ? 1 : 0) : Math.floor(1 + Math.random() * 3));
    const prevYearCap = prevYearCount * (3.5 + Math.random() * 12) * 1_000_000;

    totalOpps += count;
    totalCapital += dayCap;
    priorYearTotalOpps += prevYearCount;
    priorYearTotalCapital += prevYearCap;

    if (dayIndexFromStart < halfWindow) {
      priorOpps += count;
    } else {
      recentOpps += count;
    }

    if (i < 7) {
      recent7dOpps += count;
      recent7dCapital += dayCap;
    }

    const label = dayDate.toLocaleDateString('en-US', { month: 'short', day: '2-digit' });
    const dateStr = dayDate.toISOString().split('T')[0];

    const prevYearDate = new Date(dayDate);
    prevYearDate.setFullYear(prevYearDate.getFullYear() - 1);
    const prevYearDateStr = prevYearDate.toISOString().split('T')[0];

    if (count > peakDay.count || (count === peakDay.count && dayCap > peakDay.capital)) {
      peakDay = {
        date: dateStr,
        label,
        count,
        capital: dayCap,
        capital_formatted: `$${(dayCap / 1_000_000).toFixed(1)}M`,
      };
    }

    const yoyDailyChange = prevYearCount > 0
      ? parseFloat((((count - prevYearCount) / prevYearCount) * 100).toFixed(1))
      : count > 0 ? 100 : 0;

    data.push({
      date: dateStr,
      label,
      day_of_week: dayOfWeek,
      opportunities_count: count,
      total_capital: dayCap,
      capital_formatted: `$${(dayCap / 1_000_000).toFixed(1)}M`,
      capital_millions: parseFloat((dayCap / 1_000_000).toFixed(2)),
      prior_year_date: prevYearDateStr,
      prior_year_opportunities_count: prevYearCount,
      prior_year_capital: prevYearCap,
      prior_year_capital_millions: parseFloat((prevYearCap / 1_000_000).toFixed(2)),
      prior_year_capital_formatted: `$${(prevYearCap / 1_000_000).toFixed(1)}M`,
      yoy_daily_change_pct: yoyDailyChange,
      sample_opportunities: sampleOpps,
    });
  }

  const momentumPct = priorOpps > 0 ? parseFloat((((recentOpps - priorOpps) / priorOpps) * 100).toFixed(1)) : 0;
  const momentumStatus = momentumPct > 7 ? 'accelerating' : momentumPct < -7 ? 'decelerating' : 'steady';
  const momentumLabel = momentumStatus === 'accelerating'
    ? `Speeding Up (+${momentumPct}% vs prior ${halfWindow}d)`
    : momentumStatus === 'decelerating'
    ? `Slowing Down (${momentumPct}% vs prior ${halfWindow}d)`
    : `Steady Cadence (${momentumPct > 0 ? '+' : ''}${momentumPct}% vs prior ${halfWindow}d)`;

  const yoyOppsGrowth = priorYearTotalOpps > 0 ? parseFloat((((totalOpps - priorYearTotalOpps) / priorYearTotalOpps) * 100).toFixed(1)) : 0;
  const yoyCapitalGrowth = priorYearTotalCapital > 0 ? parseFloat((((totalCapital - priorYearTotalCapital) / priorYearTotalCapital) * 100).toFixed(1)) : 0;

  return {
    days,
    ref_date: '2026-09-01',
    start_date: data[0]?.date || '2026-07-04',
    data,
    kpis: {
      total_opportunities: totalOpps,
      total_capital: totalCapital,
      total_capital_formatted: `$${(totalCapital / 1_000_000_000).toFixed(2)}B`,
      daily_avg_opportunities: parseFloat((totalOpps / days).toFixed(1)),
      daily_avg_capital: totalCapital / days,
      daily_avg_capital_formatted: `$${(totalCapital / days / 1_000_000).toFixed(1)}M`,
      prior_period_opps: priorOpps,
      recent_period_opps: recentOpps,
      momentum_pct: momentumPct,
      momentum_status: momentumStatus,
      momentum_label: momentumLabel,
      peak_day: peakDay,
      recent_7d_opps: recent7dOpps,
      recent_7d_capital: recent7dCapital,
      recent_7d_capital_formatted: `$${(recent7dCapital / 1_000_000).toFixed(1)}M`,
      // Year-over-Year KPIs
      prior_year_total_opportunities: priorYearTotalOpps,
      prior_year_total_capital: priorYearTotalCapital,
      prior_year_total_capital_formatted: `$${(priorYearTotalCapital / 1_000_000_000).toFixed(2)}B`,
      yoy_opportunities_growth_pct: yoyOppsGrowth,
      yoy_capital_growth_pct: yoyCapitalGrowth,
      yoy_label: `+${yoyOppsGrowth}% Opps / +${yoyCapitalGrowth}% Capital vs 2025`,
      annual_trajectory: [
        { year: 2024, opps: Math.round(priorYearTotalOpps * 0.78), capital: priorYearTotalCapital * 0.76, capital_formatted: `$${((priorYearTotalCapital * 0.76) / 1_000_000_000).toFixed(2)}B` },
        { year: 2025, opps: priorYearTotalOpps, capital: priorYearTotalCapital, capital_formatted: `$${(priorYearTotalCapital / 1_000_000_000).toFixed(2)}B` },
        { year: 2026, opps: totalOpps, capital: totalCapital, capital_formatted: `$${(totalCapital / 1_000_000_000).toFixed(2)}B` },
      ],
    },
  };
}

// -------------------------------------------------------------
// System Administration Email Hub & Correspondence Interfaces
// -------------------------------------------------------------

export interface EmailAttachmentMeta {
  filename: string;
  size?: number;
  content_type?: string;
  path?: string;
}

export interface AdminEmailCampaign {
  id: number;
  user_id?: number | null;
  name: string;
  template_type: string;
  subject: string;
  body_text: string;
  body_html?: string | null;
  footer_text?: string | null;
  attachments: EmailAttachmentMeta[];
  target_criteria?: Record<string, any>;
  total_recipients: number;
  sent_count: number;
  failed_count: number;
  status: 'draft' | 'sending' | 'completed' | 'partial_failure' | 'failed' | string;
  error_summary?: string | null;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface AdminEmailLog {
  id: number;
  campaign_id: number;
  contact_id?: number | null;
  recipient_name: string;
  recipient_email: string;
  institution_name?: string | null;
  status: 'queued' | 'sent' | 'failed' | string;
  error_message?: string | null;
  message_id?: string | null;
  sent_at?: string | null;
  created_at: string;
}

export interface ContactEmailThread {
  id: number;
  contact_id: number;
  contact_email: string;
  contact_name: string;
  institution_name?: string | null;
  technology_area?: string | null;
  status: 'no_outreach' | 'pending_reply' | 'replied' | 'interested' | 'meeting_scheduled' | 'joined' | 'opted_out' | 'closed' | string;
  total_messages: number;
  outbound_count: number;
  inbound_count: number;
  unread_inbound_count: number;
  first_contacted_at?: string | null;
  last_contacted_at?: string | null;
  last_inbound_at?: string | null;
  last_activity_at?: string | null;
  conversation_summary?: string | null;
  key_takeaways: string[];
  next_action?: string | null;
  sentiment?: 'positive' | 'warm' | 'neutral' | 'unresponsive' | 'negative' | string;
}

export interface ContactEmailMessage {
  id: number;
  thread_id: number;
  contact_id: number;
  campaign_id?: number | null;
  message_id?: string | null;
  direction: 'outbound' | 'inbound';
  from_email: string;
  from_name?: string | null;
  to_email: string;
  to_name?: string | null;
  subject: string;
  snippet?: string | null;
  body_text: string;
  body_html?: string | null;
  has_attachments: boolean;
  attachments: (string | EmailAttachmentMeta)[];
  is_read: boolean;
  sent_at: string;
  synced_at: string;
  summary?: string | null;
}

export interface AdminEmailStatusResponse {
  admin_email: string;
  admin_name: string;
  display_name: string;
  smtp_host: string;
  smtp_port: number;
  imap_host: string;
  imap_port: number;
  default_footer: string;
  telemetry: {
    total_contacts_in_directory: number;
    contacts_with_direct_email: number;
    total_campaigns_dispatched: number;
    tracked_threads: number;
    unread_inbound_messages: number;
    active_engaged_conversations: number;
  };
  account_info: {
    primary_admin: string;
    service_provider: string;
    protocol: string;
  };
}

export interface AdminEmailConnectionTestResponse {
  smtp: {
    success: boolean;
    message: string;
    host: string;
    user: string;
  };
  imap: {
    success: boolean;
    message: string;
    host: string;
    user: string;
  };
  all_healthy: boolean;
  timestamp: string;
}

export interface EmailTemplate {
  id: string;
  name: string;
  category: string;
  default_subject: string;
  default_body: string;
}

export interface SendEmailRequestPayload {
  name: string;
  template_type: string;
  subject: string;
  body_text: string;
  body_html?: string;
  footer_text?: string;
  recipient_mode: 'ids' | 'all' | 'filter';
  contact_ids?: number[];
  filter_criteria?: {
    category?: string;
    role_type?: string;
    technology?: string;
    sector?: string;
    state?: string;
    deliverable_only?: boolean;
  };
}

export interface NewsItemLink {
  id?: number;
  element_type: 'opportunity' | 'organization' | 'program' | 'award' | 'technology' | 'policy' | 'proceeding' | 'sector' | 'recipient' | string;
  element_id: string;
  element_title: string;
  element_url_path: string;
  link_rationale: string;
  confidence_score?: number;
  created_at?: string;
}

export interface NewsTickerItem {
  id: number;
  title: string;
  url: string;
  source_name: string;
  source_domain?: string;
  published_at?: string;
  time_ago?: string;
  summary: string;
  sentiment: 'breakthrough' | 'commercial' | 'regulatory' | 'grant_awarded' | 'funding_round' | 'milestone' | 'neutral' | string;
  category_tag: string;
  relevance_score: number;
  primary_link?: NewsItemLink | null;
  total_links_count: number;
}

export interface NewsTickerResponse {
  count: number;
  items: NewsTickerItem[];
  mode: string;
  cadence: string;
}

export interface NewsItemDetail {
  id: number;
  title: string;
  url: string;
  canonical_url: string;
  source_name: string;
  source_domain?: string;
  published_at?: string;
  author?: string;
  raw_content?: string;
  summary: string;
  sentiment: string;
  relevance_score: number;
  category_tag: string;
  is_active: boolean;
  created_at?: string;
  links: NewsItemLink[];
}

export interface NewsTelemetry {
  total_news_items: number;
  total_explicit_links: number;
  categories: Array<{ name: string; count: number }>;
  sources: Array<{ name: string; count: number }>;
  linkage_distribution: Array<{ element_type: string; count: number }>;
  ingestion_telemetry: {
    last_run_at?: string | null;
    items_added: number;
    links_created: number;
    status: string;
  };
}

export async function fetchNewsTicker(limit: number = 25): Promise<NewsTickerResponse> {
  const res = await fetch(`/api/news/ticker?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch news ticker feed');
  return res.json();
}

export async function fetchNewsDetail(newsId: number): Promise<NewsItemDetail> {
  const res = await fetch(`/api/news/${newsId}`);
  if (!res.ok) throw new Error(`Failed to fetch news item ${newsId}`);
  return res.json();
}

export async function fetchNewsTelemetry(): Promise<NewsTelemetry> {
  const res = await fetch('/api/news/stats');
  if (!res.ok) throw new Error('Failed to fetch news telemetry');
  return res.json();
}

export async function fetchNewsForElement(elementType: string, elementId: string): Promise<any> {
  const res = await fetch(`/api/news/element/${elementType}/${elementId}`);
  if (!res.ok) throw new Error(`Failed to fetch news for ${elementType}:${elementId}`);
  return res.json();
}

export async function triggerNewsIngestion(forceSeed: boolean = true): Promise<any> {
  const res = await fetch(`/api/news/ingest?force_seed=${forceSeed}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to trigger news ingestion');
  return res.json();
}

// --------------------------------------------------------------------------
// Strategy Intelligence & Research Architecture Engine API
// --------------------------------------------------------------------------

export interface StrategyProjectInputs {
  technologies?: string[];
  fuel_vector?: string;
  trl?: number;
  target_trl?: number;
  sponsor_type?: string;
  state?: string;
  target_agency?: string;
  budget?: string;
  cost_share_pct?: string;
  technical_bottlenecks?: string[];
  custom_wedge?: string;
}

export interface StrategyFunderInputs {
  org_name?: string;
  org_type?: string;
  mandate?: string;
  tech_focus?: string[];
  fuel_focus?: string;
  program_length_years?: string;
  annual_award_distribution?: string;
  program_philosophy?: string;
  program_pool?: string;
  award_cap?: string;
  target_trl_min?: number;
  target_trl_max?: number;
  solicitation_instrument?: string;
}

export interface StrategyResultPayload {
  mode: 'project_sponsor' | 'funding_organization';
  title: string;
  technology_profile?: any;
  org_profile?: any;
  executive_thesis?: string;
  program_blueprint_narrative?: string;
  program_pathway_timeline?: {
    total_years: string;
    annual_distribution_summary: string;
    milestone_roadmap: Array<{
      timeframe: string;
      focus: string;
      awards_target: string;
      gate_criterion: string;
    }>;
  };
  workstream_decomposition?: Array<{
    phase: string;
    trl_progression: string;
    objective: string;
    deliverables: string[];
    estimated_budget: string;
    target_funding_source: string;
  }>;
  capital_stacking_strategy?: Array<{
    layer: string;
    target_program: string;
    estimated_amount: string;
    cost_share_required: string;
    strategic_utility: string;
  }>;
  win_rate_optimizations?: string[];
  reviewer_red_flags_and_mitigation?: Array<{
    risk: string;
    mitigation: string;
  }>;
  opportunities_portfolio?: {
    likely_fit: any[];
    adjacent: any[];
    future_watch: any[];
  };
  historical_award_comps?: any[];
  awards_summary?: any;
  teaming_ecosystem?: any[];
  policy_and_tax_credits?: any[];
  solicitation_structure?: {
    instrument_name: string;
    total_pool: string;
    max_award_per_project: string;
    program_length?: string;
    annual_award_target?: string;
    phases: Array<{
      phase_name: string;
      duration: string;
      award_range: string;
      go_no_go_milestone: string;
    }>;
  };
  scoring_rubric?: Array<{
    criterion: string;
    description: string;
  }>;
  draft_foa_topics?: Array<{
    topic_id: string;
    scope: string;
    technical_targets: string[];
    cost_share_rule: string;
  }>;
  strategic_recommendations?: string[];
  whitespace_analysis?: Array<{
    technology_area: string;
    historical_awards_count: number;
    historical_funding_tracked: string;
    saturation_status: string;
    programmatic_gap_recommendation: string;
  }>;
  technology_kpis?: any[];
  co_funding_synergies?: any[];
  citations?: Record<string, { id: string; text: string; url?: string; data_type: string }>;
  generated_at?: string;
  llm_engine?: string;
}

export interface StrategyTemplatesResponse {
  project_sponsor_templates: Array<{
    id: string;
    name: string;
    sector: string;
    technology: string;
    fuel_vector: string;
    current_trl: number;
    target_trl: number;
    sponsor_type: string;
    state: string;
    target_agency: string;
    budget: string;
    cost_share_pct: string;
    technical_bottlenecks: string[];
  }>;
  funding_org_templates: Array<{
    id: string;
    name: string;
    org_name: string;
    org_type: string;
    mandate: string;
    tech_focus: string[];
    fuel_focus?: string;
    program_length_years?: string;
    annual_award_distribution?: string;
    program_philosophy?: string;
    program_pool: string;
    award_cap: string;
    target_trl_min: number;
    target_trl_max: number;
    solicitation_instrument: string;
  }>;
}

export async function fetchStrategyTemplates(): Promise<StrategyTemplatesResponse> {
  const res = await fetch('/api/strategy/templates');
  if (!res.ok) throw new Error('Failed to fetch strategy templates');
  return res.json();
}

export async function quickExecuteStrategy(payload: {
  mode: 'project_sponsor' | 'funding_organization';
  title?: string;
  inputs: Record<string, any>;
}): Promise<{ status: string; mode: string; title: string; results: StrategyResultPayload }> {
  const res = await fetch('/api/strategy/quick-execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Execution error' }));
    throw new Error(err.detail || 'Failed to execute strategy analysis');
  }
  return res.json();
}

export async function createStrategyWorkspace(payload: {
  mode: string;
  title?: string;
  inputs_json: Record<string, any>;
  creatorToken?: string;
}): Promise<any> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (payload.creatorToken) {
    headers['X-Creator-Token'] = payload.creatorToken;
  }
  const res = await fetch('/api/strategy', {
    method: 'POST',
    headers,
    body: JSON.stringify({
      mode: payload.mode,
      title: payload.title,
      inputs_json: payload.inputs_json
    })
  });
  if (!res.ok) throw new Error('Failed to create strategy workspace');
  return res.json();
}

export async function executeStrategyWorkspace(strategyId: number, creatorToken?: string): Promise<any> {
  const headers: Record<string, string> = {};
  if (creatorToken) {
    headers['X-Creator-Token'] = creatorToken;
  }
  const res = await fetch(`/api/strategy/${strategyId}/execute`, {
    method: 'POST',
    headers
  });
  if (!res.ok) throw new Error('Failed to execute strategy');
  return res.json();
}

export async function fetchStrategyDetail(strategyId: number, creatorToken?: string): Promise<any> {
  const headers: Record<string, string> = {};
  if (creatorToken) {
    headers['X-Creator-Token'] = creatorToken;
  }
  const res = await fetch(`/api/strategy/${strategyId}`, { headers });
  if (!res.ok) throw new Error(`Failed to fetch strategy ${strategyId}`);
  return res.json();
}

export async function downloadStrategyPdf(results: StrategyResultPayload, title?: string, mode?: string): Promise<void> {
  const res = await fetch('/api/strategy/export-pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ results, title, mode })
  });
  if (!res.ok) throw new Error('Failed to generate PDF');
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  const cleanTitle = (title || 'strategic_plan').replace(/[^a-zA-Z0-9_-]/g, '_');
  a.download = `${cleanTitle}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}








