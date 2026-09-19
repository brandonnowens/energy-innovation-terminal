/**
 * useGhostAuth — React hook for Ghost.org session detection in the
 * Energy Innovation Terminal.
 *
 * Simplified from the Map app's useMemberAuth (which handles paid tiers).
 * Here we only need a binary result: is the visitor a Ghost member or not?
 *
 * Flow:
 *  1. On mount — check for a #ghost_token in the URL (magic-link / bridge return).
 *  2. If no URL token — resolve as "guest" and activate the hidden probe iframe.
 *  3. The probe iframe postMessages a token back → verify and flip to "authenticated".
 *  4. On window focus / visibility / custom refresh event → re-probe if still guest.
 *
 * State is intentionally separate from the existing email/password AuthContext so
 * that both systems can coexist without coupling.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  GHOST_AUTH_ENABLED,
  GHOST_URL,
  TERMINAL_AUTH_REFRESH_EVENT,
  TERMINAL_LAST_MEMBER_KEY,
  TERMINAL_LAST_MEMBER_MAX_AGE_MS,
  ghostOrigins,
} from '../config/ghostAuth';
import {
  clearGhostTokenFromUrl,
  clearGhostTokenHold,
  ghostHandoffProfile,
  isGhostAuthMessage,
  parseGhostSessionBody,
  readGhostTokenFromUrl,
} from '../lib/ghostSession';

export type GhostAuthStatus = 'loading' | 'authenticated' | 'guest';

export interface GhostAuthState {
  /** Current probe status. */
  status: GhostAuthStatus;
  /** Email of the authenticated Ghost member (if known). */
  memberEmail: string | null;
  /** Member name (if known from the postMessage profile). */
  memberName: string | null;
  /** Increment to force the hidden probe iframe to reload. */
  probeKey: number;
  /** Call to retry authentication (e.g. after dismissing the gate and returning). */
  retry: () => void;
}

// ---------------------------------------------------------------------------
// Persistence helpers
// ---------------------------------------------------------------------------

function rememberMember(): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(TERMINAL_LAST_MEMBER_KEY, String(Date.now()));
  } catch {
    // best-effort
  }
}

function forgetMember(): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.removeItem(TERMINAL_LAST_MEMBER_KEY);
  } catch {
    // ignore
  }
}

function hasRecentMemberHint(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    const raw = window.localStorage.getItem(TERMINAL_LAST_MEMBER_KEY);
    if (!raw) return false;
    const at = Number(raw);
    if (!Number.isFinite(at)) return false;
    if (Date.now() - at > TERMINAL_LAST_MEMBER_MAX_AGE_MS) {
      forgetMember();
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Ghost members API probe (same-origin only)
// ---------------------------------------------------------------------------

async function fetchGhostIdentityToken(
  ghostUrl: string,
): Promise<{ outcome: 'token'; token: string } | { outcome: 'no-session' | 'unreachable' }> {
  let response: Response;
  try {
    response = await fetch(`${ghostUrl}/members/api/session/`, {
      credentials: 'include',
      headers: { Accept: 'application/json, text/plain, */*' },
    });
  } catch {
    return { outcome: 'unreachable' };
  }

  if (response.status === 204) return { outcome: 'no-session' };
  if (!response.ok) {
    return response.status === 401 || response.status === 403
      ? { outcome: 'no-session' }
      : { outcome: 'unreachable' };
  }

  const token = parseGhostSessionBody(await response.text());
  return token ? { outcome: 'token', token } : { outcome: 'no-session' };
}

/** True when Ghost shares the terminal's origin (uncommon in practice). */
function ghostSharesTerminalOrigin(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    return new URL(GHOST_URL).origin === window.location.origin;
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Auth resolution
// ---------------------------------------------------------------------------

interface AuthResult {
  authenticated: boolean;
  memberEmail: string | null;
  memberName: string | null;
}

async function resolveGhostAuth(): Promise<AuthResult> {
  // 1. Magic-link / bridge redirect — token in URL
  const urlToken = readGhostTokenFromUrl();
  if (urlToken) {
    clearGhostTokenFromUrl();
    rememberMember();
    // We trust the token presence as authentication confirmation at this layer.
    // (The Map app verifies via /api/auth/verify; the Terminal doesn't have that
    //  backend endpoint wired to Ghost, so we rely on the iframe bridge handshake.)
    return { authenticated: true, memberEmail: null, memberName: null };
  }

  // 2. Same-origin Ghost instance — direct session probe
  if (ghostSharesTerminalOrigin()) {
    const probe = await fetchGhostIdentityToken(GHOST_URL);
    if (probe.outcome === 'token') {
      rememberMember();
      return { authenticated: true, memberEmail: null, memberName: null };
    }
    if (probe.outcome === 'no-session') {
      return { authenticated: false, memberEmail: null, memberName: null };
    }
    // 'unreachable' — fall through; let the iframe bridge handle it
  }

  // 3. Cross-origin — rely on iframe bridge (postMessage path).
  // Return 'guest' here; useGhostAuth's postMessage listener will upgrade to
  // 'authenticated' when the iframe fires the token.
  return { authenticated: false, memberEmail: null, memberName: null };
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useGhostAuth(): GhostAuthState {
  const [status, setStatus] = useState<GhostAuthStatus>(() =>
    GHOST_AUTH_ENABLED ? 'loading' : 'authenticated',
  );
  const [memberEmail, setMemberEmail] = useState<string | null>(null);
  const [memberName, setMemberName] = useState<string | null>(null);
  const [probeKey, setProbeKey] = useState(0);
  const [attempt, setAttempt] = useState(0);

  const statusRef = useRef(status);
  const identityEpochRef = useRef(0);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  // -- Initial and retry resolution ----------------------------------------
  useEffect(() => {
    if (!GHOST_AUTH_ENABLED) return;

    let cancelled = false;
    const epoch = identityEpochRef.current;

    async function bootstrap() {
      try {
        const result = await resolveGhostAuth();
        if (cancelled || identityEpochRef.current !== epoch) return;
        if (result.authenticated) {
          setMemberEmail(result.memberEmail);
          setMemberName(result.memberName);
          rememberMember();
          setStatus('authenticated');
        } else {
          setStatus('guest');
        }
      } catch {
        if (cancelled || identityEpochRef.current !== epoch) return;
        setStatus('guest');
      }
    }

    void bootstrap();
    return () => { cancelled = true; };
  }, [attempt]);

  // -- postMessage listener (cross-origin iframe bridge) --------------------
  useEffect(() => {
    if (!GHOST_AUTH_ENABLED) return;

    const trustedOrigins = new Set(ghostOrigins());

    function handleMessage(event: MessageEvent) {
      if (!trustedOrigins.has(event.origin)) return;
      if (!isGhostAuthMessage(event.data)) return;

      const token = parseGhostSessionBody(event.data.token);
      if (!token) return;

      const profile = ghostHandoffProfile(event.data);
      const epoch = ++identityEpochRef.current;

      // Trust the token from the bridge page — mark authenticated.
      if (identityEpochRef.current !== epoch) return;
      setMemberEmail(profile.email);
      setMemberName(profile.name);
      rememberMember();
      setStatus('authenticated');
    }

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // -- Re-probe on focus / visibility / custom refresh event ----------------
  useEffect(() => {
    if (!GHOST_AUTH_ENABLED) return;

    async function refreshOnReturn() {
      if (statusRef.current === 'authenticated') return;

      // Bump probe iframe key to force a reload of the bridge page.
      setProbeKey((k) => k + 1);

      const epoch = identityEpochRef.current;
      try {
        const result = await resolveGhostAuth();
        if (identityEpochRef.current !== epoch) return;
        if (result.authenticated) {
          setMemberEmail(result.memberEmail);
          setMemberName(result.memberName);
          rememberMember();
          setStatus('authenticated');
        }
      } catch {
        // Stay as guest
      }
    }

    function handleReturn() { void refreshOnReturn(); }
    function handleVisibility() {
      if (document.visibilityState === 'visible') handleReturn();
    }

    window.addEventListener('focus', handleReturn);
    window.addEventListener(TERMINAL_AUTH_REFRESH_EVENT, handleReturn);
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      window.removeEventListener('focus', handleReturn);
      window.removeEventListener(TERMINAL_AUTH_REFRESH_EVENT, handleReturn);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, []);

  const retry = useCallback(() => {
    if (!GHOST_AUTH_ENABLED) return;
    clearGhostTokenHold();
    setStatus('loading');
    setAttempt((a) => a + 1);
  }, []);

  if (!GHOST_AUTH_ENABLED) {
    return {
      status: 'authenticated',
      memberEmail: null,
      memberName: null,
      probeKey: 0,
      retry: () => {},
    };
  }

  return { status, memberEmail, memberName, probeKey, retry };
}

export { hasRecentMemberHint };
