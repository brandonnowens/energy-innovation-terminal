/**
 * Energy Innovation Terminal — First-Party Client Telemetry & Analytics Tracker
 * 
 * Manages persistent anonymous visitor identification, session lifecycle,
 * attribution parameters (UTMs/referrers), and event tracking without cookies
 * or third-party tracking scripts.
 */

import { API_BASE_URL } from '../api/client';

const STORAGE_ANON_KEY = 'eit_anon_id';
const STORAGE_SESSION_KEY = 'eit_session_id';
const STORAGE_SESSION_COUNT = 'eit_session_count';
const STORAGE_FIRST_SEEN = 'eit_first_seen';
const STORAGE_LAST_ACTIVE = 'eit_last_active';
const STORAGE_INITIAL_REFERRER = 'eit_initial_referrer';
const STORAGE_INITIAL_LANDING = 'eit_initial_landing';
const STORAGE_ATTRIBUTION = 'eit_attribution';

const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes of inactivity

function generateUUID(prefix: string = ''): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `${prefix}${crypto.randomUUID().replace(/-/g, '')}`;
  }
  const timestamp = Date.now().toString(36);
  const randomStr = Math.random().toString(36).substring(2, 10);
  return `${prefix}${timestamp}_${randomStr}`;
}

export interface ClientEnvironment {
  screen_resolution: string;
  viewport_size: string;
  client_timezone: string;
  language: string;
  touch_support: boolean;
  effective_connection?: string;
}

export interface AttributionData {
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  ref?: string;
  initial_referrer: string;
  initial_landing: string;
}

export interface TelemetryPayload {
  anon_id: string;
  session_id: string;
  action_type: string;
  endpoint: string;
  page_title?: string;
  referrer?: string;
  initial_referrer?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  screen_resolution?: string;
  viewport_size?: string;
  client_timezone?: string;
  language?: string;
  duration_ms?: number;
  event_data?: any;
}

class TelemetryTracker {
  private anonId: string = '';
  private sessionId: string = '';
  private sessionCount: number = 1;
  private attribution: AttributionData | null = null;
  private lastPagePath: string = '';
  private lastPageEnteredAt: number = Date.now();

  constructor() {
    if (typeof window !== 'undefined') {
      this.initAnonymousIdentity();
      this.initSession();
      this.initAttribution();
    }
  }

  private initAnonymousIdentity() {
    try {
      let existing = localStorage.getItem(STORAGE_ANON_KEY);
      if (!existing) {
        existing = generateUUID('anon_');
        localStorage.setItem(STORAGE_ANON_KEY, existing);
        localStorage.setItem(STORAGE_FIRST_SEEN, new Date().toISOString());
      }
      this.anonId = existing;
    } catch {
      this.anonId = generateUUID('anon_');
    }
  }

  private initSession() {
    try {
      const now = Date.now();
      const lastActive = parseInt(sessionStorage.getItem(STORAGE_LAST_ACTIVE) || '0', 10);
      let sessId = sessionStorage.getItem(STORAGE_SESSION_KEY);

      if (!sessId || (lastActive > 0 && now - lastActive > SESSION_TIMEOUT_MS)) {
        sessId = generateUUID('sess_');
        sessionStorage.setItem(STORAGE_SESSION_KEY, sessId);
        
        const count = parseInt(localStorage.getItem(STORAGE_SESSION_COUNT) || '0', 10) + 1;
        localStorage.setItem(STORAGE_SESSION_COUNT, count.toString());
        this.sessionCount = count;
      } else {
        this.sessionCount = parseInt(localStorage.getItem(STORAGE_SESSION_COUNT) || '1', 10);
      }

      sessionStorage.setItem(STORAGE_LAST_ACTIVE, now.toString());
      this.sessionId = sessId;
    } catch {
      this.sessionId = generateUUID('sess_');
    }
  }

  private initAttribution() {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const utm_source = urlParams.get('utm_source') || undefined;
      const utm_medium = urlParams.get('utm_medium') || undefined;
      const utm_campaign = urlParams.get('utm_campaign') || undefined;
      const utm_term = urlParams.get('utm_term') || undefined;
      const utm_content = urlParams.get('utm_content') || undefined;
      const ref = urlParams.get('ref') || undefined;

      let initialRef = localStorage.getItem(STORAGE_INITIAL_REFERRER);
      if (!initialRef) {
        initialRef = document.referrer || 'direct';
        localStorage.setItem(STORAGE_INITIAL_REFERRER, initialRef);
      }

      let initialLanding = localStorage.getItem(STORAGE_INITIAL_LANDING);
      if (!initialLanding) {
        initialLanding = window.location.pathname + window.location.search;
        localStorage.setItem(STORAGE_INITIAL_LANDING, initialLanding);
      }

      // If current URL contains UTM parameters, save them
      if (utm_source || utm_medium || utm_campaign || ref) {
        const attrObj: AttributionData = {
          utm_source,
          utm_medium,
          utm_campaign,
          utm_term,
          utm_content,
          ref,
          initial_referrer: initialRef,
          initial_landing: initialLanding
        };
        localStorage.setItem(STORAGE_ATTRIBUTION, JSON.stringify(attrObj));
        this.attribution = attrObj;
      } else {
        const stored = localStorage.getItem(STORAGE_ATTRIBUTION);
        if (stored) {
          try {
            this.attribution = JSON.parse(stored);
          } catch {
            this.attribution = { initial_referrer: initialRef, initial_landing: initialLanding };
          }
        } else {
          this.attribution = { initial_referrer: initialRef, initial_landing: initialLanding };
        }
      }
    } catch {
      this.attribution = { initial_referrer: 'direct', initial_landing: '/' };
    }
  }

  public getAnonymousId(): string {
    if (!this.anonId) this.initAnonymousIdentity();
    return this.anonId;
  }

  public getSessionId(): string {
    if (!this.sessionId) this.initSession();
    try {
      sessionStorage.setItem(STORAGE_LAST_ACTIVE, Date.now().toString());
    } catch {}
    return this.sessionId;
  }

  public getClientEnvironment(): ClientEnvironment {
    const isClient = typeof window !== 'undefined';
    return {
      screen_resolution: isClient ? `${window.screen.width}x${window.screen.height}` : '1920x1080',
      viewport_size: isClient ? `${window.innerWidth}x${window.innerHeight}` : '1440x900',
      client_timezone: isClient ? (Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC') : 'UTC',
      language: isClient ? (navigator.language || 'en-US') : 'en-US',
      touch_support: isClient ? ('ontouchstart' in window || navigator.maxTouchPoints > 0) : false,
      effective_connection: isClient && (navigator as any).connection ? (navigator as any).connection.effectiveType : undefined
    };
  }

  public getTelemetryHeaders(): Record<string, string> {
    const env = this.getClientEnvironment();
    const headers: Record<string, string> = {
      'X-Anonymous-ID': this.getAnonymousId(),
      'X-Session-ID': this.getSessionId(),
      'X-Client-Timezone': env.client_timezone,
      'X-Screen-Resolution': env.screen_resolution,
      'X-Viewport-Size': env.viewport_size,
    };

    if (this.attribution?.initial_referrer) {
      headers['X-Initial-Referrer'] = this.attribution.initial_referrer.substring(0, 200);
    }
    if (this.attribution?.utm_source) {
      headers['X-UTM-Source'] = this.attribution.utm_source.substring(0, 100);
    }
    if (this.attribution?.utm_medium) {
      headers['X-UTM-Medium'] = this.attribution.utm_medium.substring(0, 100);
    }
    if (this.attribution?.utm_campaign) {
      headers['X-UTM-Campaign'] = this.attribution.utm_campaign.substring(0, 100);
    }

    return headers;
  }

  public trackEvent(actionType: string, eventData?: any, endpointPath?: string) {
    if (typeof window === 'undefined') return;

    const env = this.getClientEnvironment();
    const path = endpointPath || window.location.pathname;
    const title = document.title || '';

    const payload: TelemetryPayload = {
      anon_id: this.getAnonymousId(),
      session_id: this.getSessionId(),
      action_type: actionType,
      endpoint: path,
      page_title: title,
      referrer: document.referrer || '',
      initial_referrer: this.attribution?.initial_referrer,
      utm_source: this.attribution?.utm_source,
      utm_medium: this.attribution?.utm_medium,
      utm_campaign: this.attribution?.utm_campaign,
      utm_term: this.attribution?.utm_term,
      utm_content: this.attribution?.utm_content,
      screen_resolution: env.screen_resolution,
      viewport_size: env.viewport_size,
      client_timezone: env.client_timezone,
      language: env.language,
      event_data: eventData
    };

    this.dispatchBeacon(payload);
  }

  public trackPageView(currentPath: string, pageTitle?: string) {
    if (typeof window === 'undefined') return;

    const now = Date.now();
    let timeOnPreviousPage = 0;
    if (this.lastPageEnteredAt > 0) {
      timeOnPreviousPage = now - this.lastPageEnteredAt;
    }

    this.lastPagePath = currentPath;
    this.lastPageEnteredAt = now;

    const env = this.getClientEnvironment();
    const title = pageTitle || document.title || '';

    const payload: TelemetryPayload = {
      anon_id: this.getAnonymousId(),
      session_id: this.getSessionId(),
      action_type: 'page_view',
      endpoint: currentPath,
      page_title: title,
      referrer: document.referrer || '',
      initial_referrer: this.attribution?.initial_referrer,
      utm_source: this.attribution?.utm_source,
      utm_medium: this.attribution?.utm_medium,
      utm_campaign: this.attribution?.utm_campaign,
      utm_term: this.attribution?.utm_term,
      utm_content: this.attribution?.utm_content,
      screen_resolution: env.screen_resolution,
      viewport_size: env.viewport_size,
      client_timezone: env.client_timezone,
      language: env.language,
      duration_ms: timeOnPreviousPage,
      event_data: {
        time_on_previous_page_ms: timeOnPreviousPage,
        session_visit_number: this.sessionCount
      }
    };

    this.dispatchBeacon(payload);
  }

  private dispatchBeacon(payload: TelemetryPayload) {
    const targetUrl = `${API_BASE_URL}/api/telemetry/event`;
    const jsonString = JSON.stringify(payload);

    // Prefer navigator.sendBeacon for reliable async delivery
    if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
      const blob = new Blob([jsonString], { type: 'application/json' });
      const success = navigator.sendBeacon(targetUrl, blob);
      if (success) return;
    }

    // Fallback to fetch with keepalive
    fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getTelemetryHeaders()
      },
      body: jsonString,
      keepalive: true
    }).catch(() => {});
  }
}

export const tracker = new TelemetryTracker();
