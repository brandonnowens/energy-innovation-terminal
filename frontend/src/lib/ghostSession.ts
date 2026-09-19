/**
 * Ghost.org session utilities for the Energy Innovation Terminal.
 * Ported from the AIxEnergy Map app (S:\aixenergy-global-project-map\src\lib\ghostSession.ts).
 *
 * Handles:
 *  - Reading / holding a Ghost identity JWT from the URL (magic-link return flow)
 *  - Parsing the postMessage payload sent by the Ghost auth-bridge iframe
 *  - Type guard for incoming postMessage events
 */

const JWT_PATTERN = /^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/;

/** sessionStorage keys for the token hold mechanism. */
export const GHOST_TOKEN_HOLD_KEY = 'aix_terminal_ghost_token_hold';
export const GHOST_TOKEN_HOLD_GEN_KEY = 'aix_terminal_ghost_token_hold_gen';

/**
 * Per-page-load generation ID.  A held token from a previous sign-in in the
 * same browser tab must not override a later session.
 */
const PAGE_HOLD_GENERATION =
  typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : `hold-${Math.random().toString(36).slice(2)}`;

// ---------------------------------------------------------------------------
// Token hold (survives URL rewrites within the same JS page load)
// ---------------------------------------------------------------------------

function readHeldToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    const generation = window.sessionStorage.getItem(GHOST_TOKEN_HOLD_GEN_KEY);
    if (generation !== PAGE_HOLD_GENERATION) return null;
    return window.sessionStorage.getItem(GHOST_TOKEN_HOLD_KEY);
  } catch {
    return null;
  }
}

function holdToken(token: string): void {
  if (typeof window === 'undefined') return;
  try {
    window.sessionStorage.setItem(GHOST_TOKEN_HOLD_KEY, token);
    window.sessionStorage.setItem(GHOST_TOKEN_HOLD_GEN_KEY, PAGE_HOLD_GENERATION);
  } catch {
    // Private-mode / quota — URL-capture still works synchronously.
  }
}

function clearHeldToken(): void {
  if (typeof window === 'undefined') return;
  try {
    window.sessionStorage.removeItem(GHOST_TOKEN_HOLD_KEY);
    window.sessionStorage.removeItem(GHOST_TOKEN_HOLD_GEN_KEY);
  } catch {
    // ignore
  }
}

export function clearGhostTokenHold(): void {
  clearHeldToken();
}

// ---------------------------------------------------------------------------
// URL token extraction (magic-link / bridge redirect return)
// ---------------------------------------------------------------------------

function decodeTokenValue(value: string): string | null {
  try {
    return decodeURIComponent(value.trim());
  } catch {
    return value.trim();
  }
}

/** Peek at a ghost_token in the URL without consuming (clearing) it. */
export function peekGhostTokenFromUrl(): string | null {
  if (typeof window === 'undefined') return null;

  const url = new URL(window.location.href);
  const queryToken = url.searchParams.get('ghost_token');
  if (queryToken) return decodeTokenValue(queryToken);

  const hash = window.location.hash.replace(/^#/, '');
  if (hash) {
    const hashParams = hash.startsWith('ghost_token=')
      ? new URLSearchParams(hash)
      : new URLSearchParams(hash.includes('?') ? hash.split('?').pop() ?? '' : hash);

    const hashToken = hashParams.get('ghost_token');
    if (hashToken) return decodeTokenValue(hashToken);

    const directMatch = window.location.hash.match(/^#ghost_token=(.+)$/);
    if (directMatch?.[1]) return decodeTokenValue(directMatch[1]);
  }

  return null;
}

/**
 * Read the ghost_token from the URL (or from the sessionStorage hold).
 * Stashes it for the lifetime of this page load so subsequent URL rewrites
 * (React Router replacing the hash) don't lose the token.
 */
export function readGhostTokenFromUrl(): string | null {
  const liveToken = peekGhostTokenFromUrl();
  if (liveToken) {
    holdToken(liveToken);
    return liveToken;
  }
  return readHeldToken();
}

/** Remove the ghost_token from the current URL after it has been consumed. */
export function clearGhostTokenFromUrl(): void {
  if (typeof window === 'undefined') return;

  const url = new URL(window.location.href);
  let changed = false;

  if (url.searchParams.has('ghost_token')) {
    url.searchParams.delete('ghost_token');
    changed = true;
  }

  if (url.hash.includes('ghost_token=')) {
    url.hash = '';
    changed = true;
  }

  if (changed) {
    const nextUrl = `${url.pathname}${url.search}${url.hash}`;
    window.history.replaceState({}, '', nextUrl || '/');
  }

  clearHeldToken();
}

// ---------------------------------------------------------------------------
// postMessage payload utilities
// ---------------------------------------------------------------------------

export interface GhostAuthMessage {
  type: 'aixenergy-ghost-token';
  token: string;
  member?: {
    uuid?: string | null;
    email?: string | null;
    name?: string | null;
  } | null;
}

export function isGhostAuthMessage(data: unknown): data is GhostAuthMessage {
  if (!data || typeof data !== 'object') return false;
  const msg = data as { type?: unknown; token?: unknown };
  return msg.type === 'aixenergy-ghost-token' && typeof msg.token === 'string';
}

/**
 * Parse a raw token string from the postMessage body.
 * The Ghost bridge may send a bare JWT or a JSON wrapper like {identity: "..."}.
 */
export function parseGhostSessionBody(body: string): string | null {
  const trimmed = body.trim();
  if (!trimmed) return null;
  if (JWT_PATTERN.test(trimmed)) return trimmed;
  try {
    const payload = JSON.parse(trimmed) as { identity?: string; token?: string };
    return payload.identity?.trim() || payload.token?.trim() || null;
  } catch {
    return null;
  }
}

export function ghostHandoffProfile(message: GhostAuthMessage): {
  name: string | null;
  email: string | null;
} {
  const member = message.member;
  if (!member || typeof member !== 'object') return { name: null, email: null };
  const name = typeof member.name === 'string' ? member.name.trim() : '';
  const email = typeof member.email === 'string' ? member.email.trim() : '';
  return { name: name || null, email: email || null };
}
