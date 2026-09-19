/**
 * Ghost.org authentication configuration for the Energy Innovation Terminal.
 *
 * The terminal probes whether the visitor already has an active member session
 * on aixenergy.io (the Ghost publication). If they do, they get full access
 * immediately with no interruption. If not, a simple popup invites them to
 * create a free account.
 *
 * This is a frontend-only layer — no backend changes are required.
 * It runs alongside the existing email/password AuthContext without conflict.
 */

function resolveGhostAuthEnabled(): boolean {
  const flag = import.meta.env.VITE_GHOST_AUTH_ENABLED;
  if (flag === 'false') return false;
  if (flag === 'true') return true;
  // Gate by default in production builds so deploys can't accidentally ship an open terminal.
  return import.meta.env.PROD;
}

export const GHOST_AUTH_ENABLED = resolveGhostAuthEnabled();

export const GHOST_URL =
  (import.meta.env.VITE_GHOST_URL as string | undefined)?.replace(/\/$/, '') ??
  'https://www.aixenergy.io';

export const GHOST_SIGNIN_URL =
  (import.meta.env.VITE_GHOST_SIGNIN_URL as string | undefined) ??
  'https://www.aixenergy.io/#/portal/signin';

export const GHOST_SIGNUP_URL =
  (import.meta.env.VITE_GHOST_SIGNUP_URL as string | undefined) ??
  'https://www.aixenergy.io/#/portal/signup';

/**
 * Path on the Ghost site that reads the member session cookie and
 * postMessages a token back to the terminal iframe's parent.
 * Reuse the Map's bridge page — it sends the same {type, token} message format.
 */
export const GHOST_AUTH_BRIDGE_PATH =
  (import.meta.env.VITE_GHOST_AUTH_BRIDGE_PATH as string | undefined) ??
  '/map-auth-bridge/';

/** Custom event fired when the user closes the Ghost sign-in window. */
export const TERMINAL_AUTH_REFRESH_EVENT = 'aixenergy-terminal-auth-refresh';

/** sessionStorage key — marks that the visitor explicitly dismissed the gate. */
export const TERMINAL_GATE_DISMISSED_KEY = 'aix_terminal_gate_dismissed';

/** localStorage key — breadcrumb written after any verified Ghost session. */
export const TERMINAL_LAST_MEMBER_KEY = 'aix_terminal_last_member';

/** Breadcrumb older than this is ignored (45 days). */
export const TERMINAL_LAST_MEMBER_MAX_AGE_MS = 45 * 24 * 60 * 60 * 1000;

/**
 * Build the URL that the hidden auth-probe iframe will load.
 * The bridge page on Ghost reads the member session cookie and postMessages
 * a {type:"aixenergy-ghost-token", token} back to window.parent.
 */
export function ghostTerminalAuthEmbedUrl(): string {
  const parentOrigin =
    typeof window !== 'undefined' ? window.location.origin : '';
  const bridgeUrl = new URL(GHOST_AUTH_BRIDGE_PATH, `${GHOST_URL}/`);
  bridgeUrl.searchParams.set('embed', '1');
  if (parentOrigin) {
    bridgeUrl.searchParams.set('parent_origin', parentOrigin);
  }
  return bridgeUrl.toString();
}

/** All trusted Ghost origins that may postMessage tokens back to us. */
export function ghostOrigins(): string[] {
  const base = new URL(GHOST_URL).origin;
  return [...new Set([base, 'https://aixenergy.io', 'https://www.aixenergy.io'])];
}
